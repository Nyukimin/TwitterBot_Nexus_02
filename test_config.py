#!/usr/bin/env python3
"""
config.py 動作確認テスト
"""
import os
import sys

def test_env_loading():
    """環境変数読み込みテスト"""
    print("=== 環境変数確認 ===")
    print(f"GEMINI_API_KEY: {'✅ 設定済み' if os.getenv('GEMINI_API_KEY') else '❌ 未設定'}")
    print(f"TWITTER_PASSWORD: {'✅ 設定済み' if os.getenv('TWITTER_PASSWORD') else '❌ 未設定'}")
    print(f"TWITTER_USERNAME: {'✅ 設定済み' if os.getenv('TWITTER_USERNAME') else '❌ 未設定'}")
    print()

def test_config_import():
    """config.py import テスト"""
    try:
        from reply_bot.config import GEMINI_API_KEY, USERNAME, PASSWORD
        print("=== config.py 読み込み確認 ===")
        print(f"GEMINI_API_KEY: {GEMINI_API_KEY[:10]}... ({'✅ 正常' if GEMINI_API_KEY else '❌ None'})")
        print(f"USERNAME: {USERNAME} ({'✅ 正常' if USERNAME else '❌ None'})")
        print(f"PASSWORD: {'✅ 設定済み' if PASSWORD else '❌ None'}")
        print("✅ config.py 環境変数読み込み成功")
        return True
    except Exception as e:
        print(f"❌ config.py エラー: {e}")
        return False

if __name__ == "__main__":
    test_env_loading()
    success = test_config_import()
    
    if success:
        print("\n🎉 全テスト成功: .env化の動作確認完了")
    else:
        print("\n❌ テスト失敗: 設定を確認してください")