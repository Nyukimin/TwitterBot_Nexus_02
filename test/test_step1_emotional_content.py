#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
step1_emotional_contentの内容をコンソール表示するテスト
"""

import os
import sys
from datetime import datetime

# プロジェクトパスを追加
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from shared_modules.text_processing import extract_emotional_content

def test_step1_emotional_content():
    """
    step1_emotional_contentの内容をコンソール表示
    """
    
    print("=" * 70)
    print("🔍 step1_emotional_content 内容確認テスト")
    print("=" * 70)
    
    # テスト用のSTEP1出力（最新のテスト結果から）
    step1_output = "今日は、月が魚座さんへ。感受性が豊かになる日だよね。人の気持ちがいつも以上に分かって、共感力が爆上がりしそう。繊細になりやすいから、自分の心も大切にしてあげてね。温かい飲み物を飲んで、ほっと一息ついてみて。"
    
    print(f"📝 元のstep1_output:")
    print(f"   {step1_output}")
    print(f"   文字数: {len(step1_output)}")
    
    # extract_emotional_content関数を実行
    step1_emotional_content = extract_emotional_content(step1_output)
    
    print(f"\n🎯 処理後のstep1_emotional_content:")
    print(f"   {step1_emotional_content}")
    print(f"   文字数: {len(step1_emotional_content)}")
    
    # 削除された部分を表示
    if step1_output.startswith("今日は"):
        first_sentence_end = step1_output.find("。")
        if first_sentence_end != -1:
            removed_part = step1_output[:first_sentence_end+1]
            print(f"\n❌ 削除された部分:")
            print(f"   {removed_part}")
    
    print("\n" + "=" * 70)
    print("✅ step1_emotional_content内容確認完了")
    print("=" * 70)

if __name__ == "__main__":
    test_step1_emotional_content()