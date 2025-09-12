"""
DB機能は完全削除されました。互換性のため最低限のスタブを提供します。
ファイルベースの冪等性チェック機能を追加しました。
"""

from __future__ import annotations
import os
import time
import json
from pathlib import Path
from typing import Dict, Any

# アクションログの保存ディレクトリ
ACTION_LOG_DIR = Path("logs/action_logs")


def _ensure_action_log_dir():
    """アクションログディレクトリの作成"""
    ACTION_LOG_DIR.mkdir(parents=True, exist_ok=True)


def _get_action_log_file(account: str) -> Path:
    """アカウント別のアクションログファイルパスを取得"""
    _ensure_action_log_dir()
    return ACTION_LOG_DIR / f"{account}_actions.json"


def _load_action_logs(account: str) -> Dict[str, Any]:
    """アクションログの読み込み"""
    log_file = _get_action_log_file(account)
    if not log_file.exists():
        return {}
    
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def _save_action_logs(account: str, logs: Dict[str, Any]):
    """アクションログの保存"""
    log_file = _get_action_log_file(account)
    try:
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(logs, f, ensure_ascii=False, indent=2)
    except OSError as e:
        import logging
        logging.warning(f"アクションログの保存に失敗: {e}")


def record_action_log(account: str, tweet_id: str, action_type: str, status: str, meta: str | None = None) -> None:
    """アクションログを記録する"""
    logs = _load_action_logs(account)
    
    # アカウント別ログの初期化
    if account not in logs:
        logs[account] = {}
    
    # ツイートID別ログの初期化
    if tweet_id not in logs[account]:
        logs[account][tweet_id] = {}
    
    # アクションログの記録
    logs[account][tweet_id][action_type] = {
        'status': status,
        'timestamp': int(time.time()),
        'meta': meta
    }
    
    _save_action_logs(account, logs)


def has_action_log(account: str, tweet_id: str, action_type: str) -> bool:
    """指定されたアクションが既に実行されているかチェック"""
    logs = _load_action_logs(account)
    
    if account not in logs:
        return False
    
    if tweet_id not in logs[account]:
        return False
    
    if action_type not in logs[account][tweet_id]:
        return False
    
    # 成功またはskippedのステータスがあれば実行済みとみなす
    status = logs[account][tweet_id][action_type].get('status', '')
    return status in ['success', 'skipped', 'dry_run']


def count_actions_last_hours(account: str, action_type: str, hours: int = 1) -> int:
    """指定した時間内のアクション実行回数をカウント"""
    logs = _load_action_logs(account)
    
    if account not in logs:
        return 0
    
    current_time = int(time.time())
    cutoff_time = current_time - (hours * 3600)
    count = 0
    
    for tweet_logs in logs[account].values():
        if action_type in tweet_logs:
            action_log = tweet_logs[action_type]
            timestamp = action_log.get('timestamp', 0)
            status = action_log.get('status', '')
            
            # 指定時間内で成功したアクションのみカウント
            if timestamp >= cutoff_time and status == 'success':
                count += 1
    
    return count


def cleanup_old_logs(account: str, days: int = 7):
    """古いアクションログをクリーンアップ"""
    logs = _load_action_logs(account)
    
    if account not in logs:
        return
    
    current_time = int(time.time())
    cutoff_time = current_time - (days * 24 * 3600)
    
    # 古いログを削除
    tweets_to_remove = []
    for tweet_id, tweet_logs in logs[account].items():
        all_old = True
        for action_log in tweet_logs.values():
            if action_log.get('timestamp', 0) >= cutoff_time:
                all_old = False
                break
        
        if all_old:
            tweets_to_remove.append(tweet_id)
    
    for tweet_id in tweets_to_remove:
        del logs[account][tweet_id]
    
    if tweets_to_remove:
        _save_action_logs(account, logs)
        import logging
        logging.info(f"古いアクションログを削除しました: {len(tweets_to_remove)}件")

