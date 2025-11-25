# Phase 4-01: 環境構築とTDD準備

**作成日**: 2025-11-24  
**バージョン**: 2.0 (TDD対応版)  
**対象者**: 新人エンジニア・中級エンジニア  
**実装時間**: 4-6時間

---

## 📋 目次

1. [概要](#概要)
2. [TDD開発環境構築](#tdd開発環境構築)
3. [テストフレームワーク導入](#テストフレームワーク導入)
4. [開発フロー確立](#開発フロー確立)
5. [初回テスト実行](#初回テスト実行)

---

## 🎯 概要

このフェーズでは、**テスト駆動開発（TDD）**を実践するための環境を構築します。

### **TDD開発サイクル (Red-Green-Refactor)**

```
┌─────────────────────────────────────┐
│  1. Red: テストを書く（失敗する）    │
│        ↓                            │
│  2. Green: 最小限の実装で通す        │
│        ↓                            │
│  3. Refactor: コードをリファクタ     │
│        ↓                            │
│  4. 次の機能へ（1に戻る）            │
└─────────────────────────────────────┘
```

### **Phase 4-01の目標**

- ✅ Python仮想環境構築
- ✅ pytest + coverage導入
- ✅ pre-commit hook設定
- ✅ IDE設定（VSCode）
- ✅ サンプルテスト実行

---

## 🔧 TDD開発環境構築

### **Step 1: Python仮想環境作成（5分）**

```bash
# プロジェクトディレクトリに移動
cd c:/GenerativeAI/TwitterBot_Nexus_02

# 仮想環境作成
python -m venv venv

# 仮想環境有効化（Windows）
venv\Scripts\activate

# Python/pipバージョン確認
python --version  # Python 3.10以上推奨
pip --version
```

**期待出力:**
```
Python 3.11.5
pip 23.2.1
```

---

### **Step 2: 既存依存パッケージインストール（10分）**

**⚠️ 重要: reply_bot/__init__.py作成**

```bash
# まず、reply_botをPythonパッケージとして認識させる
type nul > reply_bot/__init__.py
type nul > shared_modules/__init__.py

# 既存requirements.txt確認
cat reply_bot/requirements.txt

# 依存パッケージインストール
pip install -r reply_bot/requirements.txt

# インストール確認
pip list | grep -E "selenium|google-generativeai|beautifulsoup4"
```

**期待出力:**
```
beautifulsoup4           4.12.2
google-generativeai      0.3.1
selenium                 4.15.2
```

---

### **Step 3: テスト用パッケージインストール（5分）**

```bash
# pytest環境構築
pip install pytest pytest-cov pytest-xdist pytest-timeout pytest-mock

# コード品質ツール
pip install black flake8 mypy pylint

# pre-commit hooks
pip install pre-commit

# requirements-dev.txt作成
cat > requirements-dev.txt << 'EOF'
# テストフレームワーク
pytest==7.4.3
pytest-cov==4.1.0
pytest-xdist==3.5.0
pytest-timeout==2.2.0
pytest-mock==3.12.0

# 【必須】コード品質ツール（常時使用）
black==23.12.0
flake8==6.1.0
mypy==1.7.1

# オプションツール
pre-commit==3.6.0
EOF

# インストール
pip install -r requirements-dev.txt

# 【重要】VSCodeでblack/flake8を自動実行設定（後述）
```

---

## 📦 テストフレームワーク導入

### **⚠️ 重要: コーディングルール遵守**

**プロジェクトルール: [`docs/01_コーディング開発ガイド.md`](docs/01_コーディング開発ガイド.md:1) より**

> - **全コードは必ずblack/flake8でフォーマット・検証してからコミット**
> - **保存時に自動フォーマット実行（VSCode設定必須）**
> - **Lint警告がある状態でのコミットは禁止**

このルールを遵守するため、以下の設定を**必ず実施**してください。


### **Step 4: pytestディレクトリ構造作成（10分）**

```bash
# テストディレクトリ構造作成
mkdir -p tests/{unit,integration,e2e}
mkdir -p tests/fixtures
mkdir -p tests/mocks

# __init__.py作成（Pythonパッケージ化）
# Windowsの場合:
type nul > tests/__init__.py
type nul > tests/unit/__init__.py
type nul > tests/integration/__init__.py
type nul > tests/e2e/__init__.py

# Linux/Macの場合:
# touch tests/__init__.py
# touch tests/unit/__init__.py
# touch tests/integration/__init__.py
# touch tests/e2e/__init__.py
```

**期待ディレクトリ構造:**
```
TwitterBot_Nexus_02/
├── tests/
│   ├── __init__.py
│   ├── conftest.py           # pytest共通設定
│   ├── unit/                 # ユニットテスト
│   │   ├── __init__.py
│   │   ├── test_config.py
│   │   ├── test_utils.py
│   │   └── test_text_processing.py
│   ├── integration/          # 統合テスト
│   │   ├── __init__.py
│   │   ├── test_webdriver.py
│   │   └── test_ai_integration.py
│   ├── e2e/                  # E2Eテスト
│   │   ├── __init__.py
│   │   └── test_full_workflow.py
│   ├── fixtures/             # テストデータ
│   │   ├── sample_accounts.yaml
│   │   └── sample_tweets.json
│   └── mocks/                # モックオブジェクト
│       ├── mock_driver.py
│       └── mock_ai_response.py
```

---

### **Step 5: pytest.ini設定（5分）**

```bash
# pytest.ini作成
cat > pytest.ini << 'EOF'
[pytest]
# テストディレクトリ指定
testpaths = tests

# テストファイル命名規則
python_files = test_*.py
python_classes = Test*
python_functions = test_*

# カバレッジ設定
addopts = 
    --cov=reply_bot
    --cov=shared_modules
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=70
    --verbose
    --strict-markers
    --tb=short
    --maxfail=5

# 並列実行設定
# -n auto: CPU数に応じて自動並列化
# addopts に追加する場合: -n auto

# タイムアウト設定（長時間実行テスト防止）
timeout = 300
timeout_method = thread

# マーカー定義
markers =
    slow: 実行時間が長いテスト
    webdriver: WebDriverを使用するテスト
    ai: AI APIを使用するテスト
    integration: 統合テスト
    e2e: エンドツーエンドテスト
    unit: ユニットテスト

# ログ出力設定
log_cli = true
log_cli_level = INFO
log_file = tests/logs/pytest.log
log_file_level = DEBUG

# 警告フィルタ
filterwarnings =
    ignore::DeprecationWarning
    ignore::PendingDeprecationWarning
EOF
```

---

### **Step 6: conftest.py作成（15分）**

**tests/conftest.py:**
```python
"""pytest共通設定・フィクスチャ定義"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, MagicMock
import yaml

# プロジェクトルートをPythonパスに追加
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


# =====================================
# セッションスコープ フィクスチャ
# =====================================

@pytest.fixture(scope="session")
def project_root():
    """プロジェクトルートディレクトリパス"""
    return PROJECT_ROOT


@pytest.fixture(scope="session")
def test_data_dir(project_root):
    """テストデータディレクトリ"""
    return project_root / "tests" / "fixtures"


# =====================================
# 設定ファイル フィクスチャ
# =====================================

@pytest.fixture
def sample_account_config():
    """サンプルアカウント設定（YAML）"""
    return {
        "id": "test_account_001",
        "handle": "test_user",
        "browser": {
            "user_data_dir": "profile/test_user",
            "headless": True
        },
        "features": {
            "like": True,
            "retweet": False,
            "comment": True,
            "bookmark": True,
            "tweet": True
        },
        "PERSONALITY_PROMPT": "あなたはテスト用のAIアシスタントです。",
        "reply_prompt": "簡潔に返信してください。",
        "policies": {
            "sources": ["@test_target"],
            "reply_num_max": 5,
            "per_target": {}
        },
        "rate_limits": {
            "like_per_hour": 10,
            "min_interval_seconds": 60
        }
    }


@pytest.fixture
def mock_accounts_yaml(tmp_path, sample_account_config):
    """一時的なaccounts.yamlファイル作成"""
    yaml_file = tmp_path / "accounts.yaml"
    
    data = {
        "accounts": [
            sample_account_config,
            {
                **sample_account_config,
                "id": "test_account_002",
                "handle": "test_user2"
            }
        ]
    }
    
    with open(yaml_file, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, allow_unicode=True)
    
    return yaml_file


# =====================================
# WebDriver モック フィクスチャ
# =====================================

@pytest.fixture
def mock_webdriver():
    """Selenium WebDriverのモック"""
    driver = MagicMock()
    
    # 基本メソッドのモック
    driver.get = Mock()
    driver.quit = Mock()
    driver.find_element = Mock()
    driver.find_elements = Mock(return_value=[])
    driver.current_url = "https://twitter.com/home"
    driver.title = "Twitter"
    
    # ページソース
    driver.page_source = "<html><body>Mock Page</body></html>"
    
    return driver


@pytest.fixture
def mock_chrome_profile_manager():
    """ChromeProfileManagerのモック"""
    manager = MagicMock()
    
    manager.create_profile = Mock(return_value=True)
    manager.acquire_lock = Mock(return_value=True)
    manager.release_lock = Mock(return_value=True)
    manager.launch_chrome = Mock()
    
    return manager


# =====================================
# AI API モック フィクスチャ
# =====================================

@pytest.fixture
def mock_gemini_model():
    """Google Gemini APIのモック"""
    model = MagicMock()
    
    # generate_content メソッドのモック
    response = MagicMock()
    response.text = "これはAIからのテスト返信です。"
    
    model.generate_content = Mock(return_value=response)
    
    return model


@pytest.fixture
def mock_ai_response():
    """AI応答データのサンプル"""
    return {
        "text": "これはテスト返信です。",
        "usage": {
            "prompt_tokens": 50,
            "completion_tokens": 20,
            "total_tokens": 70
        },
        "quality_score": 0.85
    }


# =====================================
# データベース・キャッシュ フィクスチャ
# =====================================

@pytest.fixture
def temp_cache_dir(tmp_path):
    """一時キャッシュディレクトリ"""
    cache_dir = tmp_path / "cache"
    cache_dir.mkdir()
    return cache_dir


@pytest.fixture
def greeting_tracker_mock(temp_cache_dir):
    """greeting_tracker.pyのモック"""
    from datetime import datetime
    
    cache_file = temp_cache_dir / "greeting_tracker_test.json"
    
    return {
        "cache_file": cache_file,
        "last_greetings": {
            "@test_user": datetime.now().isoformat()
        },
        "daily_limits": {
            "2025-11-24": 5
        }
    }


# =====================================
# ログ設定 フィクスチャ
# =====================================

@pytest.fixture
def test_logger():
    """テスト用ロガー"""
    import logging
    
    logger = logging.getLogger("test_logger")
    logger.setLevel(logging.DEBUG)
    
    # コンソールハンドラ
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    
    logger.addHandler(handler)
    
    return logger


# =====================================
# テスト実行前後のフック
# =====================================

@pytest.fixture(autouse=True)
def reset_environment():
    """各テスト実行前に環境をリセット"""
    # テスト前処理
    yield
    # テスト後処理（クリーンアップ）
    pass


def pytest_configure(config):
    """pytest起動時の設定"""
    import os
    
    # ログディレクトリ作成
    log_dir = PROJECT_ROOT / "tests" / "logs"
    log_dir.mkdir(exist_ok=True)
    
    # 環境変数設定（テスト用）
    os.environ["TESTING"] = "1"
    os.environ["GOOGLE_API_KEY"] = "test_api_key_dummy"


def pytest_sessionstart(session):
    """テストセッション開始時の処理"""
    print("\n" + "=" * 70)
    print("TwitterBot_Nexus_02 - TDD Test Suite")
    print("=" * 70)


def pytest_sessionfinish(session, exitstatus):
    """テストセッション終了時の処理"""
    print("\n" + "=" * 70)
    print(f"Test session finished (Exit status: {exitstatus})")
    print("=" * 70)
```

---

## 🧪 開発フロー確立

### **Step 7: サンプルテスト作成（TDDデモ）（20分）**

**tests/unit/test_sample_tdd_demo.py:**
```python
"""TDD実践デモ: 簡単な機能を段階的に実装"""

import pytest


# =====================================
# Red-Green-Refactor サイクル デモ
# =====================================

class TestTweetTextCleaner:
    """ツイートテキストクリーニング機能のTDD実装デモ"""
    
    # ============ STEP 1: Red（失敗するテストを書く） ============
    
    def test_remove_urls_from_text(self):
        """URLを除去する機能（最初は実装がないので失敗）"""
        from reply_bot.utils import clean_tweet_text
        
        # Arrange（準備）
        input_text = "これは素晴らしい記事です https://example.com/article"
        expected_output = "これは素晴らしい記事です"
        
        # Act（実行）
        result = clean_tweet_text(input_text)
        
        # Assert（検証）
        assert result == expected_output
    
    def test_remove_mentions_from_text(self):
        """メンションを除去する機能"""
        from reply_bot.utils import clean_tweet_text
        
        input_text = "@user1 @user2 素晴らしい投稿ですね！"
        expected_output = "素晴らしい投稿ですね！"
        
        result = clean_tweet_text(input_text, remove_mentions=True)
        assert result == expected_output
    
    def test_normalize_whitespace(self):
        """連続する空白を正規化"""
        from reply_bot.utils import clean_tweet_text
        
        input_text = "これは    テスト   です"
        expected_output = "これは テスト です"
        
        result = clean_tweet_text(input_text)
        assert result == expected_output
    
    
    # ============ STEP 2: Green（最小限の実装） ============
    # → reply_bot/utils.py に clean_tweet_text() 関数を実装
    
    # ============ STEP 3: Refactor（リファクタリング） ============
    # → コードを整理・最適化


# =====================================
# パラメータ化テスト（複数ケース一括）
# =====================================

class TestAccountConfigValidator:
    """アカウント設定検証のパラメータ化テスト"""
    
    @pytest.mark.parametrize("config,expected_valid", [
        # 有効なケース
        ({"id": "test001", "handle": "user1"}, True),
        ({"id": "test002", "handle": "user_name_123"}, True),
        
        # 無効なケース
        ({"id": "", "handle": "user1"}, False),  # ID空
        ({"id": "test001", "handle": ""}, False),  # handle空
        ({"id": "test001", "handle": "user@invalid"}, False),  # 無効文字
        ({"handle": "user1"}, False),  # idフィールドなし
    ])
    def test_validate_account_config(self, config, expected_valid):
        """アカウント設定の妥当性検証（パラメータ化）"""
        from reply_bot.config import validate_account_config
        
        is_valid = validate_account_config(config)
        assert is_valid == expected_valid


# =====================================
# モックを使ったテスト
# =====================================

class TestWebDriverStabilizer:
    """WebDriver安定化機能のモックテスト"""
    
    def test_chrome_startup_with_retry(self, mock_webdriver, mocker):
        """Chrome起動リトライ機能のテスト"""
        from reply_bot.webdriver_stabilizer import stabilize_chrome_startup
        
        # モック設定: 最初2回失敗、3回目成功
        mock_chrome_init = mocker.patch(
            'selenium.webdriver.Chrome',
            side_effect=[
                Exception("Connection refused"),  # 1回目失敗
                Exception("Timeout"),  # 2回目失敗
                mock_webdriver  # 3回目成功
            ]
        )
        
        # 実行
        driver = stabilize_chrome_startup(max_retries=3)
        
        # 検証
        assert driver == mock_webdriver
        assert mock_chrome_init.call_count == 3
    
    def test_chrome_startup_failure_exceeds_retries(self, mocker):
        """リトライ上限超過時の例外発生テスト"""
        from reply_bot.webdriver_stabilizer import stabilize_chrome_startup
        
        # モック設定: 常に失敗
        mocker.patch(
            'selenium.webdriver.Chrome',
            side_effect=Exception("Persistent failure")
        )
        
        # 例外が発生することを確認
        with pytest.raises(RuntimeError, match="Failed to start Chrome"):
            stabilize_chrome_startup(max_retries=2)


# =====================================
# フィクスチャを使ったテスト
# =====================================

class TestYAMLConfigLoader:
    """YAML設定読み込みのテスト"""
    
    def test_load_accounts_from_yaml(self, mock_accounts_yaml):
        """YAMLファイルからアカウント設定を読み込む"""
        from reply_bot.config import load_accounts_config
        
        # 実行
        accounts = load_accounts_config(str(mock_accounts_yaml))
        
        # 検証
        assert len(accounts) == 2
        assert accounts[0]["id"] == "test_account_001"
        assert accounts[0]["handle"] == "test_user"
        assert accounts[1]["id"] == "test_account_002"
    
    def test_yaml_file_not_found(self):
        """存在しないYAMLファイル読み込み時のエラー"""
        from reply_bot.config import load_accounts_config
        
        with pytest.raises(FileNotFoundError):
            load_accounts_config("/non/existent/path.yaml")


# =====================================
# マーカーを使った分類
# =====================================

@pytest.mark.slow
@pytest.mark.ai
class TestGeminiAPIIntegration:
    """Gemini API統合テスト（実行時間長・API使用）"""
    
    def test_generate_reply_with_real_api(self, mock_gemini_model):
        """実際のGemini APIで返信生成（スキップ可）"""
        pytest.skip("実際のAPI呼び出しは手動実行時のみ")
        
        # 実装例（実際には実行されない）
        # response = gemini_model.generate_content("こんにちは")
        # assert len(response.text) > 0
```

---

## ✅ 初回テスト実行

### **Step 8: 実装ファイル作成（Greenフェーズ）（30分）**

テストを通すための最小限の実装を作成：

**reply_bot/utils.py（追加）:**
```python
"""ユーティリティ関数（TDDで段階的に実装）"""

import re


def clean_tweet_text(text: str, remove_mentions: bool = False) -> str:
    """ツイートテキストをクリーニング
    
    Args:
        text: 元のテキスト
        remove_mentions: メンションを除去するか
    
    Returns:
        クリーニング済みテキスト
    """
    # URLを除去
    text = re.sub(r'https?://\S+', '', text)
    
    # メンションを除去（オプション）
    if remove_mentions:
        text = re.sub(r'@\w+', '', text)
    
    # 連続する空白を正規化
    text = re.sub(r'\s+', ' ', text)
    
    # 前後の空白を削除
    return text.strip()
```

**reply_bot/config.py（追加）:**
```python
"""設定ファイル管理（TDDで段階的に実装）"""

import yaml
from pathlib import Path
from typing import Dict, List


def validate_account_config(config: Dict) -> bool:
    """アカウント設定の妥当性検証
    
    Args:
        config: アカウント設定辞書
    
    Returns:
        設定が有効ならTrue
    """
    # 必須フィールドチェック
    if "id" not in config or not config["id"]:
        return False
    
    if "handle" not in config or not config["handle"]:
        return False
    
    # handle形式チェック（英数字・アンダースコアのみ）
    handle = config["handle"]
    if not re.match(r'^[a-zA-Z0-9_]+$', handle):
        return False
    
    return True


def load_accounts_config(yaml_path: str) -> List[Dict]:
    """YAMLファイルからアカウント設定を読み込む
    
    Args:
        yaml_path: YAMLファイルパス
    
    Returns:
        アカウント設定リスト
    
    Raises:
        FileNotFoundError: ファイルが存在しない
    """
    path = Path(yaml_path)
    
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {yaml_path}")
    
    with open(path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    return data.get("accounts", [])


import re  # 追加忘れ防止
```

**reply_bot/webdriver_stabilizer.py（追加）:**
```python
"""WebDriver安定化機能（TDDで段階的に実装）"""

import time
from selenium import webdriver
from selenium.common.exceptions import WebDriverException


def stabilize_chrome_startup(max_retries: int = 3, retry_delay: float = 2.0):
    """Chrome起動を安定化（リトライ機能付き）
    
    Args:
        max_retries: 最大リトライ回数
        retry_delay: リトライ間隔（秒）
    
    Returns:
        WebDriverインスタンス
    
    Raises:
        RuntimeError: リトライ上限超過
    """
    last_exception = None
    
    for attempt in range(1, max_retries + 1):
        try:
            driver = webdriver.Chrome()
            return driver
        except WebDriverException as e:
            last_exception = e
            if attempt < max_retries:
                time.sleep(retry_delay)
            continue
    
    raise RuntimeError(
        f"Failed to start Chrome after {max_retries} attempts: {last_exception}"
    )
```

---

### **Step 9: テスト実行（20分）**

```bash
# 全テスト実行
pytest

# カバレッジレポート付き
pytest --cov=reply_bot --cov-report=html

# 特定のテストファイルのみ
pytest tests/unit/test_sample_tdd_demo.py

# 特定のテストクラスのみ
pytest tests/unit/test_sample_tdd_demo.py::TestTweetTextCleaner

# 特定のテストメソッドのみ
pytest tests/unit/test_sample_tdd_demo.py::TestTweetTextCleaner::test_remove_urls_from_text

# マーカー別実行（slowテストをスキップ）
pytest -m "not slow"

# 並列実行（高速化）
pytest -n auto

# 詳細出力
pytest -vv
```

**期待出力:**
```
============================== test session starts ==============================
platform win32 -- Python 3.11.5, pytest-7.4.3
rootdir: c:\GenerativeAI\TwitterBot_Nexus_02
configfile: pytest.ini
plugins: cov-4.1.0, xdist-3.5.0
collected 12 items

tests/unit/test_sample_tdd_demo.py::TestTweetTextCleaner::test_remove_urls_from_text PASSED [  8%]
tests/unit/test_sample_tdd_demo.py::TestTweetTextCleaner::test_remove_mentions_from_text PASSED [ 16%]
tests/unit/test_sample_tdd_demo.py::TestTweetTextCleaner::test_normalize_whitespace PASSED [ 25%]
tests/unit/test_sample_tdd_demo.py::TestAccountConfigValidator::test_validate_account_config[config0-True] PASSED [ 33%]
...

============================== 12 passed in 2.53s ===============================

----------- coverage: platform win32, python 3.11.5 -----------
Name                                Stmts   Miss  Cover   Missing
-----------------------------------------------------------------
reply_bot/config.py                    25      2    92%   45-46
reply_bot/utils.py                     15      0   100%
reply_bot/webdriver_stabilizer.py      18      3    83%   32-34
-----------------------------------------------------------------
TOTAL                                  58      5    91%
```

---

## 📊 開発フロー確立

### **【必須】VSCode設定（settings.json）**

**プロジェクトルートに `.vscode/settings.json` を配置:**

```json
{
  // ========================================
  // テスト実行設定
  // ========================================
  "python.testing.pytestEnabled": true,
  "python.testing.unittestEnabled": false,
  "python.testing.pytestArgs": [
    "tests"
  ],
  
  // ========================================
  // 【必須】Lint設定（常時実行）
  // ========================================
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "python.linting.flake8Args": [
    "--max-line-length=100",
    "--ignore=E203,W503"
  ],
  "python.linting.lintOnSave": true,
  
  // ========================================
  // 【必須】フォーマット設定（保存時自動実行）
  // ========================================
  "python.formatting.provider": "black",
  "python.formatting.blackArgs": [
    "--line-length=100"
  ],
  "editor.formatOnSave": true,
  "editor.formatOnPaste": false,
  "editor.formatOnType": false,
  
  // ========================================
  // エディタ設定
  // ========================================
  "editor.rulers": [100],
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  },
  
  // ========================================
  // ファイル除外設定
  // ========================================
  "files.exclude": {
    "**/__pycache__": true,
    "**/.pytest_cache": true,
    "**/*.pyc": true,
    "**/.mypy_cache": true,
    "**/.coverage": true,
    "**/htmlcov": true
  },
  
  // ========================================
  // ファイル監視除外（パフォーマンス向上）
  // ========================================
  "files.watcherExclude": {
    "**/.git/**": true,
    "**/venv/**": true,
    "**/node_modules/**": true,
    "**/__pycache__/**": true
  }
}
```

**設定ファイル作成:**
```bash
# .vscodeディレクトリ作成
mkdir -p .vscode

# settings.json作成（上記内容をコピー）
# または自動生成:
cat > .vscode/settings.json << 'EOF'
{
  "python.testing.pytestEnabled": true,
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "python.linting.lintOnSave": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "editor.rulers": [100]
}
EOF
```

### **【推奨】flake8設定（.flake8）**

```bash
# プロジェクトルートに.flake8作成
cat > .flake8 << 'EOF'
[flake8]
max-line-length = 100
ignore = E203, W503
exclude =
    .git,
    __pycache__,
    venv,
    .venv,
    build,
    dist,
    *.egg-info,
    .pytest_cache,
    .mypy_cache
per-file-ignores =
    __init__.py:F401
EOF
```

### **【推奨】pyproject.toml（black設定）**

```bash
# プロジェクトルートにpyproject.toml作成
cat > pyproject.toml << 'EOF'
[tool.black]
line-length = 100
target-version = ['py311']
include = '\.pyi?$'
extend-exclude = '''
/(
  # directories
  \.eggs
  | \.git
  | \.hg
  | \.mypy_cache
  | \.tox
  | \.venv
  | venv
  | _build
  | buck-out
  | build
  | dist
)/
'''
EOF
```

### **【必須】Lint実行確認**

**保存時に自動実行されることを確認:**

```bash
# テストファイル作成
cat > test_lint.py << 'EOF'
def bad_function(  ):
    x=1+2  # スペース不足（flake8警告）
    return x
EOF

# VSCodeでファイルを開く
code test_lint.py

# → 保存時に自動的にblackがフォーマット
# → flake8警告が表示される
```

**手動Lint実行:**

```bash
# black実行（全ファイル）
black reply_bot/ shared_modules/ tests/

# flake8実行（全ファイル）
flake8 reply_bot/ shared_modules/ tests/

# 特定ファイルのみ
black reply_bot/config.py
flake8 reply_bot/config.py
```

### **オプション: pre-commit hooks設定**

**※これは任意です。重要なのは常時Lintを実行することです。**

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.12.0
    hooks:
      - id: black
        language_version: python3.11

  - repo: https://github.com/pycqa/flake8
    rev: 6.1.0
    hooks:
      - id: flake8
        args: ['--max-line-length=100', '--ignore=E203,W503']
```

```bash
# インストール（オプション）
pre-commit install
```

---

## ✅ 完了チェックリスト

```yaml
phase4_01_completion:
  environment:
    - [x] Python仮想環境作成
    - [x] requirements.txt インストール
    - [x] requirements-dev.txt インストール
  
  testing_framework:
    - [x] pytest.ini 設定
    - [x] conftest.py 作成
    - [x] テストディレクトリ構造作成
  
  sample_implementation:
    - [x] サンプルテスト作成
    - [x] 最小実装作成（Green）
    - [x] テスト実行成功
  
  quality_tools:
    - [x] black インストール
    - [x] flake8 インストール
    - [x] pre-commit hooks 設定
  
  next_step:
    - [ ] 補足資料確認（12_Phase4_01_環境構築とTDD準備_補足.md）
    - [ ] Phase4_02へ進む（アーキテクチャ層TDD実装）
```

---

**次のフェーズ:**  
[Phase4_02_アーキテクチャ層TDD実装.md](12_Phase4_02_アーキテクチャ層TDD実装.md) へ進んでください。

---

**最終更新**: 2025-11-24