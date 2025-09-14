#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gemini-2.5-flash-image-preview (Nano Banana) 正しい実装
参考情報に基づいた画像生成テスト
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

def generate_image_with_nano_banana(prompt, save_path):
    """
    Nano Banana (Gemini-2.5-flash-image-preview) で画像生成
    参考情報の正しい実装方法を使用
    """
    
    # Gemini API エンドポイント
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image-preview:generateContent"
    
    headers = {
        "x-goog-api-key": GEMINI_API_KEY,
        "Content-Type": "application/json"
    }
    
    # リクエストデータ（参考情報の形式）
    data = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }
    
    print(f"🎨 Nano Banana画像生成開始...")
    print(f"📝 プロンプト: {prompt[:50]}...")
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
                                print(f"✅ 画像データ発見!")
                                print(f"📄 MIMEタイプ: {inline_data.get('mimeType', 'unknown')}")
                                
                                # Base64デコードして保存
                                image_data = base64.b64decode(inline_data['data'])
                                
                                with open(save_path, 'wb') as f:
                                    f.write(image_data)
                                
                                file_size = os.path.getsize(save_path)
                                print(f"💾 画像保存完了: {save_path}")
                                print(f"📏 ファイルサイズ: {file_size} bytes")
                                
                                return True
                        
                        elif 'text' in part:
                            text_content = part['text'][:100]
                            print(f"  📝 テキスト: {text_content}...")
            
            print("⚠️ 画像データが見つかりませんでした")
            # レスポンス全体をデバッグ出力
            print("🔍 レスポンス詳細:")
            print(json.dumps(result, indent=2, ensure_ascii=False)[:500] + "...")
            
        else:
            print(f"❌ APIエラー: {response.status_code}")
            print(f"📄 レスポンス: {response.text[:200]}...")
            
    except Exception as e:
        print(f"❌ リクエストエラー: {str(e)}")
        
    return False

def test_emotion_link_image_generation():
    """emotion_link用画像生成テスト"""
    
    # テスト用プロンプト（emotion_linkの朝の設定）
    test_prompts = [
        {
            "time": "朝（8:00）",
            "prompt": "A warm, gentle abstract illustration themed around emotions and psychology. Use soft pastel colors (pink, lavender, light blue) to express peace of mind and empathy. Create a flowing, curved design that heals the viewer's heart.",
            "filename": "morning_emotion_test.png"
        }
    ]
    
    emotion_folder = os.path.join("images", "emotion_link")
    os.makedirs(emotion_folder, exist_ok=True)
    
    success_count = 0
    
    for i, test in enumerate(test_prompts, 1):
        print(f"\n--- テスト {i}: {test['time']} ---")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"nanobanan_{timestamp}_{test['filename']}"
        filepath = os.path.join(emotion_folder, filename)
        
        if generate_image_with_nano_banana(test['prompt'], filepath):
            success_count += 1
            print(f"🎉 テスト {i} 成功!")
        else:
            print(f"❌ テスト {i} 失敗")
    
    return success_count > 0

def main():
    """メイン関数"""
    print("=" * 70)
    print("🍌 Nano Banana (Gemini-2.5-flash-image-preview) 実装テスト")
    print("=" * 70)
    
    print("📋 実装詳細:")
    print("• モデル: gemini-2.5-flash-image-preview") 
    print("• エンドポイント: Gemini API (AI Studio)")
    print("• 認証: x-goog-api-key ヘッダー")
    print("• 出力: inlineData.data (base64)")
    
    # 画像生成テスト
    if test_emotion_link_image_generation():
        print("\n🎉 Nano Banana画像生成テスト成功!")
        print("📁 生成画像確認: images/emotion_link/")
    else:
        print("\n⚠️ 画像生成に課題があります")
        print("💡 API設定またはエンドポイントを再確認してください")

if __name__ == "__main__":
    main()