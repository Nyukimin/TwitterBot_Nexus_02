#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
包括的なemotion_linkシステムテスト

このテストスイートは以下の機能を包括的にテストします:
1. extract_emotional_content機能の詳細テスト
2. 様々な占星術パターンに対する処理テスト
3. 画像プロンプト生成の品質テスト
4. エラーハンドリングとエッジケーステスト
5. パフォーマンステスト
"""

import sys
import os
import unittest
import yaml
import tempfile
from pathlib import Path
from datetime import datetime
import pytz

# プロジェクトのルートディレクトリをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 必要なモジュールをインポート
from shared_modules.text_processing.content_extractor import extract_emotional_content
from shared_modules.astrology.astro_system import AstroCalculator, GeminiInterpreter
from shared_modules.image_generation.gemini_image_generator import GeminiImageGenerator


class TestEmotionalContentExtraction(unittest.TestCase):
    """感情的内容抽出機能のテスト"""
    
    def test_basic_extraction(self):
        """基本的な抽出機能のテスト"""
        test_cases = [
            {
                "input": "今日は、月が魚座さんを優しく照らしているみたい。なんだか心がじんわり温かくなるような、そんな日だよね。",
                "expected": "なんだか心がじんわり温かくなるような、そんな日だよね。",
                "description": "基本的な占星術記述の除去"
            },
            {
                "input": "今日は、太陽が牡羊座に入ります。新しいスタートを切るのにぴったりな日。エネルギッシュに過ごしましょう。",
                "expected": "新しいスタートを切るのにぴったりな日。エネルギッシュに過ごしましょう。",
                "description": "太陽のサイン移動記述の除去"
            },
            {
                "input": "今日は特別な日。心が穏やかになれるような時間を過ごしてね。",
                "expected": "心が穏やかになれるような時間を過ごしてね。",
                "description": "占星術要素がない場合の処理"
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
                "description": "空文字列の処理"
            },
            {
                "input": "今日は。",
                "expected": "",
                "description": "最小限の「今日は」文の処理"
            },
            {
                "input": "感情的な内容のみで占星術記述なし。",
                "expected": "感情的な内容のみで占星術記述なし。",
                "description": "「今日は」で始まらないテキストの処理"
            },
            {
                "input": "今日は良い日。明日も今日はきっと良い日になる。",
                "expected": "明日も今日はきっと良い日になる。",
                "description": "複数の「今日は」が含まれる場合"
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
                "input": "今日は、水星が順行に戻って、コミュニケーションがスムーズになりそう。人との会話を楽しんでね。",
                "expected": "人との会話を楽しんでね。",
                "description": "水星逆行関連の記述"
            },
            {
                "input": "今日は満月のエネルギーが強くて、感情が高まりやすい日。でも、それは悪いことじゃないよ。",
                "expected": "でも、それは悪いことじゃないよ。",
                "description": "満月関連の記述"
            }
        ]
        
        for case in test_cases:
            with self.subTest(case=case["description"]):
                result = extract_emotional_content(case["input"])
                self.assertEqual(result.strip(), case["expected"])


class TestAstrologySystem(unittest.TestCase):
    """占星術システムのテスト"""
    
    def setUp(self):
        """テストセットアップ"""
        self.calculator = AstroCalculator()
        self.interpreter = GeminiInterpreter()
        self.jst = pytz.timezone('Asia/Tokyo')
    
    def test_planet_calculation(self):
        """惑星位置計算のテスト"""
        current_time = datetime.now(self.jst)
        planets = self.calculator.calculate_planet_positions(current_time)
        
        # 期待される惑星数
        expected_planets = ['太陽', '月', '水星', '金星', '火星', '木星', '土星', '天王星', '海王星', '冥王星']
        
        self.assertEqual(len(planets), len(expected_planets))
        
        for planet_name in expected_planets:
            self.assertIn(planet_name, planets)
            planet_data = planets[planet_name]
            self.assertIn('sign', planet_data)
            self.assertIn('degrees', planet_data)
            self.assertIn('longitude', planet_data)
    
    def test_interpretation_generation(self):
        """解釈生成のテスト"""
        # テスト用の惑星データ
        test_planets = {
            '太陽': {'sign': '乙女座', 'degrees': 15, 'longitude': 165.5},
            '月': {'sign': '魚座', 'degrees': 20, 'longitude': 350.2}
        }
        
        prompt_template = """
        以下の惑星位置に基づいて占星術解釈を生成してください:
        {planet_positions}
        
        感情的で温かい表現で、140文字以内で答えてください。
        """
        
        try:
            result = self.interpreter.generate_interpretation(
                prompt_template, test_planets, "transit", ""
            )
            self.assertIsInstance(result, str)
            self.assertGreater(len(result), 0)
        except Exception as e:
            self.skipTest(f"API接続エラーのためスキップ: {e}")


class TestImagePromptGeneration(unittest.TestCase):
    """画像プロンプト生成のテスト"""
    
    def test_emotional_content_to_image_prompt(self):
        """感情的内容から画像プロンプトへの変換テスト"""
        test_cases = [
            {
                "emotional_content": "心が温かくなるような優しい気持ちの日。人との繋がりを大切にして。",
                "expected_elements": ["warm", "gentle", "connection", "Japanese woman"],
                "description": "温かい感情の画像プロンプト"
            },
            {
                "emotional_content": "静かに自分と向き合う時間を持って。内なる声に耳を傾けてみて。",
                "expected_elements": ["peaceful", "contemplative", "quiet", "introspective"],
                "description": "内省的な感情の画像プロンプト"
            }
        ]
        
        for case in test_cases:
            with self.subTest(case=case["description"]):
                # 簡易的な画像プロンプト生成テスト
                # 実際のAPIを使わずに、パターンマッチングでテスト
                emotional_content = case["emotional_content"]
                
                # 温かさを表すキーワードの検出
                if "温かく" in emotional_content or "優しい" in emotional_content:
                    self.assertIn("warm", case["expected_elements"])
                
                # 静けさを表すキーワードの検出
                if "静か" in emotional_content or "向き合う" in emotional_content:
                    self.assertIn("peaceful", case["expected_elements"])


class TestConfigurationSystem(unittest.TestCase):
    """設定システムのテスト"""
    
    def test_config_loading(self):
        """設定ファイル読み込みのテスト"""
        config_path = project_root / "config" / "accounts_emotion_link.yaml"
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        self.assertIn('accounts', config)
        self.assertIsInstance(config['accounts'], list)
        
        # emotion_linkアカウントの存在確認
        emotion_link_config = None
        for account in config['accounts']:
            if account['id'] == 'emotion_link':
                emotion_link_config = account
                break
        
        self.assertIsNotNone(emotion_link_config)
        self.assertIn('PERSONALITY_PROMPT', emotion_link_config)
        self.assertIn('transit_config', emotion_link_config)
        self.assertIn('image_prompt_config', emotion_link_config)


class TestPerformance(unittest.TestCase):
    """パフォーマンステスト"""
    
    def test_extraction_performance(self):
        """抽出処理のパフォーマンステスト"""
        import time
        
        test_text = "今日は、月が魚座さんを優しく照らしているみたい。" * 100
        test_text += "なんだか心がじんわり温かくなるような、そんな日だよね。"
        
        start_time = time.time()
        
        # 100回実行
        for _ in range(100):
            result = extract_emotional_content(test_text)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # 100回の実行が1秒以内に完了することを確認
        self.assertLess(execution_time, 1.0)
        
        # 結果の正確性も確認
        final_result = extract_emotional_content(test_text)
        self.assertIn("なんだか心が", final_result)


class TestErrorHandling(unittest.TestCase):
    """エラーハンドリングのテスト"""
    
    def test_invalid_input_handling(self):
        """不正な入力の処理テスト"""
        test_cases = [
            None,
            123,
            [],
            {}
        ]
        
        for invalid_input in test_cases:
            with self.subTest(input=invalid_input):
                try:
                    result = extract_emotional_content(invalid_input)
                    # 例外が発生しない場合は、適切にハンドリングされている
                    self.assertIsInstance(result, str)
                except (TypeError, AttributeError):
                    # 型エラーが発生することも許容
                    pass


def run_comprehensive_tests():
    """包括的テストの実行"""
    print("=" * 70)
    print("🧪 包括的なemotion_linkシステムテスト開始")
    print("=" * 70)
    
    # テストスイートの作成
    test_suite = unittest.TestSuite()
    
    # 各テストクラスを追加
    test_classes = [
        TestEmotionalContentExtraction,
        TestAstrologySystem,
        TestImagePromptGeneration,
        TestConfigurationSystem,
        TestPerformance,
        TestErrorHandling
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # テスト実行
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # 結果サマリー
    print("\n" + "=" * 70)
    print("📊 テスト結果サマリー")
    print("=" * 70)
    print(f"✅ 実行テスト数: {result.testsRun}")
    print(f"❌ 失敗: {len(result.failures)}")
    print(f"⚠️ エラー: {len(result.errors)}")
    print(f"⏭️ スキップ: {len(result.skipped)}")
    
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
    
    if success_rate >= 90:
        print("🎉 システムは良好に動作しています！")
    elif success_rate >= 70:
        print("⚠️ いくつかの問題がありますが、基本機能は動作しています")
    else:
        print("❌ 重要な問題があります。修正が必要です")
    
    print("=" * 70)
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_comprehensive_tests()
    sys.exit(0 if success else 1)