import argparse
import logging
import os
import time
from typing import Dict, Any, List

import yaml
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import pyperclip
from selenium import webdriver

from .utils import setup_driver, close_driver
from . import config as cfg
from .db import init_db, record_action_log, has_action_log, count_actions_last_hours
from .thread_analysis_fix import _extract_tweet_id_robust
from .actions.like import run as action_like  # 互換性のため残置（本ファイルでは直接操作）
from .actions.bookmark import run as action_bookmark  # 同上
from .actions.retweet import run as action_retweet  # 同上
from .actions.comment import run as action_comment  # 同上（軽量投稿を本ファイルで実装）
from .actions.send_helpers import send_clipboard_paste_then_ctrl_enter, insert_text_robust


def load_accounts_config(path: str) -> Dict[str, Any]:
    with open(path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f) or {}
    if 'accounts' not in data or not isinstance(data['accounts'], list):
        raise ValueError("accounts.yaml に 'accounts' 配列が定義されていません。")
    return data


def select_account(cfg_data: Dict[str, Any], selector: str) -> Dict[str, Any]:
    selector_l = selector.strip().lower()
    for acct in cfg_data.get('accounts', []):
        acct_id = str(acct.get('id', '')).lower()
        handle = str(acct.get('handle', '')).lower()
        if acct_id == selector_l or handle == selector_l:
            return acct
    raise ValueError(f"指定されたアカウントが見つかりません: {selector}")


def wait_for_profile_tweets(driver: webdriver.Chrome, timeout_sec: int = 30) -> None:
    WebDriverWait(driver, timeout_sec).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'article[data-testid="tweet"]'))
    )


def detect_pinned_article(article: BeautifulSoup) -> bool:
    # 代表的なピン留め表示を検出（英語/日本語の両対応をゆるく）
    text = article.get_text(separator=' ').lower()
    return ('pinned' in text) or ('ピン留め' in text) or ('固定されたツイート' in text)


def detect_retweet_article(article: BeautifulSoup) -> bool:
    """プロフィールの一覧上で『リポスト／Reposted』表示がある記事を検出して対象外にする。"""
    try:
        ctx = article.find(attrs={'data-testid': 'socialContext'})
        if ctx:
            t = ctx.get_text(separator=' ').strip().lower()
            if ('repost' in t) or ('reposted' in t) or ('リポスト' in t):
                return True
        # フォールバック: 全体テキストにも簡易チェック
        all_text = article.get_text(separator=' ').lower()
        if (' リポスト' in all_text) or ('reposted' in all_text) or ('repost' in all_text):
            return True
    except Exception:
        pass
    return False


def get_latest_tweet_id_from_profile(driver: webdriver.Chrome, target_handle: str) -> str | None:
    profile_url = f"https://x.com/{target_handle}"
    logging.info(f"プロフィールに移動: {profile_url}")
    driver.get(profile_url)
    # 早期に『このアカウントは存在しません』等を検出してスキップ
    not_found_phrases = [
        'このアカウントは存在しません',
        "this account doesn't exist",
        'this account doesn’t exist',
        '帳戶不存在',
        'account does not exist',
    ]
    try:
        # 最大10回、合計約10秒で判定
        for _ in range(10):
            src = driver.page_source.lower()
            if any(p.lower() in src for p in not_found_phrases):
                logging.warning(f"@{target_handle}: アカウント不存在を検出。スキップします。")
                # 追加の構造化ログ（ID明示）
                logging.warning(f"[account-not-found] handle={target_handle}")
                return None
            # ツイートが表示されたら続行
            soup_tmp = BeautifulSoup(src, 'html.parser')
            if soup_tmp.select_one('article[data-testid="tweet"]'):
                break
            time.sleep(1)
        else:
            # タイムアウトしてもツイートもエラーメッセージも無い場合は従来待機
            wait_for_profile_tweets(driver, timeout_sec=20)
    except Exception:
        # 失敗時は従来待機にフォールバック
        wait_for_profile_tweets(driver, timeout_sec=20)

    # いったん最上部にスクロールして安定させる
    driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(2)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    # 一般的なtweet記事要素を収集
    articles = soup.select('article[data-testid="tweet"]')
    logging.info(f"記事要素検出数: {len(articles)}")
    if not articles:
        return None

    # ピン留め・リポスト記事をスキップし、最初に見つかった通常ツイートのIDを返す
    for idx, article in enumerate(articles):
        try:
            if detect_pinned_article(article):
                logging.info(f"{idx+1}件目はピン留めと推測。スキップします。")
                continue
            if detect_retweet_article(article):
                logging.info(f"{idx+1}件目はリポストと推測。スキップします。")
                continue
            tweet_id = _extract_tweet_id_robust(article)
            if tweet_id:
                logging.info(f"最新ツイートIDを取得: {tweet_id}")
                return tweet_id
        except Exception:
            continue

    # 通常ツイートが見つからない（ピン留め/リポストのみ）の場合はスキップ
    logging.warning("通常ツイートが見つかりません（ピン留め/リポストのみ）。スキップします。")
    return None


