import argparse
import logging
import os
import subprocess
import time
import yaml

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from .profile_lock import ProfileLock


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def cleanup_chrome_processes_for_profile(profile_dir=None):
    """特定のプロファイルを使用しているChromeプロセスのみを終了"""
    try:
        import psutil
        
        if profile_dir:
            abs_profile_path = os.path.normpath(os.path.abspath(profile_dir)).lower()
            logging.info(f"プロファイル {profile_dir} を使用しているChromeプロセスを確認中...")
        else:
            logging.info("全てのChromeプロセスを確認中...")
            
        killed_pids = []
        
        # 実行中の全プロセスをチェック
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['name'] and 'chrome' in proc.info['name'].lower():
                    cmdline = proc.info['cmdline'] or []
                    
                    # 特定プロファイル指定時は該当プロファイルのみ終了
                    if profile_dir:
                        profile_found = False
                        for arg in cmdline:
                            if '--user-data-dir=' in arg:
                                arg_path = os.path.normpath(arg.replace('--user-data-dir=', '')).lower()
                                if abs_profile_path in arg_path:
                                    profile_found = True
                                    break
                        
                        if profile_found:
                            logging.info(f"プロファイル {profile_dir} を使用中のChrome PID {proc.info['pid']} を終了します")
                            proc.terminate()
                            killed_pids.append(proc.info['pid'])
                    else:
                        # プロファイル指定なしの場合は全Chrome終了（従来動作）
                        logging.info(f"Chrome PID {proc.info['pid']} を終了します")
                        proc.terminate()
                        killed_pids.append(proc.info['pid'])
                        
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        
        if killed_pids:
            logging.info(f"{len(killed_pids)}個のChromeプロセスを終了しました: {killed_pids}")
            time.sleep(2)  # プロセス終了完了まで待機
            
            # 強制終了が必要なプロセスをチェック
            force_kill_count = 0
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if proc.info['name'] and 'chrome' in proc.info['name'].lower() and proc.info['pid'] in killed_pids:
                        logging.warning(f"Chrome PID {proc.info['pid']} を強制終了します")
                        proc.kill()
                        force_kill_count += 1
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
                    
            if force_kill_count > 0:
                time.sleep(1)
        else:
            if profile_dir:
                logging.info(f"プロファイル {profile_dir} を使用中のChromeプロセスは見つかりませんでした")
            else:
                logging.info("終了対象のChromeプロセスは見つかりませんでした")
                
    except ImportError:
        logging.warning("psutilがインストールされていないため、従来の方法で全Chromeプロセスを終了します")
        # psutilが使えない場合のフォールバック
        try:
            result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq chrome.exe'],
                                  capture_output=True, text=True, shell=True)
            if result.returncode == 0 and 'chrome.exe' in result.stdout:
                subprocess.run(['taskkill', '/F', '/IM', 'chrome.exe'],
                             capture_output=True, text=True, shell=True)
                logging.info("全Chromeプロセスを終了しました（プロファイル選択不可）")
                time.sleep(2)
        except Exception:
            pass
    except Exception as e:
        logging.warning(f"Chromeプロセス確認・終了処理でエラー: {e}")


def cleanup_chrome_processes():
    """下位互換性のため維持（全Chrome終了）"""
    cleanup_chrome_processes_for_profile(None)


def load_accounts(cfg_path: str):
    with open(cfg_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f) or {}
    return data.get('accounts', [])


def open_login_with_prefill(handle: str, profile_dir: str) -> None:
    # このプロファイルを使用しているChromeプロセスのみを事前終了
    cleanup_chrome_processes_for_profile(profile_dir)
    
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

    abs_profile = os.path.abspath(profile_dir)
    lock = None
    service = None
    driver = None
    # 以降のどの失敗でも lock/driver を解放するために、単一の try/finally で囲む
    try:
        # 同一プロファイル多重起動の衝突を防止
        lock = ProfileLock(abs_profile, timeout_seconds=180)
        if not lock.acquire():
            logging.error(f"[profile-lock] ロック取得に失敗: {abs_profile}")
            return

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)

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
            if driver:
                driver.quit()
        except Exception:
            pass
        finally:
            try:
                if lock:
                    lock.release()
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



