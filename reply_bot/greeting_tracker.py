"""
当日の挨拶記録を管理するモジュール
DB機能削除後の代替として、ファイルベースで簡易実装
"""

import os
import json
import random
from datetime import datetime
from typing import Dict, List, Optional


class GreetingTracker:
    """当日の挨拶記録を管理するクラス"""
    
    def __init__(self, data_dir: str = "cache"):
        self.data_dir = data_dir
        self.greeting_file = os.path.join(data_dir, "daily_greetings.json")
        self._ensure_data_dir()
    
    def _ensure_data_dir(self) -> None:
        """データディレクトリが存在することを確認"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir, exist_ok=True)
    
    def _load_daily_data(self) -> Dict:
        """当日のデータを読み込み"""
        today = datetime.now().strftime("%Y-%m-%d")
        
        if not os.path.exists(self.greeting_file):
            return {"date": today, "greetings": {}}
        
        try:
            with open(self.greeting_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 日付が変わっていればリセット
            if data.get("date") != today:
                return {"date": today, "greetings": {}}
            
            return data
        except (json.JSONDecodeError, FileNotFoundError):
            return {"date": today, "greetings": {}}
    
    def _save_daily_data(self, data: Dict) -> None:
        """当日のデータを保存"""
        try:
            with open(self.greeting_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            # ファイル保存エラーは警告のみ（機能継続）
            import logging
            logging.warning(f"挨拶記録の保存に失敗: {e}")
    
    def record_greeting(self, account_id: str, user_handle: str, greeting_type: str) -> None:
        """挨拶を記録"""
        data = self._load_daily_data()
        
        key = f"{account_id}:{user_handle}"
        if key not in data["greetings"]:
            data["greetings"][key] = []
        
        data["greetings"][key].append({
            "type": greeting_type,
            "time": datetime.now().strftime("%H:%M:%S")
        })
        
        self._save_daily_data(data)
    
    def get_greeting_count(self, account_id: str, user_handle: str, greeting_type: str) -> int:
        """特定の挨拶タイプの当日の送信回数を取得"""
        data = self._load_daily_data()
        
        key = f"{account_id}:{user_handle}"
        if key not in data["greetings"]:
            return 0
        
        count = 0
        for greeting in data["greetings"][key]:
            if greeting.get("type") == greeting_type:
                count += 1
        
        return count


# 挨拶バリエーションのパターン定義
GREETING_VARIATIONS = {
    "morning": {
        "first": ["おはよう🩷", "おはようございます🩷"],
        "repeat": [
            "今日も素敵な1日になりそう🩷",
            "今日もよろしくね🩷",
            "朝から元気いっぱいですね🩷",
            "今日もゆるゆるいこうね🩷",
            "素敵な朝ですね🩷",
            "今日もキラキラしてる🩷",
            "朝から会えて嬉しい🩷",
            "今日ものんびりいきましょ🩷",
            "ゆったりした朝だね🩷"
        ]
    },
    "afternoon": {
        "first": ["こんにちは🩷"],
        "repeat": [
            "お疲れさま🩷",
            "今日も輝いてますね🩷",
            "午後もゆるゆるいこうね🩷",
            "いいお天気で気分上がる🩷",
            "元気にしてた🩷",
            "今日もかわいい🩷",
            "お昼はなに食べました🩷",
            "午後ものんびりしよ🩷",
            "まったりしてる🩷"
        ]
    },
    "evening": {
        "first": ["こんばんは🩷"],
        "repeat": [
            "今日もお疲れさま🩷",
            "1日お疲れさまでした🩷",
            "今日はどんな1日だった🩷",
            "夜も素敵ですね🩷",
            "今夜もゆるゆるいこうね🩷",
            "お疲れさまです🩷",
            "夜も会えて嬉しい🩷",
            "夜はまったりタイムですね🩷"
        ]
    },
    "night": {
        "first": ["おやすみ🩷", "おやすみなさい🩷"],
        "repeat": [
            "今日もお疲れさまでした🩷",
            "ゆっくり休んでね🩷",
            "また明日ね🩷",
            "素敵な夢を🩷",
            "今日もありがとう🩷",
            "おやすみです🩷",
            "明日もゆるゆるいこうね🩷",
            "ゆったり休んでください🩷",
            "のんびり夢の世界へ🩷"
        ]
    },
    
    # 英語版
    "good_morning": {
        "first": ["Good morning🩷"],
        "repeat": [
            "Have a wonderful day🩷",
            "Hope you have a great day🩷",
            "Wishing you a lovely morning🩷",
            "Morning sunshine🩷",
            "Have a beautiful day🩷"
        ]
    },
    "hello": {
        "first": ["Hello🩷", "Hi🩷"],
        "repeat": [
            "How are you doing🩷",
            "Nice to see you again🩷",
            "Hope you're having a good day🩷",
            "You look great today🩷",
            "Always happy to see you🩷"
        ]
    },
    "good_evening": {
        "first": ["Good evening🩷"],
        "repeat": [
            "How was your day🩷",
            "Hope you had a great day🩷",
            "Have a lovely evening🩷",
            "Evening beautiful🩷",
            "Nice to see you tonight🩷"
        ]
    },
    "good_night": {
        "first": ["Good night🩷"],
        "repeat": [
            "Sweet dreams🩷",
            "Sleep well cutie🩷",
            "Rest well🩷",
            "Dream of nice things🩷",
            "See you tomorrow🩷"
        ]
    }
}


def get_varied_greeting(account_id: str, user_handle: str, greeting_type: str, 
                       tracker: Optional[GreetingTracker] = None) -> str:
    """バリエーションのある挨拶を取得"""
    if tracker is None:
        tracker = GreetingTracker()
    
    count = tracker.get_greeting_count(account_id, user_handle, greeting_type)
    
    if greeting_type not in GREETING_VARIATIONS:
        return "こんにちは🩷"  # フォールバック
    
    patterns = GREETING_VARIATIONS[greeting_type]
    
    if count == 0:
        # 初回は標準の挨拶から選択
        greeting = random.choice(patterns["first"])
    else:
        # 2回目以降はバリエーションから選択
        greeting = random.choice(patterns["repeat"])
    
    # 記録
    tracker.record_greeting(account_id, user_handle, greeting_type)
    
    return greeting