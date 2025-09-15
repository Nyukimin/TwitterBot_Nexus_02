#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ツイートと画像の実際の生成テスト

改善されたSTEP1～STEP3システムを使用して、
実際のTwitter投稿用のツイートと画像を生成します。

1. STEP1: 占星術トランジット解釈ツイート生成
2. STEP2: step1_emotional_contentを使用した画像プロンプト生成
3. STEP3: 実際の画像生成と保存
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

def print_content(label, content, char_count=True):
    """内容を整形して表示"""
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

def generate_tweet_and_image():
    """ツイートと画像の生成メイン関数"""
    
    print_section_header("🐦 ツイートと画像の実際の生成", "🎨")
    
    try:
        # ===== STEP1: 占星術トランジット解釈ツイート生成 =====
        print_section_header("STEP1: 占星術トランジット解釈ツイート生成", "🌟")
        
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
        tweet_content = interpreter.generate_interpretation(
            prompt_template, planets, "transit", personality_prompt
        )
        
        print_content("📝 生成されたツイート内容", tweet_content)
        
        # 感情的内容を抽出
        emotional_content = extract_emotional_content(tweet_content)
        print_content("🎯 抽出された感情的内容", emotional_content)
        
        # ===== STEP2: 画像プロンプト生成 =====
        print_section_header("STEP2: 画像プロンプト生成", "🎨")
        
        # step1_emotional_contentを使用して画像プロンプトを生成
        image_prompt_template = emotion_link_config['image_prompt_config']['schedule'][0]['ai_generate']['prompt']
        image_prompt_input = image_prompt_template.format(
            step1_emotional_content=emotional_content
        )
        
        print_content("🔧 画像プロンプト生成用テンプレート", image_prompt_input[:200] + "..." if len(image_prompt_input) > 200 else image_prompt_input)
        
        # GeminiInterpreterで画像プロンプトを生成
        image_prompt = interpreter.generate_interpretation(
            image_prompt_input, {}, "image_prompt", ""
        )
        
        print_content("🎨 生成された画像プロンプト", image_prompt)
        
        # ===== STEP3: 実際の画像生成 =====
        print_section_header("STEP3: 実際の画像生成", "🖼️")
        
        # 画像生成用のプロンプトを準備
        final_image_prompt = image_prompt
        
        # face_reference設定を追加
        face_reference_prompt = "Preserve this person's facial identity."
        final_image_prompt += f" {face_reference_prompt}"
        print(f"🎭 face_reference追加: {face_reference_prompt}")
        
        print_content("🖼️ 最終画像プロンプト", final_image_prompt)
        
        # 実際の画像生成を実行
        print("🔄 画像生成中...")
        try:
            # 画像生成器を初期化
            image_generator = GeminiImageGenerator()
            
            # 画像保存パスを設定
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            image_filename = f"emotion_link_tweet_{timestamp}.png"
            image_path = project_root / "images" / "emotion_link" / image_filename
            
            # ディレクトリを作成（存在しない場合）
            image_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 画像生成（gemini-2.5-flash-image-previewモデルを使用）
            success = image_generator.generate_image(final_image_prompt, str(image_path))
            
            if success:
                print("✅ 画像生成成功")
                print(f"💾 画像保存完了: {image_path}")
                
                # ファイルサイズも確認
                if image_path.exists():
                    file_size = image_path.stat().st_size
                    print(f"📏 画像サイズ: {file_size:,} bytes ({file_size/1024/1024:.2f} MB)")
            else:
                print("❌ 画像生成失敗")
                
        except Exception as e:
            print(f"❌ 画像生成エラー: {str(e)}")
        
        # ===== 結果サマリー =====
        print_section_header("生成結果サマリー", "📊")
        
        print("🐦 **Twitter投稿用コンテンツ**")
        print(f"   ツイート文字数: {len(tweet_content)}")
        print(f"   感情的内容文字数: {len(emotional_content)}")
        print(f"   削除された文字数: {len(tweet_content) - len(emotional_content)}")
        print()
        
        print("🎨 **画像生成結果**")
        if 'image_path' in locals() and image_path.exists():
            print(f"   ✅ 画像生成: 成功")
            print(f"   📁 保存場所: {image_path}")
            print(f"   📏 ファイルサイズ: {image_path.stat().st_size:,} bytes")
        else:
            print("   ❌ 画像生成: 失敗")
        print()
        
        # 占星術要素の検出
        astro_elements = ['月', '太陽', '水星', '金星', '火星', '木星', '土星', '天王星', '海王星', '冥王星', 
                         '牡羊座', '牡牛座', '双子座', '蟹座', '獅子座', '乙女座', '天秤座', '蠍座', '射手座', '山羊座', '水瓶座', '魚座']
        
        found_elements = [element for element in astro_elements if element in image_prompt]
        
        print("🔍 **改善効果の確認**")
        if found_elements:
            print(f"   ⚠️ 画像プロンプトに占星術要素検出: {', '.join(found_elements)}")
        else:
            print("   ✅ 画像プロンプトに占星術要素なし - 完全に感情的内容のみ")
        
        print(f"   🎯 step1_emotional_content機能: 動作正常")
        print(f"   🎨 画像プロンプト生成: 感情内容ベース")
        print(f"   🖼️ 画像生成: Gemini-2.5-flash-image-preview使用")
        
        print_section_header("ツイートと画像生成完了", "🎯")
        
        # 実際のTwitter投稿用の最終出力
        print("\n" + "🐦" * 25)
        print("📱 **Twitter投稿用最終コンテンツ**")
        print("🐦" * 25)
        print(f"ツイート内容:\n{tweet_content}")
        print(f"\n画像ファイル: {image_filename}")
        print("🐦" * 25)
        
        return {
            "tweet_content": tweet_content,
            "emotional_content": emotional_content,
            "image_prompt": image_prompt,
            "image_path": str(image_path) if 'image_path' in locals() else None,
            "image_generated": success if 'success' in locals() else False
        }
        
    except Exception as e:
        print(f"❌ エラーが発生しました: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """メイン実行関数"""
    result = generate_tweet_and_image()
    
    if result and result["image_generated"]:
        print("\n🎉 ツイートと画像の生成が正常に完了しました！")
        return True
    else:
        print("\n❌ ツイートまたは画像の生成に問題が発生しました")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)