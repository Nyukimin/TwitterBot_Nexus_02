import logging
import time
import pyperclip
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver

from ..db import record_action_log, has_action_log, count_actions_last_hours
from ..reply_processor import fetch_and_analyze_thread, generate_reply


def run(driver: webdriver.Chrome, tweets: list[dict], policy: dict, rate_limits: dict, account_id: str, dry_run: bool) -> None:
    """
    Comment(返信) アクションを実行する。
    tweets: { 'reply_id': str, ... } を含む辞書のリスト
    policy: { 'only_if_my_thread': bool, 'reply_num_max': int, ... }
    rate_limits: { 'comment_per_hour': int, 'min_interval_seconds': int }
    account_id: 実行アカウント識別子
    dry_run: ドライラン時は実行せずログのみ
    """
    comment_per_hour = int(rate_limits.get('comment_per_hour', 10))
    min_interval = int(rate_limits.get('min_interval_seconds', 7))

    processed = 0
    for row in tweets:
        tweet_id = str(row.get('reply_id'))
        if not tweet_id:
            continue

        # 冪等性
        if has_action_log(account_id, tweet_id, 'comment'):
            logging.info(f"[comment] skip by idempotency: {tweet_id}")
            continue

        # レート制御
        used = count_actions_last_hours(account_id, 'comment', hours=1)
        if used >= comment_per_hour:
            logging.warning(f"[comment] hourly limit reached ({used}/{comment_per_hour}). stop.")
            break

        # スレッド解析
        thread = fetch_and_analyze_thread(tweet_id, driver)
        if not thread or thread.get('should_skip', True):
            logging.info(f"[comment] skip by thread condition: {tweet_id}")
            continue

        # 固定コメント設定（per_target: { user_handle: fixed_text }）
        fixed_map = (policy or {}).get('per_target', {})
        current_replier = thread.get('current_replier_id')
        reply_text = None
        if current_replier and current_replier in fixed_map:
            reply_text = fixed_map[current_replier]
            logging.info(f"[comment] use fixed reply for @{current_replier}")
        else:
            # 返信生成
            reply_text = generate_reply(thread, history=[])
        if not reply_text:
            logging.info(f"[comment] no reply generated: {tweet_id}")
            continue

        try:
            if dry_run:
                logging.info(f"[DRY RUN][comment] {tweet_id}: {reply_text}")
                record_action_log(account_id, tweet_id, 'comment', 'dry_run', meta=None)
            else:
                tweet_url = f"https://x.com/any/status/{tweet_id}"
                driver.get(tweet_url)
                wait = WebDriverWait(driver, 20)
                reply_input_selector = '[data-testid="tweetTextarea_0"]'
                reply_input = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, reply_input_selector)))

                driver.execute_script("arguments[0].focus(); arguments[0].click();", reply_input)
                time.sleep(1)

                final_reply_text = reply_text.replace('<br>', '\n')
                pyperclip.copy(final_reply_text)
                reply_input.send_keys(Keys.CONTROL, 'v')
                time.sleep(0.5)
                reply_input.send_keys(Keys.CONTROL, Keys.ENTER)
                record_action_log(account_id, tweet_id, 'comment', 'success', meta=None)
                processed += 1
                logging.info(f"[comment] success: {tweet_id}")
        except Exception as e:
            logging.warning(f"[comment] failed: {tweet_id}: {e}")
            record_action_log(account_id, tweet_id, 'comment', 'failed', meta=str(e))

        time.sleep(min_interval)

    logging.info(f"[comment] processed={processed}")


