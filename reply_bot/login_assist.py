#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Twitterログイン支援ツール - fixed_chromeディレクトリの固定Chromeを使用

WebDriverManagerを使わず、fixed_chrome/chromeとfixed_chrome/chromedriverを使用します。
"""

import os
import sys
import time
import logging
import argparse
import subprocess
import psutil
import glob
import shutil
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

# プロファイルロック管理
from .profile_lock import ProfileLock

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class FixedChromeLoginAssist:
    """fixed_chromeディレクトリの固定Chromeを使用するログイン支援クラス"""
    
    def __init__(self):
        self.driver = None
        self.profile_lock = None
        
        # プロジェクトルートディレクトリを取得
        self.project_root = Path(__file__).parent.parent
        
        # fixed_chromeディレクトリのパス
        self.fixed_chrome_dir = self.project_root / "fixed_chrome"
        self.chrome_binary_path = self.fixed_chrome_dir / "chrome" / "chrome.exe"
        self.chromedriver_path = self.fixed_chrome_dir / "chromedriver" / "chromedriver.exe"
        
        # プロファイルディレクトリ
        self.profiles_dir = self.project_root / "profile"
        
    def _validate_fixed_chrome_setup(self):
        """fixed_chromeのセットアップ検証"""
        if not self.chrome_binary_path.exists():
            raise FileNotFoundError(
                f"Chrome実行ファイルが見つかりません: {self.chrome_binary_path}\n"
                f"fixed_chrome/chrome/chrome.exe が正しく配置されているか確認してください。"
            )
            
        if not self.chromedriver_path.exists():
            raise FileNotFoundError(
                f"ChromeDriver実行ファイルが見つかりません: {self.chromedriver_path}\n"
                f"fixed_chrome/chromedriver/chromedriver.exe が正しく配置されているか確認してください。"
            )
            
        logger.info(f"固定Chromeセットアップ確認完了:")
        logger.info(f"  Chrome: {self.chrome_binary_path}")
        logger.info(f"  ChromeDriver: {self.chromedriver_path}")
    
    def _cleanup_profile_processes(self, profile_path: Path):
        """プロファイル使用中のChromeプロセスをクリーンアップ"""
        try:
            logger.info(f"プロファイル {profile_path} を使用中のChromeプロセスを確認中...")
            
            killed_processes = []
            profile_str = str(profile_path)
            
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    proc_info = proc.info
                    if proc_info['name'] and 'chrome' in proc_info['name'].lower():
                        cmdline = proc_info.get('cmdline')
                        if cmdline and any(profile_str in arg for arg in cmdline):
                            logger.info(f"プロファイル使用中のChromeプロセスを終了: PID {proc.pid}")
                            proc.terminate()
                            proc.wait(timeout=5)
                            killed_processes.append(proc.pid)
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired):
                    continue
            
            if killed_processes:
                logger.info(f"終了したプロセス: {killed_processes}")
            else:
                logger.info("プロファイル使用中のChromeプロセスは見つかりませんでした")
                
        except Exception as e:
            logger.warning(f"プロセスクリーンアップ中のエラー: {e}")
    
    def _cleanup_profile_locks(self, profile_path: Path):
        """プロファイルのロックファイルをクリーンアップ"""
        try:
            lock_patterns = [
                profile_path / "Singleton*",
                profile_path / "*.lock",
                profile_path / "lockfile*",
                profile_path / "Default" / "Singleton*",
                profile_path / "Default" / "*.lock"
            ]
            
            for pattern in lock_patterns:
                for lock_file in glob.glob(str(pattern)):
                    try:
                        if os.path.exists(lock_file):
                            if os.path.isfile(lock_file):
                                os.remove(lock_file)
                                logger.debug(f"ロックファイル削除: {lock_file}")
                            elif os.path.isdir(lock_file):
                                shutil.rmtree(lock_file, ignore_errors=True)
                                logger.debug(f"ロックディレクトリ削除: {lock_file}")
                    except Exception as e:
                        logger.debug(f"ロックファイル削除失敗 {lock_file}: {e}")
                        
        except Exception as e:
            logger.warning(f"ロックファイルクリーンアップ中のエラー: {e}")

    def _setup_chrome_options(self, profile_name: str, headless: bool = False):
        """Chrome起動オプションの設定（固定Chrome用）"""
        options = Options()
        
        # 固定Chromeバイナリを指定
        options.binary_location = str(self.chrome_binary_path)
        
        # プロファイル設定
        profile_path = self.profiles_dir / profile_name
        profile_path.mkdir(parents=True, exist_ok=True)
        
        # プロファイルクリーンアップ
        self._cleanup_profile_processes(profile_path)
        self._cleanup_profile_locks(profile_path)
        
        # 少し待機してからChromeを起動
        time.sleep(1)
        
        options.add_argument(f"--user-data-dir={profile_path}")
        options.add_argument("--profile-directory=Default")
        
        # プロファイル競合を避けるための追加オプション
        options.add_argument("--disable-features=LockProfileData")
        options.add_argument("--disable-features=ProcessSingletonLock")
        options.add_argument("--remote-debugging-port=0")  # ランダムポート使用
        
        # ヘッドレス設定
        if headless:
            options.add_argument("--headless=new")
            options.add_argument("--disable-gpu")
        
        # 基本設定
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # ウィンドウサイズ設定
        options.add_argument("--window-size=1920,1080")
        
        # 通知やポップアップをブロック
        prefs = {
            "profile.default_content_setting_values": {
                "notifications": 2,
                "popups": 2
            }
        }
        options.add_experimental_option("prefs", prefs)
        
        return options
    
    def start_login_assist(self, profile_name: str, headless: bool = False):
        """ログイン支援を開始"""
        try:
            logger.info(f"=== @{profile_name} のログイン支援を開始 ===")
            
            # fixed_chromeセットアップの検証
            self._validate_fixed_chrome_setup()
            
            # プロファイルロックの取得
            profile_path = self.profiles_dir / profile_name
            profile_path.mkdir(parents=True, exist_ok=True)
            
            self.profile_lock = ProfileLock(str(profile_path))
            self.profile_lock.acquire()
            
            # Chrome起動オプション設定
            options = self._setup_chrome_options(profile_name, headless)
            
            # ChromeDriverサービス設定（fixed_chromeを使用）
            service = Service(str(self.chromedriver_path))
            
            logger.info("====== WebDriver manager ===\n====")
            
            # WebDriverを起動
            logger.info(f"固定Chrome WebDriver起動中: {self.chromedriver_path}")
            self.driver = webdriver.Chrome(service=service, options=options)
            
            # User-Agentを設定してボット検知を回避
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            # Twitterログインページに移動
            logger.info("Twitterログインページにアクセス中...")
            self.driver.get("https://x.com/login")
            
            # ページの読み込み完了を待機
            time.sleep(3)
            
            logger.info(f"@{profile_name}: ログインユーザー名をセットしました。パスワード入力・2FAなどを完了してください。")
            logger.info("続行するにはEnterキーを押してください（このアカウントのログイン完了後）。")
            
            # ユーザーの入力を待機
            input()
            
            logger.info("ログイン支援が完了しました。")
            
        except Exception as e:
            logger.error(f"ログイン支援中にエラーが発生しました: {e}")
            raise
        finally:
            self._cleanup()
    
    def _cleanup(self):
        """リソースのクリーンアップ"""
        try:
            if self.driver:
                self.driver.quit()
                self.driver = None
                
            if self.profile_lock:
                self.profile_lock.release()
                self.profile_lock = None
                
        except Exception as e:
            logger.warning(f"クリーンアップ中に警告: {e}")

def load_account_config(config_path: str):
    """アカウント設定ファイルを読み込み"""
    import yaml
    
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"設定ファイルが見つかりません: {config_path}")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    return config

def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(
        description='Twitterログイン支援ツール（fixed_chrome使用）'
    )
    parser.add_argument(
        '--config', 
        required=True,
        help='アカウント設定ファイルのパス（例: ./config/accounts_Maya19960330.yaml）'
    )
    parser.add_argument(
        '--headless', 
        action='store_true',
        help='ヘッドレスモードで起動（デバッグ用、通常は使用しない）'
    )
    
    args = parser.parse_args()
    
    try:
        # 設定ファイル読み込み
        config = load_account_config(args.config)
        
        # アカウント名を設定ファイル名から推測
        config_filename = Path(args.config).stem  # accounts_Maya19960330
        if config_filename.startswith('accounts_'):
            account_name = config_filename[9:]  # Maya19960330
        else:
            account_name = config_filename
        
        # ログイン支援を開始
        assist = FixedChromeLoginAssist()
        assist.start_login_assist(
            profile_name=account_name,
            headless=args.headless
        )
        
    except KeyboardInterrupt:
        logger.info("ユーザーによって中断されました")
    except Exception as e:
        logger.error(f"エラーが発生しました: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