def _detect_existing_actions_via_ui(driver: webdriver.Chrome) -> Dict[str, bool]:
    """
    ツイート詳細画面上で、現在のアカウントが既に実施しているアクションのUI状態を推定する。
    - いいね: [data-testid="unlike"] / aria-labelに『いいねを取り消す』『Undo like』等
    - リポスト: [data-testid="unretweet"] / 『リポストを取り消す』『Undo repost』等
    - ブックマーク: [data-testid="removeBookmark"] / 『ブックマークを削除』『Remove bookmark』等
    返信はトグルUIがないためここでは判定しない（コメント一覧探索は行わない）。
    """
    # 表示安定のため軽く待機
    time.sleep(1)
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    def _has_selector(selector: str) -> bool:
        try:
            return soup.select_one(selector) is not None
        except Exception:
            return False

    def _has_aria_contains(keywords: list[str]) -> bool:
        try:
            # button/div等のaria-labelに含まれる文言で推定（多言語を想定して部分一致）
            elems = soup.find_all(['button', 'div'], attrs={'aria-label': True})
            for el in elems:
                label = (el.get('aria-label') or '').lower()
                if any(kw.lower() in label for kw in keywords):
                    return True
            return False
        except Exception:
            return False

    liked = _has_selector('[data-testid="unlike"]') or _has_aria_contains(['いいねを取り消', 'undo like', 'unlike'])
    retweeted = _has_selector('[data-testid="unretweet"]') or _has_aria_contains(['リポストを取り消', 'undo repost', 'unretweet'])
    bookmarked = _has_selector('[data-testid="removeBookmark"]') or _has_aria_contains(['ブックマークを削除', 'remove bookmark'])

    # replied（自アカウントの返信有無）検出: スレッド内に自アカウント(@TARGET_USER)のarticleが存在するか
    commented = False
    try:
        current_handle = (cfg.TARGET_USER or '').lstrip('@')
        if current_handle:
            articles = soup.select('article[data-testid="tweet"]')
            for art in articles[:30]:  # 過度な探索を抑制
                user_div = art.select_one('div[data-testid="User-Name"]')
                if not user_div:
                    continue
                link = user_div.select_one('a[role="link"][href^="/"]')
                href = link.get('href') if link else None
                author = href.lstrip('/') if href else None
                if author and author.lower() == current_handle.lower():
                    commented = True
                    break
    except Exception:
        commented = False

    return {
        'liked': bool(liked),
        'retweeted': bool(retweeted),
        'bookmarked': bool(bookmarked),
        'commented': bool(commented),
    }


