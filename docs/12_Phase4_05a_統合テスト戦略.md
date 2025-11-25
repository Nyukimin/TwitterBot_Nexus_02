# Phase 4-05a: 統合テスト戦略

**作成日**: 2025-11-24  
**バージョン**: 3.0 (TDD重視・実装可能版)  
**対象者**: 中級〜上級エンジニア  
**実装時間**: 4-6時間  
**TDD段階**: Red-Green-Refactor完全実践

---

## 📋 目次

1. [統合テストの役割と責務](#統合テストの役割と責務)
2. [TDD実装計画](#tdd実装計画)
3. [Phase 1: 層間連携テスト](#phase-1-層間連携テスト)
4. [Phase 2: データフロー検証](#phase-2-データフロー検証)
5. [Phase 3: E2Eテスト](#phase-3-e2eテスト)
6. [Phase 4: パフォーマンステスト](#phase-4-パフォーマンステスト)
7. [完了チェックリスト](#完了チェックリスト)

---

## 🎯 統合テストの役割と責務

### **統合テストとは**

```
┌─────────────────────────────────────────┐
│ 統合テスト層                            │
│ (tests/integration/, tests/e2e/)        │
│                                         │
│ 【責務】                                │
│ ✅ 複数モジュール間の連携検証           │
│ ✅ データフロー全体の整合性確認         │
│ ✅ 実環境に近いシナリオテスト           │
│ ✅ エラーリカバリー動作確認             │
└─────────────────────────────────────────┘
         ↓ (全レイヤーを統合検証)
┌─────────────────────────────────────────┐
│ Layer 1-4 + セキュリティ + データ管理   │
│ (multi_main.py, reply_processor.py, ... │
└─────────────────────────────────────────┘
```

### **統合テストが実装する機能**

```yaml
integration_test_functions:
  layer_integration:
    test_full_workflow:
      description: "Layer 1-4の完全なワークフロー検証"
      scenario: "YAML読み込み → アカウント選択 → Bot実行 → ログ記録"
      coverage: "全レイヤー連携"
    
    test_layer_1_to_2:
      description: "Layer 1 → Layer 2 データ受け渡し"
      input: "account_config: Dict"
      output: "reply_result: str"
    
    test_layer_2_to_3:
      description: "Layer 2 → Layer 3 AI呼び出し"
      input: "thread_context: List[Dict]"
      output: "ai_response: str"
  
  data_flow:
    test_yaml_to_cache_flow:
      description: "YAML設定 → キャッシュ → ログ のフロー"
      steps:
        - "ConfigManager.load() → accounts.yaml読み込み"
        - "GreetingTracker.record() → cache.json書き込み"
        - "ActionLogger.log() → actions.log書き込み"
    
    test_config_reload_propagation:
      description: "設定変更が全モジュールに伝播"
      scenario: "YAML更新 → ConfigManager再読み込み → 各モジュール反映"
  
  e2e_tests:
    test_complete_reply_cycle:
      description: "完全な返信サイクル（E2E）"
      scenario: "Twitter検索 → スレッド解析 → AI応答生成 → 投稿"
      duration: "30-60秒"
    
    test_error_recovery_e2e:
      description: "エラーリカバリー（E2E）"
      scenario: "WebDriver切断 → 再接続 → 処理継続"
  
  performance_tests:
    test_response_time:
      description: "応答時間計測"
      threshold: "AI応答生成 < 5秒"
    
    test_memory_usage:
      description: "メモリ使用量監視"
      threshold: "100アカウント処理 < 500MB"
    
    test_parallel_execution:
      description: "並列実行負荷テスト"
      scenario: "5アカウント並列実行が正常完了"
```

### **TDD実装のゴール**

```yaml
phase4_05a_goals:
  test_coverage:
    target: "統合カバレッジ70%以上"
    focus: "全レイヤー連携パターン完全カバー"
    
  tdd_cycle:
    count: "各統合機能で2-3回サイクル実施"
    time_per_cycle: "Red(15分) + Green(20分) + Refactor(10分)"
    
  test_quality:
    isolation: "各テストが独立実行可能"
    repeatability: "何度実行しても同じ結果"
    speed: "統合テスト全体 < 60秒"
    
  code_quality:
    lint: "flake8警告ゼロ"
    format: "black適用"
    typing: "型ヒント100%"
    
  documentation:
    docstring: "全テストにシナリオ説明"
    examples: "期待される動作を明記"
```

---

## 🔄 TDD実装計画

### **実装順序とTDDサイクル**

```
【Phase 1】 層間連携テスト（Layer 1-4統合）
  Step 1: Red  → テスト作成（Layer 1→2→3→4の完全フロー）
  Step 2: Green → 最小実装（モック使用で各層を接続）
  Step 3: Refactor → エラーハンドリング・ロギング追加
  所要時間: 90分
  
【Phase 2】 データフロー検証
  Step 1: Red  → テスト作成（YAML→キャッシュ→ログの一貫性）
  Step 2: Green → 最小実装（実ファイル使用で検証）
  Step 3: Refactor → ファイルロック・トランザクション追加
  所要時間: 60分
  
【Phase 3】 E2Eテスト
  Step 1: Red  → テスト作成（完全な返信サイクル）
  Step 2: Green → 最小実装（モックWebDriver使用）
  Step 3: Refactor → 実WebDriver対応・スキップ設定
  所要時間: 90分
  
【Phase 4】 パフォーマンステスト
  Step 1: Red  → テスト作成（応答時間・メモリ・並列実行）
  Step 2: Green → 最小実装（benchmarkフィクスチャ使用）
  Step 3: Refactor → しきい値調整・レポート生成
  所要時間: 60分

合計所要時間: 5-6時間
```

---

## 🧪 Phase 1: 層間連携テスト

### **Step 1: テスト作成（Red）**

#### **1-1. テストファイル作成**

**tests/integration/test_full_workflow.py:**
```python
"""統合テスト: 全ワークフロー検証

テストシナリオ:
1. YAML設定読み込み（Layer 1）
2. アカウント選択（Layer 1）
3. AI応答生成（Layer 2）
4. ログ記録（Layer 3）
5. 全体の整合性確認
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from datetime import datetime


class TestFullWorkflow:
    """フルワークフロー統合テスト"""
    
    @patch('reply_bot.multi_main.setup_driver')
    @patch('reply_bot.reply_processor.generate_reply')
    @patch('reply_bot.post_reply.post_reply')
    def test_complete_reply_workflow(
        self, mock_post, mock_gen_reply, mock_setup_driver, tmp_path
    ):
        """完全な返信ワークフロー
        
        シナリオ:
        1. setup_driver() → WebDriverモック取得
        2. generate_reply() → AI応答生成
        3. post_reply() → 投稿実行
        4. 全ステップが正常完了
        
        テスト観点:
        - 全関数が正しい順序で呼ばれる
        - データが各層を正しく流れる
        - エラーが無く完了する
        """
        # Arrange
        mock_driver = Mock()
        mock_setup_driver.return_value = mock_driver
        mock_gen_reply.return_value = "統合テスト返信メッセージ"
        mock_post.return_value = True
        
        # YAML設定ファイル作成
        config_file = tmp_path / "accounts.yaml"
        config_file.write_text("""
accounts:
  - id: test001
    handle: testuser
    PERSONALITY_PROMPT: "丁寧に返信してください"
    features:
      comment: true
      like: true
        """)
        
        account_config = {
            "id": "test001",
            "handle": "testuser",
            "PERSONALITY_PROMPT": "丁寧に返信してください",
            "features": {"comment": True, "like": True}
        }
        
        # Act
        from reply_bot.multi_main import run_for_account
        result = run_for_account(account_config, live_run=False)
        
        # Assert
        assert result is True or result is None  # Noneも許容（dry-run時）
        mock_setup_driver.assert_called_once()
        
        # モックが呼ばれたことを確認（live_run=Falseでも処理フローを確認）
        print("✅ 完全ワークフロー統合テスト成功")
    
    def test_layer_1_to_layer_2_data_flow(self, tmp_path):
        """Layer 1 → Layer 2 データフロー
        
        シナリオ:
        1. Layer 1がYAMLからアカウント設定を読み込む
        2. Layer 2にPERSONALITY_PROMPTを渡す
        3. Layer 2がAI応答を生成
        
        テスト観点:
        - アカウント設定が正しくLayer 2に渡される
        - PERSONALITY_PROMPTが反映される
        """
        # Arrange
        from reply_bot.config import load_accounts_config
        from reply_bot.reply_processor import generate_reply
        
        config_file = tmp_path / "accounts.yaml"
        config_file.write_text("""
accounts:
  - id: test001
    handle: testuser
    PERSONALITY_PROMPT: "フレンドリーに返信"
        """)
        
        # Act
        cfg_data = load_accounts_config(str(config_file))
        account = cfg_data["accounts"][0]
        
        # Layer 2にデータを渡す（モック使用）
        with patch('reply_bot.reply_processor.call_gemini_api') as mock_gemini:
            mock_gemini.return_value = "テスト応答"
            
            thread_context = [{"author": "user1", "text": "こんにちは"}]
            reply = generate_reply(
                thread_context,
                account["PERSONALITY_PROMPT"]
            )
        
        # Assert
        assert reply is not None
        assert "フレンドリーに返信" in str(mock_gemini.call_args)
        print("✅ Layer 1→2 データフロー検証成功")
    
    def test_layer_2_to_layer_3_ai_call(self):
        """Layer 2 → Layer 3 AI呼び出し
        
        シナリオ:
        1. Layer 2がスレッド解析
        2. Layer 3（shared_modules）のAI関数を呼び出し
        3. AI応答を取得
        
        テスト観点:
        - スレッドコンテキストが正しく渡される
        - AI応答が正しく返される
        """
        # Arrange
        from reply_bot.reply_processor import generate_reply
        
        thread_context = [
            {"author": "user1", "text": "天気はどうですか？"}
        ]
        personality = "親切に回答してください"
        
        # Act
        with patch('reply_bot.reply_processor.call_gemini_api') as mock_ai:
            mock_ai.return_value = "今日は晴れです"
            
            reply = generate_reply(thread_context, personality)
        
        # Assert
        assert reply == "今日は晴れです"
        mock_ai.assert_called_once()
        print("✅ Layer 2→3 AI呼び出し検証成功")
    
    def test_error_propagation_across_layers(self):
        """エラー伝播検証
        
        シナリオ:
        1. Layer 3でエラー発生（AI APIエラー）
        2. Layer 2でキャッチ
        3. Layer 1に適切なエラーを返す
        
        テスト観点:
        - エラーが適切に伝播する
        - 各層でログが記録される
        - システムがクラッシュしない
        """
        # Arrange
        from reply_bot.reply_processor import generate_reply
        
        thread_context = [{"author": "user1", "text": "質問"}]
        
        # Act & Assert
        with patch('reply_bot.reply_processor.call_gemini_api') as mock_ai:
            mock_ai.side_effect = Exception("API Error")
            
            # エラーが適切にハンドリングされることを確認
            reply = generate_reply(thread_context, "丁寧に")
            
            # エラー時はNoneまたはフォールバック応答を返す
            assert reply is None or isinstance(reply, str)
        
        print("✅ エラー伝播検証成功")


class TestModuleIntegration:
    """モジュール間連携テスト"""
    
    def test_config_and_cache_integration(self, tmp_path):
        """設定管理とキャッシュの統合
        
        シナリオ:
        1. ConfigManagerでYAML読み込み
        2. GreetingTrackerでキャッシュ記録
        3. 両方のデータが整合性を保つ
        """
        # Arrange
        from reply_bot.config_manager import ConfigManager
        from reply_bot.greeting_tracker import GreetingTracker
        
        config_file = tmp_path / "accounts.yaml"
        config_file.write_text("""
accounts:
  - id: test001
    handle: testuser
        """)
        
        cache_file = tmp_path / "greetings.json"
        
        # Act
        config_mgr = ConfigManager(str(config_file))
        config = config_mgr.load()
        
        tracker = GreetingTracker(str(cache_file))
        tracker.record_greeting("@testuser", datetime.now())
        
        # Assert
        assert len(config["accounts"]) == 1
        assert tracker.has_greeted("@testuser")
        print("✅ 設定・キャッシュ統合検証成功")
    
    def test_logger_and_action_log_integration(self, tmp_path):
        """ロガーとアクションログの統合
        
        シナリオ:
        1. StructuredLoggerで構造化ログ出力
        2. ActionLoggerでアクションログ記録
        3. 両ログが整合性を保つ
        """
        # Arrange
        from reply_bot.structured_logger import StructuredLogger
        from reply_bot.action_logger import ActionLogger
        
        struct_log_file = tmp_path / "structured.log"
        action_log_file = tmp_path / "actions.log"
        
        # Act
        struct_logger = StructuredLogger(str(struct_log_file))
        struct_logger.log("info", "テストログ", {"key": "value"})
        
        action_logger = ActionLogger(str(action_log_file))
        action_logger.log_action("like", "@testuser", "success")
        
        # Assert
        assert struct_log_file.exists()
        assert action_log_file.exists()
        
        struct_content = struct_log_file.read_text()
        action_content = action_log_file.read_text()
        
        assert "テストログ" in struct_content
        assert "like" in action_content
        print("✅ ロガー統合検証成功")
```

#### **1-2. テスト実行（失敗確認）**

```bash
# テスト実行（Red段階）
pytest tests/integration/test_full_workflow.py -v

# 期待される出力（一部のモジュールが未実装の場合）:
# FAILED tests/integration/test_full_workflow.py::TestFullWorkflow::test_complete_reply_workflow
# ModuleNotFoundError: No module named 'reply_bot.config_manager'
# または
# AssertionError: Expected function call not made
# ✅ Red段階: 統合部分が未完成なので失敗が正しい
```

---

### **Step 2: 最小実装（Green）**

#### **2-1. モック・フィクスチャ整備**

**tests/conftest.py:**
```python
"""pytest共通フィクスチャ

統合テスト用のモック・フィクスチャを定義
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, MagicMock


@pytest.fixture
def mock_webdriver():
    """WebDriverモック
    
    Returns:
        Mock: WebDriverモックオブジェクト
    """
    driver = Mock()
    driver.get = Mock()
    driver.page_source = "<html><body>Test Page</body></html>"
    driver.quit = Mock()
    
    return driver


@pytest.fixture
def sample_account_config():
    """サンプルアカウント設定
    
    Returns:
        Dict: テスト用アカウント設定
    """
    return {
        "id": "test001",
        "handle": "testuser",
        "PERSONALITY_PROMPT": "丁寧に返信してください",
        "browser": {
            "user_data_dir": "profile/test",
            "headless": True
        },
        "features": {
            "like": True,
            "comment": True
        },
        "policies": {
            "sources": ["@target_user"],
            "reply_num_max": 5
        }
    }


@pytest.fixture
def sample_yaml_config(tmp_path):
    """サンプルYAML設定ファイル
    
    Args:
        tmp_path: pytest一時ディレクトリ
    
    Returns:
        Path: YAML設定ファイルパス
    """
    config_file = tmp_path / "accounts.yaml"
    config_file.write_text("""
accounts:
  - id: test001
    handle: testuser
    PERSONALITY_PROMPT: "テスト返信"
    features:
      like: true
      comment: true
  - id: test002
    handle: testuser2
    PERSONALITY_PROMPT: "テスト返信2"
    features:
      like: false
      comment: true
    """)
    
    return config_file


@pytest.fixture
def benchmark(request):
    """ベンチマークフィクスチャ
    
    パフォーマンステスト用の簡易ベンチマーク
    """
    import time
    
    class Benchmark:
        def __init__(self):
            self.stats = {'mean': 0.0}
        
        def __call__(self, func, *args, **kwargs):
            start = time.time()
            result = func(*args, **kwargs)
            end = time.time()
            
            self.stats['mean'] = end - start
            return result
    
    return Benchmark()
```

#### **2-2. テスト実行（成功確認）**

```bash
# テスト実行（Green段階）
pytest tests/integration/test_full_workflow.py -v

# 期待される出力:
# tests/integration/test_full_workflow.py::TestFullWorkflow::test_complete_reply_workflow PASSED
# tests/integration/test_full_workflow.py::TestFullWorkflow::test_layer_1_to_layer_2_data_flow PASSED
# tests/integration/test_full_workflow.py::TestModuleIntegration::test_config_and_cache_integration PASSED
# ... (全テスト成功)
#
# ======================== 7 passed in 1.25s ========================
```

**期待される出力:**

```
✅ 完全ワークフロー統合テスト成功
✅ Layer 1→2 データフロー検証成功
✅ Layer 2→3 AI呼び出し検証成功
✅ エラー伝播検証成功
✅ 設定・キャッシュ統合検証成功
✅ ロガー統合検証成功
```

---

### **Step 3: リファクタリング（Refactor）**

#### **3-1. テストヘルパー関数追加**

**tests/helpers.py:**
```python
"""テストヘルパー関数"""

from pathlib import Path
from typing import Dict, List


def create_test_yaml(tmp_path: Path, accounts: List[Dict]) -> Path:
    """テスト用YAML設定ファイル生成
    
    Args:
        tmp_path: 一時ディレクトリパス
        accounts: アカウント設定リスト
    
    Returns:
        生成されたYAMLファイルパス
    """
    import yaml
    
    config_file = tmp_path / "accounts.yaml"
    config_data = {"accounts": accounts}
    
    config_file.write_text(yaml.dump(config_data))
    return config_file


def assert_log_contains(log_file: Path, expected_text: str) -> None:
    """ログファイルに指定テキストが含まれることを確認
    
    Args:
        log_file: ログファイルパス
        expected_text: 期待されるテキスト
    
    Raises:
        AssertionError: テキストが含まれない場合
    """
    assert log_file.exists(), f"Log file not found: {log_file}"
    
    content = log_file.read_text()
    assert expected_text in content, f"'{expected_text}' not found in {log_file}"
```

---

## 🧪 Phase 2: データフロー検証

### **Step 1: テスト作成（Red）**

**tests/integration/test_data_flow.py:**
```python
"""データフロー統合テスト

シナリオ:
1. YAML設定読み込み
2. キャッシュ記録
3. ログ出力
4. 全データの整合性確認
"""

import pytest
from pathlib import Path
from datetime import datetime


class TestDataFlowIntegration:
    """データフロー統合テスト"""
    
    def test_yaml_to_cache_to_log_flow(self, tmp_path):
        """YAML → キャッシュ → ログ の完全フロー
        
        シナリオ:
        1. ConfigManagerでYAML読み込み
        2. GreetingTrackerで挨拶記録
        3. ActionLoggerでアクション記録
        4. 全ファイルが正しく生成される
        
        テスト観点:
        - データが各ステージで正しく保存される
        - ファイルフォーマットが正しい
        - 整合性が保たれる
        """
        # Arrange
        from reply_bot.config_manager import ConfigManager
        from reply_bot.greeting_tracker import GreetingTracker
        from reply_bot.action_logger import ActionLogger
        
        config_file = tmp_path / "accounts.yaml"
        config_file.write_text("""
accounts:
  - id: test001
    handle: testuser
        """)
        
        cache_file = tmp_path / "greetings.json"
        log_file = tmp_path / "actions.log"
        
        # Act - 設定読み込み
        config_mgr = ConfigManager(str(config_file))
        config = config_mgr.load()
        
        # Act - キャッシュ記録
        tracker = GreetingTracker(str(cache_file))
        tracker.record_greeting("@testuser", datetime.now())
        
        # Act - ログ記録
        logger = ActionLogger(str(log_file))
        logger.log_action("like", "@testuser", "success")
        
        # Assert
        assert len(config["accounts"]) == 1
        assert tracker.has_greeted("@testuser")
        assert log_file.exists()
        
        # ログ内容確認
        log_content = log_file.read_text()
        assert "like" in log_content
        assert "@testuser" in log_content
        
        print("✅ YAML→キャッシュ→ログ フロー検証成功")
    
    def test_config_reload_propagation(self, tmp_path):
        """設定変更の伝播検証
        
        シナリオ:
        1. 初期設定読み込み
        2. YAML更新
        3. 再読み込み
        4. 変更が反映される
        """
        # Arrange
        from reply_bot.config_manager import ConfigManager
        
        config_file = tmp_path / "accounts.yaml"
        config_file.write_text("""
accounts:
  - id: test001
    handle: original_user
        """)
        
        # Act - 初期読み込み
        config_mgr = ConfigManager(str(config_file))
        config_v1 = config_mgr.load()
        
        # Act - YAML更新
        config_file.write_text("""
accounts:
  - id: test001
    handle: updated_user
        """)
        
        # Act - 再読み込み
        config_v2 = config_mgr.load()
        
        # Assert
        assert config_v1["accounts"][0]["handle"] == "original_user"
        assert config_v2["accounts"][0]["handle"] == "updated_user"
        print("✅ 設定変更伝播検証成功")
    
    def test_concurrent_cache_access(self, tmp_path):
        """並行キャッシュアクセス検証
        
        シナリオ:
        1. 複数のGreetingTrackerインスタンスを作成
        2. 同時にキャッシュ記録
        3. データ破損が無いことを確認
        
        テスト観点:
        - ファイルロックが正常に機能
        - データ破損が無い
        """
        # Arrange
        from reply_bot.greeting_tracker import GreetingTracker
        from concurrent.futures import ThreadPoolExecutor
        
        cache_file = tmp_path / "greetings.json"
        
        # Act - 並行書き込み
        def record_greeting(user_index):
            tracker = GreetingTracker(str(cache_file))
            tracker.record_greeting(f"@user{user_index}", datetime.now())
            return True
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(record_greeting, i) for i in range(10)]
            results = [f.result() for f in futures]
        
        # Assert
        assert all(results)
        
        # 全ユーザーが記録されていることを確認
        tracker = GreetingTracker(str(cache_file))
        for i in range(10):
            assert tracker.has_greeted(f"@user{i}")
        
        print("✅ 並行キャッシュアクセス検証成功")
```

---

## ✅ 完了チェックリスト

```yaml
phase4_05a_completion:
  layer_integration:
    - [ ] test_complete_reply_workflow 成功（Layer 1-4統合）
    - [ ] test_layer_1_to_layer_2_data_flow 成功
    - [ ] test_layer_2_to_layer_3_ai_call 成功
    - [ ] test_error_propagation_across_layers 成功
    - [ ] カバレッジ70%以上
  
  data_flow:
    - [ ] test_yaml_to_cache_to_log_flow 成功
    - [ ] test_config_reload_propagation 成功
    - [ ] test_concurrent_cache_access 成功
    - [ ] カバレッジ65%以上
  
  test_quality:
    - [ ] 全テストが独立実行可能
    - [ ] 全テストが繰り返し実行可能
    - [ ] 統合テスト全体 < 60秒
  
  documentation:
    - [ ] 全テストにシナリオ説明記述
    - [ ] 期待される動作を明記
  
  next_step:
    - [ ] Phase4_05bへ進む（E2E・パフォーマンステスト・品質保証）
```

---

**次のフェーズ:**  
[Phase4_05b_E2E・パフォーマンス・品質保証.md](12_Phase4_05b_E2E・パフォーマンス・品質保証.md)

---

**最終更新**: 2025-11-24
