#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Nano Banana (Gemini-2.5-flash-image-preview) 16:9画像生成テスト
imageDimensionsを使用したアスペクト比指定
"""

import os
import sys
import requests
import base64
import json
from datetime import datetime

# プロジェクトのconfigからAPIキーを取得
sys.path.append(os.path.dirname(__file__))
try:
    from reply_bot.config import GEMINI_API_KEY
    print(f"✅ プロジェクト設定からAPIキーを取得: {GEMINI_API_KEY[:20]}...")
except ImportError as e:
    print(f"❌ エラー: reply_bot.configからAPIキーを取得できません: {e}")
    exit(1)

def generate_16_9_image(prompt, save_path):
    """
    16:9のアスペクト比で画像生成
    imageDimensionsを使用して1920x1080指定
    """
    
    # Gemini API エンドポイント
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image-preview:generateContent"
    
    headers = {
        "x-goog-api-key": GEMINI_API_KEY,
        "Content-Type": "application/json"
    }
    
    # 16:9指定のリクエストデータ
    data = {
        "contents": [{
            "parts": [{
                "text": f"{prompt}, aspect ratio 16:9, wide shot, cinematic composition"
            }]
        }],
        # generationConfig で画像サイズを指定
        "generationConfig": {
            "imageDimensions": {
                "width": 1920,
                "height": 1080
            }
        }
    }
    
    print(f"🎨 16:9画像生成開始...")
    print(f"📝 プロンプト: {prompt[:50]}...")
    print(f"📐 サイズ指定: 1920x1080 (16:9)")
    print(f"🌐 エンドポイント: {url}")
    
    try:
        # API リクエスト実行
        response = requests.post(url, headers=headers, json=data)
        
        print(f"📡 HTTPステータス: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ APIレスポンス成功")
            
            # デバッグ: レスポンス構造を確認
            print(f"📊 候補数: {len(result.get('candidates', []))}")
            
            if 'candidates' in result and len(result['candidates']) > 0:
                candidate = result['candidates'][0]
                
                if 'content' in candidate and 'parts' in candidate['content']:
                    parts = candidate['content']['parts']
                    print(f"📋 パート数: {len(parts)}")
                    
                    for i, part in enumerate(parts):
                        print(f"  Part {i}: {list(part.keys())}")
                        
                        # 画像データを探す
                        if 'inlineData' in part:
                            inline_data = part['inlineData']
                            if 'data' in inline_data:
                                print(f"✅ 16:9画像データ発見!")
                                print(f"📄 MIMEタイプ: {inline_data.get('mimeType', 'unknown')}")
                                
                                # Base64デコードして保存
                                image_data = base64.b64decode(inline_data['data'])
                                
                                with open(save_path, 'wb') as f:
                                    f.write(image_data)
                                
                                file_size = os.path.getsize(save_path)
                                print(f"💾 16:9画像保存完了: {save_path}")
                                print(f"📏 ファイルサイズ: {file_size} bytes")
                                
                                return True
                        
                        elif 'text' in part:
                            text_content = part['text'][:100]
                            print(f"  📝 テキスト: {text_content}...")
            
            print("⚠️ 画像データが見つかりませんでした")
            
        else:
            print(f"❌ APIエラー: {response.status_code}")
            print(f"📄 レスポンス: {response.text[:500]}...")
            
            # generationConfigがサポートされていない可能性をテスト
            print("\n🔄 代替アプローチ: プロンプトのみで16:9指定...")
            return generate_16_9_fallback(prompt, save_path)
            
    except Exception as e:
        print(f"❌ リクエストエラー: {str(e)}")
        
    return False

def generate_16_9_fallback(prompt, save_path):
    """
    プロンプトのみで16:9指定（generationConfigが使えない場合）
    """
    
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image-preview:generateContent"
    
    headers = {
        "x-goog-api-key": GEMINI_API_KEY,
        "Content-Type": "application/json"
    }
    
    # プロンプトのみで16:9指定
    enhanced_prompt = f"""Generate a high-quality image with these specifications:
- Content: {prompt}
- Aspect ratio: 16:9 (wide screen format)
- Composition: Cinematic wide shot
- Format: Horizontal landscape orientation
- Style: Professional, visually balanced for 16:9 display"""
    
    data = {
        "contents": [{
            "parts": [{"text": enhanced_prompt}]
        }]
    }
    
    print(f"🔄 フォールバック: プロンプトベース16:9生成...")
    
    try:
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 200:
            result = response.json()
            
            if 'candidates' in result and len(result['candidates']) > 0:
                candidate = result['candidates'][0]
                
                if 'content' in candidate and 'parts' in candidate['content']:
                    parts = candidate['content']['parts']
                    
                    for part in parts:
                        if 'inlineData' in part and 'data' in part['inlineData']:
                            image_data = base64.b64decode(part['inlineData']['data'])
                            
                            with open(save_path, 'wb') as f:
                                f.write(image_data)
                            
                            file_size = os.path.getsize(save_path)
                            print(f"✅ フォールバック成功: {save_path}")
                            print(f"📏 ファイルサイズ: {file_size} bytes")
                            
                            return True
        
    except Exception as e:
        print(f"❌ フォールバックエラー: {str(e)}")
    
    return False

def test_16_9_generation():
    """16:9画像生成テスト"""
    
    # テスト用プロンプト
    test_cases = [
        {
            "name": "感情抽象アート",
            "prompt": "Abstract emotional artwork with flowing curves and soft pastel colors, representing peace and empathy, gentle and warm atmosphere",
            "filename": "emotion_16_9_test.png"
        },
        {
            "name": "心理風景", 
            "prompt": "Psychological landscape with dreamy elements, soft lighting, representing inner peace and mental wellness, therapeutic atmosphere",
            "filename": "psychology_16_9_test.png"
        }
    ]
    
    emotion_folder = os.path.join("images", "emotion_link")
    os.makedirs(emotion_folder, exist_ok=True)
    
    success_count = 0
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"テスト {i}: {test['name']}")
        print(f"{'='*60}")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"16_9_{timestamp}_{test['filename']}"
        filepath = os.path.join(emotion_folder, filename)
        
        if generate_16_9_image(test['prompt'], filepath):
            success_count += 1
            print(f"🎉 テスト {i} 成功!")
        else:
            print(f"❌ テスト {i} 失敗")
    
    return success_count

def main():
    """メイン関数"""
    print("="*70)
    print("🖼️ Nano Banana 16:9画像生成テスト")
    print("="*70)
    
    print("📋 テスト内容:")
    print("• アスペクト比: 16:9 (1920x1080)")
    print("• 方法1: generationConfig.imageDimensions指定")
    print("• 方法2: プロンプトベースの16:9指定")
    print("• モデル: gemini-2.5-flash-image-preview")
    
    # テスト実行
    success_count = test_16_9_generation()
    
    if success_count > 0:
        print(f"\n🎉 16:9画像生成テスト成功! ({success_count}枚生成)")
        print("📁 生成画像確認: images/emotion_link/")
        print("💡 16:9のワイド画像が生成されました!")
    else:
        print("\n⚠️ 16:9画像生成に課題があります")
        print("💡 設定を再確認してください")

if __name__ == "__main__":
    main()