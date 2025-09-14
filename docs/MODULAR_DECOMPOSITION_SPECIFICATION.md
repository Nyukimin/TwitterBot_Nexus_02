# TwitterBot Nexus 02 - モジュール組み換え仕様書

## 📋 **概要**

本仕様書は、TwitterBot_Nexus_02プロジェクトのモジュール分解と組み換えに関する詳細仕様を定義します。

## 🎯 **分解対象と目的**

### **主要分解対象**
1. **TwitterBotOrchestrator** (650+行の巨大クラス)
2. **WebDriverログイン機能** (複数ファイルに散在)
3. **プロファイル作成+Chrome起動機能** (汎用化)

### **組み換えの目的**
- 単一責任原則の遵守
- 再利用可能なコンポーネントの作成
- 他プロジェクトでの利用可能性向上
- 保守性・拡張性の向上

## 🏗️ **Phase 1: Chrome Profile Manager (完了済み)**

### **新設モジュール**
```
shared_modules/chrome_profile_manager/
├── chrome_profile_manager/
│   ├── manager.py              # ProfiledChromeManager
│   ├── exceptions.py           # 専用例外クラス群
│   └── __init__.py
├── examples/basic_usage.py     # 使用例
├── setup.py                    # パッケージ設定
├── requirements.txt            # 依存関係
└── README.md                   # ドキュメント
```

### **主要機能**
- `ProfiledChromeManager.create_and_launch()` - プロファイル作成+Chrome起動
- `ProfiledChromeManager.launch_existing()` - 既存プロファイル利用
- プロファイル管理機能（一覧、削除、バックアップ）

### **利用方法**
```python
from chrome_profile_manager import ProfiledChromeManager
manager = ProfiledChromeManager(base_profiles_dir="./profiles")
driver = manager.create_and_launch("profile_name", headless=False)
```

## 🔧 **Phase 2: WebDriverログイン機能統合 (設計完了)**

### **新設モジュール構造**
```
twitter_bot/login/
├── __init__.py
├── login_manager.py            # 統合ログイン管理
├── login_checker.py            # ログイン状態チェック専用
├── login_assistant.py          # ログインアシスト機能
├── profile_manager.py          # プロファイル管理
└── interfaces.py               # ログイン関連インターフェース
```

### **既存コードからの移行マップ**

#### **移行元 → 移行先**
- `twitter_login.py:TwitterLoginManager.check_login_status()` → `login_checker.py:LoginChecker.comprehensive_check()`
- `twitter_login.py:TwitterLoginManager.login_assist()` → `login_assistant.py:LoginAssistant.start_assisted_login()`
- `twitter_login.py:TwitterLoginManager._login_single_account()` → `login_manager.py:LoginManager.ensure_login()`
- `twitter_bot/implementations/browser/chrome.py:check_login_status()` → `login_checker.py:LoginChecker`使用に変更

### **新しいクラス設計**

#### **LoginManager**
```python
class LoginManager:
    def ensure_login(self, account: AccountConfig, browser: BrowserInterface) -> bool
    def perform_login_assist(self, account: AccountConfig) -> bool
    def validate_account_access(self, account_id: str) -> bool
```

#### **LoginChecker**
```python
class LoginChecker:
    def check_by_url(self, current_url: str) -> bool
    def check_by_ui_elements(self, driver: WebDriver) -> bool
    def check_by_navigation(self, driver: WebDriver) -> bool
    def comprehensive_check(self, driver: WebDriver) -> bool
```

#### **LoginAssistant**
```python
class LoginAssistant:
    def start_assisted_login(self, account: AccountConfig) -> bool
    def auto_fill_username(self, driver: WebDriver, username: str) -> bool
    def wait_for_manual_completion(self, driver: WebDriver, timeout: int) -> bool
    def verify_login_success(self, driver: WebDriver) -> bool
```

