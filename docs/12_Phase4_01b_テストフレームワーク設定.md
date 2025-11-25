# Phase 4-01b: テストフレームワーク設定（TDD準備）

**作成日**: 2025-11-24  
**バージョン**: 3.0 (TDD重視・実装可能版)  
**対象者**: 新人エンジニア・中級エンジニア  
**実装時間**: 1.5-2時間  
**TDD段階**: Red-Green-Refactorサイクル準備

---

## 📋 目次

1. [pytest設定の重要性](#pytest設定の重要性)
2. [pytest.ini詳細設定](#pytestini詳細設定)
3. [conftest.py作成](#conftestpy作成)
4. [フィクスチャ設計](#フィクスチャ設計)
5. [設定完了確認](#設定完了確認)

---

## 🎯 pytest設定の重要性

### **なぜpytest設定が重要なのか**

```
【TDD開発サイクルとpytest】
┌─────────────────────────────────────────┐
│ 1. Red: テストを書く（失敗させる）       │ ← pytest実行で失敗確認
│        ↓                                │
│ 2. Green: 最小限の実装で通す             │ ← pytest実行で成功確認
│        ↓                                │
│ 3. Refactor: コードをリファクタ          │ ← pytest実行で回帰確認
│        ↓                                │
│ 4. 次の機能へ（1に戻る）                 │ ← pytestが高速実行
└─────────────────────────────────────────┘

pytest設定 = TDDサイクルの効率化
```

**pytest設定のゴール:**

```yaml
pytest_configuration_goals:
  speed:
    target: "テスト実行時間 < 5秒"
    reason: "TDDサイクルを高速化"
    
  clarity:
    target: "エラーメッセージが明確"
    reason: "失敗原因を即座に特定"
    
  coverage:
    target: "カバレッジ70%以上"
    reason: "TDDでの品質保証"
    
  automation:
    target: "自動テスト検出・実行"
    reason: "手動操作を最小化"
```

---

## ⚙️ pytest.ini詳細設定

### **Step 1: pytest.ini作成（10分）**

#### **1-1. pytest.ini基本構造**

```bash
# プロジェクトルートにpytest.ini作成
# 以下の内容をコピペ
```

**pytest.ini (完全版):**

```ini
[pytest]
# ========================================
# テストディレクトリ指定
# ========================================
testpaths = tests

# ========================================
# テストファイル/クラス/関数の命名規則
# ========================================
python_files = test_*.py
python_classes = Test*
python_functions = test_*

# ========================================
# カバレッジ設定（TDD品質保証の中心）
# ========================================
addopts = 
    # カバレッジ測定対象
    --cov=reply_bot
    --cov=shared_modules
    
    # カバレッジレポート形式
    --cov-report=html
    --cov-report=term-missing
    
    # カバレッジ目標（70%未満で失敗）
    --cov-fail-under=70
    
    # テスト実行詳細度
    --verbose
    
    # マーカー厳格モード（未定義マーカーをエラー扱い）
    --strict-markers
    
    # トレースバック表示形式（短縮版）
    --tb=short
    
    # 最大失敗数（5回失敗で中断）
    --maxfail=5

# ========================================
# 並列実行設定（高速化）
# ========================================
# 並列実行を有効化する場合:
# addopts に以下を追加:
#     -n auto
# または、実行時に: pytest -n auto

# ========================================
# タイムアウト設定（無限ループ防止）
# ========================================
timeout = 300
timeout_method = thread

# ========================================
# マーカー定義（テスト分類）
# ========================================
markers =
    # 実行時間による分類
    slow: 実行時間が長いテスト（5秒以上）
    fast: 実行時間が短いテスト（1秒未満）
    
    # 依存関係による分類
    webdriver: WebDriverを使用するテスト
    ai: AI APIを使用するテスト
    network: ネットワーク通信を使用するテスト
    
    # テストレベル分類
    unit: ユニットテスト（単体テスト）
    integration: 統合テスト
    e2e: エンドツーエンドテスト
    smoke: スモークテスト（基本動作確認）
    
    # 開発段階分類
    wip: 作業中（Work In Progress）
    skip: スキップするテスト

# ========================================
# ログ出力設定
# ========================================
log_cli = true
log_cli_level = INFO
log_file = tests/logs/pytest.log
log_file_level = DEBUG
log_file_format = %(asctime)s [%(levelname)s] %(message)s
log_file_date_format = %Y-%m-%d %H:%M:%S

# ========================================
# 警告フィルタ
# ========================================
filterwarnings =
    ignore::DeprecationWarning
    ignore::PendingDeprecationWarning
    # 特定の警告のみ表示する場合:
    # error::UserWarning

# ========================================
# プラグイン設定
# ========================================
# カスタムプラグインの読み込み
# pytest_plugins = tests.plugins.custom_plugin

# ========================================
# テスト収集設定
# ========================================
norecursedirs = .git __pycache__ .pytest_cache .mypy_cache venv node_modules
```

#### **1-2. pytest.ini作成実行**

```bash
# Windowsコマンドプロンプトで実行
(
echo [pytest]
echo testpaths = tests
echo python_files = test_*.py
echo python_classes = Test*
echo python_functions = test_*
echo.
echo addopts = 
echo     --cov=reply_bot
echo     --cov=shared_modules
echo     --cov-report=html
echo     --cov-report=term-missing
echo     --cov-fail-under=70
echo     --verbose
echo     --strict-markers
echo     --tb=short
echo     --maxfail=5
echo.
echo timeout = 300
echo timeout_method = thread
echo.
echo markers =
echo     slow: 実行時間が長いテスト
echo     webdriver: WebDriverを使用するテスト
echo     ai: AI APIを使用するテスト
echo     integration: 統合テスト
echo     e2e: エンドツーエンドテスト
echo     unit: ユニットテスト
echo.
echo log_cli = true
echo log_cli_level = INFO
echo log_file = tests/logs/pytest.log
echo log_file_level = DEBUG
echo.
echo filterwarnings =
echo     ignore::DeprecationWarning
echo     ignore::PendingDeprecationWarning
) > pytest.ini

# 作成確認
type pytest.ini
```

#### **1-3. pytest.ini動作確認**

```bash
# pytest設定確認
pytest --markers

# 期待出力:
# @pytest.mark.slow: 実行時間が長いテスト
# @pytest.mark.webdriver: WebDriverを使用するテスト
# @pytest.mark.ai: AI APIを使用するテスト
# ...

# pytestヘルプ確認
pytest -h | findstr "cov"

# 期待出力:
# --cov=SOURCE
# --cov-report=TYPE
# --cov-fail-under=MIN
```

**トラブルシューティング:**

```bash
# マーカーが認識されない
# エラー例: "PytestUnknownMarkWarning: Unknown pytest.mark.slow"
# 対処法: pytest.ini のmarkers セクション確認

# カバレッジが測定されない
# エラー例: "No data to report"
# 対処法: pytest-covインストール確認
pip show pytest-cov

# 設定が反映されない
# → pytest.iniの場所確認（プロジェクトルート）
where pytest.ini
# 期待: c:\GenerativeAI\TwitterBot_Nexus_02\pytest.ini
```

---

## 🧩 conftest.py作成

### **Step 2: conftest.py基本構造（15分）**

#### **2-1. conftest.pyの役割**

```yaml
conftest_py_purpose:
  shared_fixtures:
    description: "全テストで共有するフィクスチャ定義"
    examples: ["mock_webdriver", "test_database", "sample_config"]
    
  pytest_hooks:
    description: "pytestの動作をカスタマイズ"
    examples: ["pytest_configure", "pytest_sessionstart"]
    
  test_utilities:
    description: "テスト用ヘルパー関数"
    examples: ["create_temp_file", "setup_test_env"]

conftest_py_location:
  tests/conftest.py: "全テスト共通"
  tests/unit/conftest.py: "ユニットテスト専用"
  tests/integration/conftest.py: "統合テスト専用"
```

#### **2-2. tests/conftest.py作成**

**tests/conftest.py (完全版):**

```python
"""pytest共通設定・フィクスチャ定義

TDD開発において、繰り返し使用するモック・テストデータを
効率的に管理するためのフィクスチャを提供します。
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
import yaml
from datetime import datetime

# =====================================
# プロジェクトパス設定
# =====================================

# プロジェクトルートをPythonパスに追加
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


# =====================================
# セッションスコープ フィクスチャ
# （テストセッション全体で1回だけ作成）
# =====================================

@pytest.fixture(scope="session")
def project_root():
    """プロジェクトルートディレクトリパス
    
    使用例:
        def test_config_loading(project_root):
            config_path = project_root / "config" / "accounts.yaml"
            assert config_path.exists()
    """
    return PROJECT_ROOT


@pytest.fixture(scope="session")
def test_data_dir(project_root):
    """テストデータディレクトリ
    
    使用例:
        def test_load_sample_data(test_data_dir):
            sample_file = test_data_dir / "sample_tweets.json"
            with open(sample_file) as f:
                data = json.load(f)
    """
    return project_root / "tests" / "fixtures"


# =====================================
# 設定ファイル フィクスチャ
# =====================================

@pytest.fixture
def sample_account_config():
    """サンプルアカウント設定（YAML形式）
    
    TDDでのテストデータとして使用。
    実際のaccounts.yamlの構造を模倣。
    
    使用例:
        def test_validate_config(sample_account_config):
            assert "id" in sample_account_config
            assert "handle" in sample_account_config
    """
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
    """一時的なaccounts.yamlファイル作成
    
    TDDでYAML読み込みテストを行う際に使用。
    tmp_path は pytestが自動的に作成する一時ディレクトリ。
    
    使用例:
        def test_load_accounts(mock_accounts_yaml):
            accounts = load_accounts_config(str(mock_accounts_yaml))
            assert len(accounts) == 2
    """
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
    """Selenium WebDriverのモック
    
    TDDでWebDriver操作をテストする際に使用。
    実際のブラウザを起動せずにテスト可能。
    
    使用例:
        def test_navigate(mock_webdriver):
            mock_webdriver.get("https://twitter.com")
            mock_webdriver.get.assert_called_once()
    """
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
    
    # ウィンドウハンドル
    driver.window_handles = ["CDwindow-1234"]
    driver.current_window_handle = "CDwindow-1234"
    
    return driver


@pytest.fixture
def mock_chrome_profile_manager():
    """ChromeProfileManagerのモック
    
    TDDでChromeプロファイル管理をテストする際に使用。
    
    使用例:
        def test_profile_lock(mock_chrome_profile_manager):
            result = mock_chrome_profile_manager.acquire_lock("profile1")
            assert result is True
    """
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
    """Google Gemini APIのモック
    
    TDDでAI応答生成をテストする際に使用。
    実際のAPI呼び出しを行わずにテスト可能。
    
    使用例:
        def test_generate_reply(mock_gemini_model):
            response = mock_gemini_model.generate_content("こんにちは")
            assert "返信" in response.text
    """
    model = MagicMock()
    
    # generate_content メソッドのモック
    response = MagicMock()
    response.text = "これはAIからのテスト返信です。"
    response.usage_metadata = MagicMock()
    response.usage_metadata.prompt_token_count = 50
    response.usage_metadata.candidates_token_count = 20
    response.usage_metadata.total_token_count = 70
    
    model.generate_content = Mock(return_value=response)
    
    return model


@pytest.fixture
def mock_ai_response():
    """AI応答データのサンプル
    
    TDDでAI応答処理をテストする際に使用。
    
    使用例:
        def test_process_ai_response(mock_ai_response):
            assert "text" in mock_ai_response
            assert mock_ai_response["quality_score"] > 0.8
    """
    return {
        "text": "これはテスト返信です。",
        "usage": {
            "prompt_tokens": 50,
            "completion_tokens": 20,
            "total_tokens": 70
        },
        "quality_score": 0.85,
        "timestamp": datetime.now().isoformat()
    }


# =====================================
# データベース・キャッシュ フィクスチャ
# =====================================

@pytest.fixture
def temp_cache_dir(tmp_path):
    """一時キャッシュディレクトリ
    
    TDDでファイルキャッシュをテストする際に使用。
    テスト終了後に自動削除される。
    
    使用例:
        def test_cache_write(temp_cache_dir):
            cache_file = temp_cache_dir / "cache.json"
            cache_file.write_text('{"key": "value"}')
            assert cache_file.exists()
    """
    cache_dir = tmp_path / "cache"
    cache_dir.mkdir()
    return cache_dir


@pytest.fixture
def greeting_tracker_mock(temp_cache_dir):
    """greeting_tracker.pyのモック
    
    TDDで挨拶記録機能をテストする際に使用。
    
    使用例:
        def test_greeting_limit(greeting_tracker_mock):
            assert "@test_user" in greeting_tracker_mock["last_greetings"]
    """
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
    """テスト用ロガー
    
    TDDでログ出力をテストする際に使用。
    
    使用例:
        def test_logging(test_logger):
            test_logger.info("Test message")
            # ログ出力確認
    """
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
    
    yield logger
    
    # クリーンアップ
    logger.handlers.clear()


# =====================================
# テスト実行前後のフック
# =====================================

@pytest.fixture(autouse=True)
def reset_environment():
    """各テスト実行前に環境をリセット
    
    autouse=True により全テストで自動実行。
    テスト間の状態汚染を防ぐ。
    """
    # テスト前処理
    # （必要に応じて環境変数リセットなど）
    
    yield
    
    # テスト後処理（クリーンアップ）
    # （必要に応じて一時ファイル削除など）
    pass


def pytest_configure(config):
    """pytest起動時の設定
    
    プロジェクト全体で必要な初期設定を行う。
    """
    import os
    
    # ログディレクトリ作成
    log_dir = PROJECT_ROOT / "tests" / "logs"
    log_dir.mkdir(exist_ok=True)
    
    # 環境変数設定（テスト用）
    os.environ["TESTING"] = "1"
    os.environ["GOOGLE_API_KEY"] = "test_api_key_dummy"
    
    # カスタムマーカー登録（追加分）
    config.addinivalue_line(
        "markers", "smoke: スモークテスト（基本動作確認）"
    )


def pytest_sessionstart(session):
    """テストセッション開始時の処理
    
    TDD開発における視覚的フィードバック。
    """
    print("\n" + "=" * 70)
    print("TwitterBot_Nexus_02 - TDD Test Suite")
    print("=" * 70)
    print(f"Test Directory: {PROJECT_ROOT / 'tests'}")
    print(f"Coverage Target: 70%")
    print("=" * 70)


def pytest_sessionfinish(session, exitstatus):
    """テストセッション終了時の処理
    
    TDD開発における結果サマリ。
    """
    print("\n" + "=" * 70)
    print(f"Test session finished (Exit status: {exitstatus})")
    
    if exitstatus == 0:
        print("✅ ALL TESTS PASSED - TDD CYCLE COMPLETE")
    else:
        print("❌ SOME TESTS FAILED - RED PHASE")
    
    print("=" * 70)
```

#### **2-3. conftest.py作成実行**

```bash
# tests/conftest.py作成
# 上記の完全版コードをファイルに保存

# 簡易版（手動作成が難しい場合）
# 以下のコマンドで最小限のconftest.pyを作成

(
echo """pytest共通設定・フィクスチャ定義"""
echo.
echo import pytest
echo import sys
echo from pathlib import Path
echo.
echo PROJECT_ROOT = Path^(__file__^).parent.parent
echo sys.path.insert^(0, str^(PROJECT_ROOT^)^)
echo.
echo @pytest.fixture^(scope="session"^)
echo def project_root^(^):
echo     return PROJECT_ROOT
) > tests\conftest.py

# 作成確認
type tests\conftest.py
```

---

## 🧪 フィクスチャ設計

### **Step 3: フィクスチャ設計原則（10分）**

#### **3-1. フィクスチャスコープ理解**

```yaml
fixture_scopes:
  function:
    description: "各テスト関数ごとに作成（デフォルト）"
    use_case: "テストごとに独立したデータが必要"
    example: "@pytest.fixture"
    
  class:
    description: "テストクラスごとに1回作成"
    use_case: "同一クラス内で共有するデータ"
    example: "@pytest.fixture(scope='class')"
    
  module:
    description: "テストモジュールごとに1回作成"
    use_case: "ファイル内の全テストで共有"
    example: "@pytest.fixture(scope='module')"
    
  session:
    description: "テストセッション全体で1回作成"
    use_case: "高コストな初期化（DB接続など）"
    example: "@pytest.fixture(scope='session')"
```

#### **3-2. フィクスチャ依存関係**

```python
# フィクスチャの依存関係例

@pytest.fixture
def database_connection():
    """データベース接続（親フィクスチャ）"""
    conn = connect_to_db()
    yield conn
    conn.close()

@pytest.fixture
def test_data(database_connection):
    """テストデータ挿入（子フィクスチャ）"""
    # database_connectionに依存
    insert_test_data(database_connection)
    return database_connection

def test_query(test_data):
    """テスト実行（test_dataに依存）"""
    result = query_data(test_data)
    assert len(result) > 0
```

#### **3-3. フィクスチャ命名規則**

```yaml
fixture_naming_conventions:
  mock_*:
    pattern: "mock_webdriver, mock_api"
    purpose: "モックオブジェクト"
    
  sample_*:
    pattern: "sample_config, sample_data"
    purpose: "サンプルデータ"
    
  temp_*:
    pattern: "temp_file, temp_dir"
    purpose: "一時ファイル/ディレクトリ"
    
  test_*:
    pattern: "test_logger, test_env"
    purpose: "テスト用設定"
```

---

## ✅ 設定完了確認

### **Step 4: pytest設定動作確認（10分）**

#### **4-1. マーカー機能確認**

**tests/unit/test_markers.py 作成:**

```python
"""マーカー機能のテスト"""

import pytest


@pytest.mark.unit
def test_unit_marker():
    """ユニットマーカー確認"""
    assert True


@pytest.mark.slow
def test_slow_marker():
    """slowマーカー確認"""
    import time
    time.sleep(1)  # 1秒待機
    assert True


@pytest.mark.webdriver
def test_webdriver_marker(mock_webdriver):
    """WebDriverマーカー確認"""
    mock_webdriver.get("https://twitter.com")
    assert mock_webdriver.current_url == "https://twitter.com/home"


@pytest.mark.skip(reason="スキップテスト例")
def test_skip_example():
    """スキップされるテスト"""
    assert False  # 実行されない
```

**マーカー別実行:**

```bash
# unitマーカーのみ実行
pytest -m unit -v

# slowマーカーをスキップ
pytest -m "not slow" -v

# webdriverマーカーのみ実行
pytest -m webdriver -v

# 期待出力:
# tests/unit/test_markers.py::test_webdriver_marker PASSED [100%]
# ===================== 1 passed in 0.05s =====================
```

#### **4-2. フィクスチャ動作確認**

**tests/unit/test_fixtures.py 作成:**

```python
"""フィクスチャ動作確認テスト"""

import pytest


def test_project_root_fixture(project_root):
    """project_rootフィクスチャ確認"""
    assert project_root.exists()
    assert (project_root / "pytest.ini").exists()


def test_sample_config_fixture(sample_account_config):
    """sample_account_configフィクスチャ確認"""
    assert sample_account_config["id"] == "test_account_001"
    assert "handle" in sample_account_config


def test_mock_webdriver_fixture(mock_webdriver):
    """mock_webdriverフィクスチャ確認"""
    mock_webdriver.get("https://test.com")
    assert mock_webdriver.get.called


def test_temp_cache_dir_fixture(temp_cache_dir):
    """temp_cache_dirフィクスチャ確認"""
    assert temp_cache_dir.exists()
    
    # テストファイル作成
    test_file = temp_cache_dir / "test.txt"
    test_file.write_text("test")
    
    assert test_file.exists()
```

**実行確認:**

```bash
pytest tests/unit/test_fixtures.py -v

# 期待出力:
# tests/unit/test_fixtures.py::test_project_root_fixture PASSED        [ 25%]
# tests/unit/test_fixtures.py::test_sample_config_fixture PASSED       [ 50%]
# tests/unit/test_fixtures.py::test_mock_webdriver_fixture PASSED      [ 75%]
# tests/unit/test_fixtures.py::test_temp_cache_dir_fixture PASSED      [100%]
# ===================== 4 passed in 0.12s =====================
```

#### **4-3. カバレッジ測定確認**

```bash
# カバレッジ付きテスト実行
pytest tests/unit/test_fixtures.py --cov=tests --cov-report=term

# 期待出力:
# ----------- coverage: platform win32, python 3.11.5 -----------
# Name                                Stmts   Miss  Cover
# -------------------------------------------------------
# tests\__init__.py                       0      0   100%
# tests\conftest.py                      45     12    73%
# tests\unit\test_fixtures.py            16      0   100%
# -------------------------------------------------------
# TOTAL                                  61     12    80%

# HTML形式レポート生成
pytest tests/unit/test_fixtures.py --cov=tests --cov-report=html

# 期待: htmlcov/index.html 生成
dir htmlcov\index.html
```

---

## 📊 完了チェックリスト

```yaml
phase4_01b_completion_checklist:
  pytest_configuration:
    - [ ] pytest.ini 作成完了
    - [ ] マーカー定義確認（--markers実行）
    - [ ] カバレッジ設定確認（--cov実行）
    - [ ] ログ設定確認（tests/logs作成）
  
  conftest_py:
    - [ ] tests/conftest.py 作成完了
    - [ ] project_root フィクスチャ動作確認
    - [ ] sample_account_config フィクスチャ動作確認
    - [ ] mock_webdriver フィクスチャ動作確認
    - [ ] フィクスチャ一覧表示（pytest --fixtures）
  
  test_execution:
    - [ ] マーカー別テスト実行成功
    - [ ] フィクスチャテスト実行成功
    - [ ] カバレッジ70%以上達成
    - [ ] HTMLレポート生成成功
  
  tdd_readiness:
    - [ ] Red-Green-Refactorサイクル準備完了
    - [ ] テスト実行時間 < 5秒（高速フィードバック）
    - [ ] エラーメッセージが明確
  
  next_step:
    - [ ] Phase4_01cへ進む準備完了
```

---

## 🚀 TDDマインドセット確認

**このフェーズで身につけるべきTDD習慣:**

```yaml
tdd_habits_phase01b:
  habit_1:
    name: "フィクスチャ優先設計"
    practice: "テストデータはフィクスチャで管理"
    benefit: "テストコードの重複削減"
  
  habit_2:
    name: "マーカーによるテスト分類"
    practice: "テストをカテゴリ分け"
    benefit: "必要なテストだけを高速実行"
  
  habit_3:
    name: "カバレッジ意識"
    practice: "常に70%以上を目指す"
    benefit: "TDDでの品質保証"
```

---

## 📝 次のステップ

✅ **Phase 4-01b 完了！**

次は [`12_Phase4_01c_TDD実践ガイド.md`](12_Phase4_01c_TDD実践ガイド.md) へ進んでください。

**Phase4-01c の内容:**
- Red-Green-Refactorサイクル実践
- サンプルTDD実装
- VSCode設定完了

---

**最終更新**: 2025-11-24  
**TDD重要度**: ★★★★★ (フィクスチャはTDDの効率を左右)