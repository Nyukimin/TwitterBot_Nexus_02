## 全体仕様 (v1.0)

### 目的と要件
- **目的**: 複数のXアカウントを同一システムで運用し、アカウントごとに「Like / リツイート / コメント(AI) / ブックマーク」を個別設定で実行可能にする。
- **制約**:
  - 既存の単一アカウント実装と互換性を維持（段階的移行）。
  - WebDriverのバージョンチェックは起動時のみ行い、同一バイナリを再利用。
  - ログは `/log` 配下に集約し、Git追跡から除外。
  - デバッグ時は原則ヘッドレス無効（目視確認）。
  - AI返信は既存スタイルガイド・I/F（`lang` 返却）を踏襲。

### アーキテクチャ（決定事項）
- **多アカウント対応**: `config/accounts.yaml` でアカウント別設定を管理。単体用 `reply_bot/main.py` は後方互換。複数実行は `reply_bot/multi_main.py`。
- **セッション管理**: アカウントごとに Chrome プロファイル（`--user-data-dir`）を分離してCookie/セッションを保持。再ログインを最小化。
- **ドライバ管理**: 起動時1回のみ `webdriver-manager` で取得し、同一ドライババイナリを使い回し。
- **アクション抽象化**: `reply_bot/actions/{like,retweet,comment,bookmark}.py` に分離。統一I/F: `run(driver, tweets, policy, rate_limits, dry_run)`。
- **ポリシーエンジン**: `reply_bot/policy_engine.py` で宣言的に条件（ソース、`only_if_my_thread`、`reply_num_max` 等）を表現。
- **冪等性/レート制御**: `actions_log` による二重実行防止とレート上限・間隔の制御。
- **ログ/出力**: ログにはアカウント識別子（`[acct]` 接頭）を付与。出力CSVは `processed_replies_{account}_{timestamp}.csv`。
- **DB拡張**: 共通 `actions_log(account TEXT, tweet_id TEXT, action_type TEXT, status TEXT, ts DATETIME, meta TEXT)` を新設。`user_preferences` に `account TEXT` を追加。
- **AI返信**: 既存 `reply_processor.generate_reply` を利用。各アカウントのペルソナ/プロンプトは `accounts.yaml` で切替。`lang` 返却I/Fを維持。

### 設定ファイル構造（`config/accounts.yaml`）
- `accounts[].id`: 内部識別子
- `accounts[].handle`: Xの@なしハンドル（システム内の `TARGET_USER` として使用）
- `accounts[].browser.user_data_dir`: Chromeユーザープロファイルパス
- `accounts[].browser.headless`: ヘッドレス実行フラグ（既定: false）
- `accounts[].ai`: `provider, api_key, model, persona_prompt_file`
- `accounts[].features`: `like, retweet, comment, bookmark`（bool）
- `accounts[].policies`: `sources, only_if_my_thread, reply_num_max` 等
- `accounts[].rate_limits`: `*_per_hour`, `min_interval_seconds`
- `accounts[].schedule`: 許可時間帯など

例:
```yaml
accounts:
  - id: default
    handle: "your_handle"
    browser:
      user_data_dir: "profile/default"
      headless: false
    ai:
      provider: "gemini"
      api_key: "${GEMINI_API_KEY}"
      model: "gemini-2.0-flash-lite"
      persona_prompt_file: null
    features:
      like: true
      retweet: false
      comment: true
      bookmark: false
    policies:
      sources: ["mentions", "my_threads"]
      only_if_my_thread: true
      reply_num_max: 0
    rate_limits:
      like_per_hour: 30
      retweet_per_hour: 10
      comment_per_hour: 10
      bookmark_per_hour: 60
      min_interval_seconds: 7
    schedule:
      allowed_hours: null
```

### データベース
- 既存: `replied`（投稿済み記録）、`user_preferences`（ユーザー別の好み）
- 追加（計画）:
  - `actions_log(account TEXT, tweet_id TEXT, action_type TEXT, status TEXT, ts DATETIME, meta TEXT)`
  - `user_preferences` に `account TEXT` 列（既存データは `DEFAULT 'default'`）

### モジュール構成
- 追加: `reply_bot/multi_main.py`
- 追加（計画）: `reply_bot/actions/{like,retweet,comment,bookmark}.py`, `reply_bot/policy_engine.py`
- 変更: `reply_bot/utils.py`（`setup_driver(profile_path, headless)`）, `reply_bot/csv_generator.py`（抽出強化）, `reply_bot/post_reply.py`（分割に向けた薄いラッパー）

### 実行エントリポイント
- 単体（後方互換）: `python -m reply_bot.main`
- 複数（新規）: `python -m reply_bot.multi_main --accounts all --actions like,comment --live-run --concurrency 1`

### デフォルト運用ポリシー（初期案）
- ソース: `mentions` + `my_threads`
- Like: `only_if_my_thread=True`, `reply_num_max=0`
- Retweet: `only_if_my_thread=True`, `require_media=False`
- Comment: 既存ポリシー踏襲（短文/言語一致/末尾❤️🩷、@mention回避）
- Bookmark: `only_if_my_thread=True`
- レート: Like 30/h, Retweet 10/h, Comment 10/h, Bookmark 60/h, 間隔7秒

### リスクと対策
- UI変更によるセレクタ破綻 → セレクタ多重化・フェイルオーバー、詳細ログ
- Rate Limit/制限 → 保守的レート、待機挿入、履歴抑制
- 同時実行競合 → 既定は逐次、プロファイル分離
- Cookie破損 → プロファイル単位でバックアップ、再ログイン手順

### ロードマップ
- ステップ1: 基盤整備（設定/オーケストレータ、プロファイル対応、ログ/CSVにアカウント識別）
- ステップ2: アクション分離と冪等化（`actions/`、`actions_log`）
- ステップ3: Retweet/Bookmark追加、`policy_engine` 強化、抽出強化
- ステップ4: 並列実行（`--concurrency`）、統合テスト・ドキュメント整備
