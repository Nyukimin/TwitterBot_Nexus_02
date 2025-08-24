import logging
import pickle
import os
import time
import psutil
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, WebDriverException

from .config import LOGIN_URL, LOGIN_TIMEOUT_ENABLED, LOGIN_TIMEOUT_SECONDS, PAGE_LOAD_TIMEOUT_SECONDS
from .profile_lock import ProfileLock

COOKIE_FILE = "cookie/twitter_cookies_01.pkl"

# WebDriverインスタンスを保持するグローバル変数
_driver: webdriver.Chrome | None = None
_driver_process_count = 0  # WebDriverの起動回数をカウント
_memory_monitor_enabled = True  # メモリ監視の有効/無効フラグ
_last_profile_path: str | None = None  # 直近に使用したChromeプロファイルパス
_chromedriver_path: str | None = None  # ドライババイナリのキャッシュ（起動時1回のバージョンチェック）

def get_driver(headless: bool = True) -> webdriver.Chrome:
    """
    シングルトンパターンのように動作し、WebDriverインスタンスを一度だけ初期化して返します。
    2回目以降の呼び出しでは、既存のインスタンスを返します。
    """
    global _driver
    if _driver is None:
        options = Options()
        if headless:
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')

        try:
            service = Service(ChromeDriverManager().install())
            _driver = webdriver.Chrome(service=service, options=options)
            logging.info("新しいWebDriverインスタンスを初期化しました。")
            
            # Cookieを読み込んでログイン
            if not os.path.exists(COOKIE_FILE):
                logging.error(f"Cookieファイル {COOKIE_FILE} が見つかりません。")
                logging.error("最初に 'python -m reply_bot.get_cookie' を実行して、ログインとCookieの保存を完了させてください。")
                close_driver()
                raise FileNotFoundError(f"{COOKIE_FILE} not found.")

            try:
                with open(COOKIE_FILE, "rb") as f:
                    cookies = pickle.load(f)
                
                # Cookieをセットするために、一度ドメインにアクセス
                _driver.get("https://x.com/") 
                
                for cookie in cookies:
                    if 'expiry' in cookie:
                        # 'expiry' が存在し、浮動小数点数の場合は整数に変換
                        cookie['expiry'] = int(cookie['expiry'])
                    _driver.add_cookie(cookie)
                    
                logging.info("Cookieを正常に読み込み、ログイン状態を復元しました。")
                # ログイン確認のため、再度ページを読み込み
                _driver.get("https://x.com/home")

                # ページが完全に読み込まれ、操作可能になるまで待機する
                try:
                    wait = WebDriverWait(_driver, 15)
                    # タイムラインの主要なコンテナが表示されるのを待つ
                    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="primaryColumn"]')))
                    logging.info("Xのホームページが正常に読み込まれました。")
                except Exception as e:
                    logging.error(f"Xのホームページの読み込み待機中にタイムアウトまたはエラーが発生しました: {e}")
                    close_driver()
                    raise e

            except Exception as e:
                logging.error(f"Cookieの読み込み中にエラーが発生しました: {e}")
                close_driver()
                raise e

        except Exception as e:
            logging.error(f"WebDriverのセットアップ中にエラーが発生しました: {e}")
            raise e
            
    return _driver

def check_memory_usage():
    """
    現在のメモリ使用量を確認し、ログに記録します。
    """
    if not _memory_monitor_enabled:
        return
    
    try:
        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()
        memory_mb = memory_info.rss / 1024 / 1024
        logging.info(f"現在のメモリ使用量: {memory_mb:.1f} MB")
        
        # 500MB以上の場合は警告
        if memory_mb > 500:
            logging.warning(f"メモリ使用量が高くなっています: {memory_mb:.1f} MB")
            
        return memory_mb
    except Exception as e:
        logging.warning(f"メモリ使用量の確認中にエラー: {e}")
        return None

