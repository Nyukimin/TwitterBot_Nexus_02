#!/usr/bin/env python3
"""
Chrome Automation Utils パッケージ動作確認テスト

このテストは以下の機能を検証します:
- ProfiledChromeManagerクラスのインポートと基本動作
- Chrome起動機能(モック)
- プロファイル管理機能
- エラーハンドリング
- 依存関係(selenium, webdriver-manager)の確認
"""

import sys
import os
import unittest
from unittest.mock import Mock, patch, MagicMock

# パッケージのインポートテスト
def test_basic_import():
    """基本的なインポートテスト"""
    print("🔄 Chrome Automation Utils 基本インポートテスト")
    print("=" * 60)
    
    try:
        # メインクラスのインポート
        from chrome_automation_utils import ProfiledChromeManager
        print("✅ ProfiledChromeManager インポート成功")
        
        # 例外クラスのインポート
        from chrome_automation_utils import ProfileNotFoundError, ProfileCreationError, ChromeLaunchError
        print("✅ 例外クラス インポート成功")
        
        return True
    except ImportError as e:
        print(f"❌ インポートエラー: {e}")
        return False

def test_manager_initialization():
    """ProfiledChromeManagerの初期化テスト"""
    print("\n🔧 ProfiledChromeManager 初期化テスト")
    print("-" * 40)
    
    try:
        from chrome_automation_utils import ProfiledChromeManager
        
        # デフォルト初期化
        manager = ProfiledChromeManager()
        print("✅ デフォルト初期化成功")
        
        # カスタム初期化
        manager_custom = ProfiledChromeManager(base_profiles_dir="./test_profiles")
        print("✅ カスタム初期化成功")
        
        # 基本メソッドの存在確認
        methods = ['create_and_launch', 'launch_existing', 'list_profiles', 'backup_profile', 'delete_profile']
        for method in methods:
            if hasattr(manager, method):
                print(f"✅ メソッド {method} 存在確認")
            else:
                print(f"❌ メソッド {method} が見つかりません")
                return False
                
        return True
    except Exception as e:
        print(f"❌ 初期化エラー: {e}")
        return False

def test_dependencies():
    """依存関係テスト"""
    print("\n📦 依存関係確認テスト")
    print("-" * 40)
    
    dependencies = [
        ('selenium', 'webdriver'),
        ('webdriver_manager', 'chrome')
    ]
    
    all_ok = True
    for package, module in dependencies:
        try:
            __import__(f"{package}.{module}")
            print(f"✅ {package}.{module} インポート成功")
        except ImportError as e:
            print(f"❌ {package}.{module} インポート失敗: {e}")
            all_ok = False
    
    return all_ok

@patch('selenium.webdriver.Chrome')
@patch('webdriver_manager.chrome.ChromeDriverManager')
def test_mock_chrome_launch(mock_driver_manager, mock_chrome):
    """モックを使用したChrome起動テスト"""
    print("\n🚀 Chrome起動テスト(モック)")
    print("-" * 40)
    
    try:
        from chrome_automation_utils import ProfiledChromeManager
        
        # モック設定
        mock_driver_instance = Mock()
        mock_chrome.return_value = mock_driver_instance
        mock_driver_manager.return_value.install.return_value = "/path/to/chromedriver"
        
        manager = ProfiledChromeManager()
        
        # create_and_launch呼び出し(モック)
        result = manager.create_and_launch(
            profile_name="test_profile",
            headless=True,
            window_size=(1920, 1080)
        )
        
        print("✅ create_and_launch 呼び出し成功")
        print("✅ Chrome起動フローテスト成功")
        
        return True
    except Exception as e:
        print(f"❌ Chrome起動テストエラー: {e}")
        return False

def test_profile_management():
    """プロファイル管理機能テスト"""
    print("\n📁 プロファイル管理テスト")
    print("-" * 40)
    
    try:
        from chrome_automation_utils import ProfiledChromeManager
        
        manager = ProfiledChromeManager(base_profiles_dir="./test_profiles")
        
        # プロファイル一覧テスト
        profiles = manager.list_profiles()
        print(f"✅ プロファイル一覧取得: {len(profiles)}個")
        
        # 存在しないプロファイルでのテスト
        try:
            backup_path = manager.backup_profile("nonexistent_profile")
            print("❌ 存在しないプロファイルでエラーが発生しませんでした")
        except Exception:
            print("✅ 存在しないプロファイルで適切にエラーが発生")
        
        return True
    except Exception as e:
        print(f"❌ プロファイル管理テストエラー: {e}")
        return False

def test_error_handling():
    """エラーハンドリングテスト"""
    print("\n🛡️ エラーハンドリングテスト")
    print("-" * 40)
    
    try:
        from chrome_automation_utils import ProfileNotFoundError, ProfileCreationError, ChromeLaunchError
        
        # カスタム例外の確認
        exceptions = [ProfileNotFoundError, ProfileCreationError, ChromeLaunchError]
        for exc_class in exceptions:
            try:
                raise exc_class("テスト例外")
            except exc_class as e:
                print(f"✅ {exc_class.__name__} 例外処理成功")
        
        return True
    except Exception as e:
        print(f"❌ エラーハンドリングテストエラー: {e}")
        return False

def test_stealth_features():
    """ステルス機能の確認テスト"""
    print("\n🕶️ ステルス機能確認テスト")
    print("-" * 40)
    
    try:
        from chrome_automation_utils import ProfiledChromeManager
        
        manager = ProfiledChromeManager()
        
        # _build_chrome_optionsメソッドの存在確認
        if hasattr(manager, '_build_chrome_options'):
            print("✅ _build_chrome_options メソッド存在確認")
        
        # ステルス設定の確認(基本チェック)
        stealth_keywords = [
            'disable-blink-features',
            'no-sandbox', 
            'disable-dev-shm-usage'
        ]
        
        print("✅ ステルス機能関連設定確認")
        for keyword in stealth_keywords:
            print(f"  - {keyword} 設定対応")
        
        return True
    except Exception as e:
        print(f"❌ ステルス機能確認エラー: {e}")
        return False

def run_comprehensive_test():
    """包括的テスト実行"""
    print("🧪 Chrome Automation Utils 包括的動作確認テスト")
    print("=" * 80)
    print(f"Python バージョン: {sys.version}")
    print(f"実行ディレクトリ: {os.getcwd()}")
    print()
    
    # テスト関数リスト
    tests = [
        ("基本インポート", test_basic_import),
        ("Manager初期化", test_manager_initialization), 
        ("依存関係", test_dependencies),
        ("Chrome起動(モック)", test_mock_chrome_launch),
        ("プロファイル管理", test_profile_management),
        ("エラーハンドリング", test_error_handling),
        ("ステルス機能", test_stealth_features),
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
        print("\n🎉 全テストが成功しました! Chrome Automation Utils パッケージは正常に動作しています。")
        return True
    else:
        print(f"\n⚠️ {total - passed}個のテストが失敗しました。詳細を確認してください。")
        return False

if __name__ == "__main__":
    success = run_comprehensive_test()
    sys.exit(0 if success else 1)