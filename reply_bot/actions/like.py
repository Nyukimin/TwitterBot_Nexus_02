import logging
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver

from ..db_stubs import record_action_log, has_action_log, count_actions_last_hours
from ..utils import get_random_interval


def _is_allowed_for_user(action: str, user_handle: str | None, policy: dict) -> bool:
    per_target = (policy or {}).get('per_target', {})
    if not user_handle:
        return True
    target_cfg = per_target.get(user_handle)
    if target_cfg is None:
        return True  # 設定なし → デフォルト許可
    # 旧仕様: 文字列（固定コメントのみの指定）
    if isinstance(target_cfg, str):
        return True
    # 新仕様: { actions: [...], fixed_comment: "..." }
    actions = target_cfg.get('actions') if isinstance(target_cfg, dict) else None
    if actions is None:
        return True
    return action in actions


def run(driver: webdriver.Chrome, tweets: list[dict], policy: dict, rate_limits: dict, account_id: str, dry_run: bool) -> None:
    """
    Likeアクションを実行する。
    tweets: { 'reply_id': str, ... } を含む辞書のリスト
    policy: { 'only_if_my_thread': bool, 'reply_num_max': int, ... }
    rate_limits: { 'like_per_hour': int, 'min_interval_seconds': int }
    account_id: 実行アカウント識別子
    dry_run: ドライラン時は実行せずログのみ
    """
    like_per_hour = int(rate_limits.get('like_per_hour', 0))
    min_interval = int(rate_limits.get('min_interval_seconds', 0))

    processed = 0
    for row in tweets:
        tweet_id = str(row.get('reply_id'))
        if not tweet_id:
            continue

        user_handle = str(row.get('UserID') or '').strip()
        if not _is_allowed_for_user('like', user_handle, policy):
            logging.info(f"[like] skip by per_target policy for @{user_handle}: {tweet_id}")
            continue

        # 冪等性: 既に成功ログがあればスキップ（DB削除後もin-memoryロガーで機能）
        if has_action_log(account_id, tweet_id, 'like'):
            logging.info(f"[like] skip by idempotency: {tweet_id}")
            continue

        # レート制御: 直近1hの回数チェック
        used = count_actions_last_hours(account_id, 'like', hours=1)
        if like_per_hour > 0 and used >= like_per_hour:
            logging.warning(f"[like] hourly limit reached ({used}/{like_per_hour}). stop.")
            break

        tweet_url = f"https://x.com/any/status/{tweet_id}"
        logging.info(f"[like] target: {tweet_id}")
        driver.get(tweet_url)

        try:
            wait = WebDriverWait(driver, 20)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="tweetText"]')))

            if dry_run:
                logging.info(f"[DRY RUN][like] {tweet_id}")
                record_action_log(account_id, tweet_id, 'like', 'dry_run', meta=None)
            else:
                like_button_selector = '[data-testid="like"]'
                wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, like_button_selector)))
                like_button = driver.find_element(By.CSS_SELECTOR, like_button_selector)
                driver.execute_script("arguments[0].click();", like_button)
                record_action_log(account_id, tweet_id, 'like', 'success', meta=None)
                processed += 1
                logging.info(f"[like] success: {tweet_id}")
        except Exception as e:
            logging.warning(f"[like] failed: {tweet_id}: {e}")
            record_action_log(account_id, tweet_id, 'like', 'failed', meta=str(e))

        # インターバル
        time.sleep(get_random_interval())

    logging.info(f"[like] processed={processed}")