def _wait_for_comment_confirmation(driver: webdriver.Chrome, timeout_sec: int = 8) -> bool:
    """
    送信後に実際に自アカウントの返信がスレッド上に現れたかを検証する。
    成功: True / 未反映またはエラーページ: False
    """
    import time as _time
    deadline = _time.time() + timeout_sec
    current_handle = (cfg.TARGET_USER or '').lstrip('@').lower()
    while _time.time() < deadline:
        try:
            # エラーページ検知（Something went wrong / 再試行）
            src_l = (driver.page_source or '').lower()
            if 'something went wrong' in src_l or 'try again' in src_l:
                return False

            soup = BeautifulSoup(driver.page_source, 'html.parser')
            articles = soup.select('article[data-testid="tweet"]')
            for art in articles[:50]:
                user_div = art.select_one('div[data-testid="User-Name"]')
                if not user_div:
                    continue
                link = user_div.select_one('a[role="link"][href^="/"]')
                href = link.get('href') if link else None
                author = href.lstrip('/') if href else None
                if author and author.lower() == current_handle:
                    return True
        except Exception:
            pass
        _time.sleep(0.5)
    return False


def _build_fixed_reply_for_user(user_handle: str | None, policy: Dict[str, Any] | None) -> str | None:
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


def _get_target_cfg(user_handle: str | None, policy: Dict[str, Any] | None) -> Dict[str, Any] | None:
    if not user_handle:
        return None
    per_target = (policy or {}).get('per_target', {})
    cfg = per_target.get(user_handle)
    if isinstance(cfg, dict):
        return cfg
    return None


def _build_greet_auto_reply(user_handle: str | None, policy: Dict[str, Any] | None) -> str | None:
    cfg = _get_target_cfg(user_handle, policy)
    if not cfg:
        return None
    greet = cfg.get('greet')
    nickname = cfg.get('nickname')

    # 設定が 'auto' もしくは { mode: 'auto' } のときのみ生成
    is_auto = False
    if isinstance(greet, str) and greet.lower() == 'auto':
        is_auto = True
    elif isinstance(greet, dict) and str(greet.get('mode', '')).lower() == 'auto':
        is_auto = True
    if not is_auto:
        return None

    # 時刻ベースの簡易あいさつ（JST前提）
    try:
        hour = time.localtime().tm_hour
        if 5 <= hour < 10:
            g = 'おはよう🩷'
        elif 10 <= hour < 17:
            g = 'こんにちは🩷'
        elif 17 <= hour < 24:
            g = 'こんばんは🩷'
        else:
            g = 'おやすみ🩷'
        return f"{nickname}、{g}" if nickname else g
    except Exception:
        return None


def _is_allowed_for_user(action: str, user_handle: str | None, policy: Dict[str, Any] | None) -> bool:
    per_target = (policy or {}).get('per_target', {})
    if not user_handle:
        return True
    cfg = per_target.get(user_handle)
    if cfg is None:
        return True
    if isinstance(cfg, str):
        # 固定コメントのみ指定 → like/bookmark/retweetは明示されていなければ不可にしたい場合は調整
        return True
    if isinstance(cfg, dict):
        actions = cfg.get('actions')
        if actions is None:
            return True
        return action in actions
    return True


def _click_js(driver: webdriver.Chrome, selector: str, wait_sec: int = 20) -> None:
    wait = WebDriverWait(driver, wait_sec)
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
    el = driver.find_element(By.CSS_SELECTOR, selector)
    driver.execute_script("arguments[0].click();", el)


