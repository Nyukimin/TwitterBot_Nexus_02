#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
改善されたextract_emotional_content関数の堅牢性テスト

「今日は」で始まり「。」で終わる最初の文を確実に削除する
処理の堅牢性を詳細にテストします。
"""

import sys
import unittest
from pathlib import Path

# プロジェクトのルートディレクトリをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from shared_modules.text_processing.content_extractor import extract_emotional_content


class TestImprovedExtractionRobustness(unittest.TestCase):
    """改善されたextract_emotional_content関数の堅牢性テスト"""
    
    def test_standard_patterns(self):
        """標準的なパターンのテスト"""
        test_cases = [
            {
                "input": "今日は、月が魚座に入って、なんだか心がじんわり温かくなるような日だよね。感受性が豊かになって、人の気持ちがすごくよく分かるから、優しい気持ちで過ごせそう。",
                "expected": "感受性が豊かになって、人の気持ちがすごくよく分かるから、優しい気持ちで過ごせそう。",
                "description": "標準的な占星術記述の除去"
            },
            {
                "input": "今日は水星逆行が終わります。コミュニケーションがスムーズになりそう。大切な人との会話を楽しんでね。",
                "expected": "コミュニケーションがスムーズになりそう。大切な人との会話を楽しんでね。",
                "description": "水星逆行記述の除去"
            },
            {
                "input": "今日は満月のエネルギーが強い日。感情が高まりやすいけれど、それは悪いことじゃないよ。",
                "expected": "感情が高まりやすいけれど、それは悪いことじゃないよ。",
                "description": "満月エネルギー記述の除去"
            }
        ]
        
        for case in test_cases:
            with self.subTest(case=case["description"]):
                result = extract_emotional_content(case["input"])
                self.assertEqual(result.strip(), case["expected"])
    
    def test_complex_patterns(self):
        """複雑なパターンのテスト"""
        test_cases = [
            {
                "input": "今日は、金星と火星がトライン、そして月が蟹座で安定している配置。愛情運がアップしそうな一日だよ。素敵な出会いや再会があるかもしれません。",
                "expected": "愛情運がアップしそうな一日だよ。素敵な出会いや再会があるかもしれません。",
                "description": "複雑な占星術配置記述の除去"
            },
            {
                "input": "今日は土星の影響で、責任感が強まる日になりそう。でも焦らずに、一歩ずつ進んでいけば大丈夫。自分のペースを大切にして。",
                "expected": "でも焦らずに、一歩ずつ進んでいけば大丈夫。自分のペースを大切にして。",
                "description": "土星影響記述の除去"
            }
        ]
        
        for case in test_cases:
            with self.subTest(case=case["description"]):
                result = extract_emotional_content(case["input"])
                self.assertEqual(result.strip(), case["expected"])
    
    def test_edge_cases_robustness(self):
        """エッジケースの堅牢性テスト"""
        test_cases = [
            {
                "input": "今日は。",
                "expected": "",
                "description": "最小限の今日は文"
            },
            {
                "input": "今日は良い日だと思う。でも今日はもう一度考えてみよう。",
                "expected": "でも今日はもう一度考えてみよう。",
                "description": "複数の今日はが含まれる場合（最初のみ削除）"
            },
            {
                "input": "今日は、長い長い占星術の説明が続く日で、惑星の配置がとても複雑になっている。しかし心配することはなく、穏やかに過ごせば良いのです。",
                "expected": "しかし心配することはなく、穏やかに過ごせば良いのです。",
                "description": "長い占星術記述の除去"
            },
            {
                "input": "感情的な内容のみで今日はという単語が含まれない。",
                "expected": "感情的な内容のみで今日はという単語が含まれない。",
                "description": "今日はで始まらないテキスト"
            }
        ]
        
        for case in test_cases:
            with self.subTest(case=case["description"]):
                result = extract_emotional_content(case["input"])
                self.assertEqual(result.strip(), case["expected"])
    
    def test_whitespace_handling(self):
        """空白文字の処理テスト"""
        test_cases = [
            {
                "input": "  今日は、月が移動する日。  心が軽やかになるよ。  ",
                "expected": "心が軽やかになるよ。",
                "description": "前後の空白処理"
            },
            {
                "input": "今日は、\n複数行にわたる\n占星術記述。\n心を大切にしてね。",
                "expected": "心を大切にしてね。",
                "description": "改行を含む記述の処理"
            }
        ]
        
        for case in test_cases:
            with self.subTest(case=case["description"]):
                result = extract_emotional_content(case["input"])
                self.assertEqual(result.strip(), case["expected"])
    
    def test_real_world_examples(self):
        """実際の生成例に基づくテスト"""
        test_cases = [
            {
                "input": "今日は、月が魚座に入って、なんだか心がじんわり温かくなるような日だよね。感受性が豊かになって、人の気持ちがすごくよく分かるから、優しい気持ちで過ごせそう。相手の気持ちを想像して、寄り添ってみると、素敵な関係が築けるかも。",
                "expected": "感受性が豊かになって、人の気持ちがすごくよく分かるから、優しい気持ちで過ごせそう。相手の気持ちを想像して、寄り添ってみると、素敵な関係が築けるかも。",
                "description": "実際の生成例1"
            },
            {
                "input": "今日は、心と心がふれあう温かい日。誰かの優しさに触れたり、ふと懐かしい気持ちがこみ上げたりするかもしれません。過去の経験が、今のあなたを支える力になるでしょう。",
                "expected": "誰かの優しさに触れたり、ふと懐かしい気持ちがこみ上げたりするかもしれません。過去の経験が、今のあなたを支える力になるでしょう。",
                "description": "実際の生成例2"
            }
        ]
        
        for case in test_cases:
            with self.subTest(case=case["description"]):
                result = extract_emotional_content(case["input"])
                self.assertEqual(result.strip(), case["expected"])
    
    def test_error_handling(self):
        """エラーハンドリングのテスト"""
        test_cases = [
            {"input": None, "expected": "", "description": "None入力"},
            {"input": "", "expected": "", "description": "空文字列"},
            {"input": "   ", "expected": "", "description": "空白のみ"},
            {"input": 123, "expected": "", "description": "数値入力"},
        ]
        
        for case in test_cases:
            with self.subTest(case=case["description"]):
                result = extract_emotional_content(case["input"])
                self.assertEqual(result, case["expected"])
    
    def test_character_count_validation(self):
        """文字数削減の検証テスト"""
        test_cases = [
            {
                "input": "今日は、月が魚座さんを優しく照らしているみたい。なんだか心がじんわり温かくなるような、そんな日だよね。",
                "min_reduction": 20,  # 最低20文字は削減されるはず
                "description": "文字数削減の確認"
            }
        ]
        
        for case in test_cases:
            with self.subTest(case=case["description"]):
                original_length = len(case["input"])
                result = extract_emotional_content(case["input"])
                result_length = len(result)
                reduction = original_length - result_length
                self.assertGreaterEqual(reduction, case["min_reduction"])


def run_robustness_tests():
    """堅牢性テストの実行"""
    print("=" * 70)
    print("🔧 改善されたextract_emotional_content関数の堅牢性テスト")
    print("=" * 70)
    
    # テストスイートの作成
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestImprovedExtractionRobustness)
    
    # テスト実行
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # 結果サマリー
    print("\n" + "=" * 70)
    print("📊 堅牢性テスト結果サマリー")
    print("=" * 70)
    print(f"✅ 実行テスト数: {result.testsRun}")
    print(f"❌ 失敗: {len(result.failures)}")
    print(f"⚠️ エラー: {len(result.errors)}")
    
    if result.failures:
        print("\n❌ 失敗したテスト:")
        for test, traceback in result.failures:
            lines = traceback.split('\n')
            error_msg = lines[-2] if len(lines) > 1 else traceback
            print(f"  - {test}: {error_msg}")
    
    if result.errors:
        print("\n⚠️ エラーが発生したテスト:")
        for test, traceback in result.errors:
            lines = traceback.split('\n')
            error_msg = lines[-2] if len(lines) > 1 else traceback
            print(f"  - {test}: {error_msg}")
    
    success_rate = (result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100
    print(f"\n🎯 成功率: {success_rate:.1f}%")
    
    if success_rate == 100:
        print("🎉 完璧！改善されたextract_emotional_content関数は確実に動作しています！")
        print("✅ 「今日は」で始まり「。」で終わる文の削除処理が堅牢に実装されました")
    elif success_rate >= 90:
        print("✅ 優秀！堅牢性が大幅に改善されています")
    else:
        print("⚠️ まだ改善の余地があります")
    
    print("=" * 70)
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_robustness_tests()
    sys.exit(0 if success else 1)