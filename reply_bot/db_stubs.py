"""
DB機能は完全削除されました。互換性のため最低限のスタブを提供します。
"""

from __future__ import annotations


def record_action_log(account: str, tweet_id: str, action_type: str, status: str, meta: str | None = None) -> None:
    # 何もしない（ログはコンソール/ファイルログで閲覧）
    return None


def has_action_log(account: str, tweet_id: str, action_type: str) -> bool:
    # 冪等性はUI検出で代替
    return False


def count_actions_last_hours(account: str, action_type: str, hours: int = 1) -> int:
    # 時間当たり件数カウントは行わない
    return 0