def _open_reply_composer(driver: webdriver.Chrome, wait_sec: int = 10) -> None:
    """
    返信コンポーザーを確実に開く。
    1) 返信アイコンをクリック（有効なボタンを優先）
    2) スクロールやActionChains/JSクリックでフォールバック
    3) テキストエリアが表示されるまで待機
    """
    reply_button_selectors = [
        'button[data-testid="reply"]:not([disabled]):not([aria-disabled="true"])',
        'div[data-testid="reply"][role="button"]:not([aria-disabled="true"])',
        'div[data-testid="reply"]',
        'button[aria-label*="返信"]',
        'div[role="button"][aria-label*="返信"]',
        'button[aria-label*="Reply"]',
        'div[role="button"][aria-label*="Reply"]',
    ]

    clicked = False
    for sel in reply_button_selectors:
        try:
            btn = WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.CSS_SELECTOR, sel)))
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
            try:
                WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.CSS_SELECTOR, sel)))
            except Exception:
                pass
            try:
                ActionChains(driver).move_to_element(btn).pause(0.1).click(btn).perform()
                clicked = True
            except Exception:
                try:
                    driver.execute_script("arguments[0].click();", btn)
                    clicked = True
                except Exception:
                    continue
            if clicked:
                break
        except Exception:
            continue

    # テキストエリア表示待機（存在すればOK）
    reply_selectors = [
        '[data-testid="tweetTextarea_0"]',
        '[data-testid^="tweetTextarea_"]',
        'div[role="textbox"][data-testid*="tweetTextarea"]',
    ]
    for sel in reply_selectors:
        try:
            WebDriverWait(driver, wait_sec).until(EC.presence_of_element_located((By.CSS_SELECTOR, sel)))
            return
        except Exception:
            continue
    # 最後のフォールバック: 何もしない（上位で再検出）
    return


def _find_article_for_tweet(driver: webdriver.Chrome, tweet_id: str):
    try:
        # ツイートIDを含むリンクから親articleを特定
        link = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, f'a[href*="/status/{tweet_id}"]'))
        )
        # 祖先のarticleを辿る
        current = link
        for _ in range(8):
            try:
                if current.tag_name.lower() == 'article':
                    return current
            except Exception:
                pass
            current = current.find_element(By.XPATH, '..')
    except Exception:
        return None
    return None


def _open_reply_composer_for_tweet(driver: webdriver.Chrome, tweet_id: str, wait_sec: int = 10) -> None:
    """
    指定ツイートIDのarticle内の返信ボタンをクリックして、返信コンポーザーを開く。
    """
    article = _find_article_for_tweet(driver, tweet_id)
    if not article:
        # フォールバック: グローバル探索
        _open_reply_composer(driver, wait_sec=wait_sec)
        return

    # article内の返信ボタンを優先してクリック
    selectors = [
        'button[data-testid="reply"]:not([disabled]):not([aria-disabled="true"])',
        'div[data-testid="reply"][role="button"]:not([aria-disabled="true"])',
        'div[data-testid="reply"]',
    ]
    for sel in selectors:
        try:
            btn = article.find_element(By.CSS_SELECTOR, sel)
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
            try:
                ActionChains(driver).move_to_element(btn).pause(0.05).click(btn).perform()
            except Exception:
                driver.execute_script("arguments[0].click();", btn)
            break
        except Exception:
            continue

    # 返信用テキストエリアの存在を確認
    reply_selectors = [
        'div[role="dialog"] [data-testid^="tweetTextarea_"]',
        'div[aria-labelledby="modal-header"] [data-testid^="tweetTextarea_"]',
        '[data-testid^="tweetTextarea_"]',
        'div[role="textbox"][data-testid*="tweetTextarea"]',
    ]
    for sel in reply_selectors:
        try:
            WebDriverWait(driver, wait_sec).until(EC.presence_of_element_located((By.CSS_SELECTOR, sel)))
            return
        except Exception:
            continue
    return


def _get_reply_input_robust(driver: webdriver.Chrome, wait_sec: int = 10):
    """返信用テキストエリアを堅牢に取得（存在/有効/クリック可能を考慮）"""
    try:
        # 代表的なセレクタの候補
        selectors = [
            '[data-testid="tweetTextarea_0"]',
            '[data-testid^="tweetTextarea_"]',
            'div[role="textbox"][data-testid*="tweetTextarea"]',
        ]
        for sel in selectors:
            try:
                WebDriverWait(driver, wait_sec).until(EC.presence_of_element_located((By.CSS_SELECTOR, sel)))
            except Exception:
                continue
            try:
                el = WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.CSS_SELECTOR, sel)))
            except Exception:
                # クリック可能でなくても element を返して後段処理で focus/click 試行
                el = driver.find_element(By.CSS_SELECTOR, sel)
            try:
                driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
                driver.execute_script("arguments[0].focus(); arguments[0].click();", el)
            except Exception:
                pass
            # 無効状態の簡易判定
            aria_disabled = (el.get_attribute('aria-disabled') or '').lower() == 'true'
            contenteditable = (el.get_attribute('contenteditable') or '').lower()
            if aria_disabled:
                continue
            # contenteditable が false/空でも TweetInput は Shadow/内部構造のため続行
            return el
    except Exception:
        return None
    return None


