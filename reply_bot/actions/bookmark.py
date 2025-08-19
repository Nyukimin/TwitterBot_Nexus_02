import logging
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver

from ..db import record_action_log, has_action_log, count_actions_last_hours


def run(driver: webdriver.Chrome, tweets: list[dict], policy: dict, rate_limits: dict, account_id: str, dry_run: bool) -> None:
    """
    Bookmarkアクションを実行する。
    tweets: { 'reply_id': str, ... } を含む辞書のリスト
    rate_limits: { 'bookmark_per_hour': int, 'min_interval_seconds': int }
    """
    bookmark_per_hour = int(rate_limits.get('bookmark_per_hour', 60))
    min_interval = int(rate_limits.get('min_interval_seconds', 7))

    processed = 0
    for row in tweets:
        tweet_id = str(row.get('reply_id'))
        if not tweet_id:
            continue

        if has_action_log(account_id, tweet_id, 'bookmark'):
            logging.info(f"[bookmark] skip by idempotency: {tweet_id}")
            continue

        used = count_actions_last_hours(account_id, 'bookmark', hours=1)
        if used >= bookmark_per_hour:
            logging.warning(f"[bookmark] hourly limit reached ({used}/{bookmark_per_hour}). stop.")
            break

        tweet_url = f"https://x.com/any/status/{tweet_id}"
        logging.info(f"[bookmark] target: {tweet_id}")
        driver.get(tweet_url)

        try:
            wait = WebDriverWait(driver, 20)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="tweetText"]')))

            if dry_run:
                logging.info(f"[DRY RUN][bookmark] {tweet_id}")
                record_action_log(account_id, tweet_id, 'bookmark', 'dry_run', meta=None)
            else:
                bookmark_selector = '[data-testid="bookmark"]'
                wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, bookmark_selector)))
                button = driver.find_element(By.CSS_SELECTOR, bookmark_selector)
                driver.execute_script("arguments[0].click();", button)
                record_action_log(account_id, tweet_id, 'bookmark', 'success', meta=None)
                processed += 1
                logging.info(f"[bookmark] success: {tweet_id}")
        except Exception as e:
            logging.warning(f"[bookmark] failed: {tweet_id}: {e}")
            record_action_log(account_id, tweet_id, 'bookmark', 'failed', meta=str(e))

        time.sleep(min_interval)

    logging.info(f"[bookmark] processed={processed}")


