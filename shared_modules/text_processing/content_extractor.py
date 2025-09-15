#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
STEP1コンテンツ処理ユーティリティ
占星術記述を除去し、感情的内容のみを抽出
"""

import re
from typing import Optional

def extract_emotional_content(step1_text: str) -> str:
    """
    STEP1のテキストから「今日は」で始まる最初の文を削除し、
    感情的・心理的な内容のみを抽出する
    
    必須処理:
    - 「今日は」で始まる最初の文を確実に削除
    - トランジット表現（占星術記述）を含む先頭文の完全除去
    - 「。」で終わる部分までを確実に削除
    
    Args:
        step1_text: STEP1で生成されたテキスト
        
    Returns:
        感情的内容のみのテキスト
    """
    if not step1_text or not isinstance(step1_text, str):
        return ""
    
    # 入力テキストを正規化
    text = step1_text.strip()
    if not text:
        return ""
    
    # より厳密なパターンマッチング: 「今日は」で始まる占星術記述を確実に除去
    # 「今日は」で始まり、占星術的内容を含む部分全体を削除
    
    # まず「今日は」で始まるかチェック
    if text.startswith('今日は'):
        # 文を句点で分割
        sentences = text.split('。')
        
        # 最初の文（占星術記述）を削除
        if len(sentences) > 1:
            # 最初の文を削除し、残りを結合
            remaining_sentences = sentences[1:]
            # 空の文を除去
            remaining_sentences = [s.strip() for s in remaining_sentences if s.strip()]
            
            if remaining_sentences:
                # 最後の要素が空でない場合は「。」を付加
                if remaining_sentences[-1] and not remaining_sentences[-1].endswith('。'):
                    remaining_sentences[-1] += '。'
                cleaned_text = '。'.join(remaining_sentences)
            else:
                cleaned_text = ""
        else:
            # 句点がない場合（「今日は。」のような場合）
            cleaned_text = ""
    else:
        # 「今日は」で始まらない場合はそのまま返す
        cleaned_text = text
    
    # 結果が空の場合の処理
    if not cleaned_text:
        return ""
    
    # 追加のクリーニング: 連続する空白や改行を正規化
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
    cleaned_text = cleaned_text.strip()
    
    return cleaned_text

def test_extraction():
    """
    テスト用関数
    """
    test_cases = [
        "今日は、月が魚座さんを優しく照らしているみたい。なんだか心がじんわり温かくなるような、そんな日だよね。感受性が豊かになるから、人の気持ちに寄り添えたり、美しいものに感動したり。自分の内側の声にも耳を澄ませてみてね。",
        "今日は新しいエネルギーが流れてくる日。希望に満ちた一歩を踏み出してみて。前向きな気持ちで過ごそう。",
        "静かな夜に自分と向き合う時間を作ってみて。内なる声が聞こえてくるはず。"
    ]
    
    for i, test_text in enumerate(test_cases, 1):
        result = extract_emotional_content(test_text)
        print(f"テスト{i}:")
        print(f"入力: {test_text}")
        print(f"出力: {result}")
        print("-" * 50)

if __name__ == "__main__":
    test_extraction()