def _post_comment_light(driver: webdriver.Chrome, tweet_id: str, reply_text: str, dry_run: bool,
                        account_id: str) -> bool:
    tweet_url = f"https://x.com/any/status/{tweet_id}"
    logging.info(f"[comment-light] target: {tweet_id}")
    driver.get(tweet_url)
    try:
        # 入力欄の取得（堅牢版）。見つからなければコンポーザーを開いて再試行
        reply_input = _get_reply_input_robust(driver, wait_sec=10)
        if not reply_input:
            _open_reply_composer_for_tweet(driver, tweet_id, wait_sec=10)
            reply_input = _get_reply_input_robust(driver, wait_sec=10)
        if not reply_input:
            logging.warning("[comment-light] reply input not available")
            record_action_log(account_id, tweet_id, 'comment', 'failed', meta='no_input')
            return False

        if dry_run:
            logging.info(f"[DRY RUN][comment-light] {tweet_id}: {reply_text}")
            record_action_log(account_id, tweet_id, 'comment', 'dry_run', meta='light')
            return True

        driver.execute_script("arguments[0].focus(); arguments[0].click();", reply_input)
        time.sleep(0.3)
        # 入力済みなら上書きせず送信のみ。未入力ならヘルパーで貼り付け→送信。
        existing_text = (reply_input.text or '').strip()
        if not existing_text:
            try:
                existing_text = (driver.execute_script('return (arguments[0].innerText || arguments[0].textContent || "").trim();', reply_input) or '').strip()
            except Exception:
                existing_text = ''
        if existing_text:
            reply_input.send_keys(Keys.CONTROL, Keys.ENTER)
        else:
            # まず従来どおり貼り付け
            try:
                pyperclip.copy(reply_text)
            except Exception:
                pass
            reply_input.send_keys(Keys.CONTROL, 'v')
            time.sleep(0.2)
            # 挿入確認
            current = (reply_input.text or '').strip()
            if not current:
                try:
                    current = (driver.execute_script('return (arguments[0].innerText || arguments[0].textContent || "").trim();', reply_input) or '').strip()
                except Exception:
                    current = ''
            # 失敗時はロバスト挿入フォールバック
            if not current:
                inserted = insert_text_robust(driver, reply_input, reply_text, paste_delay_seconds=0.2)
                if not inserted:
                    logging.warning("[comment-light] insert failed (paste & fallback)")
            # 送信（Ctrl+Enter）
            reply_input.send_keys(Keys.CONTROL, Keys.ENTER)

        # 送信後の反映確認（実際に自アカの返信が現れたか）
        if _wait_for_comment_confirmation(driver, timeout_sec=8):
            record_action_log(account_id, tweet_id, 'comment', 'success', meta='light')
            logging.info(f"[comment-light] success: {tweet_id}")
            return True
        else:
            logging.warning(f"[comment-light] verification failed (no visible reply): {tweet_id}")
            record_action_log(account_id, tweet_id, 'comment', 'failed', meta='verify_failed')
            return False
    except Exception as e:
        logging.warning(f"[comment-light] failed: {tweet_id}: {e}")
        record_action_log(account_id, tweet_id, 'comment', 'failed', meta=f'light:{e}')
        return False


