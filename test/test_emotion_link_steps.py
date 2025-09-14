#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import sys
import os
from datetime import datetime
import pytz

# プロジェクトのルートディレクトリをパスに追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from shared_modules.astrology.astro_system import AstroCalculator, GeminiInterpreter

def test_emotion_link_steps():
    """emotion_linkアカウントのSTEP1-3の出力をテスト"""
    
    print("=" * 60)
    print("emotion_link STEP1-3 Output Test")
    print("=" * 60)
    
    # 日本時間で現在時刻を取得
    jst = pytz.timezone('Asia/Tokyo')
    current_time = datetime.now(jst)
    print(f"テスト実行日時: {current_time.strftime('%Y-%m-%d %H:%M:%S JST')}")
    print()
    
    try:
        # 占星術計算機の初期化
        calculator = AstroCalculator()
        
        # Gemini解釈システムの初期化
        interpreter = GeminiInterpreter()
        
        # 惑星位置の計算
        print("1. 惑星位置を計算中...")
        planets = calculator.calculate_planet_positions(current_time)
        print(f"   取得した惑星数: {len(planets)}")
        print()
        
        # STEP1: トランジット解釈（06:00）
        print("=" * 50)
        print("STEP1: トランジット解釈ツイート（06:00）")
        print("=" * 50)
        
        step1_prompt = """今日の惑星トランジットから、感情や心理状態への影響を解釈してください。

特に以下の点に注目して140文字以内で簡潔に：
- 今日の感情の流れ
- 心理的な変化のサイン
- 感情バランスのアドバイス

占星術的根拠を含めながら、実生活に役立つメッセージを。"""
        
        step1_result = interpreter.generate_interpretation(step1_prompt, planets, "emotion_step1")
        print("【STEP1 出力】")
        print(step1_result)
        print(f"文字数: {len(step1_result)}")
        print()
        
        # STEP2: 心理的アドバイス（06:15）
        print("=" * 50)
        print("STEP2: 心理的アドバイスツイート（06:15）")
        print("=" * 50)
        
        step2_prompt = f"""STEP1の解釈「{step1_result}」を受けて、具体的な心理的アドバイスを140文字以内で提供してください。

以下の要素を含めて：
- 今日の感情管理のコツ
- ストレス対処法
- 前向きな気持ちを維持する方法
- 人間関係での注意点

実践的で温かいアドバイスを心がけて。"""
        
        step2_result = interpreter.generate_interpretation(step2_prompt, planets, "emotion_step2")
        print("【STEP2 出力】")
        print(step2_result)
        print(f"文字数: {len(step2_result)}")
        print()
        
        # STEP3: 画像生成用プロンプト（06:30）
        print("=" * 50)
        print("STEP3: 画像付きツイート（06:30）")
        print("=" * 50)
        
        step3_prompt = f"""STEP1「{step1_result}」とSTEP2「{step2_result}」の内容を統合して、感情と心理をテーマにした温かいメッセージを140文字以内で作成してください。

以下の点を意識して：
- 今日一日を前向きに過ごすためのメッセージ
- 感情の豊かさを大切にする視点
- 読者との共感を生む表現
- 希望と癒しを感じられる内容

この後、このメッセージに合う画像を生成します。"""
        
        step3_text = interpreter.generate_interpretation(step3_prompt, planets, "emotion_step3")
        print("【STEP3 テキスト出力】")
        print(step3_text)
        print(f"文字数: {len(step3_text)}")
        print()
        
        # 画像生成プロンプト
        image_prompt = f"""テキスト内容: {step3_text}

このメッセージに合う16:9の画像を生成してください。

画像の特徴:
- 温かみのある色調（パステルカラー中心）
- 自然や空、花などの癒し要素
- 穏やかで希望的な雰囲気
- 感情の豊かさを表現する抽象的要素
- 朝の光や優しい雲など

顔参照: images/emotion_link/face_reference/ の画像を使用"""
        
        print("【STEP3 画像生成プロンプト】")
        print(image_prompt)
        print()
        
        print("=" * 60)
        print("STEP1-3 出力確認完了")
        print("=" * 60)
        
        return {
            'step1': step1_result,
            'step2': step2_result, 
            'step3': step3_text,
            'image_prompt': image_prompt
        }
        
    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    test_emotion_link_steps()