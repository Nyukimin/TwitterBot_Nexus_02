#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成された画像のサイズを確認するスクリプト
"""

import os
from PIL import Image

def check_image_dimensions():
    """生成された画像の実際のサイズを確認"""
    
    emotion_folder = os.path.join("images", "emotion_link")
    
    if not os.path.exists(emotion_folder):
        print("❌ 画像フォルダが見つかりません")
        return
    
    # フォルダ内の画像ファイルを取得
    image_files = [f for f in os.listdir(emotion_folder) if f.endswith('.png')]
    
    if not image_files:
        print("❌ 画像ファイルが見つかりません")
        return
    
    print("🔍 生成された画像のサイズ確認:")
    print("="*60)
    
    for filename in sorted(image_files):
        filepath = os.path.join(emotion_folder, filename)
        
        try:
            with Image.open(filepath) as img:
                width, height = img.size
                aspect_ratio = width / height
                
                print(f"📁 ファイル: {filename}")
                print(f"📐 サイズ: {width} x {height}")
                print(f"📊 アスペクト比: {aspect_ratio:.3f} ({width}:{height})")
                
                # 16:9の理論値は1.778
                if abs(aspect_ratio - 1.778) < 0.1:
                    print("✅ 16:9に近い比率")
                elif abs(aspect_ratio - 1.0) < 0.1:
                    print("⚠️  1:1 (正方形)")
                else:
                    print(f"ℹ️  カスタム比率")
                
                print("-" * 40)
                
        except Exception as e:
            print(f"❌ {filename} の読み込みエラー: {e}")
    
    print("\n📋 結論:")
    print("• Gemini-2.5-flash-image-previewの実際の出力サイズを確認")
    print("• プロンプトで16:9を指定してもファイルサイズが変わるかをチェック")

if __name__ == "__main__":
    check_image_dimensions()