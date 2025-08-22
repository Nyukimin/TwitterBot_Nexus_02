"""
薄いラッパー: CSV行からアクションモジュールに委譲する。
既存のシグネチャ互換のため main_process は維持。
単体実行は非推奨。
"""

import pandas as pd
import argparse
import logging
import os
from selenium import webdriver

from .config import POST_INTERVAL_SECONDS, LEGACY_COMMENT_ENABLED
from .actions.like import run as run_like
from .actions.comment import run as run_comment

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main_process(driver: webdriver.Chrome, input_csv: str, dry_run: bool = True, limit: int | None = None, interval: int = 15):
    try:
        df = pd.read_csv(input_csv)
    except FileNotFoundError:
        logging.error(f"入力ファイルが見つかりません: {input_csv}")
        return

    if limit and limit > 0:
        df = df.head(limit)

    rows = df.fillna('').to_dict(orient='records')

    # ファイル名パターンからアカウントIDを推定（multi_main命名に依存）
    base = os.path.basename(input_csv)
    account_id = 'default'
    try:
        if base.startswith('extracted_tweets_'):
            account_id = base.split('_')[2]
        elif base.startswith('processed_replies_'):
            account_id = base.split('_')[2]
    except Exception:
        pass

    policy = { 'only_if_my_thread': True, 'reply_num_max': 0 }
    rate_limits = { 'like_per_hour': 0, 'comment_per_hour': 0, 'min_interval_seconds': interval or POST_INTERVAL_SECONDS }

    run_like(driver, rows, policy, rate_limits, account_id=account_id, dry_run=dry_run)
    if LEGACY_COMMENT_ENABLED:
        run_comment(driver, rows, policy, rate_limits, account_id=account_id, dry_run=dry_run)
    else:
        logging.info("[legacy-comment] disabled by config (LEGACY_COMMENT_ENABLED=False)")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='生成された返信をXに投稿します。')
    parser.add_argument('input_csv', type=str, help='入力CSVファイルのパス (例: output/generated_replies_....csv)')
    parser.add_argument('--live-run', action='store_true', help='このフラグを立てると、実際に投稿やいいねを行います（ドライランを無効化）。')
    parser.add_argument('--limit', type=int, default=None, help='処理するツイートの最大数を指定します。')
    parser.add_argument('--interval', type=int, default=None, help=f'投稿間の待機時間（秒）。指定しない場合はconfig.pyの値({POST_INTERVAL_SECONDS}秒)が使われます。')
    
    args = parser.parse_args()
    
    logging.error('post_reply.py の単体起動は非推奨です。multi_main から呼び出してください。')