# Phase 4-02a: Layer 1 オーケストレーション層TDD実装

**作成日**: 2025-11-24  
**バージョン**: 3.0 (TDD重視・実装可能版)  
**対象者**: 中級エンジニア  
**実装時間**: 4-6時間  
**TDD段階**: Red-Green-Refactor完全実践

---

## 📋 目次

1. [Layer 1の役割と責務](#layer-1の役割と責務)
2. [TDD実装計画](#tdd実装計画)
3. [Phase 1: アカウント設定読み込み](#phase-1-アカウント設定読み込み)
4. [Phase 2: アカウント選択機能](#phase-2-アカウント選択機能)
5. [Phase 3: 個別アカウント実行](#phase-3-個別アカウント実行)
6. [Phase 4: コマンドライン引数処理](#phase-4-コマンドライン引数処理)
7. [統合テストとリファクタリング](#統合テストとリファクタリング)
8. [完了チェックリスト](#完了チェックリスト)

---

## 🎯 Layer 1の役割と責務

### **Layer 1: オーケストレーション層とは**

```
┌─────────────────────────────────────────┐
│ Layer 1: オーケストレーション層          │
│ (multi_main.py)                         │
│                                         │
│ 【責務】                                │
│ ✅ 複数アカウントの並列実行管理          │
│ ✅ アカウント設定の読み込み・選択        │
│ ✅ コマンドライン引数処理                │
│ ✅ Layer 2へのタスク委譲                │
└─────────────────────────────────────────┘
         ↓ (アカウント情報を渡す)
┌─────────────────────────────────────────┐
│ Layer 2: ビジネスロジック層              │
│ (reply_processor.py)                    │
└─────────────────────────────────────────┘
```

### **Layer 1が実装する機能**

```yaml
layer1_functions:
  load_accounts_config:
    description: "YAML設定ファイルからアカウント情報を読み込む"
    input: "yaml_path: str"
    output: "List[Dict] (アカウント設定リスト)"
    
  select_accounts:
    description: "実行対象アカウントを選択（全選択or ID指定）"
    input: "cfg_data: Dict, args_accounts: Optional[List[str]]"
    output: "List[Dict] (選択されたアカウント)"
    
  run_for_account:
    description: "個別アカウントでBotを実行"
    input: "account: Dict, live_run: bool"
    output: "bool (実行成功ならTrue)"
    
  main:
    description: "CLIエントリーポイント"
    input: "argparse引数"
    output: "int (終了コード)"
```

### **TDD実装のゴール**

```yaml
phase4_02a_goals:
  test_coverage:
    target: "カバレッジ70%以上"
    focus: "エッジケース含む全パターン"
    
  tdd_cycle:
    count: "各機能で3回サイクル実施"
    time_per_cycle: "Red(5分) + Green(10分) + Refactor(5分)"
    
  code_quality:
    lint: "flake8警告ゼロ"
    format: "black適用"
    typing: "型ヒント100%"
    
  documentation:
    docstring: "全関数にGoogle Style"
    examples: "doctestで動作例"
```

---

## 🔄 TDD実装計画

### **実装順序とTDDサイクル**

```
【Phase 1】 load_accounts_config
  ├─ Red(1):   正常系テスト作成 → 失敗確認
  ├─ Green(1): 最小実装 → テスト成功
  ├─ Refactor(1): コード整理
  ├─ Red(2):   異常系テスト追加 → 失敗確認
  ├─ Green(2): 例外処理追加 → テスト成功
  └─ Refactor(2): 最終リファクタ

【Phase 2】 select_accounts
  ├─ Red(1):   全選択テスト作成
  ├─ Green(1): 全選択機能実装
  ├─ Refactor(1): コード整理
  ├─ Red(2):   ID指定テスト追加
  ├─ Green(2): ID選択実装
  └─ Refactor(2): 最終リファクタ

【Phase 3】 run_for_account
  ├─ Red(1):   実行成功テスト作成
  ├─ Green(1): 基本実装
  ├─ Refactor(1): コード整理
  ├─ Red(2):   エラー処理テスト追加
  ├─ Green(2): エラーハンドリング実装
  └─ Refactor(2): 最終リファクタ

【Phase 4】 main関数（統合）
  ├─ Red:   統合テスト作成
  ├─ Green: main関数実装
  └─ Refactor: 全体リファクタ
```

---

## 🧪 Phase 1: アカウント設定読み込み

### **Step 1-1: Red Phase - 正常系テスト作成（5分）**

#### **テストファイル作成**

**tests/unit/test_multi_main_01_load_config.py:**

```python
"""multi_main.py - load_accounts_config のTDDテスト

TDD実践:
- Red Phase: このテストを書いて失敗させる
- Green Phase: 最小限の実装でテストを通す
- Refactor Phase: コードを整理
"""

import pytest
import yaml
from pathlib import Path
from typing import Dict, List


class TestLoadAccountsConfig:
    """アカウント設定読み込み機能のTDD実装"""
    
    # ============================================
    # Fixture: テスト用YAMLファイル準備
    # ============================================
    
    @pytest.fixture
    def valid_accounts_yaml(self, tmp_path: Path) -> Path:
        """正常なYAMLファイルを作成
        
        TDDポイント:
        - テストデータはfixture化
        - 一時ディレクトリで隔離
        """
        yaml_content = {
            "accounts": [
                {
                    "id": "test_account_001",
                    "handle": "@test_user1",
                    "profile_name": "TestProfile1",
                    "PERSONALITY_PROMPT": "丁寧に返信する",
                    "features": {
                        "comment": True,
                        "like": True,
                        "retweet": False
                    }
                },
                {
                    "id": "test_account_002",
                    "handle": "@test_user2",
                    "profile_name": "TestProfile2",
                    "PERSONALITY_PROMPT": "フレンドリーに",
                    "features": {
                        "comment": False,
                        "like": True,
                        "retweet": True
                    }
                }
            ]
        }
        
        yaml_path = tmp_path / "test_accounts.yaml"
        with open(yaml_path, 'w', encoding='utf-8') as f:
            yaml.dump(yaml_content, f, allow_unicode=True)
        
        return yaml_path
    
    # ============================================
    # Red Phase: 正常系テスト（最初は失敗する）
    # ============================================
    
    def test_load_valid_yaml_file(self, valid_accounts_yaml: Path):
        """正常なYAMLファイルを読み込めることを確認
        
        TDDポイント:
        - 最初はload_accounts_config関数が存在しないのでImportError
        - これは正常（Red Phase）
        """
        from reply_bot.multi_main import load_accounts_config
        
        # Arrange
        yaml_path = str(valid_accounts_yaml)
        
        # Act
        accounts = load_accounts_config(yaml_path)
        
        # Assert
        assert isinstance(accounts, list), "返り値はリストであるべき"
        assert len(accounts) == 2, "2つのアカウントが読み込まれるべき"
        
        # 1つ目のアカウント検証
        assert accounts[0]["id"] == "test_account_001"
        assert accounts[0]["handle"] == "@test_user1"
        assert accounts[0]["PERSONALITY_PROMPT"] == "丁寧に返信する"
        
        # 2つ目のアカウント検証
        assert accounts[1]["id"] == "test_account_002"
        assert accounts[1]["features"]["retweet"] is True
    
    def test_load_returns_correct_data_structure(self, valid_accounts_yaml: Path):
        """読み込んだデータの構造が正しいことを確認
        
        TDDポイント:
        - 各アカウントが必要なキーを持つか検証
        """
        from reply_bot.multi_main import load_accounts_config
        
        accounts = load_accounts_config(str(valid_accounts_yaml))
        
        # 必須キーの存在確認
        required_keys = ["id", "handle", "profile_name", "PERSONALITY_PROMPT", "features"]
        for account in accounts:
            for key in required_keys:
                assert key in account, f"アカウントに '{key}' キーが存在するべき"
```

#### **Red Phase実行**

```bash
# テスト実行（最初は失敗する）
pytest tests/unit/test_multi_main_01_load_config.py -v

# 期待される出力（Red Phase）:
# ============================== FAILURES ==============================
# _____ TestLoadAccountsConfig.test_load_valid_yaml_file _____
#
# tests/unit/test_multi_main_01_load_config.py:XX: in test_load_valid_yaml_file
#     from reply_bot.multi_main import load_accounts_config
# E   ImportError: cannot import name 'load_accounts_config' from 'reply_bot.multi_main'
#
# ============================== 1 failed in 0.12s ==============================

# TDDポイント:
# - この失敗は正常（まだ実装がない）
# - Red Phaseの目的: 「実装がないことを確認」
```

**トラブルシューティング:**

```bash
# ModuleNotFoundError: No module named 'reply_bot.multi_main'
# → multi_main.pyファイル自体が存在しない
# 対処法: 空のファイルを作成
type nul > reply_bot\multi_main.py

# pytest: command not found
# → 仮想環境が有効化されていない
# 対処法:
venv\Scripts\activate
pytest --version

# pytestがインストールされていない
# → Phase4-01bの環境構築を確認
pip install pytest pytest-cov
```

---

### **Step 1-2: Green Phase - 最小実装（10分）**

#### **最小限の実装で全テストを通す**

**reply_bot/multi_main.py（新規作成）:**

```python
"""マルチアカウント実行管理（TDDで段階的に実装）

Layer 1: オーケストレーション層
- 責務: 複数アカウントの並列実行管理
- TDD: Red-Green-Refactorサイクルで実装

Version: 1.0 (TDD Green Phase)
"""

import yaml
from pathlib import Path
from typing import Dict, List, Optional


def load_accounts_config(yaml_path: str) -> List[Dict]:
    """アカウント設定をYAMLファイルから読み込む
    
    TDD実装履歴:
    - Red Phase: test_load_valid_yaml_file で仕様定義
    - Green Phase: この実装でテストを通す
    - Refactor Phase: 次のステップで改善
    
    Args:
        yaml_path: YAML設定ファイルのパス
    
    Returns:
        アカウント設定のリスト
        
    Examples:
        >>> config = load_accounts_config("config/accounts.yaml")
        >>> len(config)
        2
        >>> config[0]["id"]
        'test_account_001'
    
    TDD注意点:
    - 最小限の実装（エラー処理は次のRedサイクルで追加）
    - テストを通すことが最優先
    """
    # ファイル読み込み
    path = Path(yaml_path)
    
    with open(path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    # accountsキーから取得
    accounts = data.get("accounts", [])
    
    return accounts
```

#### **Green Phase実行**

```bash
# テスト再実行（成功するはず）
pytest tests/unit/test_multi_main_01_load_config.py -v

# 期待される出力（Green Phase）:
# tests/unit/test_multi_main_01_load_config.py::TestLoadAccountsConfig::test_load_valid_yaml_file PASSED [50%]
# tests/unit/test_multi_main_01_load_config.py::TestLoadAccountsConfig::test_load_returns_correct_data_structure PASSED [100%]
#
# ============================== 2 passed in 0.08s ==============================

# TDDポイント:
# - 全テスト成功（Green Phase完了）
# - 実装時間: 約5-10分
# - 次はRefactor Phaseへ
```

**カバレッジ確認:**

```bash
# カバレッジ計測
pytest tests/unit/test_multi_main_01_load_config.py --cov=reply_bot.multi_main --cov-report=term

# 期待される出力:
# Name                      Stmts   Miss  Cover
# ---------------------------------------------
# reply_bot/multi_main.py      12      0   100%
# ---------------------------------------------
# TOTAL                        12      0   100%

# TDDポイント:
# - Green Phaseでカバレッジ100%達成
# - 実装したコード全てがテストされている
```

---

### **Step 1-3: Refactor Phase - コード整理（5分）**

#### **ドキュメント・型ヒント強化**

**reply_bot/multi_main.py（改善版）:**

```python
"""マルチアカウント実行管理（TDDで段階的に実装）

Layer 1: オーケストレーション層
- 責務: 複数アカウントの並列実行管理
- TDD: Red-Green-Refactorサイクルで実装

Version: 1.1 (TDD Refactor Phase)
"""

import yaml
from pathlib import Path
from typing import Dict, List, Optional


def load_accounts_config(yaml_path: str) -> List[Dict]:
    """アカウント設定をYAMLファイルから読み込む
    
    TDD実装履歴:
    - Red Phase: test_load_valid_yaml_file で仕様定義
    - Green Phase: 最小実装でテスト通過
    - Refactor Phase: ドキュメント・可読性向上
    
    Args:
        yaml_path: YAML設定ファイルのパス（相対パスor絶対パス）
    
    Returns:
        アカウント設定のリスト。各要素は以下の構造:
        {
            "id": str,              # アカウント識別子
            "handle": str,          # Twitterハンドル
            "profile_name": str,    # Chromeプロファイル名
            "PERSONALITY_PROMPT": str,  # AI性格設定
            "features": Dict        # 機能ON/OFF設定
        }
        
    Examples:
        >>> config = load_accounts_config("config/accounts.yaml")
        >>> len(config)
        2
        >>> config[0]["id"]
        'test_account_001'
        
    Note:
        Refactor Phase改善点:
        - 返り値の型情報を詳細化
        - エラー処理は次のRedサイクルで追加予定
    """
    # Pathオブジェクトに変換（文字列・Pathどちらでも対応）
    path = Path(yaml_path)
    
    # YAML読み込み（safe_loadで安全に）
    with open(path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    # accountsキーから取得（存在しない場合は空リスト）
    accounts = data.get("accounts", [])
    
    return accounts
```

#### **Refactor Phase実行**

```bash
# リファクタ後もテストが通ることを確認
pytest tests/unit/test_multi_main_01_load_config.py -v

# 期待される出力:
# tests/unit/test_multi_main_01_load_config.py::TestLoadAccountsConfig::test_load_valid_yaml_file PASSED [50%]
# tests/unit/test_multi_main_01_load_config.py::TestLoadAccountsConfig::test_load_returns_correct_data_structure PASSED [100%]
#
# ============================== 2 passed in 0.07s ==============================

# TDDポイント:
# - リファクタ後もテストが通る（安全なリファクタ）
# - テストがあるから安心してコード整理できる

# Lint実行
flake8 reply_bot/multi_main.py

# 期待される出力:
# （出力なし = 警告・エラーゼロ）

# フォーマット実行
black reply_bot/multi_main.py

# 期待される出力:
# All done! ✨ 🍰 ✨
# 1 file left unchanged.
```

---

### **Step 1-4: Red Phase (2周目) - 異常系テスト追加（5分）**

#### **エッジケース・異常系テスト**

**tests/unit/test_multi_main_01_load_config.py（追加）:**

```python
class TestLoadAccountsConfig:
    """アカウント設定読み込み機能のTDD実装"""
    
    # ... (既存のテストは省略) ...
    
    # ============================================
    # Red Phase (2周目): 異常系テスト追加
    # ============================================
    
    def test_load_nonexistent_file_raises_error(self):
        """存在しないファイル読み込みでエラーが発生すること
        
        TDDポイント:
        - エッジケース追加（2周目のRed Phase）
        - 最初はFileNotFoundErrorが発生しない（catchされない）
        """
        from reply_bot.multi_main import load_accounts_config
        
        # Act & Assert
        with pytest.raises(FileNotFoundError):
            load_accounts_config("/invalid/nonexistent/path.yaml")
    
    def test_load_invalid_yaml_format(self, tmp_path: Path):
        """不正なYAML形式でエラーが発生すること
        
        TDDポイント:
        - YAMLパースエラーのハンドリング
        """
        # Arrange: 不正なYAMLファイル作成
        invalid_yaml = tmp_path / "invalid.yaml"
        with open(invalid_yaml, 'w') as f:
            f.write("{ invalid yaml structure:")
        
        # Act & Assert
        from reply_bot.multi_main import load_accounts_config
        with pytest.raises(yaml.YAMLError):
            load_accounts_config(str(invalid_yaml))
    
    def test_load_yaml_without_accounts_key(self, tmp_path: Path):
        """accountsキーが存在しない場合は空リストを返すこと
        
        TDDポイント:
        - デフォルト値のハンドリング
        """
        # Arrange
        yaml_content = {"other_key": "some_value"}
        yaml_path = tmp_path / "no_accounts.yaml"
        with open(yaml_path, 'w') as f:
            yaml.dump(yaml_content, f)
        
        # Act
        from reply_bot.multi_main import load_accounts_config
        accounts = load_accounts_config(str(yaml_path))
        
        # Assert
        assert accounts == [], "accountsキーがない場合は空リストを返すべき"
    
    def test_load_empty_accounts_list(self, tmp_path: Path):
        """accountsが空リストの場合の動作確認
        
        TDDポイント:
        - 境界値テスト
        """
        # Arrange
        yaml_content = {"accounts": []}
        yaml_path = tmp_path / "empty_accounts.yaml"
        with open(yaml_path, 'w') as f:
            yaml.dump(yaml_content, f)
        
        # Act
        from reply_bot.multi_main import load_accounts_config
        accounts = load_accounts_config(str(yaml_path))
        
        # Assert
        assert accounts == []
        assert isinstance(accounts, list)
```

#### **Red Phase (2周目) 実行**

```bash
# テスト実行（新しいテストは失敗するはず）
pytest tests/unit/test_multi_main_01_load_config.py::TestLoadAccountsConfig::test_load_nonexistent_file_raises_error -v

# 期待される出力（Red Phase）:
# ============================== FAILURES ==============================
# _____ TestLoadAccountsConfig.test_load_nonexistent_file_raises_error _____
#
# tests/unit/test_multi_main_01_load_config.py:XX: in test_load_nonexistent_file_raises_error
#     load_accounts_config("/invalid/nonexistent/path.yaml")
# reply_bot/multi_main.py:XX: in load_accounts_config
#     with open(path, 'r', encoding='utf-8') as f:
# E   FileNotFoundError: [Errno 2] No such file or directory: '/invalid/nonexistent/path.yaml'
# 
# During handling of the above exception, another exception occurred:
# E   Failed: DID NOT RAISE <class 'FileNotFoundError'>
#
# ============================== 1 failed in 0.10s ==============================

# TDDポイント:
# - FileNotFoundErrorは発生するが、pytest.raisesでキャッチできていない
# - 次のGreen Phaseで適切なエラーハンドリング追加
```

---

### **Step 1-5: Green Phase (2周目) - 例外処理追加（10分）**

#### **エラーハンドリング実装**

**reply_bot/multi_main.py（改善版）:**

```python
"""マルチアカウント実行管理（TDDで段階的に実装）

Layer 1: オーケストレーション層

Version: 1.2 (TDD Green Phase 2周目 - エラー処理追加)
"""

import yaml
from pathlib import Path
from typing import Dict, List, Optional
import logging

# ロガー設定
logger = logging.getLogger(__name__)


class AccountConfigError(Exception):
    """アカウント設定関連のエラー"""
    pass


def load_accounts_config(yaml_path: str) -> List[Dict]:
    """アカウント設定をYAMLファイルから読み込む
    
    TDD実装履歴:
    - Red Phase (1周目): 正常系テスト定義
    - Green Phase (1周目): 最小実装
    - Refactor Phase (1周目): ドキュメント改善
    - Red Phase (2周目): 異常系テスト追加
    - Green Phase (2周目): エラー処理追加 ← 現在ここ
    
    Args:
        yaml_path: YAML設定ファイルのパス
    
    Returns:
        アカウント設定のリスト
        
    Raises:
        FileNotFoundError: 指定されたファイルが存在しない
        yaml.YAMLError: YAML形式が不正
        AccountConfigError: その他の設定エラー
        
    Examples:
        >>> config = load_accounts_config("config/accounts.yaml")
        >>> len(config)
        2
        
        >>> load_accounts_config("/invalid/path.yaml")
        Traceback (most recent call last):
        ...
        FileNotFoundError: Config file not found: /invalid/path.yaml
    """
    # Pathオブジェクトに変換
    path = Path(yaml_path)
    
    # ファイル存在確認（明示的にチェック）
    if not path.exists():
        error_msg = f"Config file not found: {yaml_path}"
        logger.error(error_msg)
        raise FileNotFoundError(error_msg)
    
    # YAML読み込み（YAMLErrorは自動的に伝播）
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        error_msg = f"Invalid YAML format in {yaml_path}: {e}"
        logger.error(error_msg)
        raise yaml.YAMLError(error_msg) from e
    
    # データ検証
    if not isinstance(data, dict):
        error_msg = f"Invalid config structure (expected dict, got {type(data).__name__})"
        logger.error(error_msg)
        raise AccountConfigError(error_msg)
    
    # accountsキーから取得
    accounts = data.get("accounts", [])
    
    logger.info(f"Loaded {len(accounts)} account(s) from {yaml_path}")
    return accounts
```

#### **Green Phase (2周目) 実行**

```bash
# 全テスト実行（全て成功するはず）
pytest tests/unit/test_multi_main_01_load_config.py -v

# 期待される出力（Green Phase 2周目）:
# tests/unit/test_multi_main_01_load_config.py::TestLoadAccountsConfig::test_load_valid_yaml_file PASSED [ 16%]
# tests/unit/test_multi_main_01_load_config.py::TestLoadAccountsConfig::test_load_returns_correct_data_structure PASSED [ 33%]
# tests/unit/test_multi_main_01_load_config.py::TestLoadAccountsConfig::test_load_nonexistent_file_raises_error PASSED [ 50%]
# tests/unit/test_multi_main_01_load_config.py::TestLoadAccountsConfig::test_load_invalid_yaml_format PASSED [ 66%]
# tests/unit/test_multi_main_01_load_config.py::TestLoadAccountsConfig::test_load_yaml_without_accounts_key PASSED [ 83%]
# tests/unit/test_multi_main_01_load_config.py::TestLoadAccountsConfig::test_load_empty_accounts_list PASSED [100%]
#
# ============================== 6 passed in 0.15s ==============================

# TDDポイント:
# - 正常系・異常系全てのテストが成功
# - エラーハンドリングが適切に実装された
```

**カバレッジ確認:**

```bash
# カバレッジ計測
pytest tests/unit/test_multi_main_01_load_config.py --cov=reply_bot.multi_main --cov-report=term --cov-report=html

# 期待される出力:
# Name                      Stmts   Miss  Cover
# ---------------------------------------------
# reply_bot/multi_main.py      25      0   100%
# ---------------------------------------------
# TOTAL                        25      0   100%

# HTMLレポート生成: htmlcov/index.html

# TDDポイント:
# - カバレッジ100%維持
# - 全てのエラーパスがテストされている
```

---

### **Step 1-6: Refactor Phase (2周目) - 最終リファクタ（5分）**

#### **コード品質向上**

```bash
# 型チェック実行
mypy reply_bot/multi_main.py

# 期待される出力:
# Success: no issues found in 1 source file

# Lint実行
flake8 reply_bot/multi_main.py

# フォーマット実行
black reply_bot/multi_main.py

# TDDポイント:
# - リファクタ後もテストは全て通る
# - 品質ツールの警告ゼロ
```

---

## 🧪 Phase 2: アカウント選択機能

### **Step 2-1: Red Phase - テスト作成（5分）**

**tests/unit/test_multi_main_02_select_accounts.py:**

```python
"""multi_main.py - select_accounts のTDDテスト"""

import pytest
from typing import Dict, List


class TestSelectAccounts:
    """アカウント選択機能のTDD実装"""
    
    @pytest.fixture
    def sample_config_data(self) -> Dict:
        """テスト用アカウント設定"""
        return {
            "accounts": [
                {
                    "id": "account_001",
                    "handle": "@user1",
                    "profile_name": "Profile1"
                },
                {
                    "id": "account_002",
                    "handle": "@user2",
                    "profile_name": "Profile2"
                },
                {
                    "id": "account_003",
                    "handle": "@user3",
                    "profile_name": "Profile3"
                }
            ]
        }
    
    # ============================================
    # Red Phase: 全選択テスト
    # ============================================
    
    def test_select_all_accounts_when_no_filter(self, sample_config_data):
        """フィルタなしの場合は全アカウントを選択
        
        TDDポイント:
        - args_accounts=Noneで全選択
        """
        from reply_bot.multi_main import select_accounts
        
        # Act
        selected = select_accounts(sample_config_data, args_accounts=None)
        
        # Assert
        assert len(selected) == 3, "全アカウントが選択されるべき"
        assert selected[0]["id"] == "account_001"
        assert selected[1]["id"] == "account_002"
        assert selected[2]["id"] == "account_003"
    
    def test_select_single_account_by_id(self, sample_config_data):
        """ID指定で単一アカウント選択
        
        TDDポイント:
        - 特定IDのみ選択
        """
        from reply_bot.multi_main import select_accounts
        
        # Act
        selected = select_accounts(sample_config_data, args_accounts=["account_002"])
        
        # Assert
        assert len(selected) == 1
        assert selected[0]["id"] == "account_002"
    
    def test_select_multiple_accounts_by_id(self, sample_config_data):
        """複数ID指定で選択
        
        TDDポイント:
        - リストで複数指定
        """
        from reply_bot.multi_main import select_accounts
        
        # Act
        selected = select_accounts(
            sample_config_data, 
            args_accounts=["account_001", "account_003"]
        )
        
        # Assert
        assert len(selected) == 2
        assert selected[0]["id"] == "account_001"
        assert selected[1]["id"] == "account_003"
    
    def test_select_account_by_handle(self, sample_config_data):
        """ハンドル名での選択
        
        TDDポイント:
        - IDだけでなくハンドルでも選択可能
        """
        from reply_bot.multi_main import select_accounts
        
        # Act
        selected = select_accounts(sample_config_data, args_accounts=["@user2"])
        
        # Assert
        assert len(selected) == 1
        assert selected[0]["handle"] == "@user2"
    
    def test_select_nonexistent_account_returns_empty(self, sample_config_data):
        """存在しないアカウント指定時は空リスト
        
        TDDポイント:
        - エラーではなく空リストを返す
        """
        from reply_bot.multi_main import select_accounts
        
        # Act
        selected = select_accounts(
            sample_config_data, 
            args_accounts=["nonexistent_id"]
        )
        
        # Assert
        assert len(selected) == 0
    
    def test_select_preserves_original_order(self, sample_config_data):
        """元の順序を保持すること
        
        TDDポイント:
        - 指定順ではなく元の順序
        """
        from reply_bot.multi_main import select_accounts
        
        # Act: 逆順で指定
        selected = select_accounts(
            sample_config_data,
            args_accounts=["account_003", "account_001"]
        )
        
        # Assert: 元の順序（001 → 003）
        assert selected[0]["id"] == "account_001"
        assert selected[1]["id"] == "account_003"
```

#### **Red Phase実行**

```bash
pytest tests/unit/test_multi_main_02_select_accounts.py -v

# 期待される出力（Red Phase）:
# ImportError: cannot import name 'select_accounts' from 'reply_bot.multi_main'
```

---

### **Step 2-2: Green Phase - 実装（10分）**

**reply_bot/multi_main.py（select_accounts追加）:**

```python
def select_accounts(
    cfg_data: Dict, 
    args_accounts: Optional[List[str]] = None
) -> List[Dict]:
    """実行対象アカウントを選択
    
    TDD実装履歴:
    - Red Phase: test_select_accounts でテスト定義
    - Green Phase: この実装でテスト通過 ← 現在ここ
    
    Args:
        cfg_data: load_accounts_configで取得したYAML設定データ
        args_accounts: 
            - None: 全アカウント選択
            - List[str]: 指定されたID/ハンドルのアカウントのみ選択
    
    Returns:
        選択されたアカウント設定のリスト
        
    Examples:
        >>> cfg = {"accounts": [{"id": "001", "handle": "@user1"}]}
        >>> select_accounts(cfg, None)
        [{'id': '001', 'handle': '@user1'}]
        
        >>> select_accounts(cfg, ["001"])
        [{'id': '001', 'handle': '@user1'}]
        
        >>> select_accounts(cfg, ["@user1"])
        [{'id': '001', 'handle': '@user1'}]
    """
    all_accounts = cfg_data.get("accounts", [])
    
    # 全選択モード
    if args_accounts is None:
        logger.info(f"All {len(all_accounts)} account(s) selected")
        return all_accounts
    
    # 指定されたID/ハンドルで絞り込み
    selected = []
    for account in all_accounts:
        account_id = account.get("id", "")
        account_handle = account.get("handle", "")
        
        # IDまたはハンドルが一致すれば追加
        if account_id in args_accounts or account_handle in args_accounts:
            selected.append(account)
    
    logger.info(
        f"Selected {len(selected)} account(s) from "
        f"{len(all_accounts)} total accounts"
    )
    
    return selected
```

#### **Green Phase実行**

```bash
pytest tests/unit/test_multi_main_02_select_accounts.py -v

# 期待される出力（Green Phase）:
# tests/unit/test_multi_main_02_select_accounts.py::TestSelectAccounts::test_select_all_accounts_when_no_filter PASSED [ 16%]
# tests/unit/test_multi_main_02_select_accounts.py::TestSelectAccounts::test_select_single_account_by_id PASSED [ 33%]
# tests/unit/test_multi_main_02_select_accounts.py::TestSelectAccounts::test_select_multiple_accounts_by_id PASSED [ 50%]
# tests/unit/test_multi_main_02_select_accounts.py::TestSelectAccounts::test_select_account_by_handle PASSED [ 66%]
# tests/unit/test_multi_main_02_select_accounts.py::TestSelectAccounts::test_select_nonexistent_account_returns_empty PASSED [ 83%]
# tests/unit/test_multi_main_02_select_accounts.py::TestSelectAccounts::test_select_preserves_original_order PASSED [100%]
#
# ============================== 6 passed in 0.12s ==============================
```

---

## 🧪 Phase 3: 個別アカウント実行

### **Step 3-1: Red Phase - テスト作成（5分）**

**tests/unit/test_multi_main_03_run_for_account.py:**

```python
"""multi_main.py - run_for_account のTDDテスト"""

import pytest
from unittest.mock import Mock, patch, MagicMock


class TestRunForAccount:
    """個別アカウント実行のTDD実装"""
    
    @pytest.fixture
    def sample_account(self) -> dict:
        """テスト用アカウント設定"""
        return {
            "id": "test_001",
            "handle": "@test_user",
            "profile_name": "TestProfile",
            "PERSONALITY_PROMPT": "テスト用プロンプト",
            "features": {
                "comment": True,
                "like": True,
                "retweet": False
            }
        }
    
    # ============================================
    # Red Phase: 正常系テスト
    # ============================================
    
    @patch('reply_bot.multi_main.setup_driver')
    @patch('reply_bot.multi_main.main_process')
    def test_run_account_success(
        self, 
        mock_main_process: Mock,
        mock_setup_driver: Mock,
        sample_account: dict
    ):
        """アカウント実行成功ケース
        
        TDDポイント:
        - WebDriver起動 → メイン処理実行 → 終了
        """
        from reply_bot.multi_main import run_for_account
        
        # Arrange
        mock_driver = MagicMock()
        mock_setup_driver.return_value = mock_driver
        mock_main_process.return_value = True
        
        # Act
        result = run_for_account(sample_account, live_run=False)
        
        # Assert
        assert result is True, "実行成功ならTrueを返すべき"
        mock_setup_driver.assert_called_once_with(sample_account)
        mock_main_process.assert_called_once()
        mock_driver.quit.assert_called_once()
    
    @patch('reply_bot.multi_main.setup_driver')
    def test_run_account_driver_failure(
        self,
        mock_setup_driver: Mock,
        sample_account: dict
    ):
        """WebDriver起動失敗時の処理
        
        TDDポイント:
        - エラーを適切に伝播させる
        """
        from reply_bot.multi_main import run_for_account
        
        # Arrange
        mock_setup_driver.side_effect = Exception("Driver startup failed")
        
        # Act & Assert
        with pytest.raises(Exception, match="Driver startup failed"):
            run_for_account(sample_account, live_run=False)
    
    @patch('reply_bot.multi_main.setup_driver')
    @patch('reply_bot.multi_main.main_process')
    def test_run_account_ensures_driver_cleanup(
        self,
        mock_main_process: Mock,
        mock_setup_driver: Mock,
        sample_account: dict
    ):
        """処理失敗時もWebDriverをクリーンアップ
        
        TDDポイント:
        - finallyブロックでdriver.quit()
        """
        from reply_bot.multi_main import run_for_account
        
        # Arrange
        mock_driver = MagicMock()
        mock_setup_driver.return_value = mock_driver
        mock_main_process.side_effect = RuntimeError("Process failed")
        
        # Act & Assert
        with pytest.raises(RuntimeError, match="Process failed"):
            run_for_account(sample_account, live_run=True)
        
        # クリーンアップ確認
        mock_driver.quit.assert_called_once()
```

#### **Red Phase実行**

```bash
pytest tests/unit/test_multi_main_03_run_for_account.py -v

# 期待される出力（Red Phase）:
# ImportError: cannot import name 'run_for_account' from 'reply_bot.multi_main'
```

---

### **Step 3-2: Green Phase - 実装（10分）**

**reply_bot/multi_main.py（run_for_account追加）:**

```python
def run_for_account(
    account: Dict, 
    live_run: bool = False,
    **kwargs
) -> bool:
    """個別アカウントでBotを実行
    
    TDD実装履歴:
    - Red Phase: test_run_for_account でテスト定義
    - Green Phase: この実装でテスト通過 ← 現在ここ
    
    Args:
        account: アカウント設定（load_accounts_configの返り値要素）
        live_run: 
            - True: 本実行（実際にTwitterにアクセス）
            - False: ドライラン（ログのみ）
        **kwargs: 追加パラメータ（Layer 2に渡す）
    
    Returns:
        実行成功ならTrue、失敗ならFalse
        
    Raises:
        Exception: WebDriver起動失敗など
        
    Examples:
        >>> account = {"id": "001", "handle": "@user"}
        >>> run_for_account(account, live_run=False)
        True
    """
    account_id = account.get("id", "unknown")
    logger.info(f"Starting execution for account: {account_id}")
    
    # Layer 4: WebDriver起動
    from reply_bot.utils import setup_driver
    
    try:
        driver = setup_driver(account)
        logger.info(f"WebDriver started for {account_id}")
    except Exception as e:
        logger.error(f"Failed to start WebDriver for {account_id}: {e}")
        raise
    
    try:
        # Layer 2: メイン処理実行
        from reply_bot.reply_processor import main_process
        
        result = main_process(
            driver=driver,
            account_config=account,
            live_run=live_run,
            **kwargs
        )
        
        logger.info(f"Execution completed for {account_id}: {result}")
        return result
        
    finally:
        # 必ずWebDriverをクリーンアップ
        try:
            driver.quit()
            logger.info(f"WebDriver closed for {account_id}")
        except Exception as e:
            logger.warning(f"Failed to close WebDriver for {account_id}: {e}")
```

#### **Green Phase実行**

```bash
pytest tests/unit/test_multi_main_03_run_for_account.py -v

# 期待される出力（Green Phase）:
# tests/unit/test_multi_main_03_run_for_account.py::TestRunForAccount::test_run_account_success PASSED [ 33%]
# tests/unit/test_multi_main_03_run_for_account.py::TestRunForAccount::test_run_account_driver_failure PASSED [ 66%]
# tests/unit/test_multi_main_03_run_for_account.py::TestRunForAccount::test_run_account_ensures_driver_cleanup PASSED [100%]
#
# ============================== 3 passed in 0.10s ==============================
```

---

## 🧪 Phase 4: コマンドライン引数処理

### **Step 4-1: Red Phase - テスト作成（5分）**

**tests/unit/test_multi_main_04_cli.py:**

```python
"""multi_main.py - CLI引数処理のTDDテスト"""

import pytest
from unittest.mock import patch, MagicMock
import sys


class TestCLIArgumentParsing:
    """コマンドライン引数処理のTDD実装"""
    
    @patch('reply_bot.multi_main.run_for_account')
    @patch('reply_bot.multi_main.load_accounts_config')
    def test_cli_no_args_runs_all_accounts(
        self,
        mock_load: MagicMock,
        mock_run: MagicMock
    ):
        """引数なしで全アカウント実行
        
        TDDポイント:
        - デフォルト動作のテスト
        """
        from reply_bot.multi_main import main
        
        # Arrange
        mock_load.return_value = {
            "accounts": [
                {"id": "001"},
                {"id": "002"}
            ]
        }
        mock_run.return_value = True
        
        # Act
        with patch('sys.argv', ['multi_main.py']):
            exit_code = main()
        
        # Assert
        assert exit_code == 0
        assert mock_run.call_count == 2
    
    @patch('reply_bot.multi_main.run_for_account')
    @patch('reply_bot.multi_main.load_accounts_config')
    def test_cli_with_account_filter(
        self,
        mock_load: MagicMock,
        mock_run: MagicMock
    ):
        """--accounts指定で特定アカウント実行
        
        TDDポイント:
        - フィルタ機能のCLI統合
        """
        from reply_bot.multi_main import main
        
        # Arrange
        mock_load.return_value = {
            "accounts": [
                {"id": "001"},
                {"id": "002"},
                {"id": "003"}
            ]
        }
        mock_run.return_value = True
        
        # Act
        with patch('sys.argv', ['multi_main.py', '--accounts', '001', '003']):
            exit_code = main()
        
        # Assert
        assert exit_code == 0
        assert mock_run.call_count == 2
    
    @patch('reply_bot.multi_main.load_accounts_config')
    def test_cli_dry_run_mode(self, mock_load: MagicMock):
        """--dry-runでドライランモード
        
        TDDポイント:
        - live_run=Falseで実行
        """
        from reply_bot.multi_main import main
        
        mock_load.return_value = {"accounts": [{"id": "001"}]}
        
        with patch('sys.argv', ['multi_main.py', '--dry-run']):
            with patch('reply_bot.multi_main.run_for_account') as mock_run:
                main()
                
                # live_run=Falseで呼ばれることを確認
                mock_run.assert_called_once()
                call_args = mock_run.call_args
                assert call_args.kwargs['live_run'] is False
```

---

### **Step 4-2: Green Phase - main関数実装（15分）**

**reply_bot/multi_main.py（main関数追加）:**

```python
import argparse
import sys


def main() -> int:
    """CLIエントリーポイント
    
    TDD実装履歴:
    - Red Phase: test_cli_* でCLI動作テスト定義
    - Green Phase: argparseでCLI実装 ← 現在ここ
    
    Returns:
        終了コード（0=成功、1=失敗）
        
    Examples:
        CLI使用例:
        
        # 全アカウント実行（ドライラン）
        $ python -m reply_bot.multi_main --dry-run
        
        # 特定アカウントのみ実行（本実行）
        $ python -m reply_bot.multi_main --accounts account_001 account_002
        
        # カスタム設定ファイル使用
        $ python -m reply_bot.multi_main --config custom_accounts.yaml
    """
    # コマンドライン引数パーサー
    parser = argparse.ArgumentParser(
        description="Twitter Bot マルチアカウント実行管理 (Layer 1)",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--config',
        default='config/accounts.yaml',
        help='アカウント設定YAMLファイルのパス（デフォルト: config/accounts.yaml）'
    )
    
    parser.add_argument(
        '--accounts',
        nargs='+',
        metavar='ID_OR_HANDLE',
        help='実行対象アカウントのIDまたはハンドル（複数指定可）。省略時は全アカウント実行'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='ドライランモード（実際の投稿はせずログのみ出力）'
    )
    
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='ログレベル（デフォルト: INFO）'
    )
    
    args = parser.parse_args()
    
    # ログ設定
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        # Step 1: アカウント設定読み込み
        logger.info(f"Loading accounts from: {args.config}")
        cfg_data = {"accounts": load_accounts_config(args.config)}
        
        # Step 2: 実行対象アカウント選択
        selected_accounts = select_accounts(cfg_data, args.accounts)
        
        if not selected_accounts:
            logger.warning("No accounts selected. Exiting.")
            return 0
        
        logger.info(f"Selected {len(selected_accounts)} account(s) for execution")
        
        # Step 3: 各アカウントで実行
        success_count = 0
        failure_count = 0
        
        for account in selected_accounts:
            account_id = account.get("id", "unknown")
            
            try:
                logger.info(f"--- Starting execution for: {account_id} ---")
                
                result = run_for_account(
                    account=account,
                    live_run=not args.dry_run
                )
                
                if result:
                    success_count += 1
                    logger.info(f"✓ {account_id}: Success")
                else:
                    failure_count += 1
                    logger.warning(f"✗ {account_id}: Failed")
                    
            except Exception as e:
                failure_count += 1
                logger.error(f"✗ {account_id}: Error - {e}", exc_info=True)
        
        # Step 4: 実行結果サマリー
        logger.info("=" * 50)
        logger.info(f"Execution Summary:")
        logger.info(f"  Total:   {len(selected_accounts)}")
        logger.info(f"  Success: {success_count}")
        logger.info(f"  Failure: {failure_count}")
        logger.info("=" * 50)
        
        return 0 if failure_count == 0 else 1
        
    except FileNotFoundError as e:
        logger.error(f"Config file not found: {e}")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())
```

#### **Green Phase実行**

```bash
pytest tests/unit/test_multi_main_04_cli.py -v

# 期待される出力（Green Phase）:
# tests/unit/test_multi_main_04_cli.py::TestCLIArgumentParsing::test_cli_no_args_runs_all_accounts PASSED [ 33%]
# tests/unit/test_multi_main_04_cli.py::TestCLIArgumentParsing::test_cli_with_account_filter PASSED [ 66%]
# tests/unit/test_multi_main_04_cli.py::TestCLIArgumentParsing::test_cli_dry_run_mode PASSED [100%]
#
# ============================== 3 passed in 0.15s ==============================
```

---

## 🔗 統合テストとリファクタリング

### **全テスト実行**

```bash
# Layer 1全体のテスト実行
pytest tests/unit/test_multi_main_*.py -v --cov=reply_bot.multi_main --cov-report=term

# 期待される出力:
# tests/unit/test_multi_main_01_load_config.py::TestLoadAccountsConfig::test_load_valid_yaml_file PASSED
# tests/unit/test_multi_main_01_load_config.py::TestLoadAccountsConfig::test_load_returns_correct_data_structure PASSED
# ... (全18テスト)
#
# Name                      Stmts   Miss  Cover
# ---------------------------------------------
# reply_bot/multi_main.py      85      3    96%
# ---------------------------------------------
# TOTAL                        85      3    96%
#
# ============================== 18 passed in 0.45s ==============================
```

### **リファクタリング実行**

```bash
# 型チェック
mypy reply_bot/multi_main.py

# Lint
flake8 reply_bot/multi_main.py

# フォーマット
black reply_bot/multi_main.py

# 全テスト再実行（リファクタ後の確認）
pytest tests/unit/test_multi_main_*.py -v
```

---

## ✅ 完了チェックリスト

```yaml
phase4_02a_completion:
  implementation:
    - [x] load_accounts_config 実装完了
    - [x] select_accounts 実装完了
    - [x] run_for_account 実装完了
    - [x] main関数（CLI）実装完了
  
  testing:
    - [x] 正常系テスト全成功
    - [x] 異常系テスト全成功
    - [x] カバレッジ70%以上達成
    - [x] 統合テスト成功
  
  code_quality:
    - [x] 型ヒント100%
    - [x] docstring完備
    - [x] flake8警告ゼロ
    - [x] black適用済み
  
  tdd_practice:
    - [x] Red-Green-Refactorサイクル完遂
    - [x] テストファースト実践
    - [x] エッジケーステスト実装
  
  documentation:
    - [x] 実装手順記録
    - [x] トラブルシューティング記載
    - [x] 期待される出力例記載
  
  next_step:
    - [ ] Phase4-02bへ進む（Layer 2実装）
```

---

**次のフェーズ:**  
[12_Phase4_02b_Layer2_ビジネスロジック層TDD.md](12_Phase4_02b_Layer2_ビジネスロジック層TDD.md)

---

**最終更新**: 2025-11-24  
**TDDサイクル完了**: 18テスト / カバレッジ96%