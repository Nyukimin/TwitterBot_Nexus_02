#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
共有画像生成モジュールのテストスクリプト
shared_modules/image_generation/gemini_image_generator.py のテスト
"""

import os
import sys
from datetime import datetime

# プロジェクトパスを追加
sys.path.append(os.path.dirname(__file__))

# 共有画像生成モジュールをインポート
from shared_modules.image_generation import GeminiImageGenerator

def test_shared_image_generation():
    """共有画像生成モジュールのテスト"""
    
    print("=" * 70)
    print("🧪 共有画像生成モジュール テスト")
    print("=" * 70)
    
    # 画像生成器のインスタンス化
    try:
        generator = GeminiImageGenerator()
        print("✅ GeminiImageGeneratorのインスタンス化成功")
    except Exception as e:
        print(f"❌ インスタンス化エラー: {str(e)}")
        return False
    
    # テスト用プロンプト
    test_prompt = "A warm, gentle abstract illustration themed around emotions and psychology. Use soft pastel colors (pink, lavender, light blue) to express peace of mind and empathy. Create a flowing, curved design that heals the viewer's heart. Preserve this person's facial identity."
    
    # emotion_link用画像生成テスト
    print("\n📝 テストプロンプト:", test_prompt[:60] + "...")
    
    output_path = generator.generate_emotion_link_image(test_prompt)
    
    if output_path and os.path.exists(output_path):
        file_size = os.path.getsize(output_path)
        print(f"🎉 テスト成功!")
        print(f"📁 保存パス: {output_path}")
        print(f"📏 ファイルサイズ: {file_size} bytes")
        
        if file_size > 0:
            print("✅ ファイルサイズ0 bytes問題は修正されました!")
            return True
        else:
            print("❌ ファイルサイズが0 bytesです")
            return False
    else:
        print("❌ 画像生成に失敗しました")
        return False

def main():
    """メイン関数"""
    
    success = test_shared_image_generation()
    
    print("\n" + "=" * 70)
    if success:
        print("🎉 共有画像生成モジュールは正常に動作しています!")
        print("📂 画像確認先: images/emotion_link/")
        print("🔧 修正版Base64デコード処理により、ファイルサイズ0 bytes問題が解決されました")
    else:
        print("❌ 共有画像生成モジュールに問題があります")
    print("=" * 70)

if __name__ == "__main__":
    main()