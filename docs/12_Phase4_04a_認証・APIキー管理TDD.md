# Phase 4-04a: 認証・APIキー管理TDD実装

**作成日**: 2025-11-24  
**バージョン**: 3.0 (TDD重視・実装可能版)  
**対象者**: 上級エンジニア  
**実装時間**: 3-5時間  
**TDD段階**: Red-Green-Refactor完全実践

---

## 📋 目次

1. [セキュリティ層の役割と責務](#セキュリティ層の役割と責務)
2. [TDD実装計画](#tdd実装計画)
3. [Phase 1: Chrome認証・セッション管理](#phase-1-chrome認証セッション管理)
4. [Phase 2: APIキー管理](#phase-2-apiキー管理)
5. [Phase 3: 環境変数セキュリティ](#phase-3-環境変数セキュリティ)
6. [統合テストとリファクタリング](#統合テストとリファクタリング)
7. [完了チェックリスト](#完了チェックリスト)

---

## 🎯 セキュリティ層の役割と責務

### **セキュリティ層とは**

```
┌─────────────────────────────────────────┐
│ セキュリティ層                          │
│ (authentication.py, api_key_manager.py) │
│                                         │
│ 【責務】                                │
│ ✅ Twitter認証セッション管理             │
│ ✅ APIキー安全管理・暗号化               │
│ ✅ 環境変数読み込み・検証                │
│ ✅ プロファイル分離・権限管理            │
└─────────────────────────────────────────┘
         ↓ (セキュアな認証情報を提供)
┌─────────────────────────────────────────┐
│ Layer 1: オーケストレーション層          │
│ (multi_main.py)                         │
└─────────────────────────────────────────┘
```

### **セキュリティ層が実装する機能**

```yaml
security_layer_functions:
  authentication:
    ChromeSessionManager:
      description: "Chromeプロファイル管理・セッション永続化"
      methods:
        - create_profile(account_id) -> str
        - get_profile_path(account_id) -> str
        - validate_profile_exists(account_id) -> bool
    
    validate_session:
      description: "セッション有効性検証"
      input: "session_data: Dict"
      output: "bool (有効ならTrue)"
    
    create_secure_profile:
      description: "セキュアなプロファイル作成"
      input: "account_id: str, base_dir: Path"
      output: "Path (プロファイルパス)"
  
  api_key_management:
    APIKeyManager:
      description: "APIキー管理（環境変数・暗号化）"
      methods:
        - get_key(key_name, required=False) -> Optional[str]
        - load_from_env() -> Dict[str, str]
        - encrypt_key(plain_key) -> str
        - decrypt_key(encrypted) -> str
    
    load_api_keys:
      description: "全APIキー一括読み込み"
      output: "Dict[str, str] (キー名: 値)"
    
    rotate_api_key:
      description: "APIキーローテーション"
      input: "key_name: str, new_value: str"
      output: "bool (成功ならTrue)"
```

### **TDD実装のゴール**

```yaml
phase4_04a_goals:
  test_coverage:
    target: "カバレッジ75%以上"
    focus: "セキュリティエッジケース完全カバー"
    
  tdd_cycle:
    count: "各セキュリティ機能で3-5回サイクル実施"
    time_per_cycle: "Red(10分) + Green(15分) + Refactor(10分)"
    
  security_standards:
    profile_permissions: "0o700 (所有者のみアクセス)"
    api_key_encryption: "Fernet暗号化必須"
    env_validation: "必須キー欠落時は即エラー"
    
  code_quality:
    lint: "flake8警告ゼロ"
    format: "black適用"
    typing: "型ヒント100%"
    security_scan: "banditスキャン合格"
    
  documentation:
    docstring: "全関数にGoogle Style + セキュリティ注意事項"
    examples: "doctestで安全な使用例"
```

---

## 🔄 TDD実装計画

### **実装順序とTDDサイクル**

```
【Phase 1】 ChromeSessionManager（認証・セッション管理）
  Step 1: Red  → テスト作成（プロファイル作成・分離・権限）
  Step 2: Green → 最小実装（ディレクトリ作成・chmod）
  Step 3: Refactor → パス検証・エラーハンドリング追加
  所要時間: 60分
  
【Phase 2】 APIKeyManager（APIキー管理）
  Step 1: Red  → テスト作成（環境変数読み込み・暗号化・検証）
  Step 2: Green → 最小実装（os.getenv・Fernet暗号化）
  Step 3: Refactor → キーローテーション・キャッシュ追加
  所要時間: 90分
  
【Phase 3】 環境変数セキュリティ検証
  Step 1: Red  → テスト作成（必須キー検証・型変換）
  Step 2: Green → 最小実装（dotenv読み込み・検証）
  Step 3: Refactor → .envテンプレート生成機能
  所要時間: 60分
  
【Phase 4】 統合テスト
  Step 1: 認証→APIキーの完全フロー検証
  Step 2: セキュリティスキャン（bandit）実施
  Step 3: ドキュメント整備・トラブルシューティング追加
  所要時間: 60分

合計所要時間: 4.5-5時間
```

---

## 🧪 Phase 1: Chrome認証・セッション管理

### **Step 1: テスト作成（Red）**

#### **1-1. テストファイル作成**

**tests/unit/test_authentication.py:**
```python
"""認証・セッション管理のTDDテスト

セキュリティ要件:
- プロファイルディレクトリは所有者のみアクセス（0o700）
- アカウント間でプロファイルが完全分離
- 無効なセッションは即座に検出
"""

import pytest
from pathlib import Path
from datetime import datetime, timedelta
from reply_bot.authentication import (
    ChromeSessionManager,
    validate_session,
    create_secure_profile,
    SessionValidationError
)


class TestChromeSessionManager:
    """Chromeセッション管理のテスト"""
    
    def test_create_profile_directory(self, tmp_path):
        """プロファイルディレクトリ作成
        
        テスト観点:
        - ディレクトリが正常に作成される
        - 返されるパスが文字列型
        - パスが実際に存在する
        """
        # Arrange
        manager = ChromeSessionManager(base_dir=str(tmp_path))
        
        # Act
        profile_path = manager.create_profile("test_user")
        
        # Assert
        assert isinstance(profile_path, str)
        assert Path(profile_path).exists()
        assert Path(profile_path).is_dir()
        print(f"✅ プロファイル作成成功: {profile_path}")
    
    def test_profile_permissions_are_secure(self, tmp_path):
        """プロファイルの権限が安全（0o700）
        
        セキュリティ要件:
        - 所有者のみ読み書き実行可能
        - 他ユーザーはアクセス不可
        """
        # Arrange
        manager = ChromeSessionManager(base_dir=str(tmp_path))
        
        # Act
        profile_path = manager.create_profile("secure_user")
        
        # Assert
        stat_info = Path(profile_path).stat()
        permissions = oct(stat_info.st_mode)[-3:]
        assert permissions == '700', f"権限が不正: {permissions} (期待: 700)"
        print(f"✅ セキュアな権限設定: {permissions}")
    
    def test_profile_isolation(self, tmp_path):
        """プロファイル分離の確認
        
        テスト観点:
        - 異なるアカウントで異なるパスが生成
        - パス同士が重複しない
        """
        # Arrange
        manager = ChromeSessionManager(base_dir=str(tmp_path))
        
        # Act
        profile1 = manager.create_profile("user1")
        profile2 = manager.create_profile("user2")
        
        # Assert
        assert profile1 != profile2
        assert not Path(profile1).samefile(profile2)
        print(f"✅ プロファイル分離確認: user1≠user2")
    
    def test_get_existing_profile_path(self, tmp_path):
        """既存プロファイルパス取得
        
        テスト観点:
        - 作成済みプロファイルのパスを正しく返す
        - パスが実在する
        """
        # Arrange
        manager = ChromeSessionManager(base_dir=str(tmp_path))
        original_path = manager.create_profile("existing_user")
        
        # Act
        retrieved_path = manager.get_profile_path("existing_user")
        
        # Assert
        assert retrieved_path == original_path
        assert Path(retrieved_path).exists()
        print(f"✅ 既存パス取得成功: {retrieved_path}")
    
    def test_validate_profile_exists_true(self, tmp_path):
        """プロファイル存在確認（存在する場合）"""
        # Arrange
        manager = ChromeSessionManager(base_dir=str(tmp_path))
        manager.create_profile("valid_user")
        
        # Act
        exists = manager.validate_profile_exists("valid_user")
        
        # Assert
        assert exists is True
        print("✅ プロファイル存在確認: True")
    
    def test_validate_profile_exists_false(self, tmp_path):
        """プロファイル存在確認（存在しない場合）"""
        # Arrange
        manager = ChromeSessionManager(base_dir=str(tmp_path))
        
        # Act
        exists = manager.validate_profile_exists("nonexistent_user")
        
        # Assert
        assert exists is False
        print("✅ プロファイル不存在確認: False")


class TestSessionValidation:
    """セッション検証のテスト"""
    
    def test_validate_active_session(self):
        """有効なセッション検証
        
        テスト観点:
        - 有効期限内のセッションはTrue
        - 必要なフィールドが全て揃っている
        """
        # Arrange
        now = datetime.now()
        session_data = {
            "created_at": (now - timedelta(hours=1)).isoformat(),
            "expires_at": (now + timedelta(days=30)).isoformat(),
            "user_id": "test001",
            "session_id": "abc123"
        }
        
        # Act
        is_valid = validate_session(session_data)
        
        # Assert
        assert is_valid is True
        print("✅ 有効セッション検証: True")
    
    def test_validate_expired_session(self):
        """期限切れセッション検証
        
        テスト観点:
        - 有効期限切れのセッションはFalse
        """
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
        print("✅ 期限切れセッション検証: False")
    
    def test_validate_session_missing_expires_at(self):
        """expires_atフィールド欠落時の検証
        
        テスト観点:
        - 必須フィールドが欠落している場合は例外発生
        """
        # Arrange
        session_data = {
            "created_at": "2025-11-24T00:00:00",
            "user_id": "test001"
            # expires_atが欠落
        }
        
        # Act & Assert
        with pytest.raises(SessionValidationError, match="expires_at"):
            validate_session(session_data, strict=True)
        print("✅ 欠落フィールド検出: SessionValidationError")
    
    def test_validate_session_invalid_date_format(self):
        """不正な日付フォーマット検証
        
        テスト観点:
        - ISO8601形式以外の日付は例外発生
        """
        # Arrange
        session_data = {
            "created_at": "2025-11-24T00:00:00",
            "expires_at": "invalid-date-format",
            "user_id": "test001"
        }
        
        # Act & Assert
        with pytest.raises(SessionValidationError, match="Invalid date format"):
            validate_session(session_data, strict=True)
        print("✅ 不正日付フォーマット検出: SessionValidationError")


class TestSecureProfileCreation:
    """セキュアプロファイル作成のテスト"""
    
    def test_create_secure_profile(self, tmp_path):
        """セキュアプロファイル作成
        
        テスト観点:
        - プロファイルが作成される
        - 権限が0o700に設定される
        - .gitignoreが自動生成される
        """
        # Arrange
        account_id = "secure_test"
        
        # Act
        profile_path = create_secure_profile(account_id, base_dir=tmp_path)
        
        # Assert
        assert profile_path.exists()
        assert profile_path.is_dir()
        
        # 権限確認
        stat_info = profile_path.stat()
        assert oct(stat_info.st_mode)[-3:] == '700'
        
        # .gitignore確認
        gitignore_path = profile_path / ".gitignore"
        assert gitignore_path.exists()
        assert gitignore_path.read_text().strip() == "*"
        
        print(f"✅ セキュアプロファイル作成完了: {profile_path}")
```

#### **1-2. テスト実行（失敗確認）**

```bash
# テスト実行（このタイミングでは失敗するのが正解）
pytest tests/unit/test_authentication.py -v

# 期待される出力（Red）:
# FAILED tests/unit/test_authentication.py::TestChromeSessionManager::test_create_profile_directory - ModuleNotFoundError: No module named 'reply_bot.authentication'
# FAILED tests/unit/test_authentication.py::TestSessionValidation::test_validate_active_session - ModuleNotFoundError
# ... (全テスト失敗)

# ✅ Red段階: 全テスト失敗を確認（これが正しい）
```

**トラブルシューティング:**

```bash
# pytest自体が見つからない場合
pip install pytest pytest-cov

# テストファイルが認識されない場合
# tests/__init__.py を作成
echo "" > tests/__init__.py
echo "" > tests/unit/__init__.py

# インポートエラーが出る場合
# reply_bot/__init__.py を確認
dir reply_bot\__init__.py
```

---

### **Step 2: 最小実装（Green）**

#### **2-1. 認証モジュール作成**

**reply_bot/authentication.py:**
```python
"""認証・セッション管理（TDDで段階的に実装）

セキュリティ設計原則:
1. プロファイル分離: アカウント毎に独立したディレクトリ
2. 最小権限: 0o700（所有者のみアクセス）
3. セッション検証: 有効期限チェック必須
4. エラーハンドリング: セキュリティ例外を明確に区別
"""

import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional


class SessionValidationError(Exception):
    """セッション検証エラー"""
    pass


class ChromeSessionManager:
    """Chromeセッション管理
    
    プロファイル管理の中心クラス。アカウント毎に独立した
    Chromeプロファイルディレクトリを管理します。
    
    Attributes:
        base_dir (Path): プロファイル格納ベースディレクトリ
    
    Example:
        >>> manager = ChromeSessionManager(base_dir="profile")
        >>> path = manager.create_profile("user001")
        >>> print(path)
        'profile/user001'
    """
    
    def __init__(self, base_dir: str = "profile"):
        """初期化
        
        Args:
            base_dir: プロファイル格納ベースディレクトリ
        """
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
    
    def create_profile(self, account_id: str) -> str:
        """プロファイルディレクトリ作成
        
        Args:
            account_id: アカウントID（ディレクトリ名に使用）
        
        Returns:
            作成されたプロファイルの絶対パス
        
        Raises:
            ValueError: account_idが空文字列の場合
        
        Security:
            作成されたディレクトリは0o700（所有者のみアクセス）に設定
        """
        if not account_id:
            raise ValueError("account_id must not be empty")
        
        profile_path = self.base_dir / account_id
        profile_path.mkdir(parents=True, exist_ok=True)
        
        # セキュリティ: 所有者のみアクセス可能に設定
        profile_path.chmod(0o700)
        
        return str(profile_path)
    
    def get_profile_path(self, account_id: str) -> str:
        """既存プロファイルパス取得
        
        Args:
            account_id: アカウントID
        
        Returns:
            プロファイルパス（存在しない場合でもパスを返す）
        """
        return str(self.base_dir / account_id)
    
    def validate_profile_exists(self, account_id: str) -> bool:
        """プロファイル存在確認
        
        Args:
            account_id: アカウントID
        
        Returns:
            プロファイルが存在する場合True
        """
        profile_path = self.base_dir / account_id
        return profile_path.exists() and profile_path.is_dir()


def validate_session(session_data: Dict, strict: bool = False) -> bool:
    """セッション有効性検証
    
    Args:
        session_data: セッション情報辞書
            必須フィールド: expires_at（ISO8601形式）
            推奨フィールド: created_at, user_id, session_id
        strict: Trueの場合、検証エラー時に例外発生
    
    Returns:
        セッションが有効な場合True
    
    Raises:
        SessionValidationError: strictモードで検証失敗時
    
    Example:
        >>> from datetime import datetime, timedelta
        >>> now = datetime.now()
        >>> session = {
        ...     "expires_at": (now + timedelta(days=30)).isoformat(),
        ...     "user_id": "user001"
        ... }
        >>> validate_session(session)
        True
    """
    # 必須フィールドチェック
    if "expires_at" not in session_data:
        if strict:
            raise SessionValidationError("Missing required field: expires_at")
        return False
    
    try:
        # 日付パース
        expires_at = datetime.fromisoformat(session_data["expires_at"])
        
        # 有効期限チェック
        is_valid = datetime.now() < expires_at
        return is_valid
    
    except ValueError as e:
        if strict:
            raise SessionValidationError(f"Invalid date format: {e}")
        return False


def create_secure_profile(account_id: str, base_dir: Path = Path("profile")) -> Path:
    """セキュアプロファイル作成（完全版）
    
    Args:
        account_id: アカウントID
        base_dir: ベースディレクトリ
    
    Returns:
        作成されたプロファイルのPathオブジェクト
    
    Features:
        - プロファイルディレクトリ作成
        - 権限を0o700に設定
        - .gitignoreを自動生成（プロファイル内全てを除外）
    """
    profile_path = base_dir / account_id
    profile_path.mkdir(parents=True, exist_ok=True)
    
    # セキュリティ設定
    profile_path.chmod(0o700)
    
    # .gitignore生成（プロファイル内のファイルをGit管理外に）
    gitignore_path = profile_path / ".gitignore"
    gitignore_path.write_text("*\n")
    
    return profile_path
```

#### **2-2. テスト実行（成功確認）**

```bash
# テスト実行（Green段階）
pytest tests/unit/test_authentication.py -v

# 期待される出力（Green）:
# tests/unit/test_authentication.py::TestChromeSessionManager::test_create_profile_directory PASSED
# tests/unit/test_authentication.py::TestChromeSessionManager::test_profile_permissions_are_secure PASSED
# tests/unit/test_authentication.py::TestChromeSessionManager::test_profile_isolation PASSED
# tests/unit/test_authentication.py::TestSessionValidation::test_validate_active_session PASSED
# ... (全テスト成功)
#
# ======================== 12 passed in 0.15s ========================

# ✅ Green段階: 全テスト成功を確認
```

**期待される出力:**

```
✅ プロファイル作成成功: C:\GenerativeAI\TwitterBot_Nexus_02\profile\test_user
✅ セキュアな権限設定: 700
✅ プロファイル分離確認: user1≠user2
✅ 既存パス取得成功: C:\GenerativeAI\TwitterBot_Nexus_02\profile\existing_user
✅ プロファイル存在確認: True
✅ プロファイル不存在確認: False
✅ 有効セッション検証: True
✅ 期限切れセッション検証: False
✅ 欠落フィールド検出: SessionValidationError
✅ 不正日付フォーマット検出: SessionValidationError
✅ セキュアプロファイル作成完了: C:\GenerativeAI\TwitterBot_Nexus_02\profile\secure_test
```

---

### **Step 3: リファクタリング（Refactor）**

#### **3-1. エラーハンドリング強化**

**reply_bot/authentication.py（改善版）:**
```python
# （既存のインポート文に追加）
import logging

logger = logging.getLogger(__name__)


class ChromeSessionManager:
    """Chromeセッション管理（リファクタリング版）"""
    
    def __init__(self, base_dir: str = "profile"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"ChromeSessionManager initialized: {self.base_dir}")
    
    def create_profile(self, account_id: str) -> str:
        """プロファイルディレクトリ作成（改善版）"""
        if not account_id:
            raise ValueError("account_id must not be empty")
        
        # パス安全性チェック（ディレクトリトラバーサル対策）
        if ".." in account_id or "/" in account_id or "\\" in account_id:
            raise ValueError(f"Invalid account_id: {account_id}")
        
        profile_path = self.base_dir / account_id
        
        try:
            profile_path.mkdir(parents=True, exist_ok=True)
            profile_path.chmod(0o700)
            
            logger.info(f"Profile created: {profile_path}")
            return str(profile_path)
        
        except OSError as e:
            logger.error(f"Failed to create profile: {e}")
            raise
```

#### **3-2. リファクタリング後のテスト**

```bash
# リファクタリング後も全テスト成功を確認
pytest tests/unit/test_authentication.py -v

# カバレッジ測定
pytest tests/unit/test_authentication.py --cov=reply_bot.authentication --cov-report=term

# 期待カバレッジ: 80%以上
# reply_bot/authentication.py    85%
```

---

## 🧪 Phase 2: APIキー管理

### **Step 1: テスト作成（Red）**

**tests/unit/test_api_key_manager.py:**
```python
"""APIキー管理のTDDテスト

セキュリティ要件:
- APIキーは環境変数から読み込み（.envファイル対応）
- 必須キーが欠落している場合は即座にエラー
- キーは暗号化して保存可能（Fernet使用）
- ログにAPIキーが出力されないこと
"""

import pytest
import os
from unittest.mock import patch
from reply_bot.api_key_manager import (
    APIKeyManager,
    load_api_keys,
    rotate_api_key,
    APIKeyError
)


class TestAPIKeyManager:
    """APIキー管理のテスト"""
    
    def test_load_from_env(self, monkeypatch):
        """環境変数からキー読み込み
        
        テスト観点:
        - os.getenvで環境変数を読み込める
        - 読み込んだ値が正しく返される
        """
        # Arrange
        monkeypatch.setenv("GOOGLE_API_KEY", "test_api_key_12345")
        manager = APIKeyManager()
        
        # Act
        api_key = manager.get_key("GOOGLE_API_KEY")
        
        # Assert
        assert api_key == "test_api_key_12345"
        print("✅ 環境変数読み込み成功")
    
    def test_missing_required_key(self):
        """必須キーが存在しない場合
        
        テスト観点:
        - required=Trueで呼び出した際、キーが無ければ例外
        """
        # Arrange
        manager = APIKeyManager()
        
        # Act & Assert
        with pytest.raises(APIKeyError, match="Required API key not found"):
            manager.get_key("NONEXISTENT_KEY", required=True)
        print("✅ 必須キー欠落検出: APIKeyError")
    
    def test_optional_key_returns_none(self):
        """任意キーが存在しない場合
        
        テスト観点:
        - required=Falseの場合、Noneを返す
        """
        # Arrange
        manager = APIKeyManager()
        
        # Act
        result = manager.get_key("OPTIONAL_KEY", required=False)
        
        # Assert
        assert result is None
        print("✅ 任意キー不在: None返却")
    
    def test_key_encryption(self):
        """APIキーの暗号化
        
        テスト観点:
        - 暗号化された値は元の値と異なる
        - 復号化すると元の値に戻る
        """
        # Arrange
        manager = APIKeyManager(encrypt=True)
        plain_key = "test_api_key_secret"
        
        # Act
        encrypted = manager.encrypt_key(plain_key)
        decrypted = manager.decrypt_key(encrypted)
        
        # Assert
        assert encrypted != plain_key
        assert decrypted == plain_key
        print(f"✅ 暗号化・復号化成功")
    
    def test_load_all_keys_from_env(self, monkeypatch):
        """全APIキー一括読み込み
        
        テスト観点:
        - 複数のAPIキーを一度に読み込める
        - 辞書形式で返される
        """
        # Arrange
        monkeypatch.setenv("GOOGLE_API_KEY", "google_key_123")
        monkeypatch.setenv("OPENAI_API_KEY", "openai_key_456")
        
        # Act
        keys = load_api_keys(["GOOGLE_API_KEY", "OPENAI_API_KEY"])
        
        # Assert
        assert keys["GOOGLE_API_KEY"] == "google_key_123"
        assert keys["OPENAI_API_KEY"] == "openai_key_456"
        print("✅ 全キー一括読み込み成功")
    
    def test_rotate_api_key(self, tmp_path):
        """APIキーローテーション
        
        テスト観点:
        - 古いキーを新しいキーに置き換える
        - 履歴が記録される
        """
        # Arrange
        key_file = tmp_path / "api_keys.json"
        
        # Act
        result = rotate_api_key(
            "GOOGLE_API_KEY",
            "new_key_789",
            key_file=str(key_file)
        )
        
        # Assert
        assert result is True
        assert key_file.exists()
        print("✅ キーローテーション成功")


class TestDotEnvLoading:
    ".envファイル読み込みのテスト"""
    
    def test_load_from_dotenv_file(self, tmp_path, monkeypatch):
        """.envファイルからキー読み込み
        
        テスト観点:
        - .envファイルが存在する場合、自動読み込み
        - python-dotenvライブラリが正しく機能
        """
        # Arrange
        env_file = tmp_path / ".env"
        env_file.write_text("TEST_API_KEY=from_dotenv_123\n")
        
        monkeypatch.chdir(tmp_path)
        
        # Act
        from dotenv import load_dotenv
        load_dotenv(env_file)
        
        manager = APIKeyManager()
        key = manager.get_key("TEST_API_KEY")
        
        # Assert
        assert key == "from_dotenv_123"
        print("✅ .envファイル読み込み成功")
```

#### **1-2. テスト実行（失敗確認）**

```bash
# テスト実行（Red段階）
pytest tests/unit/test_api_key_manager.py -v

# 期待される出力:
# ModuleNotFoundError: No module named 'reply_bot.api_key_manager'
# ✅ Red段階: 実装前なので失敗が正しい
```

---

### **Step 2: 最小実装（Green）**

**reply_bot/api_key_manager.py:**
```python
"""APIキー管理（TDDで段階的に実装）

セキュリティ設計:
1. 環境変数優先: os.environ経由で読み込み
2. .env対応: python-dotenvで.envファイルサポート
3. 暗号化: Fernet（AES-128）で暗号化保存
4. ログ保護: APIキーをログに出力しない
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)


class APIKeyError(Exception):
    """APIキー関連エラー"""
    pass


class APIKeyManager:
    """APIキー管理クラス
    
    環境変数からAPIキーを読み込み、必要に応じて暗号化します。
    
    Attributes:
        encrypt (bool): 暗号化機能を有効にするか
        _cipher (Fernet): 暗号化・復号化用オブジェクト
    
    Example:
        >>> import os
        >>> os.environ["GOOGLE_API_KEY"] = "test_key_123"
        >>> manager = APIKeyManager()
        >>> manager.get_key("GOOGLE_API_KEY")
        'test_key_123'
    """
    
    def __init__(self, encrypt: bool = False):
        """初期化
        
        Args:
            encrypt: True の場合、暗号化機能を有効化
        """
        self.encrypt = encrypt
        self._cipher = None
        
        if encrypt:
            # 暗号化キー生成（本番環境では環境変数から取得推奨）
            key = Fernet.generate_key()
            self._cipher = Fernet(key)
            logger.info("Encryption enabled for APIKeyManager")
    
    def get_key(self, key_name: str, required: bool = False) -> Optional[str]:
        """APIキー取得
        
        Args:
            key_name: 環境変数名
            required: Trueの場合、キーが無ければ例外発生
        
        Returns:
            APIキー（存在しない場合はNone）
        
        Raises:
            APIKeyError: requiredがTrueでキーが見つからない場合
        """
        value = os.getenv(key_name)
        
        if value is None and required:
            raise APIKeyError(f"Required API key not found: {key_name}")
        
        return value
    
    def encrypt_key(self, plain_key: str) -> str:
        """APIキー暗号化
        
        Args:
            plain_key: 平文APIキー
        
        Returns:
            暗号化されたキー（Base64エンコード）
        
        Raises:
            RuntimeError: 暗号化が無効化されている場合
        """
        if not self.encrypt or self._cipher is None:
            raise RuntimeError("Encryption is not enabled")
        
        encrypted = self._cipher.encrypt(plain_key.encode())
        return encrypted.decode()
    
    def decrypt_key(self, encrypted_key: str) -> str:
        """APIキー復号化
        
        Args:
            encrypted_key: 暗号化されたキー
        
        Returns:
            復号化された平文キー
        """
        if not self.encrypt or self._cipher is None:
            raise RuntimeError("Encryption is not enabled")
        
        decrypted = self._cipher.decrypt(encrypted_key.encode())
        return decrypted.decode()


def load_api_keys(key_names: List[str]) -> Dict[str, str]:
    """全APIキー一括読み込み
    
    Args:
        key_names: 読み込むキー名のリスト
    
    Returns:
        キー名: 値 の辞書（存在しないキーは含まれない）
    
    Example:
        >>> os.environ["KEY1"] = "value1"
        >>> os.environ["KEY2"] = "value2"
        >>> load_api_keys(["KEY1", "KEY2", "KEY3"])
        {'KEY1': 'value1', 'KEY2': 'value2'}
    """
    result = {}
    
    for key_name in key_names:
        value = os.getenv(key_name)
        if value is not None:
            result[key_name] = value
    
    logger.info(f"Loaded {len(result)}/{len(key_names)} API keys")
    return result


def rotate_api_key(
    key_name: str,
    new_value: str,
    key_file: str = "config/api_keys.json"
) -> bool:
    """APIキーローテーション
    
    Args:
        key_name: キー名
        new_value: 新しいキー値
        key_file: キー保存先ファイル
    
    Returns:
        成功したらTrue
    
    Note:
        本番環境ではAWS Secrets Managerなどを使用推奨
    """
    key_file_path = Path(key_file)
    key_file_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 既存データ読み込み
    data = {}
    if key_file_path.exists():
        data = json.loads(key_file_path.read_text())
    
    # キー更新
    data[key_name] = {
        "value": new_value,
        "rotated_at": datetime.now().isoformat()
    }
    
    # 保存
    key_file_path.write_text(json.dumps(data, indent=2))
    
    logger.info(f"API key rotated: {key_name}")
    return True
```

#### **2-2. 依存パッケージ追加**

```bash
# cryptography パッケージインストール
pip install cryptography python-dotenv

# requirements.txtに追加
echo "cryptography>=41.0.0" >> reply_bot/requirements.txt
echo "python-dotenv>=1.0.0" >> reply_bot/requirements.txt
```

#### **2-3. テスト実行（成功確認）**

```bash
# テスト実行（Green段階）
pytest tests/unit/test_api_key_manager.py -v

# 期待される出力:
# tests/unit/test_api_key_manager.py::TestAPIKeyManager::test_load_from_env PASSED
# tests/unit/test_api_key_manager.py::TestAPIKeyManager::test_missing_required_key PASSED
# tests/unit/test_api_key_manager.py::TestAPIKeyManager::test_key_encryption PASSED
# ... (全テスト成功)
#
# ======================== 7 passed in 0.22s ========================
```

---

### **Step 3: リファクタリング（Refactor）**

#### **3-1. ログ保護機能追加**

**reply_bot/api_key_manager.py（改善版）:**
```python
# （既存コードに追加）

class SensitiveDataFilter(logging.Filter):
    """ログからAPIキーを除外するフィルタ"""
    
    def filter(self, record):
        """ログレコードをフィルタリング
        
        Args:
            record: ログレコード
        
        Returns:
            フィルタ結果（常にTrue）
        
        Side Effects:
            record.msgからAPIキーらしき文字列をマスキング
        """
        if isinstance(record.msg, str):
            # APIキーパターンをマスキング
            # 例: AIzaSy... → API_KEY_***
            import re
            record.msg = re.sub(
                r'(AIza[A-Za-z0-9_-]{35})',
                'API_KEY_***',
                record.msg
            )
        return True


# ログフィルタ適用
logger.addFilter(SensitiveDataFilter())
```

---

## 🧪 Phase 3: 環境変数セキュリティ

### **Step 1: .envテンプレート生成**

**reply_bot/api_key_manager.py（機能追加）:**
```python
def generate_env_template(output_path: str = ".env.template") -> None:
    """.envテンプレートファイル生成
    
    Args:
        output_path: テンプレートファイルの保存先
    
    Example:
        >>> generate_env_template()
        # .env.templateが作成される
    """
    template = """# TwitterBot APIキー設定テンプレート
# このファイルをコピーして.envを作成してください
# 警告: .envファイルは絶対にGitにコミットしないこと

# Google Gemini API
GOOGLE_API_KEY=your_google_api_key_here

# OpenAI API（オプション）
OPENAI_API_KEY=your_openai_api_key_here

# Twitter API（将来的に使用予定）
# TWITTER_API_KEY=your_twitter_api_key_here
# TWITTER_API_SECRET=your_twitter_api_secret_here
"""
    
    Path(output_path).write_text(template)
    logger.info(f".env template created: {output_path}")
```

---

## ✅ 完了チェックリスト

```yaml
phase4_04a_completion:
  authentication:
    - [ ] ChromeSessionManager テスト成功（12テスト）
    - [ ] validate_session テスト成功（4テスト）
    - [ ] create_secure_profile テスト成功（1テスト）
    - [ ] プロファイル権限0o700確認
    - [ ] カバレッジ80%以上
  
  api_key_management:
    - [ ] APIKeyManager テスト成功（7テスト）
    - [ ] 環境変数読み込み確認
    - [ ] 暗号化・復号化テスト成功
    - [ ] .envファイル読み込み確認
    - [ ] カバレッジ75%以上
  
  security_validation:
    - [ ] ログにAPIキーが出力されないこと確認
    - [ ] banditセキュリティスキャン実施
    - [ ] 脆弱性ゼロ確認
  
  documentation:
    - [ ] 全関数にdocstring記述
    - [ ] セキュリティ注意事項明記
    - [ ] .env.template生成確認
  
  next_step:
    - [ ] Phase4_04bへ進む（データ保護・アクセス制御TDD）
```

---

**次のフェーズ:**  
[Phase4_04b_データ保護・アクセス制御TDD.md](12_Phase4_04b_データ保護・アクセス制御TDD.md)

---

**最終更新**: 2025-11-24
