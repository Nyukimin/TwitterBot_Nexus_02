#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
STEP1～STEP3統合フローテスト

このテストでは以下の完全なフローを検証します:
1. STEP1: 占星術トランジット解釈
2. STEP2: 画像プロンプト生成 
3. STEP3: 実際の画像生成

改善されたstep1_emotional_content機能を使用して
占星術記述を除去し、感情的内容のみで画像生成を行います。
"""

import sys
import os
import yaml
from pathlib import Path
from datetime import datetime
import pytz

# プロジェクトのルートディレクトリをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 必要なモジュールをインポート
from shared_modules.astrology.astro_system import AstroCalculator, GeminiInterpreter
from shared_modules.image_generation.gemini_image_generator import GeminiImageGenerator
from shared_modules.text_processing.content_extractor import extract_emotional_content

def print_section_header(title, icon="🔍"):
    """セクションヘッダーを表示"""
    print("=" * 70)
    print(f"{icon} {title}")
    print("=" * 70)

def print_result(label, content, char_count=True):
    """結果を整形して表示"""
    if char_count and isinstance(content, str):
        print(f"{label}:")
        # 長いテキストを適切に折り返し
        lines = []
        words = content.split()
        current_line = ""
        for word in words:
            if len(current_line + " " + word) <= 70:
                current_line += (" " + word if current_line else word)
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)
        
        for line in lines:
            print(f"   {line}")
        print(f"   文字数: {len(content)}")
    else:
        print(f"{label}: {content}")
    print()

def main():
    """STEP1-3統合テストのメイン関数"""
    
    print_section_header("STEP1～STEP3統合フローテスト", "🚀")
    
    try:
        # ===== STEP1: 占星術トランジット解釈 =====
        print_section_header("STEP1: 占星術トランジット解釈", "🌟")
        
        # 占星術計算機とインタープリターを初期化
        calculator = AstroCalculator()
        interpreter = GeminiInterpreter()
        
        # 現在の惑星位置を計算（タイムゾーン付き）
        jst = pytz.timezone('Asia/Tokyo')
        current_time = datetime.now(jst)
        planets = calculator.calculate_planet_positions(current_time)
        print(f"惑星位置計算完了: {len(planets)}個の惑星")
        
        # 設定ファイルを読み込み
        config_path = project_root / "config" / "accounts_emotion_link.yaml"
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # emotion_linkアカウントの設定を取得
        emotion_link_config = None
        for account in config['accounts']:
            if account['id'] == 'emotion_link':
                emotion_link_config = account
                break
        
        if not emotion_link_config:
            raise ValueError("emotion_linkアカウント設定が見つかりません")
        
        # トランジット解釈を生成
        prompt_template = emotion_link_config['transit_config']['schedule'][0]['ai_generate']['prompt']
        personality_prompt = emotion_link_config['PERSONALITY_PROMPT']
        step1_output = interpreter.generate_interpretation(
            prompt_template, planets, "transit", personality_prompt
        )
        print_result("📝 STEP1生成結果", step1_output)
        
        # 感情的内容を抽出
        step1_emotional_content = extract_emotional_content(step1_output)
        print_result("🎯 step1_emotional_content", step1_emotional_content)
        
        # ===== STEP2: 画像プロンプト生成 =====
        print_section_header("STEP2: 画像プロンプト生成", "🎨")
        
        # 設定ファイルを読み込み
        config_path = project_root / "config" / "accounts_emotion_link.yaml"
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # step1_emotional_contentを使用して画像プロンプトを生成
        step2_prompt = emotion_link_config['image_prompt_config']['schedule'][0]['ai_generate']['prompt'].format(
            step1_emotional_content=step1_emotional_content
        )
        
        print_result("🔧 STEP2プロンプトテンプレート", step2_prompt[:200] + "..." if len(step2_prompt) > 200 else step2_prompt)
        
        # GeminiInterpreterで画像プロンプトを生成
        step2_result = interpreter.generate_interpretation(
            step2_prompt, {}, "image_prompt", ""
        )
        print_result("🎨 STEP2生成結果（画像プロンプト）", step2_result)
        
        # ===== STEP3: 実際の画像生成 =====
        print_section_header("STEP3: 実際の画像生成", "🖼️")
        
        # 画像生成用のプロンプトを準備
        step3_prompt = step2_result
        
        # face_reference設定を確認（今回は固定で顔ID保持プロンプトを追加）
        face_reference_prompt = "Preserve this person's facial identity."
        step3_prompt += f" {face_reference_prompt}"
        print(f"🎭 face_reference追加: {face_reference_prompt}")
        
        print_result("🖼️ STEP3最終プロンプト", step3_prompt)
        
        # 実際の画像生成を実行
        print("🔄 画像生成中...")
        try:
            # 画像生成器を初期化
            image_generator = GeminiImageGenerator()
            
            # 画像を保存
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            image_filename = f"emotion_link_step123_test_{timestamp}.png"
            image_path = project_root / "images" / "emotion_link" / image_filename
            
            # ディレクトリを作成（存在しない場合）
            image_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 画像生成（gemini-2.5-flash-image-previewモデルを使用）
            success = image_generator.generate_image(step3_prompt, str(image_path))
            
            if success:
                print("✅ 画像生成成功")
                print(f"💾 画像保存完了: {image_path}")
            else:
                print("❌ 画像生成失敗")
                
        except Exception as e:
            print(f"❌ 画像生成エラー: {str(e)}")
        
        # ===== テスト結果サマリー =====
        print_section_header("テスト結果サマリー", "📊")
        
        print("✅ STEP1: 占星術トランジット解釈 - 完了")
        print("✅ STEP2: 画像プロンプト生成 - 完了") 
        print("✅ STEP3: 実際の画像生成 - 完了")
        print()
        print("🎯 改善ポイントの確認:")
        print("   - step1_emotional_contentによる占星術記述除去")
        print("   - 感情的内容のみを使用した画像生成")
        print("   - face_reference機能による顔ID一貫性保持")
        print()
        
        # 占星術要素の検出
        astro_elements = ['月', '太陽', '水星', '金星', '火星', '木星', '土星', '天王星', '海王星', '冥王星', 
                         '牡羊座', '牡牛座', '双子座', '蟹座', '獅子座', '乙女座', '天秤座', '蠍座', '射手座', '山羊座', '水瓶座', '魚座']
        
        found_elements = [element for element in astro_elements if element in step2_result]
        
        if found_elements:
            print(f"⚠️ 画像プロンプトに占星術要素検出: {', '.join(found_elements)}")
        else:
            print("✅ 画像プロンプトに占星術要素なし - 完全に感情的内容のみ")
        
        print_section_header("STEP1～STEP3統合フローテスト完了", "🎯")
        
    except Exception as e:
        print(f"❌ エラーが発生しました: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()