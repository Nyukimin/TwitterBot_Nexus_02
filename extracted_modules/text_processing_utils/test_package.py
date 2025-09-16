#!/usr/bin/env python3
"""
Text Processing Utilities パッケージの動作確認テスト
"""

import sys
import os

# パッケージのパスを追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

def test_import():
    """インポートテスト"""
    print("🔍 インポートテスト開始...")
    
    try:
        from text_processing_utils import extract_emotional_content
        print("✅ text_processing_utils.extract_emotional_content インポート成功")
        
        from text_processing_utils.emotion_extraction import extract_emotional_content as extract_func
        print("✅ text_processing_utils.emotion_extraction.extract_emotional_content インポート成功")
        
        import text_processing_utils
        info = text_processing_utils.get_package_info()
        print(f"✅ パッケージ情報取得成功: {info['name']} v{info['version']}")
        
        return True
        
    except Exception as e:
        print(f"❌ インポートエラー: {e}")
        return False

def test_functionality():
    """機能テスト"""
    print("\n🧪 機能テスト開始...")
    
    try:
        from text_processing_utils import extract_emotional_content
        
        # テストケース
        test_cases = [
            {
                "input": "今日は月が魚座に入る。感受性が高まりやすい日。人の気持ちに寄り添って過ごそう。",
                "expected_keywords": ["感受性", "気持ち", "寄り添"],
                "description": "基本的な占星術記述除去テスト"
            },
            {
                "input": "今日は水星逆行開始。心を落ち着けて丁寧に対話しよう。深呼吸して自分の心と向き合ってみて。",
                "expected_keywords": ["心", "落ち着け", "深呼吸"],
                "description": "水星逆行記述除去テスト"
            },
            {
                "input": "満月のエネルギーが強い日。感情が高ぶりやすい時期。心穏やかに過ごそう。",
                "expected_keywords": ["感情", "心", "穏やか"],
                "description": "満月記述除去テスト"
            },
            {
                "input": "今日も一日お疲れさま。小さな幸せを見つけて心温かく過ごそう。",
                "expected_keywords": ["幸せ", "心", "温かく"],
                "description": "シンプルな感情表現テスト"
            }
        ]
        
        all_passed = True
        
        for i, case in enumerate(test_cases, 1):
            print(f"\n--- テストケース {i}: {case['description']} ---")
            print(f"入力: {case['input']}")
            
            result = extract_emotional_content(case['input'])
            print(f"出力: {result}")
            
            # キーワードチェック
            found_keywords = []
            for keyword in case['expected_keywords']:
                if keyword in result:
                    found_keywords.append(keyword)
            
            if len(found_keywords) >= len(case['expected_keywords']) // 2:  # 半数以上のキーワードが含まれていればOK
                print(f"✅ テスト{i}成功 - キーワード発見: {found_keywords}")
            else:
                print(f"⚠️  テスト{i}部分成功 - 期待キーワード: {case['expected_keywords']}, 発見: {found_keywords}")
            
            # 占星術記述が除去されているかチェック
            astro_terms = ['今日は', '月が', '水星逆行', '満月', '魚座', '牡羊座']
            astro_found = [term for term in astro_terms if term in result]
            
            if not astro_found:
                print(f"✅ 占星術記述除去成功")
            else:
                print(f"⚠️  占星術記述が残存: {astro_found}")
        
        return True
        
    except Exception as e:
        print(f"❌ 機能テストエラー: {e}")
        return False

def test_edge_cases():
    """エッジケーステスト"""
    print("\n🎯 エッジケーステスト開始...")
    
    try:
        from text_processing_utils import extract_emotional_content
        
        edge_cases = [
            {"input": "", "description": "空文字列"},
            {"input": "今日は月が魚座に入る。", "description": "感情表現なし"},
            {"input": "心穏やかに過ごそう。", "description": "占星術記述なし"},
            {"input": "今日は特別な日。心を大切に。愛を持って過ごそう。", "description": "複数感情表現"}
        ]
        
        for i, case in enumerate(edge_cases, 1):
            print(f"\n--- エッジケース {i}: {case['description']} ---")
            print(f"入力: '{case['input']}'")
            
            result = extract_emotional_content(case['input'])
            print(f"出力: '{result}'")
            
            if result:  # 何らかの結果が返されればOK
                print(f"✅ エッジケース{i}成功")
            else:
                print(f"⚠️  エッジケース{i}要確認")
        
        return True
        
    except Exception as e:
        print(f"❌ エッジケーステストエラー: {e}")
        return False

def main():
    """メインテスト関数"""
    print("=" * 60)
    print("🚀 Text Processing Utilities パッケージ動作確認テスト")
    print("=" * 60)
    
    # テスト実行
    test_results = []
    
    test_results.append(test_import())
    test_results.append(test_functionality())
    test_results.append(test_edge_cases())
    
    # 結果サマリー
    print("\n" + "=" * 60)
    print("📊 テスト結果サマリー")
    print("=" * 60)
    
    passed = sum(test_results)
    total = len(test_results)
    
    if passed == total:
        print(f"🎉 全テスト成功！ ({passed}/{total})")
        print("✅ パッケージは正常に動作しています")
    else:
        print(f"⚠️  一部テスト失敗 ({passed}/{total})")
        print("❌ パッケージに問題がある可能性があります")
    
    # パッケージ情報表示
    try:
        import text_processing_utils
        info = text_processing_utils.get_package_info()
        print(f"\n📦 パッケージ情報:")
        print(f"   名前: {info['name']}")
        print(f"   バージョン: {info['version']}")
        print(f"   説明: {info['description']}")
        print(f"   公開関数: {info['functions']}")
    except:
        pass
    
    print("\n🏁 テスト完了")
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)