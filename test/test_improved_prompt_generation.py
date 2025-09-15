#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
改善版プロンプト生成システムのテスト
占星術記述除去機能付き
"""

import os
import sys
from datetime import datetime

# プロジェクトパスを追加
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from shared_modules.text_processing import extract_emotional_content

def test_improved_prompt_flow():
    """
    改善版STEP1-3フロー（占星術記述除去機能付き）テスト
    """
    
    print("=" * 70)
    print("🔧 改善版プロンプト生成システムテスト")
    print("=" * 70)
    
    # テスト用のSTEP1出力（実際の出力例）
    step1_output = "今日は、月が魚座さんを優しく照らしているみたい。なんだか心がじんわり温かくなるような、そんな日だよね。感受性が豊かになるから、人の気持ちに寄り添えたり、美しいものに感動したり。自分の内側の声にも耳を澄ませてみてね。"
    
    print(f"📝 元のSTEP1出力:")
    print(f"   {step1_output}")
    print(f"   文字数: {len(step1_output)}")
    
    # 占星術記述を除去し、感情的内容のみを抽出
    emotional_content = extract_emotional_content(step1_output)
    
    print(f"\n🎯 抽出された感情的内容:")
    print(f"   {emotional_content}")
    print(f"   文字数: {len(emotional_content)}")
    
    # 改善版プロンプト生成デモ
    improved_prompt = generate_improved_prompt(emotional_content)
    
    print(f"\n🎨 改善版画像プロンプト:")
    print(f"   {improved_prompt}")
    print(f"   文字数: {len(improved_prompt)}")
    
    print("\n" + "=" * 70)
    print("✅ 改善版プロンプト生成テスト完了")
    print("📊 改善点:")
    print("  - 占星術記述の自動除去")
    print("  - 感情的内容のみに基づく画像生成")
    print("  - より簡潔で効果的なプロンプト")
    print("=" * 70)

def generate_improved_prompt(emotional_content: str) -> str:
    """
    感情的内容から改善版プロンプトを生成
    """
    
    # 感情キーワード分析
    emotion_keywords = {
        "温かい": "warm golden light",
        "感受性": "gentle and empathetic expression", 
        "寄り添": "caring and supportive pose",
        "美しい": "surrounded by natural beauty",
        "内側の声": "contemplative and introspective mood"
    }
    
    # 検出された感情要素
    detected_elements = []
    for keyword, visual_element in emotion_keywords.items():
        if keyword in emotional_content:
            detected_elements.append(visual_element)
    
    # 基本プロンプト構成
    base_prompt = "A beautiful young Japanese woman with a gentle expression, standing in a serene natural setting."
    
    # 感情要素を統合
    if detected_elements:
        emotional_description = " ".join(detected_elements[:3])  # 最大3要素
        enhanced_prompt = f"{base_prompt} She has a {emotional_description}, with soft natural lighting creating a peaceful atmosphere. Full-body view, flowing dress, photorealistic style. Preserve this person's facial identity."
    else:
        enhanced_prompt = f"{base_prompt} Peaceful and serene atmosphere with soft lighting. Full-body view, flowing dress, photorealistic style. Preserve this person's facial identity."
    
    return enhanced_prompt

def compare_old_vs_new():
    """
    旧システムと新システムの比較
    """
    
    print("\n" + "=" * 70)
    print("📊 旧システム vs 新システム比較")
    print("=" * 70)
    
    print("❌ 旧システムの問題:")
    print("  - 占星術記述も画像生成に使用")
    print("  - 固定的な制約（年齢、髪型、色調）")
    print("  - 長すぎるプロンプト（800+文字）")
    print("  - JSON+英語プロンプトの二重構造")
    
    print("\n✅ 新システムの改善:")
    print("  - 感情的内容のみを使用")
    print("  - 内容に応じた動的な要素調整")
    print("  - 簡潔で効果的なプロンプト（200-300文字）")
    print("  - 直接的な英語プロンプト生成")
    
    print("=" * 70)

def main():
    """
    メイン関数
    """
    test_improved_prompt_flow()
    compare_old_vs_new()

if __name__ == "__main__":
    main()
