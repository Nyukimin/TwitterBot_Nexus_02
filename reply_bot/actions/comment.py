import logging
import time
import pyperclip
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver

from ..db_stubs import record_action_log, has_action_log, count_actions_last_hours
from .send_helpers import send_clipboard_paste_then_ctrl_enter
from ..reply_processor import fetch_and_analyze_thread, generate_reply
from ..utils import get_random_interval


def _build_fixed_reply_for_user(user_handle: str | None, policy: dict) -> str | None:
    per_target = (policy or {}).get('per_target', {})
    if not user_handle:
        return None
    cfg = per_target.get(user_handle)
    if cfg is None:
        return None
    if isinstance(cfg, str):
        return cfg
    if isinstance(cfg, dict):
        return cfg.get('fixed_comment')
    return None


def _is_allowed_for_user(action: str, user_handle: str | None, policy: dict) -> bool:
    per_target = (policy or {}).get('per_target', {})
    if not user_handle:
        return True
    cfg = per_target.get(user_handle)
    if cfg is None:
        return True
    if isinstance(cfg, str):
        return True  # 固定コメント指定のみ → コメントは許可
    if isinstance(cfg, dict):
        actions = cfg.get('actions')
        if actions is None:
            return True
        return action in actions
    return True


def run(driver: webdriver.Chrome, tweets: list[dict], policy: dict, rate_limits: dict, account_id: str, dry_run: bool) -> None:
    """
    Comment(返信) アクションを実行する。
    tweets: { 'reply_id': str, ... } を含む辞書のリスト
    policy: { 'only_if_my_thread': bool, 'reply_num_max': int, ... }
    rate_limits: { 'comment_per_hour': int, 'min_interval_seconds': int }
    account_id: 実行アカウント識別子
    dry_run: ドライラン時は実行せずログのみ
    """
    comment_per_hour = int(rate_limits.get('comment_per_hour', 0))
    min_interval = int(rate_limits.get('min_interval_seconds', 0))

    processed = 0
    for row in tweets:
        tweet_id = str(row.get('reply_id'))
        if not tweet_id:
            continue

        # 冪等性チェック（ファイルベース）
        if has_action_log(account_id, tweet_id, 'comment'):
            logging.info(f"[comment] skip by action log: {tweet_id}")
            continue

        # レート制御
        used = count_actions_last_hours(account_id, 'comment', hours=1)
        if comment_per_hour > 0 and used >= comment_per_hour:
            logging.warning(f"[comment] hourly limit reached ({used}/{comment_per_hour}). stop.")
            break

        # スレッド解析
        thread = fetch_and_analyze_thread(tweet_id, driver)
        if not thread or thread.get('should_skip', True):
            logging.info(f"[comment] skip by thread condition: {tweet_id}")
            continue

        # per-target ポリシーでコメント許可/固定文面
        current_replier = thread.get('current_replier_id')
        if not _is_allowed_for_user('comment', current_replier, policy):
            logging.info(f"[comment] skip by per_target policy for @{current_replier}: {tweet_id}")
            continue

        # 1) greet 設定の解釈（fixed / auto）
        reply_text = None
        per_target = (policy or {}).get('per_target', {})
        target_cfg = per_target.get(current_replier) if current_replier else None
        greet_cfg = None
        nickname = None

        if isinstance(target_cfg, dict):
            greet_cfg = target_cfg.get('greet')
            nickname = target_cfg.get('nickname')

        # ニックネームが設定されていない場合はDBから取得
        # DB廃止に伴い nickname は accounts.yaml の policies.per_target で設定する運用に変更

        def _detect_greeting_type(text: str, lang: str) -> str | None:
            """ツイート内容から挨拶タイプを判定"""
            t = text.lower()
            try:
                if lang == 'ja':
                    if 'おはよ' in text or 'おはよう' in text:
                        return 'morning'
                    if 'こんにちは' in text:
                        return 'afternoon'
                    if 'こんばんは' in text:
                        return 'evening'
                    if 'おやすみ' in text:
                        return 'night'
                    # デフォルトは時刻ベース判定に委ねる
                    return None
                if 'good morning' in t or t.startswith('gm'):
                    return 'good_morning'
                if 'good night' in t or t.startswith('gn'):
                    return 'good_night'
                if 'good evening' in t:
                    return 'good_evening'
                if 'hello' in t or t.startswith('hi'):
                    return 'hello'
                return 'hello' if lang == 'en' else None
            except Exception:
                return None

        if greet_cfg:
            # 文字列で 'auto' 指定も許容
            if isinstance(greet_cfg, str) and greet_cfg.lower() == 'auto':
                # 新しい挨拶システムを使用
                detected_type = _detect_greeting_type(thread.get('current_reply_text', ''), thread.get('lang', 'und'))
                if detected_type:
                    greeting = get_varied_greeting(account_id, current_replier, detected_type, GreetingTracker())
                else:
                    # 時刻ベース判定
                    hour = time.localtime().tm_hour
                    if 5 <= hour < 10:
                        greeting_type = 'morning'
                    elif 10 <= hour < 17:
                        greeting_type = 'afternoon'
                    elif 17 <= hour < 24:
                        greeting_type = 'evening'
                    else:
                        greeting_type = 'night'
                    greeting = get_varied_greeting(account_id, current_replier, greeting_type, GreetingTracker())
                reply_text = f"{nickname}\n{greeting}" if nickname else greeting
            elif isinstance(greet_cfg, dict):
                mode = str(greet_cfg.get('mode', '')).lower()
                if mode == 'fixed':
                    text = greet_cfg.get('text')
                    if text:
                        reply_text = f"{nickname}\n{text}" if nickname else text
                elif mode == 'auto':
                    # 新しい挨拶システムを使用
                    detected_type = _detect_greeting_type(thread.get('current_reply_text', ''), thread.get('lang', 'und'))
                    if detected_type:
                        greeting = get_varied_greeting(account_id, current_replier, detected_type, GreetingTracker())
                    else:
                        # 時刻ベース判定
                        hour = time.localtime().tm_hour
                        if 5 <= hour < 10:
                            greeting_type = 'morning'
                        elif 10 <= hour < 17:
                            greeting_type = 'afternoon'
                        elif 17 <= hour < 24:
                            greeting_type = 'evening'
                        else:
                            greeting_type = 'night'
                        greeting = get_varied_greeting(account_id, current_replier, greeting_type, GreetingTracker())
                    reply_text = f"{nickname}\n{greeting}" if nickname else greeting

        # 2) 固定コメントがあれば優先
        if not reply_text:
            reply_text = _build_fixed_reply_for_user(current_replier, policy)

        # 3) ここまでで決まらなければ通常生成
        if not reply_text:
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

                send_clipboard_paste_then_ctrl_enter(driver, reply_input, reply_text, paste_delay_seconds=0.5)
                record_action_log(account_id, tweet_id, 'comment', 'success', meta=None)
                processed += 1
                logging.info(f"[comment] success: {tweet_id}")
        except Exception as e:
            logging.warning(f"[comment] failed: {tweet_id}: {e}")
            record_action_log(account_id, tweet_id, 'comment', 'failed', meta=str(e))

        time.sleep(get_random_interval())

    logging.info(f"[comment] processed={processed}")