def _post_comment_light_on_current_page(driver: webdriver.Chrome, tweet_id: str, reply_text: str,
                                        dry_run: bool, account_id: str) -> bool:
    try:
        # 入力欄の取得（堅牢版）。未オープンなら開いてから再試行
        reply_input = _get_reply_input_robust(driver, wait_sec=10)
        if not reply_input:
            _open_reply_composer_for_tweet(driver, tweet_id, wait_sec=10)
            reply_input = _get_reply_input_robust(driver, wait_sec=10)
        if not reply_input:
            logging.warning("[comment-light] reply input not available (on-current)")
            record_action_log(account_id, tweet_id, 'comment', 'failed', meta='no_input:on-current')
            return False

        if dry_run:
            logging.info(f"[DRY RUN][comment-light] {tweet_id}: {reply_text}")
            record_action_log(account_id, tweet_id, 'comment', 'dry_run', meta='light')
            return True

        driver.execute_script("arguments[0].focus(); arguments[0].click();", reply_input)
        time.sleep(0.3)
        # 入力済みなら上書きせず送信のみ。未入力ならヘルパーで貼り付け→送信。
        existing_text = (reply_input.text or '').strip()
        if not existing_text:
            try:
                existing_text = (driver.execute_script('return (arguments[0].innerText || arguments[0].textContent || "").trim();', reply_input) or '').strip()
            except Exception:
                existing_text = ''
        if existing_text:
            reply_input.send_keys(Keys.CONTROL, Keys.ENTER)
        else:
            # まず従来どおり貼り付け
            try:
                pyperclip.copy(reply_text)
            except Exception:
                pass
            reply_input.send_keys(Keys.CONTROL, 'v')
            time.sleep(0.2)
            # 挿入確認
            current = (reply_input.text or '').strip()
            if not current:
                try:
                    current = (driver.execute_script('return (arguments[0].innerText || arguments[0].textContent || "").trim();', reply_input) or '').strip()
                except Exception:
                    current = ''
            # 失敗時はロバスト挿入フォールバック
            if not current:
                inserted = insert_text_robust(driver, reply_input, reply_text, paste_delay_seconds=0.2)
                if not inserted:
                    logging.warning("[comment-light] insert failed (on-current: paste & fallback)")
            # 送信（Ctrl+Enter）
            reply_input.send_keys(Keys.CONTROL, Keys.ENTER)

        # 送信後の反映確認
        if _wait_for_comment_confirmation(driver, timeout_sec=8):
            record_action_log(account_id, tweet_id, 'comment', 'success', meta='light')
            logging.info(f"[comment-light] success: {tweet_id}")
            return True
        else:
            logging.warning(f"[comment-light] verification failed (on-current): {tweet_id}")
            record_action_log(account_id, tweet_id, 'comment', 'failed', meta='verify_failed:on-current')
            return False
    except Exception as e:
        logging.warning(f"[comment-light] failed(on-current): {tweet_id}: {e}")
        record_action_log(account_id, tweet_id, 'comment', 'failed', meta=f'light:on-current:{e}')
        return False


def _attempt_comment_light(driver: webdriver.Chrome, tweet_id: str, policy: Dict[str, Any],
                           rate_limits: Dict[str, Any], account_id: str, target_handle: str,
                           dry_run: bool) -> None:
    # 冪等性
    if has_action_log(account_id, tweet_id, 'comment'):
        logging.info(f"[comment-light] skip by idempotency: {tweet_id}")
        return

    # レート制御
    used = count_actions_last_hours(account_id, 'comment', hours=1)
    limit = int(rate_limits.get('comment_per_hour', 0))
    # limit <= 0 のときはレート制限を無効化
    if limit > 0 and used >= limit:
        logging.warning(f"[comment-light] hourly limit reached ({used}/{limit}). skip.")
        return

    # fixed_comment 優先。なければ greet:auto を使用
    reply_text = _build_fixed_reply_for_user(target_handle, policy)
    if not reply_text:
        reply_text = _build_greet_auto_reply(target_handle, policy)
    if not reply_text:
        logging.info("[comment-light] fixed_comment / greet:auto が未設定のためスキップ")
        return

    # 投稿
    _post_comment_light(driver, tweet_id, reply_text, dry_run=dry_run, account_id=account_id)


