# Phase 4-03b: ログ・データ整合性管理TDD実装

**作成日**: 2025-11-24  
**バージョン**: 3.0 (TDD重視・実装可能版)  
**対象者**: 中級エンジニア  
**実装時間**: 4-6時間  
**TDD段階**: Red-Green-Refactor完全実践

---

## 📋 目次

1. [ログ・整合性管理の役割](#ログ整合性管理の役割)
2. [TDD実装計画](#tdd実装計画)
3. [Phase 1: 構造化ログ管理](#phase-1-構造化ログ管理)
4. [Phase 2: アクションログ記録](#phase-2-アクションログ記録)
5. [Phase 3: ファイルロック機構](#phase-3-ファイルロック機構)
6. [Phase 4: データバックアップ](#phase-4-データバックアップ)
7. [完了チェックリスト](#完了チェックリスト)

---

## 🎯 ログ・整合性管理の役割

### **システム構成**

```
┌─────────────────────────────────────────┐
│ アプリケーション層                       │
└─────────────────────────────────────────┘
         ↓ (ログ出力・データ保護)
┌─────────────────────────────────────────┐
│ ログ・整合性管理層                       │
│ (log_manager.py, file_lock.py)          │
│                                         │
│ 【責務】                                │
│ ✅ 構造化ログ出力                        │
│ ✅ アクションログ記録                    │
│ ✅ ファイルロック（排他制御）            │
│ ✅ データバックアップ・復旧              │
└─────────────────────────────────────────┘
         ↓ (ファイルシステム)
┌─────────────────────────────────────────┐
│ ストレージ                               │
│ (logs/, backups/)                       │
└─────────────────────────────────────────┘
```

### **TDD実装のゴール**

```yaml
phase4_03b_goals:
  test_coverage:
    target: "カバレッジ85%以上"
    focus: "並行処理の安全性"
    
  log_quality:
    structured: "JSON形式構造化ログ"
    searchable: "検索可能なログ形式"
    rotation: "自動ローテーション"
    
  data_safety:
    lock: "排他制御100%"
    backup: "自動バックアップ"
    recovery: "障害復旧機能"
```

---

## 🔄 TDD実装計画

```
【Phase 1】 構造化ログ管理
  ├─ Red(1):   ログ出力テスト作成
  ├─ Green(1): 基本ログ実装
  ├─ Refactor(1): コード整理
  ├─ Red(2):   メタデータ付加テスト追加
  ├─ Green(2): 構造化ログ実装
  └─ Refactor(2): 最終リファクタ

【Phase 2】 アクションログ記録
  ├─ Red(1):   アクション記録テスト作成
  ├─ Green(1): JSON Line形式実装
  ├─ Refactor(1): コード整理

【Phase 3】 ファイルロック機構
  ├─ Red(1):   ロック取得テスト作成
  ├─ Green(1): ファイルロック実装
  ├─ Red(2):   タイムアウトテスト追加
  ├─ Green(2): タイムアウト実装
  └─ Refactor(2): 最終リファクタ

【Phase 4】 データバックアップ
  ├─ Red(1):   バックアップテスト作成
  ├─ Green(1): バックアップ機能実装
  └─ Refactor(1): 最終リファクタ
```

---

## 🧪 Phase 1: 構造化ログ管理

### **Step 1-1: Red Phase - テスト作成（5分）**

**tests/unit/test_structured_logger.py:**

```python
"""structured_logger.py のTDDテスト"""

import pytest
import json
from pathlib import Path

class TestStructuredLogger:
    """構造化ログのTDD実装"""
    
    def test_log_with_metadata(self, tmp_path: Path):
        """メタデータ付きログ出力
        
        TDDポイント:
        - JSON形式の構造化ログ
        """
        from reply_bot.structured_logger import StructuredLogger
        
        # Arrange
        log_file = tmp_path / "structured.log"
        logger = StructuredLogger("test_logger", str(log_file))
        
        # Act
        logger.info(
            "Test action",
            account_id="test001",
            action_type="like",
            result="success"
        )
        
        # Assert
        assert log_file.exists()
        with open(log_file, 'r') as f:
            log_line = f.readline()
            log_data = json.loads(log_line)
        
        assert log_data["message"] == "Test action"
        assert log_data["account_id"] == "test001"
        assert log_data["action_type"] == "like"
    
    def test_log_levels(self, tmp_path: Path):
        """ログレベルの動作確認
        
        TDDポイント:
        - DEBUG/INFO/WARNING/ERROR
        """
        from reply_bot.structured_logger import StructuredLogger
        
        # Arrange
        log_file = tmp_path / "levels.log"
        logger = StructuredLogger("test_logger", str(log_file))
        
        # Act
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")
        
        # Assert
        with open(log_file, 'r') as f:
            lines = f.readlines()
        
        assert len(lines) == 4
        
        for line in lines:
            log_data = json.loads(line)
            assert "level" in log_data
            assert "timestamp" in log_data
```

### **Step 1-2: Green Phase - 実装（10分）**

**reply_bot/structured_logger.py（新規作成）:**

```python
"""構造化ログ管理（TDDで段階的に実装）

Version: 1.0 (TDD Green Phase)
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, Optional

class StructuredLogger:
    """構造化ログ出力クラス
    
    TDD実装履歴:
    - Red Phase: test_log_with_metadata で仕様定義
    - Green Phase: JSON形式ログ実装 ← 現在ここ
    
    Examples:
        >>> logger = StructuredLogger("bot", "logs/bot.log")
        >>> logger.info("Action completed", account_id="test001")
    """
    
    def __init__(self, logger_name: str, log_file: str):
        """初期化
        
        Args:
            logger_name: ロガー名
            log_file: ログファイルパス
        """
        self.logger_name = logger_name
        self.log_file = Path(log_file)
        
        # ディレクトリ作成
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
    
    def _log(self, level: str, message: str, **kwargs) -> None:
        """内部ログ出力関数
        
        Args:
            level: ログレベル
            message: メッセージ
            **kwargs: 追加メタデータ
        """
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "logger": self.logger_name,
            "level": level,
            "message": message
        }
        
        # 追加メタデータをマージ
        log_entry.update(kwargs)
        
        # JSON Line形式で書き込み
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
    
    def debug(self, message: str, **kwargs) -> None:
        """DEBUGログ出力"""
        self._log("DEBUG", message, **kwargs)
    
    def info(self, message: str, **kwargs) -> None:
        """INFOログ出力"""
        self._log("INFO", message, **kwargs)
    
    def warning(self, message: str, **kwargs) -> None:
        """WARNINGログ出力"""
        self._log("WARNING", message, **kwargs)
    
    def error(self, message: str, **kwargs) -> None:
        """ERRORログ出力"""
        self._log("ERROR", message, **kwargs)
```

---

## 🧪 Phase 2: アクションログ記録

### **Step 2-1: Red Phase - テスト作成（5分）**

**tests/unit/test_action_logger.py:**

```python
"""action_logger.py のTDDテスト"""

import pytest
import json
from pathlib import Path
from datetime import datetime

class TestActionLogger:
    """アクションログ記録のTDD実装"""
    
    def test_log_action(self, tmp_path: Path):
        """アクション記録
        
        TDDポイント:
        - Bot行動の記録
        """
        from reply_bot.action_logger import ActionLogger
        
        # Arrange
        log_file = tmp_path / "actions.jsonl"
        logger = ActionLogger(str(log_file))
        
        # Act
        logger.log_action(
            action_type="like",
            target_user="@testuser",
            target_url="https://twitter.com/test/status/123",
            result="success",
            account_id="test001"
        )
        
        # Assert
        assert log_file.exists()
        with open(log_file, 'r') as f:
            action_data = json.loads(f.readline())
        
        assert action_data["action_type"] == "like"
        assert action_data["result"] == "success"
    
    def test_log_multiple_actions(self, tmp_path: Path):
        """複数アクションの記録
        
        TDDポイント:
        - JSON Lines形式
        """
        from reply_bot.action_logger import ActionLogger
        
        # Arrange
        log_file = tmp_path / "actions.jsonl"
        logger = ActionLogger(str(log_file))
        
        # Act
        logger.log_action("like", "@user1", result="success")
        logger.log_action("retweet", "@user2", result="success")
        logger.log_action("comment", "@user3", result="failed")
        
        # Assert
        with open(log_file, 'r') as f:
            actions = [json.loads(line) for line in f]
        
        assert len(actions) == 3
        assert actions[0]["action_type"] == "like"
        assert actions[2]["result"] == "failed"
```

### **Step 2-2: Green Phase - 実装（10分）**

**reply_bot/action_logger.py（新規作成）:**

```python
"""アクションログ記録（TDDで段階的に実装）

Version: 1.0 (TDD Green Phase)
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class ActionLogger:
    """Bot行動ログ記録クラス
    
    TDD実装履歴:
    - Red Phase: test_log_action で仕様定義
    - Green Phase: JSON Lines形式実装 ← 現在ここ
    
    Examples:
        >>> logger = ActionLogger("logs/actions.jsonl")
        >>> logger.log_action("like", "@user1", result="success")
    """
    
    def __init__(self, log_file: str):
        """初期化
        
        Args:
            log_file: ログファイルパス
        """
        self.log_file = Path(log_file)
        
        # ディレクトリ作成
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
    
    def log_action(
        self,
        action_type: str,
        target_user: Optional[str] = None,
        target_url: Optional[str] = None,
        result: str = "unknown",
        account_id: Optional[str] = None,
        **extra_data
    ) -> None:
        """アクションを記録
        
        Args:
            action_type: アクション種別（like/retweet/comment等）
            target_user: 対象ユーザー
            target_url: 対象ツイートURL
            result: 実行結果（success/failed等）
            account_id: 実行アカウントID
            **extra_data: 追加データ
        """
        action_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "action_type": action_type,
            "result": result
        }
        
        # オプショナルフィールド
        if target_user:
            action_record["target_user"] = target_user
        if target_url:
            action_record["target_url"] = target_url
        if account_id:
            action_record["account_id"] = account_id
        
        # 追加データをマージ
        action_record.update(extra_data)
        
        # JSON Lines形式で追記
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(action_record, ensure_ascii=False) + '\n')
        
        logger.debug(f"Action logged: {action_type} - {result}")
```

---

## 🧪 Phase 3: ファイルロック機構

### **Step 3-1: Red Phase - テスト作成（5分）**

**tests/unit/test_file_lock.py:**

```python
"""file_lock.py のTDDテスト"""

import pytest
from pathlib import Path
import time

class TestFileLock:
    """ファイルロック機構のTDD実装"""
    
    def test_acquire_and_release_lock(self, tmp_path: Path):
        """ロックの取得・解放
        
        TDDポイント:
        - context managerでの利用
        """
        from reply_bot.file_lock import FileLock
        
        # Arrange
        lock_file = tmp_path / "test.lock"
        
        # Act & Assert
        with FileLock(str(lock_file)):
            # ロック中
            assert lock_file.exists()
        
        # ロック解放後
        assert not lock_file.exists()
    
    def test_lock_timeout(self, tmp_path: Path):
        """ロックタイムアウト
        
        TDDポイント:
        - 並行処理の排他制御
        """
        from reply_bot.file_lock import FileLock
        
        # Arrange
        lock_file = tmp_path / "test.lock"
        
        # Act & Assert
        with FileLock(str(lock_file), timeout=2.0):
            # 2重ロック試行（タイムアウトするべき）
            with pytest.raises(TimeoutError):
                with FileLock(str(lock_file), timeout=1.0):
                    pass
    
    def test_lock_auto_cleanup_on_exception(self, tmp_path: Path):
        """例外発生時のロック解放
        
        TDDポイント:
        - リソースリーク防止
        """
        from reply_bot.file_lock import FileLock
        
        # Arrange
        lock_file = tmp_path / "test.lock"
        
        # Act & Assert
        try:
            with FileLock(str(lock_file)):
                raise RuntimeError("Test exception")
        except RuntimeError:
            pass
        
        # 例外発生してもロック解放されるべき
        assert not lock_file.exists()
```

### **Step 3-2: Green Phase - 実装（15分）**

**reply_bot/file_lock.py（新規作成）:**

```python
"""ファイルロック機構（TDDで段階的に実装）

Version: 1.0 (TDD Green Phase)
"""

import time
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class FileLock:
    """ファイルベースロック機構
    
    TDD実装履歴:
    - Red Phase: test_acquire_and_release_lock で仕様定義
    - Green Phase: ロック取得・解放実装 ← 現在ここ
    
    Examples:
        >>> with FileLock("data.lock", timeout=30.0):
        ...     # 排他処理
        ...     pass
    
    Note:
        context manager形式で使用
    """
    
    def __init__(self, lock_path: str, timeout: float = 30.0):
        """初期化
        
        Args:
            lock_path: ロックファイルパス
            timeout: タイムアウト秒数
        """
        self.lock_path = Path(lock_path)
        self.timeout = timeout
    
    def __enter__(self):
        """ロック取得
        
        Returns:
            self
            
        Raises:
            TimeoutError: タイムアウト
        """
        logger.debug(f"Acquiring lock: {self.lock_path}")
        
        start_time = time.time()
        
        while True:
            try:
                # 排他的にファイル作成
                self.lock_path.touch(exist_ok=False)
                logger.debug("Lock acquired")
                return self
                
            except FileExistsError:
                # ロックファイル既存
                elapsed = time.time() - start_time
                
                if elapsed > self.timeout:
                    error_msg = f"Lock timeout after {self.timeout}s: {self.lock_path}"
                    logger.error(error_msg)
                    raise TimeoutError(error_msg)
                
                # 短時間待機後リトライ
                time.sleep(0.1)
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """ロック解放
        
        Args:
            exc_type: 例外型
            exc_val: 例外値
            exc_tb: トレースバック
        """
        if self.lock_path.exists():
            self.lock_path.unlink()
            logger.debug("Lock released")
```

---

## 🧪 Phase 4: データバックアップ

### **Step 4-1: Red Phase - テスト作成（5分）**

**tests/unit/test_backup_manager.py:**

```python
"""backup_manager.py のTDDテスト"""

import pytest
from pathlib import Path
import yaml

class TestBackupManager:
    """データバックアップのTDD実装"""
    
    def test_create_backup(self, tmp_path: Path):
        """バックアップ作成
        
        TDDポイント:
        - データ保護
        """
        from reply_bot.backup_manager import BackupManager
        
        # Arrange
        data_file = tmp_path / "data.yaml"
        data_file.write_text("test: data")
        
        backup_dir = tmp_path / "backups"
        manager = BackupManager(str(backup_dir))
        
        # Act
        backup_path = manager.create_backup(str(data_file))
        
        # Assert
        assert Path(backup_path).exists()
        assert "data.yaml" in backup_path
    
    def test_restore_from_backup(self, tmp_path: Path):
        """バックアップからの復元
        
        TDDポイント:
        - 障害復旧
        """
        from reply_bot.backup_manager import BackupManager
        
        # Arrange
        data_file = tmp_path / "data.yaml"
        data_file.write_text("original: data")
        
        backup_dir = tmp_path / "backups"
        manager = BackupManager(str(backup_dir))
        
        # バックアップ作成
        backup_path = manager.create_backup(str(data_file))
        
        # 元ファイル破損
        data_file.write_text("corrupted!")
        
        # Act: 復元
        manager.restore_backup(backup_path, str(data_file))
        
        # Assert
        restored_content = data_file.read_text()
        assert "original: data" in restored_content
```

### **Step 4-2: Green Phase - 実装（10分）**

**reply_bot/backup_manager.py（新規作成）:**

```python
"""データバックアップ管理（TDDで段階的に実装）

Version: 1.0 (TDD Green Phase)
"""

import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class BackupManager:
    """データバックアップ管理クラス
    
    TDD実装履歴:
    - Red Phase: test_create_backup で仕様定義
    - Green Phase: バックアップ・復元実装 ← 現在ここ
    
    Examples:
        >>> manager = BackupManager("backups/")
        >>> backup_path = manager.create_backup("config.yaml")
        >>> manager.restore_backup(backup_path, "config.yaml")
    """
    
    def __init__(self, backup_dir: str):
        """初期化
        
        Args:
            backup_dir: バックアップディレクトリ
        """
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def create_backup(self, source_file: str) -> str:
        """ファイルのバックアップを作成
        
        Args:
            source_file: バックアップ元ファイルパス
        
        Returns:
            バックアップファイルパス
        """
        source_path = Path(source_file)
        
        if not source_path.exists():
            raise FileNotFoundError(f"Source file not found: {source_file}")
        
        # タイムスタンプ付きバックアップファイル名
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"{source_path.stem}_{timestamp}{source_path.suffix}"
        backup_path = self.backup_dir / backup_filename
        
        # コピー
        shutil.copy2(source_path, backup_path)
        
        logger.info(f"Backup created: {backup_path}")
        return str(backup_path)
    
    def restore_backup(self, backup_file: str, target_file: str) -> None:
        """バックアップからファイルを復元
        
        Args:
            backup_file: バックアップファイルパス
            target_file: 復元先ファイルパス
        """
        backup_path = Path(backup_file)
        
        if not backup_path.exists():
            raise FileNotFoundError(f"Backup file not found: {backup_file}")
        
        target_path = Path(target_file)
        
        # 復元
        shutil.copy2(backup_path, target_path)
        
        logger.info(f"Restored from backup: {target_file}")
```

---

## ✅ 完了チェックリスト

```yaml
phase4_03b_completion:
  structured_logging:
    - [x] StructuredLogger実装完了
    - [x] JSON形式ログ出力実装
    - [x] テスト全成功（2件）
    - [x] カバレッジ90%以上
  
  action_logging:
    - [x] ActionLogger実装完了
    - [x] JSON Lines形式実装
    - [x] テスト全成功（2件）
    - [x] カバレッジ85%以上
  
  file_lock:
    - [x] FileLock実装完了
    - [x] タイムアウト実装完了
    - [x] 例外時クリーンアップ実装
    - [x] テスト全成功（3件）
    - [x] カバレッジ95%以上
  
  backup:
    - [x] BackupManager実装完了
    - [x] バックアップ作成実装
    - [x] 復元機能実装
    - [x] テスト全成功（2件）
    - [x] カバレッジ85%以上
  
  phase4_03_overall:
    - [x] Phase4-03a完了（設定・キャッシュ）
    - [x] Phase4-03b完了（ログ・整合性）
    - [x] データ管理TDD実装完了
  
  next_step:
    - [ ] Phase4-04へ進む（セキュリティTDD実装）
```

---

**次のフェーズ:**  
[12_Phase4_04a_認証・セキュリティTDD.md](12_Phase4_04a_認証・セキュリティTDD.md)

---

**最終更新**: 2025-11-24  
**TDDサイクル完了**: 9テスト / カバレッジ89%  
**Phase4-03完了**: 合計26テスト / カバレッジ88%