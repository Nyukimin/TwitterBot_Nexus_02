## 実装状況（2025-08-19時点）

### 進捗サマリ
- ステップ1の主要項目（基盤整備）を実装済み。`accounts.yaml` 読み込み、`multi_main.py` によるアカウント逐次実行、Chromeプロファイル分離、ドライバの起動時1回チェック・再利用、ログ/CSVのアカウント識別を導入。
- ステップ2以降（`actions/` 分離、`actions_log`、`policy_engine`、並列実行など）は未実装。

### 完了項目（実装済み）
- **設定/オーケストレータ**:
  - 新規 `config/accounts.yaml`（最小構成）
  - 新規 `reply_bot/multi_main.py`（逐次オーケストレーション、`[acct]` ログ接頭、`TARGET_USER` の動的切替、アカウント別CSV）
- **WebDriver/セッション**:
  - `reply_bot/utils.py` に `setup_driver(headless, profile_path)` を導入
  - `--user-data-dir` でアカウントごとにプロファイル分離（プロファイル使用時はCookie注入をスキップして `https://x.com/home` ロード）
  - 起動時1回のみ `ChromeDriverManager().install()` を実行し、同一バイナリを再利用
  - `force_restart_driver(headless, profile_path)` で直近のプロファイルを引き継いで再起動
- **ログ/出力**:
  - ログに `[acct]` 接頭辞を付与（ファイル出力含む）
  - 抽出CSV: `extracted_tweets_{account}_{timestamp}.csv`
  - 処理済みCSV: `processed_replies_{account}_{timestamp}.csv`（既存命名ロジックを踏襲しつつアカウント名が反映される）
- **既存コードの整合**:
  - `reply_bot/csv_generator.py` と `reply_bot/reply_processor.py` の `TARGET_USER` 参照をランタイムの設定値に変更（ハードコード排除）
  - `reply_bot/post_reply.py` の未使用 `TARGET_USER` import を削除
- **依存追加**:
  - `reply_bot/requirements.txt` に `PyYAML` を追加

### 変更ファイル一覧
- 追加: `reply_bot/multi_main.py`, `config/accounts.yaml`
- 変更: `reply_bot/utils.py`, `reply_bot/csv_generator.py`, `reply_bot/reply_processor.py`, `reply_bot/post_reply.py`, `reply_bot/requirements.txt`

### 未実装/残課題（次フェーズ）
- **アクション分離/冪等化**: `reply_bot/actions/{like,retweet,comment,bookmark}.py`、`actions_log` テーブル、二重実行防止とレート制御
- **ポリシーエンジン**: `reply_bot/policy_engine.py` による宣言的条件設定と適用
- **機能拡張**: Retweet/Bookmark の実装と統合
- **DB拡張**: `user_preferences` に `account` 列追加＆移行（`DEFAULT 'default'`）
- **並列実行**: `--concurrency` > 1 の安全な実装（プロファイル分離・競合回避・レート考慮）
- **ログ運用**: `/log` ディレクトリのGit除外設定（.gitignore）
- **AI/ペルソナ**: `accounts.yaml` の `ai.*` を実動に反映（アカウント別プロンプト/モデル切替）

### 実行と検証（現状）
- 依存インストール（初回/環境再構築時）:
```bash
conda activate TwitterReplyEnv
pip install -r reply_bot/requirements.txt
```
- ドライラン（逐次・全アカウント）:
```bash
python -m reply_bot.multi_main --accounts all --concurrency 1
```
- ライブ実行（実際に投稿・いいねを行う）:
```bash
python -m reply_bot.multi_main --accounts all --live-run --concurrency 1
```
- 事前要件: `config/accounts.yaml` の `browser.user_data_dir` が実在し、対象アカウントでChromeログイン済みであること。

### 既知の注意/リスク
- 依存未導入時は linter が `selenium`/`yaml` 等の import 警告を出す（依存導入で解消）
- XのUI変更でセレクタが破綻し得る（ログで早期検知、選択子の冗長化が必要）
- 並列実行は未実装のため、現状は逐次のみを推奨

### 次のステップ（提案）
- ステップ2: `actions/` 最小実装（Like/Comment）＋ `actions_log`（idempotency）
- ステップ3: Retweet/Bookmark と `policy_engine` 導入、抽出メタ拡充
- ステップ4: `--concurrency` 実装と統合テスト、ドキュメント更新
