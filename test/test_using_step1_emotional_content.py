#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
step1_emotional_contentを実際に利用するテスト
削除済みテキストで画像プロンプト生成を実行
"""

import os
import sys
from datetime import datetime
import pytz

# プロジェクトパスを追加
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from shared_modules.text_processing import extract_emotional_content
from shared_modules.astrology.astro_system import AstroCalculator, GeminiInterpreter

def test_using_step1_emotional_content():
    """
    step1_emotional_contentを実際に利用した画像プロンプト生成テスト
    """
    
    print("=" * 70)
    print("🚀 step1_emotional_content実利用テスト")
    print("=" * 70)
    
    # 1. STEP1出力の生成
    calculator = AstroCalculator()
    interpreter = GeminiInterpreter()
    
    # 現在の惑星位置を計算（タイムゾーン付き）
    jst = pytz.timezone('Asia/Tokyo')
    current_time = datetime.now(jst)
    planets = calculator.calculate_planet_positions(current_time)
    print(f"惑星位置計算完了: {len(planets)}個の惑星")
    
    # STEP1: トランジット解釈生成
    step1_prompt = """今日のトランジットを少し柔らかいトーンでわかりやすく表現。
「今日は」で始めて。
その後 トランジットを 140文字以内で解釈。
感情・人間関係・内面成長をテーマに、温かく寄り添う一言メッセージ。
ハッシュタグなし。140文字程度。"""
    
    step1_output = interpreter.generate_interpretation(step1_prompt, planets, "transit")
    print(f"\n📝 STEP1生成結果:")
    print(f"   {step1_output}")
    print(f"   文字数: {len(step1_output)}")
    
    # 2. step1_emotional_contentの抽出
    step1_emotional_content = extract_emotional_content(step1_output)
    print(f"\n🎯 step1_emotional_content:")
    print(f"   {step1_emotional_content}")
    print(f"   文字数: {len(step1_emotional_content)}")
    
    # 3. step1_emotional_contentを使用した画像プロンプト生成
    step2_prompt = f"""You are a Prompt Compiler. Convert emotional/psychological content from a Japanese tweet into an English image-generation prompt.

## PREPROCESSING STEP
The input text has already been processed to remove astronomical content.

Input text: {step1_emotional_content}

## FIXED CONSTRAINTS
- One Japanese woman, 25–30 years old.
- Photorealistic, realistic, high-quality photography style.
- single subject, no text, no logo.
- End with: "Preserve this person's facial identity."

## OUTPUT
Write one cohesive English prompt (6–8 sentences).  
Use ONLY the processed emotional content (not the astronomical part) to decide her hair style, facial expression, clothing, pose, background, time of day, and atmosphere.  
End with: "Preserve this person's facial identity\""""
    
    step3_image_prompt = interpreter.generate_interpretation(step2_prompt, {}, "image_prompt_generation")
    
    print(f"\n🎨 step1_emotional_content使用の画像プロンプト:")
    print(f"   前半: {step3_image_prompt[:80]}...")
    print(f"   文字数: {len(step3_image_prompt)}")
    
    # 4. 占星術要素の検出
    astronomical_terms = ["魚座", "Pisces", "moon", "星座", "planet", "transit", "astrology"]
    found_terms = [term for term in astronomical_terms if term.lower() in step3_image_prompt.lower()]
    
    print(f"\n🔍 占星術要素検出:")
    if found_terms:
        print(f"   ❌ 発見された占星術要素: {found_terms}")
    else:
        print(f"   ✅ 占星術要素なし - 完全に感情的内容のみ")
    
    print("\n" + "=" * 70)
    print("🎯 step1_emotional_content実利用テスト完了")
    print("=" * 70)
    
    return {
        "step1_output": step1_output,
        "step1_emotional_content": step1_emotional_content,
        "step3_image_prompt": step3_image_prompt,
        "astronomical_terms_found": found_terms
    }

if __name__ == "__main__":
    results = test_using_step1_emotional_content()