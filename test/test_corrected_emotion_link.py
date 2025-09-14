#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import sys
import os
from datetime import datetime
import pytz

# プロジェクトのルートディレクトリをパスに追加
# testフォルダから親ディレクトリ（プロジェクトルート）をパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared_modules.astrology.astro_system import AstroCalculator, GeminiInterpreter

def test_corrected_emotion_link_flow():
    """修正されたemotion_linkアカウントのSTEP1-3フローをテスト"""
    
    print("=" * 60)
    print("emotion_link 修正版 STEP1-3 Flow Test")
    print("=" * 60)
    
    # 日本時間で現在時刻を取得
    jst = pytz.timezone('Asia/Tokyo')
    current_time = datetime.now(jst)
    print(f"テスト実行日時: {current_time.strftime('%Y-%m-%d %H:%M:%S JST')}")
    print()
    
    try:
        # 占星術計算機の初期化
        calculator = AstroCalculator()
        
        # Gemini解釈システムの初期化
        interpreter = GeminiInterpreter()
        
        # 惑星位置の計算
        print("1. 惑星位置を計算中...")
        planets = calculator.calculate_planet_positions(current_time)
        print(f"   取得した惑星数: {len(planets)}")
        print()
        
        # STEP1: トランジット解釈ツイート（06:00）
        print("=" * 50)
        print("STEP1: トランジット解釈ツイート（06:00）")
        print("=" * 50)
        
        # YAML設定からPERSONALITY_PROMPTとtransit_configを読み込み
        import yaml
        with open('config/accounts_emotion_link.yaml', 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        account_config = config['accounts'][0]  # emotion_linkアカウント
        personality_prompt = account_config.get('PERSONALITY_PROMPT', '')
        transit_config = account_config.get('transit_config', {})
        
        # YAML設定のSTEP1プロンプトを使用
        step1_base_prompt = """今日のトランジット（惑星配置）から、心理的・感情的な側面を重視した今日の全体的な傾向を解釈してください。特に感情の変化、人間関係への影響、内面的な成長の機会について詳しく分析し、読む人が自分の感情と向き合う手助けとなるような、温かく寄り添う言葉で表現してください。"""
        
        if transit_config.get('schedule'):
            schedule_config = transit_config['schedule'][0]
            if schedule_config.get('ai_generate', {}).get('prompt'):
                step1_base_prompt = schedule_config['ai_generate']['prompt']
        
        step1_result = interpreter.generate_interpretation(step1_base_prompt, planets, "emotion_step1", personality_prompt=personality_prompt)
        print("【STEP1 出力（最終ツイート用テキスト）】")
        print(step1_result)
        print(f"文字数: {len(step1_result)}")
        print()
        
        # STEP2: STEP3用画像プロンプト生成（06:15）
        print("=" * 50)
        print("STEP2: STEP3用画像プロンプト生成（06:15）")
        print("=" * 50)
        
        step2_prompt = f"""STEP1のトランジット解釈「{step1_result}」を受けて、この内容に最も適した画像生成プロンプト（英語）を作成してください。以下の要素を含めた英語のプロンプトを生成してください：1) 感情・心理テーマの視覚的表現、2) STEP1の内容に対応する色調や雰囲気、3) 温かさと希望を伝える要素、4) 'Preserve this person's facial identity'で始まる、5) 全身、平和的表情を含む。"""
        
        step2_image_prompt = interpreter.generate_interpretation(step2_prompt, planets, "emotion_step2_image_prompt")
        print("【STEP2 出力（STEP3用画像生成プロンプト）】")
        print(step2_image_prompt)
        print(f"文字数: {len(step2_image_prompt)}")
        print()
        
        # STEP3: 最終ツイート投稿（06:30）
        print("=" * 50)
        print("STEP3: 最終ツイート投稿（06:30）")
        print("=" * 50)
        print("【最終ツイート構成】")
        print(f"テキスト: {step1_result}")
        print(f"画像プロンプト: {step2_image_prompt}")
        print()
        print("face_reference機能:")
        print("- images/emotion_link/face_reference/face_01.jpg")
        print("- images/emotion_link/face_reference/face_02.jpg") 
        print("- images/emotion_link/face_reference/face_03.jpg")
        print("- preserve_identity: true")
        print()
        
        print("=" * 60)
        print("修正版 STEP1-3 フロー確認完了")
        print("=" * 60)
        print()
        print("【システムの流れ】")
        print("1. STEP1: トランジット解釈テキスト生成 → step1_output変数に保存")
        print("2. STEP2: STEP1を受けた画像プロンプト生成 → step3_image_prompt変数に保存")
        print("3. STEP3: STEP1のテキスト + STEP2の画像プロンプトで生成した画像 = 1つのツイート")
        print()
        
        return {
            'step1_text': step1_result,
            'step2_image_prompt': step2_image_prompt,
            'final_tweet': {
                'text': step1_result,
                'image_prompt': step2_image_prompt
            }
        }
        
    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    test_corrected_emotion_link_flow()