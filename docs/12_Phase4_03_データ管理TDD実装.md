# Phase 4-03: データ管理TDD実装

**作成日**: 2025-11-24  
**バージョン**: 2.0 (TDD対応版・概要版)  
**対象者**: 中級エンジニア  
**実装時間**: 8-12時間

---

## 📋 目次

1. [概要](#概要)
2. [YAML設定管理TDD実装](#yaml設定管理tdd実装)
3. [JSONキャッシュ管理TDD実装](#jsonキャッシュ管理tdd実装)
4. [ログファイル管理TDD実装](#ログファイル管理tdd実装)
5. [データ整合性保証TDD実装](#データ整合性保証tdd実装)
6. [完了チェックリスト](#完了チェックリスト)

---

## 🎯 概要

このフェーズでは、**ファイルベースのデータ管理機能**をTDD形式で実装します。

### **実装対象**

```
データ管理システム
├── YAML設定管理
│   ├── アカウント設定読み込み・保存
│   ├── 設定バリデーション
│   └── Hot Reload機能
├── JSONキャッシュ管理
│   ├── greeting_tracker（挨拶記録）
│   ├── ai_response_cache（AI応答キャッシュ）
│   └── session_cache（セッション情報）
├── ログファイル管理
│   ├── 構造化ログ出力
│   ├── ログローテーション
│   └── アクションログ記録
└── データ整合性保証
    ├── ファイルロック機構
    ├── アトミック書き込み
    └── バックアップ・復旧
```

---

## 🧪 YAML設定管理TDD実装

### **Step 1: テスト作成（Red）**

**tests/unit/test_config_manager.py:**
```python
"""YAML設定管理のTDDテスト"""

import pytest
from pathlib import Path
from reply_bot.config_manager import (
    ConfigManager,
    validate_account_schema,
    save_account_config
)


class TestConfigManager:
    """YAML設定管理のテスト"""
    
    def test_load_valid_config(self, tmp_path):
        """有効な設定ファイル読み込み"""
        # Arrange
        config_path = tmp_path / "accounts.yaml"
        config_path.write_text("""
accounts:
  - id: test001
    handle: testuser
    features:
      like: true
""")
        
        # Act
        manager = ConfigManager(str(config_path))
        config = manager.load()
        
        # Assert
        assert len(config["accounts"]) == 1
        assert config["accounts"][0]["id"] == "test001"
    
    def test_validate_account_schema(self):
        """アカウント設定のスキーマ検証"""
        # Arrange
        valid_account = {
            "id": "test001",
            "handle": "testuser",
            "features": {"like": True}
        }
        
        invalid_account = {
            "id": "",  # 空のID（無効）
            "handle": "testuser"
        }
        
        # Act & Assert
        assert validate_account_schema(valid_account) is True
        assert validate_account_schema(invalid_account) is False
    
    def test_save_config_atomically(self, tmp_path):
        """設定の原子的保存"""
        # Arrange
        config_path = tmp_path / "accounts.yaml"
        config_data = {"accounts": [{"id": "test001"}]}
        
        # Act
        save_account_config(str(config_path), config_data)
        
        # Assert
        assert config_path.exists()
        from yaml import safe_load
        with open(config_path) as f:
            loaded = safe_load(f)
        assert loaded == config_data
```

### **Step 2: 最小実装（Green）**

**reply_bot/config_manager.py:**
```python
"""YAML設定管理（TDDで段階的に実装）"""

import yaml
from pathlib import Path
from typing import Dict


class ConfigManager:
    """YAML設定ファイル管理"""
    
    def __init__(self, config_path: str):
        self.config_path = Path(config_path)
    
    def load(self) -> Dict:
        """設定読み込み"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config not found: {self.config_path}")
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)


def validate_account_schema(account: Dict) -> bool:
    """アカウント設定スキーマ検証"""
    required_fields = ["id", "handle"]
    
    for field in required_fields:
        if field not in account or not account[field]:
            return False
    
    return True


def save_account_config(config_path: str, config_data: Dict) -> None:
    """設定を原子的に保存"""
    path = Path(config_path)
    
    # 一時ファイルに書き込み
    temp_path = path.with_suffix('.yaml.tmp')
    with open(temp_path, 'w', encoding='utf-8') as f:
        yaml.dump(config_data, f, allow_unicode=True)
    
    # 原子的にリネーム
    temp_path.replace(path)
```

---

## 🧪 JSONキャッシュ管理TDD実装

### **Step 1: テスト作成（Red）**

**tests/unit/test_cache_manager.py:**
```python
"""JSONキャッシュ管理のTDDテスト"""

import pytest
from datetime import datetime
from reply_bot.cache_manager import GreetingTracker, AIResponseCache


class TestGreetingTracker:
    """挨拶記録キャッシュのテスト"""
    
    def test_record_greeting(self, tmp_path):
        """挨拶記録の保存"""
        # Arrange
        cache_file = tmp_path / "greeting.json"
        tracker = GreetingTracker(str(cache_file))
        
        # Act
        tracker.record_greeting("@user1", datetime.now())
        
        # Assert
        assert tracker.has_greeted("@user1") is True
    
    def test_check_daily_limit(self, tmp_path):
        """日次制限チェック"""
        # Arrange
        cache_file = tmp_path / "greeting.json"
        tracker = GreetingTracker(str(cache_file), daily_limit=3)
        
        # Act
        for i in range(3):
            tracker.record_greeting(f"@user{i}", datetime.now())
        
        # Assert
        assert tracker.is_daily_limit_reached() is True


class TestAIResponseCache:
    """AI応答キャッシュのテスト"""
    
    def test_cache_response(self, tmp_path):
        """AI応答のキャッシュ"""
        # Arrange
        cache_file = tmp_path / "ai_cache.json"
        cache = AIResponseCache(str(cache_file))
        
        context_hash = "abc123"
        response = "これはキャッシュされた応答です。"
        
        # Act
        cache.store(context_hash, response)
        
        # Assert
        cached = cache.get(context_hash)
        assert cached == response
    
    def test_cache_expiration(self, tmp_path):
        """キャッシュの有効期限"""
        # Arrange
        cache_file = tmp_path / "ai_cache.json"
        cache = AIResponseCache(str(cache_file), ttl_seconds=1)
        
        # Act
        cache.store("key1", "value1")
        
        import time
        time.sleep(2)  # TTL経過
        
        # Assert
        assert cache.get("key1") is None  # 期限切れ
```

---

## 🧪 ログファイル管理TDD実装

### **Step 1: テスト作成（Red）**

**tests/unit/test_log_manager.py:**
```python
"""ログ管理のTDDテスト"""

import pytest
import logging
from reply_bot.log_manager import StructuredLogger, ActionLogger


class TestStructuredLogger:
    """構造化ログのテスト"""
    
    def test_log_with_metadata(self, tmp_path):
        """メタデータ付きログ出力"""
        # Arrange
        log_file = tmp_path / "test.log"
        logger = StructuredLogger("test_logger", str(log_file))
        
        # Act
        logger.info("Test message", extra={"account_id": "test001"})
        
        # Assert
        with open(log_file) as f:
            log_content = f.read()
        assert "test001" in log_content
        assert "Test message" in log_content


class TestActionLogger:
    """アクションログのテスト"""
    
    def test_log_action(self, tmp_path):
        """アクション記録"""
        # Arrange
        log_file = tmp_path / "actions.json"
        logger = ActionLogger(str(log_file))
        
        # Act
        logger.log_action(
            action_type="like",
            target_user="@testuser",
            result="success"
        )
        
        # Assert
        import json
        with open(log_file) as f:
            actions = [json.loads(line) for line in f]
        
        assert len(actions) == 1
        assert actions[0]["action_type"] == "like"
```

---

## 🧪 データ整合性保証TDD実装

### **Step 1: テスト作成（Red）**

**tests/unit/test_data_integrity.py:**
```python
"""データ整合性のTDDテスト"""

import pytest
from pathlib import Path
from reply_bot.file_lock import FileLock, acquire_lock


class TestFileLock:
    """ファイルロック機構のテスト"""
    
    def test_acquire_lock(self, tmp_path):
        """ロック取得"""
        # Arrange
        lock_file = tmp_path / "test.lock"
        
        # Act
        with FileLock(str(lock_file)):
            # ロック中
            assert lock_file.exists()
        
        # Assert
        assert not lock_file.exists()  # ロック解除
    
    def test_lock_timeout(self, tmp_path):
        """ロックタイムアウト"""
        # Arrange
        lock_file = tmp_path / "test.lock"
        
        # Act & Assert
        with FileLock(str(lock_file)):
            with pytest.raises(TimeoutError):
                # 2重ロック試行（タイムアウト）
                with FileLock(str(lock_file), timeout=1):
                    pass
```

### **Step 2: 最小実装（Green）**

**reply_bot/file_lock.py:**
```python
"""ファイルロック機構（TDDで段階的に実装）"""

import time
from pathlib import Path


class FileLock:
    """ファイルベースロック"""
    
    def __init__(self, lock_path: str, timeout: float = 30.0):
        self.lock_path = Path(lock_path)
        self.timeout = timeout
    
    def __enter__(self):
        """ロック取得"""
        start_time = time.time()
        
        while True:
            try:
                self.lock_path.touch(exist_ok=False)
                return self
            except FileExistsError:
                if time.time() - start_time > self.timeout:
                    raise TimeoutError(f"Lock timeout: {self.lock_path}")
                time.sleep(0.1)
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """ロック解放"""
        if self.lock_path.exists():
            self.lock_path.unlink()
```

---

## ✅ 完了チェックリスト

```yaml
phase4_03_completion:
  yaml_config_management:
    - [ ] ConfigManager テスト成功
    - [ ] validate_account_schema テスト成功
    - [ ] save_account_config テスト成功
    - [ ] カバレッジ70%以上
  
  json_cache_management:
    - [ ] GreetingTracker テスト成功
    - [ ] AIResponseCache テスト成功
    - [ ] SessionCache テスト成功
    - [ ] カバレッジ70%以上
  
  log_management:
    - [ ] StructuredLogger テスト成功
    - [ ] ActionLogger テスト成功
    - [ ] ログローテーション動作確認
    - [ ] カバレッジ70%以上
  
  data_integrity:
    - [ ] FileLock テスト成功
    - [ ] アトミック書き込み テスト成功
    - [ ] バックアップ・復旧 テスト成功
    - [ ] カバレッジ80%以上
  
  next_step:
    - [ ] Phase4_04へ進む（セキュリティTDD実装）
```

---

**次のフェーズ:**  
[Phase4_04_セキュリティTDD実装.md](12_Phase4_04_セキュリティTDD実装.md)

---

**最終更新**: 2025-11-24