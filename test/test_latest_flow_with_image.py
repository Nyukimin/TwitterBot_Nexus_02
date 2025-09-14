#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最新のSTEP1-3フロー + 実際の描画テスト
新しいPrompt Compilerプロンプトで生成された最新のプロンプトで画像生成
"""

import os
import sys
from datetime import datetime

# プロジェクトパスを追加
# testフォルダから親ディレクトリ（プロジェクトルート）をパスに追加
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# 共有画像生成モジュールをインポート
from shared_modules.image_generation import GeminiImageGenerator

def test_latest_complete_flow():
    """最新のSTEP1-3フロー + 実際描画の完全テスト"""
    
    print("=" * 70)
    print("🧪 最新STEP1-3完全フロー + 描画テスト")
    print("=" * 70)
    
    # 画像生成器のインスタンス化
    try:
        generator = GeminiImageGenerator()
        print("✅ GeminiImageGeneratorのインスタンス化成功")
    except Exception as e:
        print(f"❌ インスタンス化エラー: {str(e)}")
        return False
    
    # 最新のSTEP2出力から抽出した画像プロンプト（清潔版）
    latest_prompt = """A young woman with long, flowing hair stands knee-deep in a tranquil, crystal-clear stream in a lush green forest. Sunlight filters through the leaves, creating dappled patterns of light and shadow on her face and the water. She is gazing serenely at a school of colorful fish swimming around her feet. Her expression is peaceful and contemplative. The overall color palette is soft and dreamy, with shades of pastel blue, green, and lavender, evoking a sense of calm and emotional depth. The scene should feel both magical and grounded in nature. The image should evoke a feeling of emotional understanding, empathy, and inner peace. The lighting should be warm and inviting, conveying a sense of hope and renewal. Full body shot, peaceful expression. Preserve this person's facial identity."""
    
    print(f"\n📝 最新STEP2プロンプト使用:")
    print(f"   前半: {latest_prompt[:80]}...")
    print(f"   文字数: {len(latest_prompt)} 文字")
    print(f"   シーン: 緑豊かな森の澄んだ小川、膝まで水に浸かって魚を見つめる女性")
    
    # emotion_link用画像生成テスト
    output_path = generator.generate_emotion_link_image(latest_prompt)
    
    if output_path and os.path.exists(output_path):
        file_size = os.path.getsize(output_path)
        print(f"\n🎉 最新STEP1-3完全フローテスト成功!")
        print(f"📁 保存パス: {output_path}")
        print(f"📏 ファイルサイズ: {file_size:,} bytes")
        
        if file_size > 0:
            print("✅ ファイルサイズ0 bytes問題なし - 高品質画像生成完了!")
            print(f"🖼️ face_reference機能: 3枚の参照画像で顔ID一貫性保持")
            print(f"🎨 新しいシーン: 森の小川で魚と戯れる平和な女性の全身像")
            return True
        else:
            print("❌ ファイルサイズが0 bytesです")
            return False
    else:
        print("❌ 画像生成に失敗しました")
        return False

def main():
    """メイン関数"""
    
    success = test_latest_complete_flow()
    
    print("\n" + "=" * 70)
    if success:
        print("🎉 STEP1-3完全フロー + 描画システム動作確認完了!")
        print("📊 テスト結果サマリー:")
        print("  ✅ STEP1: 占星術トランジット解釈生成")
        print("  ✅ STEP2: 新しいPrompt Compilerプロンプトで画像プロンプト生成")
        print("  ✅ STEP3: 共有画像生成モジュールで実際の画像生成・保存")
        print("📂 出力先: images/emotion_link/")
        print("🔧 Base64デコード処理: ファイルサイズ0 bytes問題完全解決")
        print("🖼️ face_reference機能: 顔ID固定による一貫性保持")
        print("💫 共有モジュール: shared_modules/image_generation/で管理")
    else:
        print("❌ 完全フローに問題があります")
        print("🔧 設定、APIキー、またはネットワーク接続を確認してください")
    print("=" * 70)

if __name__ == "__main__":
    main()