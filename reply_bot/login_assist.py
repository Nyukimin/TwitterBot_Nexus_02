import argparse
import logging
import os
import time
import yaml

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def load_accounts(cfg_path: str):
    with open(cfg_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f) or {}
    return data.get('accounts', [])


def open_login_with_prefill(handle: str, profile_dir: str) -> None:
    options = Options()
    abs_profile = os.path.abspath(profile_dir)
    os.makedirs(abs_profile, exist_ok=True)
    options.add_argument(f"--user-data-dir={abs_profile}")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")
    options.add_argument("--no-first-run")
    options.add_argument("--no-default-browser-check")
    options.add_argument("--remote-debugging-port=0")
    try:
        options.add_experimental_option('excludeSwitches', ['enable-automation', 'enable-logging'])
        options.add_experimental_option('useAutomationExtension', False)
    except Exception:
        pass

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    try:
        # 視認用の案内ページ
        html = f"""
        <html><body style='font-family: sans-serif'>
          <h1>このウィンドウは @{handle} のログイン用です</h1>
          <p>続いてXのログイン画面に移動し、ユーザー名欄にハンドルをセットします。</p>
        </body></html>
        """
        driver.get("data:text/html;charset=utf-8," + html)
        time.sleep(1.5)

        driver.get("https://x.com/login")
        wait = WebDriverWait(driver, 30)
        # ユーザー名入力欄の検出とプレフィル（name="text" or autocomplete="username"）
        locator_candidates = [
            (By.NAME, "text"),
            (By.CSS_SELECTOR, "input[autocomplete='username']"),
            (By.CSS_SELECTOR, "input[type='text']")
        ]
        filled = False
        for by, sel in locator_candidates:
            try:
                input_elem = wait.until(EC.presence_of_element_located((by, sel)))
                if input_elem:
                    input_elem.clear()
                    input_elem.send_keys(handle)
                    filled = True
                    break
            except Exception:
                continue
        if filled:
            logging.info(f"@{handle}: ログインユーザー名をセットしました。パスワード入力・2FAなどを完了してください。")
        else:
            logging.info(f"@{handle}: ログイン入力欄の検出に失敗。手動で入力してください。")

        input("続行するにはEnterキーを押してください（このアカウントのログイン完了後）。")
    finally:
        try:
            driver.quit()
        except Exception:
            pass


def main():
    parser = argparse.ArgumentParser(description='Xログイン支援（ユーザー名プレフィル）')
    parser.add_argument('--accounts', type=str, default='all', help='対象アカウント（id/handleのカンマ区切り）/ all')
    parser.add_argument('--config', type=str, default=os.path.join('config', 'accounts.yaml'))
    args = parser.parse_args()

    accounts = load_accounts(args.config)
    if args.accounts.lower() != 'all':
        wanted = {s.strip().lower() for s in args.accounts.split(',')}
        accounts = [a for a in accounts if str(a.get('id','')).lower() in wanted or str(a.get('handle','')).lower() in wanted]

    for acct in accounts:
        handle = acct.get('handle')
        profile = (acct.get('browser') or {}).get('user_data_dir')
        if not handle or not profile:
            logging.warning(f"スキップ: handleまたはprofile未設定: {acct}")
            continue
        logging.info(f"=== @{handle} のログイン支援を開始 ===")
        open_login_with_prefill(handle, profile)


if __name__ == '__main__':
    main()



