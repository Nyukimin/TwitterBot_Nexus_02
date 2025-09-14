#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gemini-2.5-flash-image-preview正しい実装でのテスト
"""

import os
import sys
import google.generativeai as genai
from datetime import datetime
import base64
import io
from PIL import Image

# プロジェクトのconfigからAPIキーを取得
sys.path.append(os.path.dirname(__file__))
try:
    from reply_bot.config import GEMINI_API_KEY
    print(f"✅ プロジェクト設定からAPIキーを取得: {GEMINI_API_KEY[:20]}...")
except ImportError as e:
    print(f"❌ エラー: reply_bot.configからAPIキーを取得できません: {e}")
    exit(1)

def test_gemini_image_generation():
    """Gemini-2.5-flash-image-previewでの正しい画像生成テスト"""
    
    try:
        # Gemini APIの設定
        genai.configure(api_key=GEMINI_API_KEY)
        
        print("🔍 利用可能なモデルを確認...")
        models = list(genai.list_models())
        
        # 画像生成モデルを探す
        image_models = []
        for model in models:
            if 'image' in model.name.lower() and 'generateContent' in model.supported_generation_methods:
                image_models.append(model.name)
                print(f"  📋 発見: {model.name}")
        
        # Gemini-2.5-flash-image-previewが利用可能か確認
        target_model = "gemini-2.5-flash-image-preview"
        full_model_names = [m for m in image_models if 'gemini-2.5-flash' in m and 'image' in m]
        
        if full_model_names:
            model_name = full_model_names[0]
            print(f"✅ 使用モデル: {model_name}")
        else:
            # 代替モデルを試す
            alternative_models = [
                "gemini-2.0-flash-exp-image-generation",
                "gemini-2.0-flash-preview-image-generation"
            ]
            
            available_alt = [m for m in image_models if any(alt in m for alt in alternative_models)]
            if available_alt:
                model_name = available_alt[0]
                print(f"⚠️ 代替モデル使用: {model_name}")
            else:
                print("❌ 画像生成対応モデルが見つかりません")
                return False
        
        # テスト用プロンプト
        test_prompt = """感情と心理をテーマにした、温かく優しい印象を与える抽象的なイラスト。
柔らかなパステルカラー（ピンク、薄紫、水色）を使用し、
心の平穏さや共感を表現した画像を生成してください。
曲線的で流れるようなデザインで、見る人の心を癒すような画像にしてください。"""
        
        print(f"\n🎨 画像生成開始...")
        print(f"📝 プロンプト: {test_prompt[:50]}...")
        
        # モデル初期化
        model = genai.GenerativeModel(model_name)
        
        # 正しい画像生成リクエスト形式
        response = model.generate_content([test_prompt])
        
        print(f"📡 APIレスポンス受信: {type(response)}")
        print(f"📊 候補数: {len(response.candidates) if response.candidates else 0}")
        
        if response.candidates and len(response.candidates) > 0:
            candidate = response.candidates[0]
            print(f"📋 候補内容: {len(candidate.content.parts) if candidate.content and candidate.content.parts else 0} parts")
            
            if candidate.content and candidate.content.parts:
                for i, part in enumerate(candidate.content.parts):
                    print(f"  Part {i}: {type(part)}")
                    
                    # 画像データを探す
                    if hasattr(part, 'inline_data') and part.inline_data:
                        print(f"  ✅ 画像データ発見: {part.inline_data.mime_type}")
                        
                        # 画像保存
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = f"gemini_test_{timestamp}.png"
                        filepath = os.path.join("images", "emotion_link", filename)
                        
                        # Base64デコードして保存
                        image_data = base64.b64decode(part.inline_data.data)
                        
                        with open(filepath, "wb") as f:
                            f.write(image_data)
                        
                        file_size = os.path.getsize(filepath)
                        print(f"✅ 画像保存成功!")
                        print(f"📁 保存先: {filepath}")
                        print(f"📏 ファイルサイズ: {file_size} bytes")
                        
                        if file_size > 0:
                            return True
                        else:
                            print("⚠️ ファイルサイズが0バイトです")
                    
                    elif hasattr(part, 'text'):
                        print(f"  📝 テキスト応答: {part.text[:100]}...")
        
        # 代替アプローチ：直接generate_images API使用を試す
        print("\n🔄 代替アプローチを試行...")
        
        try:
            # Imagen API直接呼び出しを試す（存在する場合）
            if hasattr(genai, 'generate_images'):
                print("🎨 generate_images APIを発見")
                result = genai.generate_images(
                    model=model_name,
                    prompt=test_prompt,
                    number_of_images=1
                )
                print(f"📡 代替API結果: {type(result)}")
                
        except Exception as alt_error:
            print(f"⚠️ 代替アプローチエラー: {alt_error}")
        
        return False
        
    except Exception as e:
        print(f"❌ 画像生成エラー: {str(e)}")
        print(f"📋 エラータイプ: {type(e)}")
        
        # デバッグ情報を表示
        import traceback
        print(f"🔍 スタックトレース:")
        traceback.print_exc()
        
        return False

def main():
    """メイン関数"""
    print("=" * 70)
    print("🧪 Gemini-2.5-flash-image-preview 修正テスト")
    print("=" * 70)
    
    # フォルダ確認
    emotion_folder = os.path.join("images", "emotion_link")
    if not os.path.exists(emotion_folder):
        print(f"📁 フォルダを作成: {emotion_folder}")
        os.makedirs(emotion_folder, exist_ok=True)
    
    # 画像生成テスト
    success = test_gemini_image_generation()
    
    if success:
        print("\n🎉 成功: Gemini画像生成が動作しました！")
    else:
        print("\n⚠️ 画像生成に問題があります")
        print("💡 設定を再確認するか、OpenAI DALL-E 3の使用を検討してください")

if __name__ == "__main__":
    main()