def run_actions_on_tweet(driver: webdriver.Chrome,
                         account_id: str,
                         target_handle: str,
                         tweet_id: str,
                         actions: List[str],
                         policy: Dict[str, Any] | None,
                         rate_limits: Dict[str, Any] | None,
                         live_run: bool,
                         existing_states: Dict[str, bool] | None = None) -> None:
    dry_run = not live_run
    policy = policy or {}
    rate_limits = rate_limits or {}
    states = existing_states or {'liked': False, 'bookmarked': False, 'retweeted': False}

    # 'comment' は最後に実行
    ordered = [a for a in actions if a.strip().lower() != 'comment'] + \
              [a for a in actions if a.strip().lower() == 'comment']

    min_interval = int(rate_limits.get('min_interval_seconds', 0))

    for action in ordered:
        action_l = action.strip().lower()

        if action_l in ('like', 'bookmark', 'retweet'):
            if not _is_allowed_for_user(action_l, target_handle, policy):
                logging.info(f"[{action_l}] per_target policyによりスキップ (@{target_handle})")
                continue

            if has_action_log(account_id, tweet_id, action_l):
                logging.info(f"[{action_l}] idempotencyでスキップ: {tweet_id}")
                continue

            per_hour_key = f"{action_l}_per_hour"
            used = count_actions_last_hours(account_id, action_l, hours=1)
            limit = int(rate_limits.get(per_hour_key, 0))
            if limit > 0 and used >= limit:
                logging.warning(f"[{action_l}] hourly limit reached ({used}/{limit}). skip.")
                continue

            # UI状態に基づき未実施のみ実行
            if action_l == 'like':
                if states.get('liked'):
                    logging.info("[like] 既に実施済み（UI検出）")
                else:
                    try:
                        _click_js(driver, '[data-testid="like"]')
                        record_action_log(account_id, tweet_id, 'like', 'success', meta='inline')
                        states['liked'] = True
                        logging.info(f"[like] success: {tweet_id}")
                    except Exception as e:
                        logging.warning(f"[like] failed inline: {e}")
                        record_action_log(account_id, tweet_id, 'like', 'failed', meta=f'inline:{e}')
                time.sleep(min_interval)

            elif action_l == 'bookmark':
                if states.get('bookmarked'):
                    logging.info("[bookmark] 既に実施済み（UI検出）")
                else:
                    try:
                        _click_js(driver, '[data-testid="bookmark"]')
                        record_action_log(account_id, tweet_id, 'bookmark', 'success', meta='inline')
                        states['bookmarked'] = True
                        logging.info(f"[bookmark] success: {tweet_id}")
                    except Exception as e:
                        logging.warning(f"[bookmark] failed inline: {e}")
                        record_action_log(account_id, tweet_id, 'bookmark', 'failed', meta=f'inline:{e}')
                time.sleep(min_interval)

            elif action_l == 'retweet':
                if states.get('retweeted'):
                    logging.info("[retweet] 既に実施済み（UI検出）")
                else:
                    try:
                        _click_js(driver, '[data-testid="retweet"]')
                        _click_js(driver, '[data-testid="retweetConfirm"]')
                        record_action_log(account_id, tweet_id, 'retweet', 'success', meta='inline')
                        states['retweeted'] = True
                        logging.info(f"[retweet] success: {tweet_id}")
                    except Exception as e:
                        logging.warning(f"[retweet] failed inline: {e}")
                        record_action_log(account_id, tweet_id, 'retweet', 'failed', meta=f'inline:{e}')
                time.sleep(min_interval)

        elif action_l == 'comment':
            # 固定コメントがある場合のみ軽量投稿を、同一ページ上で最後に実行
            #（重いスレッド解析やページ再読み込みは行わない）
            # UI検出で既に自アカウントの返信がある場合はスキップ（要素ベースの済/未）
            if states.get('commented'):
                logging.info(f"[comment-light] 既に返信済み（UI検出）: {tweet_id}")
                continue
            used = count_actions_last_hours(account_id, 'comment', hours=1)
            limit = int(rate_limits.get('comment_per_hour', 0))
            if limit > 0 and used >= limit:
                logging.warning(f"[comment-light] hourly limit reached ({used}/{limit}). skip.")
                continue
            reply_text = _build_fixed_reply_for_user(target_handle, policy)
            if not reply_text:
                reply_text = _build_greet_auto_reply(target_handle, policy)
            if not reply_text:
                logging.info("[comment-light] fixed_comment / greet:auto 未設定のためスキップ")
                continue
            _post_comment_light_on_current_page(driver, tweet_id, reply_text, dry_run=dry_run, account_id=account_id)
            time.sleep(min_interval)
        else:
            logging.warning(f"未知のアクションのためスキップ: {action}")