### **統合方法**
```python
# 変更前
if not browser.check_login_status():
    raise LoginError(f"ログインが必要: @{account.handle}")

# 変更後
login_manager = LoginManager(self.config)
if not login_manager.ensure_login(account, browser):
    raise LoginError(f"ログインが必要: @{account.handle}")
```

## 🎪 **Phase 3: TwitterBotOrchestrator分解 (設計完了)**

### **分解対象メソッドの責任分析**
```
TwitterBotOrchestrator (15メソッド):
├── 初期化: __init__, _setup_logging
├── プロセス管理: process_account, process_multiple_accounts
├── アクション実行: execute_all_per_target_actions, _execute_fixed_tweet
├── バッチ処理: _execute_target_interactions_batch, _execute_target_interaction
├── 個別アクション: _execute_single_*_action (like, bookmark, retweet, comment)
├── 収集機能: _collect_tweet_ids
└── 人間行動: _run_human_like_startup, _visit_user_tweets
```

### **新設モジュール構造**
```
twitter_bot/orchestration/
├── __init__.py
├── process_manager.py          # アカウント処理管理
├── action_executor.py          # アクション実行管理
├── interaction_processor.py    # 個別インタラクション処理
├── human_behavior.py           # 人間らしい行動シミュレーション
└── tweet_collector.py          # ツイート収集機能
```

### **分解されるクラス**

#### **ProcessManager**
**責任**: 単一/複数アカウントの処理フロー管理
```python
class ProcessManager:
    def process_single_account(self, account_id: str, live_run: bool) -> ProcessResult
    def process_multiple_accounts(self, account_ids: List[str], live_run: bool) -> ProcessResult
```

#### **ActionExecutor** 
**責任**: 各種アクションの実行とバッチ処理
```python
class ActionExecutor:
    def execute_per_target_actions(self, account_id: str, live_run: bool, target_filter: List[str]) -> ProcessResult
    def execute_fixed_tweet(self, browser: BrowserInterface, tweet_poster, comment: str, images: List[str], account_id: str) -> bool
    def execute_batch_interactions(self, browser: BrowserInterface, handler, target: str, actions: List[str], comment: str, top_n: int) -> Dict[str, int]
```

#### **InteractionProcessor**
**責任**: 個別インタラクションの実行
```python
class InteractionProcessor:
    def execute_like(self, tweet_element, driver) -> bool
    def execute_bookmark(self, tweet_element, driver) -> bool
    def execute_retweet(self, tweet_element, driver) -> bool
    def execute_comment(self, tweet_element, driver, text: str) -> bool
```

#### **HumanBehaviorSimulator**
**責任**: 人間らしい行動パターンの実装
```python
class HumanBehaviorSimulator:
    def run_startup_sequence(self, browser: BrowserInterface, account: AccountConfig) -> None
    def visit_user_timeline(self, browser: BrowserInterface, handle: str, top_n: int, dwell_seconds: int) -> None
```

#### **TweetCollector**
**責任**: ツイートIDの収集と処理
```python
class TweetCollector:
    def collect_valid_tweet_ids(self, browser: BrowserInterface, target_handle: str, top_n: int) -> List[str]
```

### **軽量化されたTwitterBotOrchestrator**
```python
class TwitterBotOrchestrator:
    def __init__(self, config_path: str):
        self.config = ConfigImplementation()
        self.loader = ModuleLoader(self.config)
        self.process_manager = ProcessManager(self.config, self.loader)
    
    def run_account_processing(self, account_id: str, live_run: bool) -> ProcessResult:
        return self.process_manager.process_single_account(account_id, live_run)
    
    def run_batch_processing(self, account_ids: List[str], live_run: bool) -> ProcessResult:
        return self.process_manager.process_multiple_accounts(account_ids, live_run)
```

## 📊 **Phase 4: レガシーコード統合**

### **twitter_posting.py との統合計画**

