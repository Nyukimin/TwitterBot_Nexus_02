#!/usr/bin/env python3
"""
スケジュール型ツイート実行メインスクリプト
emotion_linkアカウントのtransit_config, image_configに基づいてツイートを実行
"""

import argparse
import logging
import os
import sys
import time
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, List
import yaml
import json

# プロジェクトルートを sys.path に追加
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from reply_bot.utils import setup_driver, close_driver
from shared_modules.astrology.astro_system import get_transit_info
from shared_modules.text_processing.emotion_extraction import extract_emotional_content


def load_account_config(config_path: str) -> Dict[str, Any]:
    """アカウント設定を読み込み"""
    with open(config_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f) or {}
    
    if 'accounts' not in data or not isinstance(data['accounts'], list):
        raise ValueError("設定ファイルに 'accounts' 配列が定義されていません。")
    
    return data['accounts'][0]  # 最初のアカウントを返す


def check_schedule_time(schedule_config: List[Dict[str, Any]], current_time: datetime) -> Optional[Dict[str, Any]]:
    """現在時刻がスケジュール時刻と一致するかチェック"""
    current_hour_min = current_time.strftime("%H:%M")
    current_weekday = current_time.weekday()  # 0=月曜, 6=日曜
    
    for schedule in schedule_config:
        schedule_time = schedule.get('time', '')
        schedule_days = schedule.get('days', ['all'])
        
        # 時刻チェック
        if schedule_time != current_hour_min:
            continue
            
        # 曜日チェック
        if 'all' in schedule_days:
            return schedule
        
        # 特定曜日の場合（monday, tuesday, etc.）
        day_names = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        current_day_name = day_names[current_weekday]
        
        if current_day_name in schedule_days:
            return schedule
    
    return None


def generate_ai_content(prompt: str, max_length: int = 140) -> str:
    """AI コンテンツ生成（仮実装 - 実際のAI APIと連携予定）"""
    try:
        # 実際にはOpenAI/Gemini APIを使用
        import openai
        
        # この部分は実際のAI APIキーと設定が必要
        # 現在は仮の実装として固定文を返す
        if "今日は" in prompt:
            return "今日は月が魚座に入る。感受性が高まりやすい日。人の気持ちに寄り添って過ごそう。"
        else:
            return "心に寄り添う画像プロンプトが生成されました。"
            
    except Exception as e:
        logging.error(f"AI コンテンツ生成エラー: {e}")
        return "今日も心穏やかに過ごしましょう。"


def generate_image_prompt(emotional_content: str, template: str) -> str:
    """画像プロンプト生成"""
    try:
        # テンプレートに感情コンテンツを埋め込み
        return template.format(step1_emotional_content=emotional_content)
    except Exception as e:
        logging.error(f"画像プロンプト生成エラー: {e}")
        return template


def post_tweet(driver, text_content: str, image_path: Optional[str] = None) -> bool:
    """ツイート投稿"""
    try:
        # X(Twitter)のホームページに移動
        driver.get("https://x.com/home")
        time.sleep(3)
        
        # ツイート入力欄を探す
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        
        # ツイート作成ボタンをクリック
        tweet_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="tweetButtonInline"]'))
        )
        tweet_button.click()
        time.sleep(2)
        
        # テキスト入力
        text_area = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="tweetTextarea_0"]'))
        )
        text_area.clear()
        text_area.send_keys(text_content)
        time.sleep(2)
        
        # 画像がある場合は添付
        if image_path and os.path.exists(image_path):
            # 画像添付ボタンを探してクリック
            try:
                image_input = driver.find_element(By.CSS_SELECTOR, 'input[accept*="image"]')
                image_input.send_keys(os.path.abspath(image_path))
                time.sleep(3)
                logging.info(f"画像を添付しました: {image_path}")
            except Exception as e:
                logging.warning(f"画像添付に失敗: {e}")
        
        # ツイート投稿ボタンをクリック
        post_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="tweetButton"]'))
        )
        post_button.click()
        time.sleep(3)
        
        logging.info(f"ツイートを投稿しました: {text_content[:50]}...")
        return True
        
    except Exception as e:
        logging.error(f"ツイート投稿エラー: {e}")
        return False