def main() -> None:
    parser = argparse.ArgumentParser(description='対象ユーザーの最新ツイートに対して、指定アクションを実行します。')
    parser.add_argument('--account', type=str, required=True, help='実行アカウント（id または handle）')
    parser.add_argument('--target', type=str, required=True, help='対象ユーザーのhandle（@なし）')
    parser.add_argument('--actions', type=str, default='like', help='実行するアクションのカンマ区切り（like,bookmark,retweet,comment）')
    parser.add_argument('--config', type=str, default=os.path.join('config', 'accounts.yaml'), help='アカウント設定YAMLのパス')
    parser.add_argument('--live-run', action='store_true', help='実際に操作を実行（デフォルト: ドライラン）')
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    if not os.path.exists(args.config):
        raise FileNotFoundError(f"アカウント設定ファイルが見つかりません: {args.config}")

    # DB初期化
    init_db()

    cfg_data = load_accounts_config(args.config)
    account = select_account(cfg_data, args.account)
    account_id = str(account.get('id', 'unknown'))
    handle = str(account.get('handle', '')).strip()
    browser = account.get('browser', {}) or {}
    profile_dir = browser.get('user_data_dir')
    headless = bool(browser.get('headless', False))
    features = account.get('features', {}) or {}
    policy = account.get('policies', {}) or {}
    rate_limits = account.get('rate_limits', {}) or {}

    # 実行するアクション（featuresで無効なものは除外）
    requested_actions = [a.strip() for a in args.actions.split(',') if a.strip()]
    enabled_actions = [a for a in requested_actions if features.get(a, False)]
    disabled = [a for a in requested_actions if not features.get(a, False)]
    if disabled:
        logging.warning(f"featuresで無効なアクションはスキップします: {', '.join(disabled)}")
    if not enabled_actions:
        logging.error("実行可能なアクションがありません。accounts.yamlのfeaturesを確認してください。")
        return

    driver = None
    try:
        logging.info(f"=== アカウント '{account_id}' (@{handle}) で実行します ===")
        driver = setup_driver(headless=headless, profile_path=profile_dir)
        if not driver:
            logging.error("WebDriverの初期化に失敗しました。終了します。")
            return

        tweet_id = get_latest_tweet_id_from_profile(driver, args.target)
        if not tweet_id:
            logging.error("最新ツイートIDの取得に失敗しました。")
            return

        # 事前チェック: 該当ツイート画面で既存アクションのUI状態を確認し、
        # 何か一つでも既に行われていれば即終了（コメント一覧の探索は行わない）
        tweet_url = f"https://x.com/any/status/{tweet_id}"
        logging.info(f"対象ツイートに移動して既存アクションを確認: {tweet_url}")
        driver.get(tweet_url)
        wait_for_profile_tweets(driver, timeout_sec=30)
        states = _detect_existing_actions_via_ui(driver)
        logging.info(f"UI状態検出: {states}")

        run_actions_on_tweet(
            driver=driver,
            account_id=account_id,
            target_handle=args.target,
            tweet_id=tweet_id,
            actions=enabled_actions,
            policy=policy,
            rate_limits=rate_limits,
            live_run=args.live_run,
            existing_states=states,
        )

        logging.info("=== 指定アクションの実行が完了しました ===")
    except Exception as e:
        logging.error(f"処理中にエラー: {e}", exc_info=True)
    finally:
        close_driver()


if __name__ == '__main__':
    main()


