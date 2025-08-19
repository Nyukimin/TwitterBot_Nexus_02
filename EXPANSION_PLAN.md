# システム拡張方針 v1.0

## 1. 目的と要件
- **目的**: 複数のXアカウントを同一システムで運用し、アカウントごとに「Like / リツイート / コメント(AI) / ブックマーク」を個別設定で実行できるようにする。
- **制約**:
  - 既存の単一アカウント実装と互換性を維持（段階的移行）。
  - WebDriverのバージョンチェックは起動時のみ行い、既存ドライバを再利用する [[memory:2279885]].
  - ログは `/log` 配下に集約し、Git追跡から除外する [[memory:2238773]].
  - 実行前に `conda activate TwitterReplyEnv` を徹底する [[memory:2213769]].
  - デバッグ時は原則ヘッドレス無効（目視確認） [[memory:2213753]].
  - AI返信は既存のスタイル・ガイドを踏襲し、`lang` パラメータ返却を維持する [[memory:2840411]]. 返信文では @mention やID呼びを避ける運用を継続する [[memory:2304233]].

## 2. 決定事項（アーキテクチャ）
- **多アカウント対応**: 新規 `config/accounts.yaml` でアカウントごとの設定を管理。`main.py` は後方互換、複数実行は新規 `multi_main.py` で制御。
- **セッション管理**: アカウントごとにChromeユーザープロファイル（`--user-data-dir`）を分離し、Cookieを保持。ログインの再実行を最小化。
- **ドライバ管理**: ドライバのバージョンチェックは起動時1回のみ。各アカウントの実行で同一ドライババイナリを再利用 [[memory:2279885]].
- **アクション抽象化**: `actions/` に Like / Retweet / Comment / Bookmark をモジュール化。統一IF: `run(driver, tweets, policy, rate_limits, dry_run)`。
- **ポリシーエンジン**: `policy_engine.py` を新設。ソース（mentions/my_threads）、各アクション条件（is_my_thread, reply_num 等）を宣言的に表現。
- **実行モード**: 既定はアカウント毎に順次実行。`--concurrency` で並列（上限N）を選択可能。初期値は1（安全重視）。
- **レート制御/冪等性**: アクション毎のレート上限、間隔、実行履歴による二重実行防止。
- **ログ/出力**: ログはアカウント識別子付きで `/log` 配下に出力（`[acct]`接頭辞 or サブフォルダ）。出力CSVは `processed_replies_{account}_{timestamp}.csv` に変更。
- **DB拡張**: 共通 `actions_log` テーブルでアクション履歴を管理（`account`, `tweet_id`, `action_type`, `status`, `ts`, `meta`）。`user_preferences` は `account` 列を追加してスコープ分離。
- **AI返信（コメント）**: 既存 `reply_processor.generate_reply` を再利用。各アカウントのペルソナ/プロンプトは `accounts.yaml` で切替。`lang` を返すI/Fを維持 [[memory:2840411]].

## 3. 設計変更の詳細
### 3.1 設定（新規ファイル）
- `config/accounts.yaml`
  - `accounts[].id`: 内部識別子
  - `accounts[].handle`: Xの@なしハンドル
  - `accounts[].browser.user_data_dir`: プロファイルディレクトリ
  - `accounts[].browser.headless`: 既定false（デバッグ優先） [[memory:2213753]]
  - `accounts[].ai`: `provider, api_key, model, persona_prompt_file`
  - `accounts[].features`: `like, retweet, comment, bookmark`（bool）
  - `accounts[].policies`: ソース/条件（例: `only_if_my_thread`, `reply_num_max`）
  - `accounts[].rate_limits`: 各アクション毎の/時 上限、アクション間隔秒
  - `accounts[].schedule`: 許可時間帯

### 3.2 データベース
- 新規: `actions_log(account TEXT, tweet_id TEXT, action_type TEXT, status TEXT, ts DATETIME, meta TEXT)`
- 変更: `user_preferences` に `account TEXT` 追加。既存データは `DEFAULT 'default'` で移行。

### 3.3 モジュール構成（追加/変更）
- 追加: `reply_bot/multi_main.py`（多アカウント制御）
- 追加: `reply_bot/actions/{like,retweet,comment,bookmark}.py`
- 追加: `reply_bot/policy_engine.py`
- 変更: `reply_bot/utils.py`（`setup_driver(profile_path, headless)` 受け取り）
- 変更: `reply_bot/csv_generator.py`（必要情報の抽出強化、ソース選択）
- 変更: `reply_bot/post_reply.py` → `reply_bot/actions/` に分割（後方互換の薄いラッパーを残置）

### 3.4 CLI/エントリポイント
- 既存: `python -m reply_bot.main`（単一アカウント、後方互換）
- 新規: `python -m reply_bot.multi_main --accounts all --actions like,comment --live-run --concurrency 1` 

## 4. 実装ステップ（段階的移行）
1) 基盤整備（設定/Orchestrator）
- `accounts.yaml` 読み込み、`multi_main.py` でアカウント単位の逐次実行
- `utils.setup_driver` に `profile_path` / `headless` を導入
- ログに `[acct]` 接頭辞を付与、CSV出力にアカウント名を付加

2) アクション分離/冪等化
- `actions/` 実装（最初は Like と Comment）
- `actions_log` 導入、二重実行防止とレート制御
- `reply_processor.generate_reply` を Commentから呼出

3) Retweet/Bookmark/ポリシー強化
- Retweet/Bookmark 追加
- `policy_engine` で条件表現を宣言的に統一
- `csv_generator` の抽出強化（必要メタを追加）

4) 並列実行・テスト
- `--concurrency` 実装（既定1、上限は環境に応じて）
- 統合テストとログ検証、ドキュメント更新

## 5. リスクと対策
- **UI変更によるセレクタ破綻**: セレクタ多重化・フェイルオーバー、詳細ログで早期検知
- **Rate Limit/制限**: レート設定を保守的に、待機挿入、アクション履歴で抑制
- **同時実行の競合**: 既定は順次実行。並列は上限Nとし、プロファイル分離で衝突回避
- **Cookie破損**: プロファイルごとにバックアップ、再ログイン手順を容易化

## 6. デフォルト運用ポリシー（初期提案）
- ソース: `mentions` + `my_threads`
- Like: `only_if_my_thread=True`, `reply_num_max=0`
- Retweet: `only_if_my_thread=True`, `require_media=False`
- Comment: 既存ポリシー踏襲（短文/言語一致/末尾❤️🩷、@mention回避） [[memory:2304233]]
- Bookmark: `only_if_my_thread=True`
- レート: Like 30/h, Retweet 10/h, Comment 10/h, Bookmark 60/h, 間隔7秒

## 7. 追加確認事項（実装前の最終確認）
- 運用するアカウント数と@ハンドル一覧
- 各アカウントのデフォルト機能ON/OFF、時間帯制限の要否
- Retweet/Bookmarkの条件（メディア必須など）
- コメントのペルソナ差分・プロンプト差分の要否
- 並列実行の可否（既定は逐次）

## 8. 付録（サンプルCLI）
```bash
# すべてのアカウントで Like + Comment をライブ実行（逐次）
conda activate TwitterReplyEnv
python -m reply_bot.multi_main --accounts all --actions like,comment --live-run --concurrency 1
```
