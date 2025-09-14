#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
コメント重複防止機能のテストスクリプト
"""

import logging
import time
from reply_bot.db_stubs import record_action_log, has_action_log, cleanup_old_logs

def test_comment_duplication_prevention():
    """コメント重複防止のテスト"""
    
    # ログ設定
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # テストデータ
    account_id = "Maya19960330"
    tweet_id = "test_tweet_123"
    action_type = "comment"
    
    print(f"=== コメント重複防止テスト開始 ===")
    
    # 初回実行前の状態確認
    has_log_before = has_action_log(account_id, tweet_id, action_type)
    print(f"1. 初回実行前のログ状態: {has_log_before}")
    assert not has_log_before, "初回実行前にログが存在すべきではない"
    
    # 初回コメント実行をシミュレート
    print("2. 初回コメント実行をシミュレート...")
    record_action_log(account_id, tweet_id, action_type, 'success', meta='test_first')
    
    # 初回実行後の状態確認
    has_log_after_first = has_action_log(account_id, tweet_id, action_type)
    print(f"3. 初回実行後のログ状態: {has_log_after_first}")
    assert has_log_after_first, "初回実行後にログが存在すべき"
    
    # 2回目実行（重複）をシミュレート
    print("4. 2回目実行（重複チェック）をシミュレート...")
    if has_action_log(account_id, tweet_id, action_type):
        print("   → 重複検出！コメント投稿をスキップしました")
        record_action_log(account_id, tweet_id, action_type, 'skipped', meta='duplicate_prevented')
    else:
        print("   → エラー：重複が検出されませんでした")
        
    # 異なるツイートでのテスト
    print("5. 異なるツイートでのテスト...")
    different_tweet_id = "test_tweet_456"
    has_log_different = has_action_log(account_id, different_tweet_id, action_type)
    print(f"   異なるツイートのログ状態: {has_log_different}")
    assert not has_log_different, "異なるツイートのログは存在すべきではない"
    
    # クリーンアップテスト
    print("6. ログクリーンアップテスト...")
    cleanup_old_logs(account_id, days=0)  # 即座にクリーンアップ
    
    print("=== テスト完了 ===")
    print("重複コメント防止機能は正常に動作しています！")

def test_rate_limit_counting():
    """レート制限カウントのテスト"""
    from reply_bot.db_stubs import count_actions_last_hours
    
    print(f"=== レート制限カウントテスト開始 ===")
    
    account_id = "Maya19960330"
    action_type = "comment"
    
    # 複数のコメント実行をシミュレート
    for i in range(3):
        tweet_id = f"rate_test_tweet_{i}"
        record_action_log(account_id, tweet_id, action_type, 'success', meta=f'rate_test_{i}')
        time.sleep(0.1)  # 短時間待機
    
    # 最近1時間のアクション数をカウント
    count = count_actions_last_hours(account_id, action_type, hours=1)
    print(f"最近1時間のコメント数: {count}")
    assert count >= 3, f"期待値3以上, 実際の値: {count}"
    
    print("=== レート制限カウントテスト完了 ===")

if __name__ == "__main__":
    test_comment_duplication_prevention()
    test_rate_limit_counting()