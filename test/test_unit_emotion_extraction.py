#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
感情抽出機能の単体テスト

extract_emotional_content機能の詳細な単体テストを実行します。
様々なパターンの占星術記述に対する処理を検証し、
感情的内容のみが正確に抽出されることを確認します。
"""

import sys
import unittest
from pathlib import Path

# プロジェクトのルートディレクトリをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from shared_modules.text_processing.content_extractor import extract_emotional_content


class TestEmotionalContentExtraction(unittest.TestCase):
    """感情的内容抽出機能の単体テスト"""
    
    def test_basic_astrology_removal(self):
        """基本的な占星術記述の除去テスト"""
        test_cases = [
            {
                "input": "今日は、月が魚座さんを優しく照らしているみたい。なんだか心がじんわり温かくなるような、そんな日だよね。",
                "expected": "なんだか心がじんわり温かくなるような、そんな日だよね。",
                "description": "月と星座の記述除去"
            },
            {
                "input": "今日は、太陽が牡羊座に入ります。新しいスタートを切るのにぴったりな日。",
                "expected": "新しいスタートを切るのにぴったりな日。",
                "description": "太陽のサイン移動記述の除去"
            },
            {
                "input": "今日は水星逆行が終わります。コミュニケーションがスムーズになりそう。",
                "expected": "コミュニケーションがスムーズになりそう。",
                "description": "水星逆行記述の除去"
            }
        ]
        
        for case in test_cases:
            with self.subTest(case=case["description"]):
                result = extract_emotional_content(case["input"])
                self.assertEqual(result.strip(), case["expected"])
    
    def test_complex_astrology_patterns(self):
        """複雑な占星術パターンのテスト"""
        test_cases = [
            {
                "input": "今日は、金星と火星がトラインを形成して、恋愛運がアップしそう。素敵な出会いがあるかもしれません。",
                "expected": "素敵な出会いがあるかもしれません。",
                "description": "アスペクト記述の除去"
            },
            {
                "input": "今日は満月のエネルギーが強くて、感情が高まりやすい日。でも、それは悪いことじゃないよ。",
                "expected": "でも、それは悪いことじゃないよ。",
                "description": "満月エネルギー記述の除去"
            },
            {
                "input": "今日は、木星が幸運をもたらしてくれる配置。積極的に行動してみて。",
                "expected": "積極的に行動してみて。",
                "description": "惑星の幸運配置記述の除去"
            }
        ]
        
        for case in test_cases:
            with self.subTest(case=case["description"]):
                result = extract_emotional_content(case["input"])
                self.assertEqual(result.strip(), case["expected"])
    
    def test_multiple_sentences(self):
        """複数文からなるテキストのテスト"""
        test_cases = [
            {
                "input": "今日は、心と心がふれあう温かい日。誰かの優しさに触れたり、ふと懐かしい気持ちがこみ上げたりするかもしれません。",
                "expected": "誰かの優しさに触れたり、ふと懐かしい気持ちがこみ上げたりするかもしれません。",
                "description": "温かい心の交流記述"
            },
            {
                "input": "今日は、感受性が豊かになる日だよね。人の気持ちがいつも以上に分かって、共感力が爆上がりしそう。",
                "expected": "人の気持ちがいつも以上に分かって、共感力が爆上がりしそう。",
                "description": "感受性と共感力の記述"
            }
        ]
        
        for case in test_cases:
            with self.subTest(case=case["description"]):
                result = extract_emotional_content(case["input"])
                self.assertEqual(result.strip(), case["expected"])
    
    def test_edge_cases(self):
        """エッジケースのテスト"""
        test_cases = [
            {
                "input": "",
                "expected": "",
                "description": "空文字列"
            },
            {
                "input": "今日は。",
                "expected": "",
                "description": "最小限の今日は文"
            },
            {
                "input": "感情的な内容のみで占星術記述なし。",
                "expected": "感情的な内容のみで占星術記述なし。",
                "description": "今日はで始まらないテキスト"
            },
            {
                "input": "今日は良い日。明日も今日はきっと良い日になる。",
                "expected": "明日も今日はきっと良い日になる。",
                "description": "複数の今日はが含まれる場合"
            }
        ]
        
        for case in test_cases:
            with self.subTest(case=case["description"]):
                result = extract_emotional_content(case["input"])
                self.assertEqual(result.strip(), case["expected"])
    
    def test_no_astrology_content(self):
        """占星術記述がない場合のテスト"""
        test_cases = [
            {
                "input": "心が温かくなるような優しい気持ちの日。人との繋がりを大切にして。",
                "expected": "心が温かくなるような優しい気持ちの日。人との繋がりを大切にして。",
                "description": "純粋な感情記述のみ"
            },
            {
                "input": "静かに自分と向き合う時間を持って。内なる声に耳を傾けてみて。",
                "expected": "静かに自分と向き合う時間を持って。内なる声に耳を傾けてみて。",
                "description": "内省的な感情記述"
            }
        ]
        
        for case in test_cases:
            with self.subTest(case=case["description"]):
                result = extract_emotional_content(case["input"])
                self.assertEqual(result.strip(), case["expected"])
    
    def test_character_count_reduction(self):
        """文字数削減の確認テスト"""
        test_cases = [
            {
                "input": "今日は、月が魚座さんを優しく照らしているみたい。なんだか心がじんわり温かくなるような、そんな日だよね。",
                "min_reduction": 10,  # 最低10文字は削減されるはず
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
    
    def test_real_world_examples(self):
        """実際の使用例に基づくテスト"""
        test_cases = [
            {
                "input": "今日は、月が魚座さんへ。感受性が豊かになる日だよね。人の気持ちがいつも以上に分かって、共感力が爆上がりしそう。",
                "expected": "感受性が豊かになる日だよね。人の気持ちがいつも以上に分かって、共感力が爆上がりしそう。",
                "description": "実際のプロダクション例1"
            },
            {
                "input": "今日は、心と心がふれあう温かい日。誰かの優しさに触れたり、ふと懐かしい気持ちがこみ上げたりするかもしれません。",
                "expected": "誰かの優しさに触れたり、ふと懐かしい気持ちがこみ上げたりするかもしれません。",
                "description": "実際のプロダクション例2"
            }
        ]
        
        for case in test_cases:
            with self.subTest(case=case["description"]):
                result = extract_emotional_content(case["input"])
                self.assertEqual(result.strip(), case["expected"])


def run_unit_tests():
    """単体テストの実行"""
    print("=" * 70)
    print("🧪 感情抽出機能の単体テスト開始")
    print("=" * 70)
    
    # テストスイートの作成
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestEmotionalContentExtraction)
    
    # テスト実行
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # 結果サマリー
    print("\n" + "=" * 70)
    print("📊 単体テスト結果サマリー")
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
        print("🎉 全テスト成功！感情抽出機能は完璧に動作しています！")
    elif success_rate >= 90:
        print("✅ 優秀！感情抽出機能は正常に動作しています")
    elif success_rate >= 70:
        print("⚠️ 一部問題がありますが、基本機能は動作しています")
    else:
        print("❌ 重要な問題があります。修正が必要です")
    
    print("=" * 70)
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_unit_tests()
    sys.exit(0 if success else 1)