def force_restart_driver(headless: bool = True, profile_path: str | None = None):
    """
    WebDriverを強制的に再起動します。
    メモリリークやクラッシュからの回復に使用します。
    """
    global _driver, _driver_process_count
    
    logging.warning("WebDriverの強制再起動を実行します...")
    
    # 既存のWebDriverを終了
    if _driver:
        try:
            _driver.quit()
            logging.info("既存のWebDriverを終了しました。")
        except Exception as e:
            logging.warning(f"WebDriver終了時にエラー（無視して続行）: {e}")
        finally:
            _driver = None
    
    # プロセスの完全終了を待機
    time.sleep(2)
    
    # 新しいWebDriverを起動
    try:
        # 直近のプロファイルを優先的に使用
        effective_profile = profile_path if profile_path is not None else _last_profile_path
        _driver = setup_driver(headless=headless, profile_path=effective_profile)
        _driver_process_count += 1
        logging.info(f"WebDriverを再起動しました（起動回数: {_driver_process_count}）")
        check_memory_usage()
        return _driver
    except Exception as e:
        logging.error(f"WebDriverの再起動中にエラー: {e}")
        return None

def close_driver():
    """
    グローバルなWebDriverインスタンスを終了します。
    """
    global _driver
    if _driver:
        try:
            _driver.quit()
            logging.info("WebDriverインスタンスを終了しました。")
        except Exception as e:
            logging.warning(f"WebDriver終了時にエラー（無視して続行）: {e}")
        finally:
            _driver = None
            check_memory_usage()

