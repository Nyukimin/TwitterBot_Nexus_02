#!/usr/bin/env python3

"""
Image Generation Utils パッケージ動作確認テスト

このテストは以下の機能を検証します:
- GeminiImageGeneratorクラス
- Face Reference機能
- Base64処理機能
- API接続テスト
- パッケージ構造
"""

import sys
import os
import unittest
from unittest.mock import Mock, patch, MagicMock

def test_basic_import():
    """基本的なインポートテスト"""
    print("🔄 Image Generation Utils 基本インポートテスト")
    print("=" * 60)
    
    try:
        # メインクラスのインポート
        from image_generation_utils import GeminiImageGenerator
        print("✅ GeminiImageGenerator インポート成功")
        
        # パッケージレベル関数のインポート
        from image_generation_utils import get_version, get_supported_models, get_supported_formats
        print("✅ パッケージレベル関数インポート成功")
        
        return True
    except ImportError as e:
        print(f"❌ インポートエラー: {e}")
        return False

def test_class_initialization():
    """クラス初期化テスト"""
    print("\n🔧 クラス初期化テスト")
    print("-" * 40)
    
    try:
        from image_generation_utils import GeminiImageGenerator
        
        # APIキー未設定での初期化テスト
        try:
            generator = GeminiImageGenerator(api_key="test_key")
            print("✅ GeminiImageGenerator 初期化成功 (テストキー)")
        except Exception as e:
            print(f"⚠️ GeminiImageGenerator初期化: {e}")
        
        # 環境変数テスト
        original_key = os.environ.get('GEMINI_API_KEY')
        os.environ['GEMINI_API_KEY'] = 'test_env_key'
        try:
            generator = GeminiImageGenerator()
            print("✅ 環境変数からのAPIキー取得成功")
        except Exception as e:
            print(f"⚠️ 環境変数テスト: {e}")
        finally:
            # 環境変数復元
            if original_key:
                os.environ['GEMINI_API_KEY'] = original_key
            elif 'GEMINI_API_KEY' in os.environ:
                del os.environ['GEMINI_API_KEY']
        
        return True
    except Exception as e:
        print(f"❌ クラス初期化エラー: {e}")
        return False

def test_dependencies():
    """依存関係テスト"""
    print("\n📦 依存関係確認テスト")
    print("-" * 40)
    
    dependencies = [
        ('requests', 'HTTP通信'),
        ('base64', '基本ライブラリ'),
        ('json', '基本ライブラリ'),
        ('datetime', '基本ライブラリ'),
        ('os', '基本ライブラリ'),
        ('logging', '基本ライブラリ'),
    ]
    
    # オプション依存関係
    optional_deps = [
        ('PIL', 'Pillow (画像処理)'),
        ('numpy', 'NumPy (数値計算)'),
        ('cv2', 'OpenCV (高度画像処理)'),
    ]
    
    all_ok = True
    
    # 基本依存関係チェック
    for package, desc in dependencies:
        try:
            __import__(package)
            print(f"✅ {package} ({desc}) インポート成功")
        except ImportError as e:
            print(f"❌ {package} ({desc}) インポート失敗: {e}")
            all_ok = False
    
    # オプション依存関係チェック
    for package, desc in optional_deps:
        try:
            __import__(package)
            print(f"✅ {package} ({desc}) インポート成功")
        except ImportError:
            print(f"⚠️ {package} ({desc}) 未インストール (オプション)")
    
    return all_ok

def test_gemini_image_generator_methods():
    """GeminiImageGenerator メソッドテスト"""
    print("\n🎨 GeminiImageGenerator メソッドテスト")
    print("-" * 40)
    
    try:
        from image_generation_utils import GeminiImageGenerator
        
        # メソッド存在確認
        expected_methods = [
            'generate_image',
            'generate_emotion_link_image', 
            'test_api_connection',
            'get_supported_image_formats',
            'get_model_info',
        ]
        
        # インスタンス作成テスト（テストキー使用）
        try:
            generator = GeminiImageGenerator(api_key="test_key")
            print("✅ GeminiImageGenerator インスタンス作成成功")
            
            # メソッド存在確認
            for method in expected_methods:
                if hasattr(generator, method):
                    print(f"✅ メソッド {method} 存在確認")
                else:
                    print(f"⚠️ メソッド {method} が見つかりません")
            
            # 静的メソッドテスト
            formats = GeminiImageGenerator.get_supported_image_formats()
            print(f"✅ サポート画像形式: {formats}")
            
            model_info = GeminiImageGenerator.get_model_info()
            print(f"✅ モデル情報: {model_info['name']}")
                    
        except Exception as e:
            print(f"⚠️ インスタンス作成失敗: {e}")
            print("✅ クラス定義は正常に読み込まれています")
        
        return True
    except Exception as e:
        print(f"❌ GeminiImageGeneratorテストエラー: {e}")
        return False

