# Phase 4-04: セキュリティTDD実装

**作成日**: 2025-11-24  
**バージョン**: 2.0 (TDD対応版・概要版)  
**対象者**: 上級エンジニア  
**実装時間**: 6-10時間

---

## 📋 目次

1. [概要](#概要)
2. [認証・セッション管理TDD実装](#認証セッション管理tdd実装)
3. [APIキー管理TDD実装](#apiキー管理tdd実装)
4. [データ保護TDD実装](#データ保護tdd実装)
5. [アクセス制御TDD実装](#アクセス制御tdd実装)
6. [完了チェックリスト](#完了チェックリスト)

---

## 🎯 概要

このフェーズでは、**セキュリティ機能**をTDD形式で実装します。

### **実装対象**

```
セキュリティシステム
├── 認証・セッション管理
│   ├── Chromeプロファイル認証
│   ├── セッション永続化
│   └── セッション検証
├── APIキー管理
│   ├── 環境変数読み込み
│   ├── キーローテーション
│   └── キー暗号化
├── データ保護
│   ├── ログマスキング
│   ├── 個人情報匿名化
│   └── データ暗号化
└── アクセス制御
    ├── ファイル権限管理
    ├── プロセス分離
    └── ネットワーク制限
```

---

## 🧪 認証・セッション管理TDD実装

### **Step 1: テスト作成（Red）**

**tests/unit/test_authentication.py:**
```python
"""認証・セッション管理のTDDテスト"""

import pytest
from pathlib import Path
from reply_bot.authentication import (
    ChromeSessionManager,
    validate_session,
    create_secure_profile
)


class TestChromeSessionManager:
    """Chromeセッション管理のテスト"""
    
    def test_create_profile_directory(self, tmp_path):
        """プロファイルディレクトリ作成"""
        # Arrange
        manager = ChromeSessionManager(base_dir=str(tmp_path))
        
        # Act
        profile_path = manager.create_profile("test_user")
        
        # Assert
        assert Path(profile_path).exists()
        assert Path(profile_path).is_dir()
    
    def test_profile_isolation(self, tmp_path):
        """プロファイル分離の確認"""
        # Arrange
        manager = ChromeSessionManager(base_dir=str(tmp_path))
        
        # Act
        profile1 = manager.create_profile("user1")
        profile2 = manager.create_profile("user2")
        
        # Assert
        assert profile1 != profile2
        assert not Path(profile1).samefile(profile2)


class TestSessionValidation:
    """セッション検証のテスト"""
    
    def test_validate_active_session(self):
        """有効なセッション検証"""
        # Arrange
        session_data = {
            "created_at": "2025-11-24T00:00:00",
            "expires_at": "2025-12-24T00:00:00",
            "user_id": "test001"
        }
        
        # Act
        is_valid = validate_session(session_data)
        
        # Assert
        assert is_valid is True
    
    def test_validate_expired_session(self):
        """期限切れセッション検証"""
        # Arrange
        session_data = {
            "created_at": "2024-01-01T00:00:00",
            "expires_at": "2024-01-02T00:00:00",
            "user_id": "test001"
        }
        
        # Act
        is_valid = validate_session(session_data)
        
        # Assert
        assert is_valid is False
```

### **Step 2: 最小実装（Green）**

**reply_bot/authentication.py:**
```python
"""認証・セッション管理（TDDで段階的に実装）"""

from pathlib import Path
from datetime import datetime
from typing import Dict, Optional


class ChromeSessionManager:
    """Chromeセッション管理"""
    
    def __init__(self, base_dir: str = "profile"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(exist_ok=True)
    
    def create_profile(self, account_id: str) -> str:
        """プロファイルディレクトリ作成
        
        Args:
            account_id: アカウントID
        
        Returns:
            プロファイルパス
        """
        profile_path = self.base_dir / account_id
        profile_path.mkdir(parents=True, exist_ok=True)
        
        # 権限設定（所有者のみアクセス）
        profile_path.chmod(0o700)
        
        return str(profile_path)


def validate_session(session_data: Dict) -> bool:
    """セッション有効性検証
    
    Args:
        session_data: セッション情報
    
    Returns:
        有効ならTrue
    """
    if "expires_at" not in session_data:
        return False
    
    expires_at = datetime.fromisoformat(session_data["expires_at"])
    return datetime.now() < expires_at
```

---

## 🧪 APIキー管理TDD実装

### **Step 1: テスト作成（Red）**

**tests/unit/test_api_key_manager.py:**
```python
"""APIキー管理のTDDテスト"""

import pytest
import os
from reply_bot.api_key_manager import (
    APIKeyManager,
    load_api_keys,
    rotate_api_key
)


class TestAPIKeyManager:
    """APIキー管理のテスト"""
    
    def test_load_from_env(self, monkeypatch):
        """環境変数からキー読み込み"""
        # Arrange
        monkeypatch.setenv("GOOGLE_API_KEY", "test_api_key_12345")
        manager = APIKeyManager()
        
        # Act
        api_key = manager.get_key("GOOGLE_API_KEY")
        
        # Assert
        assert api_key == "test_api_key_12345"
    
    def test_missing_required_key(self):
        """必須キーが存在しない場合"""
        # Arrange
        manager = APIKeyManager()
        
        # Act & Assert
        with pytest.raises(ValueError, match="Required API key not found"):
            manager.get_key("NONEXISTENT_KEY", required=True)
    
    def test_key_encryption(self):
        """APIキーの暗号化"""
        # Arrange
        manager = APIKeyManager(encrypt=True)
        plain_key = "test_api_key_secret"
        
        # Act
        encrypted = manager.encrypt_key(plain_key)
        decrypted = manager.decrypt_key(encrypted)
        
        # Assert
        assert encrypted != plain_key
        assert decrypted == plain_key
```

---

## 🧪 データ保護TDD実装

### **Step 1: テスト作成（Red）**

**tests/unit/test_data_protection.py:**
```python
"""データ保護のTDDテスト"""

import pytest
from reply_bot.data_protection import (
    mask_sensitive_data,
    anonymize_user_info
)


class TestSensitiveDataMasking:
    """機密データマスキングのテスト"""
    
    def test_mask_user_id(self):
        """ユーザーIDマスキング"""
        # Arrange
        log_entry = "User @testuser123 performed action"
        
        # Act
        masked = mask_sensitive_data(log_entry)
        
        # Assert
        assert "@testuser123" not in masked
        assert "@USER_" in masked
    
    def test_mask_api_key(self):
        """APIキーマスキング"""
        # Arrange
        log_entry = "API Key: AIzaSyABCDEF123456"
        
        # Act
        masked = mask_sensitive_data(log_entry)
        
        # Assert
        assert "AIzaSyABCDEF123456" not in masked
        assert "API_KEY_" in masked


class TestAnonymization:
    """匿名化のテスト"""
    
    def test_anonymize_user_data(self):
        """ユーザーデータ匿名化"""
        # Arrange
        user_data = {
            "user_id": "12345",
            "handle": "@testuser",
            "display_name": "Test User"
        }
        
        # Act
        anonymized = anonymize_user_info(user_data)
        
        # Assert
        assert anonymized["user_id"] != "12345"
        assert anonymized["user_id"].startswith("USER_")
```

---

## 🧪 アクセス制御TDD実装

### **Step 1: テスト作成（Red）**

**tests/unit/test_access_control.py:**
```python
"""アクセス制御のTDDテスト"""

import pytest
from pathlib import Path
from reply_bot.access_control import (
    set_secure_permissions,
    verify_file_permissions,
    IsolatedProcess
)


class TestFilePermissions:
    """ファイル権限管理のテスト"""
    
    def test_set_secure_permissions(self, tmp_path):
        """セキュアなファイル権限設定"""
        # Arrange
        test_file = tmp_path / "sensitive.txt"
        test_file.write_text("secret data")
        
        # Act
        set_secure_permissions(str(test_file), mode=0o600)
        
        # Assert
        stat_info = test_file.stat()
        assert oct(stat_info.st_mode)[-3:] == '600'
    
    def test_verify_permissions(self, tmp_path):
        """権限検証"""
        # Arrange
        test_file = tmp_path / "test.txt"
        test_file.write_text("data")
        test_file.chmod(0o600)
        
        # Act & Assert
        assert verify_file_permissions(str(test_file), expected_mode=0o600) is True
        assert verify_file_permissions(str(test_file), expected_mode=0o644) is False
```

---

## ✅ 完了チェックリスト

```yaml
phase4_04_completion:
  authentication:
    - [ ] ChromeSessionManager テスト成功
    - [ ] validate_session テスト成功
    - [ ] create_secure_profile テスト成功
    - [ ] カバレッジ80%以上
  
  api_key_management:
    - [ ] APIKeyManager テスト成功
    - [ ] load_api_keys テスト成功
    - [ ] rotate_api_key テスト成功
    - [ ] カバレッジ75%以上
  
  data_protection:
    - [ ] mask_sensitive_data テスト成功
    - [ ] anonymize_user_info テスト成功
    - [ ] カバレッジ80%以上
  
  access_control:
    - [ ] set_secure_permissions テスト成功
    - [ ] verify_file_permissions テスト成功
    - [ ] IsolatedProcess テスト成功
    - [ ] カバレッジ70%以上
  
  security_scan:
    - [ ] bandit セキュリティスキャン実施
    - [ ] 脆弱性ゼロ確認
    - [ ] セキュリティレポート作成
  
  next_step:
    - [ ] Phase4_05へ進む（統合テストと品質保証）
```

---

**次のフェーズ:**  
[Phase4_05_統合テストと品質保証.md](12_Phase4_05_統合テストと品質保証.md)

---

**最終更新**: 2025-11-24