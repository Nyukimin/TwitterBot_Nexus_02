#!/usr/bin/env python3

"""
挨拶システムの動作テスト
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'reply_bot'))

from reply_bot.greeting_tracker import GreetingTracker, get_varied_greeting

def test_greeting_variations():
    """挨拶バリエーションのテスト"""
    print("=== 挨拶バリエーションテスト ===")
    
    tracker = GreetingTracker("test_cache")
    account_id = "Maya19960330"
    user_handle = "manami_ofp"
    
    # 朝の挨拶を複数回テスト
    print("\n朝の挨拶テスト (morning):")
    for i in range(4):
        greeting = get_varied_greeting(account_id, user_handle, "morning", tracker)
        count = tracker.get_greeting_count(account_id, user_handle, "morning")
        print(f"  {i+1}回目: {greeting} (カウント: {count})")
    
    # 昼の挨拶テスト
    print("\n昼の挨拶テスト (afternoon):")
    for i in range(3):
        greeting = get_varied_greeting(account_id, user_handle, "afternoon", tracker)
        count = tracker.get_greeting_count(account_id, user_handle, "afternoon")
        print(f"  {i+1}回目: {greeting} (カウント: {count})")
    
    # 別のユーザーでテスト
    print(f"\n別ユーザー (test_user) での朝の挨拶:")
    for i in range(2):
        greeting = get_varied_greeting(account_id, "test_user", "morning", tracker)
        print(f"  {i+1}回目: {greeting}")
    
    print("\n=== テスト完了 ===")

def test_data_persistence():
    """データ永続化のテスト"""
    print("\n=== データ永続化テスト ===")
    
    # 新しいトラッカーインスタンスで既存データを読み込み
    tracker = GreetingTracker("test_cache")
    account_id = "Maya19960330" 
    user_handle = "manami_ofp"
    
    morning_count = tracker.get_greeting_count(account_id, user_handle, "morning")
    afternoon_count = tracker.get_greeting_count(account_id, user_handle, "afternoon")
    
    print(f"保存されたデータ:")
    print(f"  manami_ofp - morning: {morning_count}回")
    print(f"  manami_ofp - afternoon: {afternoon_count}回")

if __name__ == "__main__":
    try:
        test_greeting_variations()
        test_data_persistence()
    except Exception as e:
        print(f"テストエラー: {e}")
        import traceback
        traceback.print_exc()