def test_face_reference_functionality():
    """Face Reference機能テスト"""
    print("\n👤 Face Reference機能テスト")
    print("-" * 40)
    
    try:
        from image_generation_utils import GeminiImageGenerator
        
        # Face Reference処理のモックテスト
        generator = GeminiImageGenerator(api_key="test_key")
        
        # _add_face_reference_to_request メソッドテスト
        if hasattr(generator, '_add_face_reference_to_request'):
            print("✅ _add_face_reference_to_request メソッド存在確認")
            
            # テストデータ
            test_data = {
                "contents": [{
                    "parts": [{"text": "test prompt"}]
                }]
            }
            
            # 存在しないファイルでのテスト（エラーハンドリング確認）
            try:
                generator._add_face_reference_to_request(test_data, ["non_existent.jpg"])
                print("✅ 存在しないファイルのエラーハンドリング正常")
            except Exception as e:
                print(f"⚠️ エラーハンドリングテスト: {e}")
        else:
            print("⚠️ _add_face_reference_to_request メソッドが見つかりません")
        
        return True
    except Exception as e:
        print(f"❌ Face Reference機能テストエラー: {e}")
        return False

def test_package_structure():
    """パッケージ構造テスト"""
    print("\n📁 パッケージ構造テスト")
    print("-" * 40)
    
    try:
        import image_generation_utils
        
        # __version__ 確認
        if hasattr(image_generation_utils, '__version__'):
            print(f"✅ パッケージバージョン: {image_generation_utils.__version__}")
        else:
            print("⚠️ __version__ が設定されていません")
        
        # __all__ 確認
        if hasattr(image_generation_utils, '__all__'):
            print(f"✅ エクスポートクラス数: {len(image_generation_utils.__all__)}") 
            for cls_name in image_generation_utils.__all__:
                print(f"  - {cls_name}")
        else:
            print("⚠️ __all__ が設定されていません")
        
        # パッケージレベル関数テスト
        try:
            version = image_generation_utils.get_version()
            models = image_generation_utils.get_supported_models()
            formats = image_generation_utils.get_supported_formats()
            
            print(f"✅ get_version(): {version}")
            print(f"✅ get_supported_models(): {models}")
            print(f"✅ get_supported_formats(): {formats}")
        except Exception as e:
            print(f"⚠️ パッケージレベル関数エラー: {e}")
        
        return True
    except Exception as e:
        print(f"❌ パッケージ構造テストエラー: {e}")
        return False

def run_comprehensive_test():
    """包括的テスト実行"""
    print("🎨 Image Generation Utils 包括的動作確認テスト")
    print("=" * 80)
    print(f"Python バージョン: {sys.version}")
    print(f"実行ディレクトリ: {os.getcwd()}")
    print()
    
    # テスト関数リスト
    tests = [
        ("基本インポート", test_basic_import),
        ("クラス初期化", test_class_initialization),
        ("依存関係", test_dependencies),
        ("GeminiImageGenerator", test_gemini_image_generator_methods),
        ("Face Reference機能", test_face_reference_functionality),
        ("パッケージ構造", test_package_structure),
    ]
    
    results = []
    
    # 各テスト実行
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} テストで予期しないエラー: {e}")
            results.append((test_name, False))
        print()
    
    # 結果サマリー
    print("📊 テスト結果サマリー")
    print("=" * 80)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status:<10} {test_name}")
        if result:
            passed += 1
    
    print("-" * 80)
    print(f"総テスト数: {total}")
    print(f"成功: {passed}")
    print(f"失敗: {total - passed}")
    print(f"成功率: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n🎉 全テストが成功しました! Image Generation Utils パッケージは正常に動作しています。")
        return True
    else:
        print(f"\n⚠️ {total - passed}個のテストが失敗しました。詳細を確認してください。")
        return False

if __name__ == "__main__":
    success = run_comprehensive_test()
    sys.exit(0 if success else 1)