def execute_step1_transit_tweet(account_config: Dict[str, Any], driver, dry_run: bool = False, force_run: bool = False) -> Optional[str]:
    """STEP1: トランジット解釈ツイート実行"""
    transit_config = account_config.get('transit_config', {})
    if not transit_config.get('enabled', False):
        logging.info("STEP1: transit_config が無効です")
        return None
    
    schedule_config = transit_config.get('schedule', [])
    if not schedule_config:
        logging.warning("STEP1: スケジュール設定がありません")
        return None
    
    current_time = datetime.now()
    if not force_run:
        active_schedule = check_schedule_time(schedule_config, current_time)
        if not active_schedule:
            logging.info("STEP1: 現在時刻はスケジュール対象外です")
            return None
    else:
        active_schedule = schedule_config[0]  # 強制実行時は最初のスケジュールを使用
        logging.info("STEP1: 強制実行モード")
    
    ai_config = active_schedule.get('ai_generate', {})
    if not ai_config.get('enabled', False):
        logging.info("STEP1: AI生成が無効です")
        return None
    
    # プロンプト構築
    personality_prompt = account_config.get('PERSONALITY_PROMPT', '')
    prompt_template = ai_config.get('prompt', '')
    full_prompt = prompt_template.format(PERSONALITY_PROMPT=personality_prompt)
    
    # トランジット情報取得
    try:
        transit_info = get_transit_info()
        full_prompt = full_prompt.replace("{transit_info}", str(transit_info))
    except Exception as e:
        logging.warning(f"トランジット情報取得失敗: {e}")
    
    # AI コンテンツ生成
    max_length = ai_config.get('max_length', 140)
    step1_content = generate_ai_content(full_prompt, max_length)
    
    logging.info(f"STEP1生成コンテンツ: {step1_content}")
    
    if not dry_run:
        success = post_tweet(driver, step1_content)
        if success:
            logging.info("STEP1: ツイート投稿成功")
        else:
            logging.error("STEP1: ツイート投稿失敗")
    else:
        logging.info("STEP1: ドライラン - 実際の投稿はスキップ")
    
    return step1_content


def execute_step2_image_prompt_generation(account_config: Dict[str, Any], step1_content: str) -> Optional[str]:
    """STEP2: 画像プロンプト生成"""
    image_prompt_config = account_config.get('image_prompt_config', {})
    if not image_prompt_config.get('enabled', False):
        logging.info("STEP2: image_prompt_config が無効です")
        return None
    
    ai_config = image_prompt_config.get('schedule', [{}])[0].get('ai_generate', {})
    if not ai_config.get('enabled', False):
        logging.info("STEP2: AI生成が無効です")
        return None
    
    # 感情コンテンツ抽出
    try:
        step1_emotional_content = extract_emotional_content(step1_content)
        logging.info(f"抽出された感情コンテンツ: {step1_emotional_content}")
    except Exception as e:
        logging.warning(f"感情コンテンツ抽出失敗: {e}")
        step1_emotional_content = step1_content
    
    # 画像プロンプト生成
    prompt_template = ai_config.get('prompt', '')
    step3_image_prompt = generate_image_prompt(step1_emotional_content, prompt_template)
    
    logging.info(f"STEP2生成プロンプト: {step3_image_prompt}")
    return step3_image_prompt


