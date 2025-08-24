import logging
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver

from ..db_stubs import record_action_log, has_action_log, count_actions_last_hours


def _is_allowed_for_user(action: str, user_handle: str | None, policy: dict) -> bool:
    per_target = (policy or {}).get('per_target', {})
    if not user_handle:
        return True
    cfg = per_target.get(user_handle)
    if cfg is None:
        return True
    if isinstance(cfg, str):
        # 固定コメント指定のみ → retweet の明示指定がない場合は許可（運用に合わせて調整可）
        return True
    if isinstance(cfg, dict):
        actions = cfg.get('actions')
        if actions is None:
            return True
        return action in actions
    return True


def run(driver: webdriver.Chrome, tweets: list[dict], policy: dict, rate_limits: dict, account_id: str, dry_run: bool) -> None:
    retweet_per_hour = int(rate_limits.get('retweet_per_hour', 0))
    min_interval = int(rate_limits.get('min_interval_seconds', 0))

    processed = 0
    for row in tweets:
        tweet_id = str(row.get('reply_id'))
        if not tweet_id:
            continue

        user_handle = str(row.get('UserID') or '').strip()
        if not _is_allowed_for_user('retweet', user_handle, policy):
            logging.info(f"[retweet] skip by per_target policy for @{user_handle}: {tweet_id}")
            continue

        if has_action_log(account_id, tweet_id, 'retweet'):
            logging.info(f"[retweet] skip by idempotency: {tweet_id}")
            continue

        used = count_actions_last_hours(account_id, 'retweet', hours=1)
        if retweet_per_hour > 0 and used >= retweet_per_hour:
            logging.warning(f"[retweet] hourly limit reached ({used}/{retweet_per_hour}). stop.")
            break

        tweet_url = f"https://x.com/any/status/{tweet_id}"
        logging.info(f"[retweet] target: {tweet_id}")
        driver.get(tweet_url)

        try:
            wait = WebDriverWait(driver, 20)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="tweetText"]')))

            if dry_run:
                logging.info(f"[DRY RUN][retweet] {tweet_id}")
                record_action_log(account_id, tweet_id, 'retweet', 'dry_run', meta=None)
            else:
                # 1) Retweet ボタンを押す
                rt_selector = '[data-testid="retweet"]'
                wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, rt_selector)))
                rt_button = driver.find_element(By.CSS_SELECTOR, rt_selector)
                driver.execute_script("arguments[0].click();", rt_button)

                # 2) 確認ダイアログで Retweet を押す
                confirm_selector = '[data-testid="retweetConfirm"]'
                wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, confirm_selector)))
                confirm_button = driver.find_element(By.CSS_SELECTOR, confirm_selector)
                driver.execute_script("arguments[0].click();", confirm_button)

                record_action_log(account_id, tweet_id, 'retweet', 'success', meta=None)
                processed += 1
                logging.info(f"[retweet] success: {tweet_id}")
        except Exception as e:
            logging.warning(f"[retweet] failed: {tweet_id}: {e}")
            record_action_log(account_id, tweet_id, 'retweet', 'failed', meta=str(e))

        time.sleep(min_interval)

    logging.info(f"[retweet] processed={processed}")