#### **移行対象クラス**
- `TweetPoster` → `implementations/tweet_poster/legacy.py`
- `ScheduledTweetPoster` → `implementations/tweet_poster/scheduled.py`
- `HourlyScheduler` → `scheduling/hourly_scheduler.py`
- `ImprovedScheduler` → `scheduling/improved_scheduler.py`

#### **新設スケジューリングモジュール**
```
twitter_bot/scheduling/
├── __init__.py
├── scheduler_interface.py      # スケジューラーインターフェース
├── hourly_scheduler.py         # 時間別スケジューリング
├── improved_scheduler.py       # 改良版スケジューラー
└── scheduler_manager.py        # スケジューラー統合管理
```

## 🚀 **実装優先度と段階的移行計画**

### **Phase 1: 基盤モジュール (完了)**
1. ✅ `shared_modules/chrome_profile_manager` - Chrome起動統合機能

### **Phase 2: ログインモジュール**
2. `LoginChecker` 実装 - ログイン状態判定を独立化
3. `ProfileManager` 実装 - プロファイル管理機能
4. `LoginAssistant` 実装 - ログインアシスト機能
5. `LoginManager` 実装 - 統合ログイン管理
6. 既存コードの段階的移行

### **Phase 3: オーケストレーション分解**
7. `InteractionProcessor` 実装 - 個別アクション処理
8. `TweetCollector` 実装 - ツイート収集機能
9. `ActionExecutor` 実装 - アクション実行管理
10. `HumanBehaviorSimulator` 実装 - 人間行動シミュレーション
11. `ProcessManager` 実装 - プロセス管理
12. `TwitterBotOrchestrator` 軽量化

### **Phase 4: レガシー統合**
13. スケジューリングモジュール作成
14. `twitter_posting.py` のクラス移行
15. 統合テストと最適化

## 🧪 **テスト戦略**

### **単体テスト**
- 各新規モジュールの単体テスト作成
- 既存機能の回帰テスト実行
- モックを使用したインターフェーステスト

### **統合テスト**
- モジュール間の連携テスト
- 実際のTwitter環境での動作確認
- パフォーマンステスト

### **移行テスト**
- 段階的移行時の互換性確認
- 既存設定ファイルとの互換性テスト
- バックアップ・復旧手順の確認

## 📋 **後方互換性とマイグレーション**

### **後方互換性維持**
- 既存のAPIは段階的に非推奨化
- 移行期間中は新旧両方のAPIをサポート
- 明確な移行ガイドとサンプルコード提供

### **設定ファイルの移行**
- 既存の設定ファイル形式をサポート
- 新しい設定オプションは追加形式で提供
- 自動マイグレーションツールの提供

### **マイグレーション手順**
1. 新規モジュールの導入とテスト
2. 既存コードの段階的置き換え
3. 非推奨機能の段階的削除
4. 最終的なクリーンアップ

## 📈 **期待される効果**

### **保守性の向上**
- 各モジュールが単一責任を持つ
- テストしやすい小さなクラス群
- 独立した機能単位での開発・デバッグ

### **再利用性の向上**
- 他プロジェクトでの部分利用が可能
- Chrome起動機能は汎用ライブラリとして利用
- ログイン機能は他の自動化プロジェクトで再利用

### **拡張性の向上**
- 新しい機能の追加が容易
- 既存機能への影響を最小化
- プラグイン形式での機能拡張が可能

## 🔄 **継続的改善**

### **定期見直し**
- 四半期ごとのアーキテクチャ見直し
- パフォーマンス指標の監視
- ユーザーフィードバックの収集と反映

### **ドキュメント保守**
- 実装に合わせたドキュメント更新
- 使用例とベストプラクティスの追加
- トラブルシューティングガイドの充実

---

**最終更新日**: 2025-09-07  
**バージョン**: 1.0.0  
**ステータス**: Phase 1完了、Phase 2-4設計完了