def execute_step3_image_tweet(account_config: Dict[str, Any], step1_content: str, step3_image_prompt: str, driver, dry_run: bool = False, force_run: bool = False) -> bool:
    """STEP3: 画像付きツイート実行"""
    image_config = account_config.get('image_config', {})
    if not image_config.get('enabled', False):
        logging.info("STEP3: image_config が無効です")
        return False
    
    # スケジュールチェック（force_runでない場合）
    if not force_run:
        schedule_config = image_config.get('schedule', [])
        if schedule_config:
            current_time = datetime.now()
            active_schedule = check_schedule_time(schedule_config, current_time)
            if not active_schedule:
                logging.info("STEP3: 現在時刻はスケジュール対象外です")
                return False
    
    # STEP1のコンテンツを再利用
    if image_config.get('ai_generate', {}).get('use_previous_content') == 'step1_output':
        tweet_content = step1_content
        logging.info(f"STEP3: STEP1のコンテンツを使用: {tweet_content}")
    else:
        tweet_content = "心に寄り添う今日のメッセージです。"
    
    # 画像生成（仮実装）
    image_path = None
    if image_config.get('image', {}).get('enabled', False):
        # 実際には画像生成APIを使用
        folder = image_config['image'].get('folder', 'images/emotion_link')
        os.makedirs(folder, exist_ok=True)
        
        # 既存画像を順次選択する実装
        try:
            import glob
            existing_images = glob.glob(os.path.join(folder, "*.png")) + glob.glob(os.path.join(folder, "*.jpg"))
            if existing_images:
                # sequential selection
                selection_mode = image_config['image'].get('selection', 'sequential')
                if selection_mode == 'sequential':
                    # 最後に使用した画像のインデックスを保存・読み込み
                    index_file = os.path.join(folder, '.last_used_index.txt')
                    last_index = 0
                    if os.path.exists(index_file):
                        try:
                            with open(index_file, 'r') as f:
                                last_index = int(f.read().strip())
                        except:
                            last_index = 0
                    
                    # 次のインデックス
                    next_index = (last_index + 1) % len(existing_images)
                    image_path = existing_images[next_index]
                    
                    # インデックスを保存
                    with open(index_file, 'w') as f:
                        f.write(str(next_index))
                        
                    logging.info(f"選択された画像: {image_path}")
        except Exception as e:
            logging.warning(f"画像選択エラー: {e}")
    
    if not dry_run:
        success = post_tweet(driver, tweet_content, image_path)
        if success:
            logging.info("STEP3: 画像付きツイート投稿成功")
        else:
            logging.error("STEP3: 画像付きツイート投稿失敗")
        return success
    else:
        logging.info("STEP3: ドライラン - 実際の投稿はスキップ")
        return True


def main():
    parser = argparse.ArgumentParser(description='emotion_link スケジュールツイート実行')
    parser.add_argument('--config', type=str, default='config/accounts_emotion_link.yaml', help='アカウント設定YAML')
    parser.add_argument('--live-run', action='store_true', help='実際にツイートを投稿（デフォルト: ドライラン）')
    parser.add_argument('--force-run', action='store_true', help='スケジュール時刻を無視して強制実行')
    parser.add_argument('--step', type=str, choices=['step1', 'step2', 'step3', 'all'], default='all', help='実行するステップ')
    parser.add_argument('--target', type=str, default='emotion_link', help='対象アカウントのID（デフォルト: emotion_link）')
    
    args = parser.parse_args()
    
    # ログ設定
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - [emotion_link] - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('log/emotion_link_schedule.log', encoding='utf-8')
        ]
    )
    
    # ログディレクトリ作成
    os.makedirs('log', exist_ok=True)
    
    try:
        # 設定読み込み
        if not os.path.exists(args.config):
            raise FileNotFoundError(f"設定ファイルが見つかりません: {args.config}")
            
        account_config = load_account_config(args.config)
        logging.info(f"設定ファイル読み込み完了: {args.config}")
        logging.info(f"対象アカウント: {args.target}")
        
        # ブラウザ設定
        browser_config = account_config.get('browser', {})
        profile_dir = browser_config.get('user_data_dir', 'profile/emotion_link')
        headless = browser_config.get('headless', True)
        
        # WebDriver 起動
        driver = setup_driver(headless=headless, profile_path=profile_dir)
        if not driver:
            raise RuntimeError("WebDriver の初期化に失敗しました")
        
        logging.info("WebDriver 起動完了")
        
        # ステップ実行
        step1_content = None
        step3_image_prompt = None
        
        if args.step in ['step1', 'all']:
            step1_content = execute_step1_transit_tweet(account_config, driver, dry_run=not args.live_run, force_run=args.force_run)
        
        if args.step in ['step2', 'all'] and step1_content:
            step3_image_prompt = execute_step2_image_prompt_generation(account_config, step1_content)
        
        if args.step in ['step3', 'all'] and step1_content and step3_image_prompt:
            execute_step3_image_tweet(account_config, step1_content, step3_image_prompt, driver, dry_run=not args.live_run, force_run=args.force_run)
        
        logging.info("スケジュールツイート実行完了")
        
    except Exception as e:
        logging.error(f"実行エラー: {e}", exc_info=True)
        sys.exit(1)
    finally:
        close_driver()


if __name__ == '__main__':
    main()