def setup_driver(headless: bool = True, profile_path: str | None = None, max_retries: int = 3) -> webdriver.Chrome | None:
    """
    Selenium WebDriverをセットアップし、Cookieを使ってログイン状態を復元します。
    ホームページの読み込みに失敗した場合、指定された回数だけ再試行します。
    """
    global _driver_process_count
    
    options = Options()
    if headless:
        options.add_argument("--headless")
        logging.info("ヘッドレスモードでWebDriverを起動します。")
    
    # アカウントごとにChromeユーザープロファイルを分離
    if profile_path:
        try:
            abs_profile = os.path.abspath(profile_path)
            os.makedirs(abs_profile, exist_ok=True)
        except Exception as e:
            logging.warning(f"ユーザープロファイルディレクトリの作成に失敗しました: {profile_path} ({e})")
        else:
            options.add_argument(f"--user-data-dir={abs_profile}")
            logging.info(f"Chromeユーザープロファイルを使用します: {abs_profile}")
            # 最後に使用したプロファイルを記録
            global _last_profile_path
            _last_profile_path = abs_profile
    else:
        abs_profile = None
    
    # メモリリーク対策とパフォーマンス向上のオプション
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")
    options.add_argument("--no-first-run")
    options.add_argument("--no-default-browser-check")
    options.add_argument("--remote-debugging-port=0")
    options.add_argument('--log-level=3') # INFO, WARNING, ERROR 以外のログを抑制
    try:
        options.add_experimental_option('excludeSwitches', ['enable-automation', 'enable-logging'])
        options.add_experimental_option('useAutomationExtension', False)
    except Exception:
        pass
    
    # メモリ使用量を監視
    check_memory_usage()

    # WebDriverのセットアップ（同一プロファイルの同時起動を防ぐロック取得）
    try:
        profile_lock = None
        if abs_profile:
            try:
                profile_lock = ProfileLock(abs_profile, timeout_seconds=180)
                if not profile_lock.acquire():
                    logging.error(f"[profile-lock] ロック取得に失敗しました: {abs_profile}")
                    return None
            except Exception as e:
                logging.warning(f"[profile-lock] 取得中に例外が発生しました（続行）: {e}")

        global _chromedriver_path
        if not _chromedriver_path:
            _chromedriver_path = ChromeDriverManager().install()
        service = Service(_chromedriver_path)
        driver = webdriver.Chrome(service=service, options=options)
        _driver_process_count += 1
        logging.info(f"新しいWebDriverインスタンスを初期化しました（起動回数: {_driver_process_count}）")
        check_memory_usage()

        # quit 時にロックを解放するようにフック
        if profile_lock is not None:
            original_quit = driver.quit

            def _quit_and_release(*args, **kwargs):
                try:
                    return original_quit(*args, **kwargs)
                finally:
                    try:
                        profile_lock.release()
                    except Exception:
                        pass

            driver.quit = _quit_and_release  # type: ignore[attr-defined]
    except Exception as e:
        logging.error(f"WebDriverの初期化中にエラーが発生しました: {e}")
        return None

    # ログイン状態の確認と初期遷移（プロファイルあり/なしで分岐、リトライ付き）
    for attempt in range(max_retries):
        try:
            logging.info(f"初期ナビゲーションを実行します... ({attempt + 1}/{max_retries})")

            if profile_path:
                # プロファイルを使用する場合はCookie注入を行わず、ホームに直接アクセス
                driver.get("https://x.com/home")
                WebDriverWait(driver, PAGE_LOAD_TIMEOUT_SECONDS).until(
                    EC.presence_of_element_located((By.XPATH, '//article[@data-testid="tweet"]'))
                )
                logging.info("Xのホームページが正常に読み込まれました（プロファイル使用）。")
                return driver
            else:
                # 従来のCookieファイルを使用してログイン状態を復元
                driver.get(LOGIN_URL)
                if os.path.exists(COOKIE_FILE):
                    with open(COOKIE_FILE, "rb") as f:
                        cookies = pickle.load(f)
                    for cookie in cookies:
                        if 'sameSite' in cookie and cookie['sameSite'] == 'None':
                            cookie['secure'] = True
                        driver.add_cookie(cookie)
                    logging.info("Cookieを正常に読み込み、ログイン状態を復元しました。")
                else:
                    logging.warning("Cookieファイルが見つかりません。ログインページから手動でログインしてください。")

                driver.get("https://x.com/home")
                WebDriverWait(driver, PAGE_LOAD_TIMEOUT_SECONDS).until(
                    EC.presence_of_element_located((By.XPATH, '//article[@data-testid="tweet"]'))
                )
                logging.info("Xのホームページが正常に読み込まれました。")
                return driver

        except TimeoutException as e:
            logging.warning(f"ホームページの読み込み中にタイムアウトしました。({attempt + 1}/{max_retries})")
            if attempt == max_retries - 1:
                logging.error(f"最大リトライ回数({max_retries}回)に達しました。ホームページの読み込みに失敗しました。")
                driver.quit()
                return None
            logging.info("リトライします...")
            time.sleep(5)
        except WebDriverException as e:
            logging.error(f"WebDriver関連のエラーが発生しました: {e} ({attempt + 1}/{max_retries})")
            if attempt == max_retries - 1:
                logging.error(f"最大リトライ回数({max_retries}回)に達しました。WebDriverエラーにより処理を中断します。")
                driver.quit()
                return None
            logging.info("リトライします...")
            time.sleep(5)
        except Exception as e:
            logging.error(f"初期遷移中に予期せぬエラーが発生しました: {e}", exc_info=True)
            driver.quit()
            return None
    
    return None # ループが正常に終了した場合（通常は起こらない）

def get_cookie(driver: webdriver.Chrome):
    """
    指定されたURLにアクセスし、ユーザーがログインを完了するのを待ってから、
    Cookieをファイルに保存します。
    """
    try:
        # ログインページにアクセス
        driver.get(LOGIN_URL)
        logging.info(f"{LOGIN_URL} にアクセスしました。ログインを完了してください...")

        # ユーザーが手動でログインし、ホームページにリダイレクトされるのを待つ
        # タイムアウトを長めに設定 (例: 5分)
        WebDriverWait(driver, 300).until(
            EC.url_contains("x.com/home")
        )
        
        logging.info("ホームページへのリダイレクトを検出しました。Cookieを保存します。")
        
        # Cookieを保存
        cookies = driver.get_cookies()
        with open(COOKIE_FILE, "wb") as f:
            pickle.dump(cookies, f)
            
        logging.info(f"Cookieを {COOKIE_FILE} に保存しました。")

    except TimeoutException:
        logging.error("ログイン待機中にタイムアウトしました。時間内にログインが完了しなかった可能性があります。")
    except Exception as e:
        logging.error(f"Cookieの保存中にエラーが発生しました: {e}")
        raise e
        
    return None # ループが正常に終了した場合（通常は起こらない） 