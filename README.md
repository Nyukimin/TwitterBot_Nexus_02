# Twitter自動返信ボット (v0.95)

## 概要
このシステムは、あなた（@nyukimi_AI）のX（旧Twitter）アカウントのツイートに対する他ユーザーからのリプライを自動的に検出し、AI（「Maya」）が文脈を理解した応答文を生成・投稿することを目的としています。**システムのコアは `reply_processor.py` に集約されており、単なる返信だけでなく、会話の文脈全体を考慮したインテリジェントな対話を実現します。**

---

## バージョン履歴

### **v0.95 (現在)**: 挨拶バリエーション機能の追加
- **挨拶重複回避システム**: `greet: auto` 設定において、当日同じユーザーへの重複挨拶を自動回避する機能を実装。2回目以降は豊富なバリエーションから選択されるため、より自然な交流が可能になりました。
- **挨拶追跡システム** (`greeting_tracker.py`): ファイルベースの軽量記録システムで、ユーザー別・挨拶タイプ別の送信履歴を当日限定で管理。日付変更時に自動リセット。
- **多様な挨拶パターン**:
  - **初回**: 標準的な挨拶（`おはよう🩷`、`こんにちは🩷` など）
  - **2回目以降**: バリエーション豊富な挨拶（`今日も素敵な1日を🩷`、`お疲れさまです🩷` など）
- **時刻・言語対応**: 時間帯と相手のツイート言語を自動判定し、適切な挨拶を選択

### **v0.94**: インテリジェント返信処理への進化
- **アーキテクチャ刷新**: `thread_checker.py`と`gen_reply.py`を廃止し、スレッド解析、AIによる返信生成、投稿前チェックの全機能を`reply_bot/reply_processor.py`に統合。処理が効率化され、モジュール間の依存関係が簡潔になりました。
- **AIの文脈理解能力の向上**: AIにスレッド全体の会話履歴を渡すことで、より文脈に沿った自然な返信が可能になりました。
- **返信の多様性向上**:
    - **動的禁止ワード**: AIが自己模倣に陥るのを防ぐため、過去の返信で使われた動詞・形容詞を「禁止ワード」として動的にプロンプトへ追加する機能を実装。
    - **定型文の拡充**: 短い挨拶や外国語への返信が単調にならないよう、複数パターンの感謝フレーズを`config.py`で管理し、ランダムに選択して使用するように改善。
- **堅牢な投稿ルール**:
    - **最優先返信ルール**: 「自分のスレッドへの最初の返信(`reply_num=0` and `is_my_thread=True`)」には、後続ツイートがあっても必ず返信するルールを実装。判定はCSVの情報ではなく、処理実行時の**ライブ情報**で行われます。
    - **ライブ情報のCSV反映**: スキップされたツイートについても、スキップ判断の根拠となったライブの「返信件数」「いいね数」を最終的なCSVに記録し、データの正確性を向上させました。

### **v0.9**: 重複投稿チェック機能の堅牢化
- **動的な重複投稿チェック**: `post_reply.py`に、返信対象のツイートページを直接開き、そのツイートよりも**後**に誰かの返信が既に存在するかをリアルタイムで確認する機能を追加。後続の返信がある場合は会話への割り込みと判断し、投稿をスキMップするようにしました。

### **v0.8**: 基本機能の実装
- **パイプライン処理**: `csv_generator` -> `thread_checker` -> `gen_reply` -> `post_reply`という、各機能が独立したモジュールとしてCSVファイルを介して連携するアーキテクチャでした。
- **基本的な返信機能**: 自分のスレッド(`is_my_thread=True`)への返信に対して、AIが応答を生成し、投稿する基本機能を実装していました。

---

## 🚀 主要機能一覧

### 🤖 **1. インテリジェント自動返信システム**
- **スレッド文脈理解**: AIが会話の流れを読み解き、自然な応答を生成 (`reply_processor.py`)
- **多様な返信ロジック**:
    - **ニックネーム呼びかけ**: `accounts.yaml`の`per_target`設定で顔なじみユーザーにニックネーム付き返信
    - **🆕 スマート挨拶システム**: `greet: auto` 設定での重複回避機能。同日同一ユーザーへの2回目以降は自動的にバリエーション豊富な挨拶に切り替え
    - **多言語対応の定型文**: 短い挨拶・絵文字のみツイートに言語判定＋複数パターンから選択
    - **自己模倣防止**: 過去返信で多用した表現を禁止ワードとして動的に回避
- **堅牢な投稿管理**:
    - **ライブ情報による重複チェック**: 会話割り込み厳密判定
    - **最優先ルール**: 自分スレッドへの初リプライは確実返信
    - **状態管理**: 重複いいね・投稿防止

### 🎯 **2. ターゲットユーザーへのあいさつ回り機能**
- **`per_target`システム**: 各ユーザー個別の対応設定（ニックネーム・アクション・あいさつ）
- **🆕 挨拶バリエーション機能**: `greet: auto` 設定で当日の重複挨拶を自動回避。時刻・言語・送信履歴に基づく適切な挨拶選択
- **事前閲覧機能** (`per_target_prefetch`): ターゲットの最新ツイートを事前チェック
- **自動アクション実行**: like・comment・bookmark・retweetを自動実行
- **人間らしい動作**: 閲覧パターン・滞在時間・間隔のランダム化

### 🌐 **3. 多アカウント並列運用**
- **複数アカウント同時動作**: 各アカウント独立設定・並列実行
- **プロファイル管理**: アカウント別Chromeプロファイル自動管理
- **ログイン支援**: ユーザー名自動入力・手動ログイン補助 (`login_assist.py`)
- **セッション管理**: Cookie保存・復元による認証維持

### 📊 **4. 高度なデータ収集・分析**
- **通知ページ監視**: メンション・返信自動抽出 (`csv_generator.py`)
- **スレッド解析**: 会話全体の文脈・関係性分析
- **ライブ情報取得**: リアルタイムのいいね数・返信数・UI状態検出
- **統合返信検出**: 複数手法による返信判定エンジン (`reply_detection_unified.py`)

### 🛠️ **5. WebDriver安定化・エラー処理**
- **自動再起動機能**: セッション無効・メモリリーク検出時の自動回復
- **プロファイルロック**: 同時起動防止・競合回避 (`profile_lock.py`)
- **堅牢なエラー処理**: タイムアウト・例外からの自動復旧
- **メモリ監視**: 使用量監視・閾値超過時の自動対処

### 🔒 **6. セキュリティ・プライバシー**
- **X API不使用**: Selenium活用によるコスト効率・API制限回避
- **ローカル処理**: 全データはローカル処理・外部送信なし
- **Cookie暗号化**: 認証情報の安全な保存・管理
- **重複防止**: DB不使用でもUI状態による冪等性担保

## 技術スタック
- Python
- `selenium` / `webdriver-manager`
- `BeautifulSoup`
- `google-generativeai` (Gemini)
- （DB依存なし）
- `pandas`

## ディレクトリ構成
```
Twitter_reply/
├── reply_bot/
│   ├─ main.py            # 全体制御スクリプト
│   ├─ csv_generator.py   # Selenium を使ったリプライ収集ロジック
│   ├─ reply_processor.py # ★(New) スレッド分析・返信生成・ルール適用のコアモジュール
│   ├─ greeting_tracker.py # ★(New) 挨拶重複回避・バリエーション管理システム
│   ├─ post_reply.py      # 返信投稿と「いいね」を実行
│   ├─ add_user_preferences.py # ユーザー設定をDBに一括登録
│   ├─ config.py          # 各種設定（アカウント情報、APIキーなど）
│   ├─ db.py              # SQLite データベース操作
│   ├─ get_cookie.py      # Cookieの保存と読み込み
│   └─ requirements.txt   # 依存ライブラリ
├── cookie/
├── log/
├── source/
├── output/
└── .gitignore
```
*`thread_checker.py` と `gen_reply.py` は `reply_processor.py` に統合され、廃止されました。*

## セットアップと実行

### 1. Conda環境のアクティベート
```bash
conda activate TwitterReplyEnv
```

### 2. 依存ライブラリのインストール
```bash
pip install -r reply_bot/requirements.txt
```

### 3. `config.py` の設定
`reply_bot/config.py` に、Xのアカウント情報やGemini APIキーなどを設定します。
```python
# reply_bot/config.py の例
TARGET_USER = "nyukimi_AI"
LOGIN_URL = "https://x.com/login"
USERNAME = "..."
PASSWORD = "..."
GEMINI_API_KEY = "..."
（DBファイルは使用しません）

### DBについて

- 本ツールはDBを使用しません。冪等性はUI検出（既に実施済みのUI状態や自アカウントの返信有無）で担保します。

# 多言語対応の感謝フレーズ
THANK_YOU_PHRASES = {
    "en": ["thanks❤", "Thank you so much!❤", "I appreciate it!❤", "Thanks a lot!❤"],
    "es": ["Gracias❤", "¡Muchas gracias!❤", "Te lo agradezco❤", "¡Mil gracias!❤"],
    # ... 他の言語も同様に複数パターンを定義 ...
}
```

### 4. Cookieの取得と保存
初回実行時のみ、以下のコマンドで手動ログインし、Cookieを保存します。
```bash
python -m reply_bot.get_cookie
```

### 5. ユーザー設定の初期登録（任意）
```bash
python -m reply_bot.add_user_preferences
```

### 6. スクリプトの実行
全てのセットアップが完了したら、`main.py` を実行します。
```bash
python -m reply_bot.main
```
デフォルトでは、投稿や「いいね」を行わない**ドライランモード**で実行されます。実際に投稿するには `--live-run` フラグを追加します。
```bash
python -m reply_bot.main --live-run
```

### 7. 定期実行設定
`cron`（Linux/macOS）やタスクスケジューラ（Windows）で定期的に実行するよう設定します。
```cron
# 毎時0分に main.py をライブモードで実行
0 * * * * cd /path/to/Twitter_reply && /path/to/conda/envs/TwitterReplyEnv/bin/python -m reply_bot.main --live-run >> /path/to/Twitter_reply/log/cron.log 2>&1
```

## 出力ファイル
`/output` フォルダに、処理結果のCSVファイル (`replies_YYYYMMDD_HHMMSS.csv`) が生成されます。このファイルには、収集したツイート、生成した返信、AIの思考プロセス、投稿結果などがすべて記録されます。

---

## CLI 実行方法と引数（最新版）

### 1) 多アカウント・直接アクション実行（推奨）
人間らしさモードや事前閲覧を含め、`accounts.yaml` の `features`/`policies` に従って like・comment 等を実行します。

- コマンド
```bash
python -m reply_bot.multi_main [--accounts <id_or_handle_csv>|all] [--live-run] [--hours N] [--concurrency 1] [--config config/accounts.yaml]
```

- 引数
  - `--accounts`: 実行対象アカウント。id または handle のカンマ区切り。省略/`all` は全アカウント。
  - `--live-run`: 実操作を有効化（省略時はドライラン）。
  - `--hours`: 旧パイプラインでの収集対象時間。直接アクション時は未使用。
  - `--concurrency`: 予約（現状逐次のみ）。
  - `--config`: `accounts.yaml` のパス（デフォルト `config/accounts.yaml`）。

- 例
```bash
python -m reply_bot.multi_main --accounts Maya19960330 --live-run
```

- 補足
  - `policies.human_like_on_start` が有効なら、起動直後に人間らしい閲覧（open/dwell）を実施。
  - `policies.per_target_prefetch` が有効なら、対象ユーザーごとに `top_n` 件を事前閲覧し、その全ツイートへ `actions`（例: like, comment）を実行。
  - `policies.tweet_selection.top_n` と `user_switch_interval_seconds` で、各対象の件数と切替待機を制御。

### 2) 単一ターゲットに直接アクション
対象ユーザーの最新ツイートに対して、指定のアクションを実行します。

- コマンド
```bash
python -m reply_bot.operate_latest_tweet --account <acct> --target <handle> [--actions like,comment] [--config config/accounts.yaml] [--live-run]
```

- 引数
  - `--account`: 実行アカウント（id または handle）。
  - `--target`: 対象ユーザーの handle（@なし）。
  - `--actions`: 実行アクションのカンマ区切り（`like,bookmark,retweet,comment`）。
  - `--config`: `accounts.yaml` のパス。
  - `--live-run`: 実操作を有効化（省略時はドライラン）。

- 例
```bash
python -m reply_bot.operate_latest_tweet --account Maya19960330 --target 2nd_karen_ai --actions like,comment --live-run
```

### 3) ログイン支援（任意）
ユーザー名のプレフィルを行い、手動ログインを補助します。

```bash
python -m reply_bot.login_assist [--accounts <id_or_handle_csv>|all] [--config config/accounts.yaml]
```

### 4) 旧パイプライン（抽出→分析/生成→投稿）
必要に応じて従来の一連の処理も単体実行できます。

- 全体（メインコントローラー）
```bash
python -m reply_bot.main [--timestamp YYYYMMDD_HHMMSS] [--hours N] [--live-run]
```

- リプライ抽出
```bash
python -m reply_bot.csv_generator [--output <path>] [--scrolls N] [--pixels N] [--hours N]
```

- 返信生成（スレッド解析）
```bash
python -m reply_bot.reply_processor input_csv [--limit N]
```

- 返信投稿
```bash
python -m reply_bot.post_reply input_csv [--limit N] [--interval SEC] [--live-run]
```


アカウント登録（ログインプロファイル作成）コマンド
使用例
```bash
python -m reply_bot.login_assist --config <設定ファイルパス> --accounts <アカウントID>
```
例えば、config/accounts.yaml に定義されている Maya19960330 というアカウントのログインプロファイルを作成したい場合：
```bash
python -m reply_bot.login_assist --config .\config\accounts_Maya19960330.yaml --accounts Maya19960330
```
コマンドの説明
--config <設定ファイルパス>: 使用する accounts.yaml ファイルのパスを指定します。
--accounts <アカウントID>: ログインプロファイルを作成したいアカウントの id を指定します。
注意点
このコマンドを実行すると、指定されたアカウントのプロファイルでChromeブラウザが起動します。
初回のみ、手動でTwitterにログインしてください。
ログイン後、ブラウザを閉じるとログイン状態がプロファイルに保存されます。
以前使用されていた add_user_preferences.py はデータベースの削除に伴い廃止されました。アカウントの設定（ニックネームなど）は accounts.yaml 内の policies.per_target セクションで直接管理するようになっています。


動作開始コマンド
使用例
```bash
python -m reply_bot.multi_main --config <設定ファイルパス> --live-run
```
例えば、config/accounts.yaml に定義されているアカウント群を動作させたい場合：
```bash
python -m reply_bot.multi_main --config .\config\accounts_Maya19960330.yaml --live-run
```
コマンドの説明
--config <設定ファイルパス>: 使用する accounts.yaml ファイルのパスを指定します。
--live-run: このフラグを付けることで、実際にアクションが実行されます。このフラグがない場合（ドライランモード）、ログに記録されるだけで実際のアクションは行われません。
その他のオプション（必要に応じて）
--accounts <アカウントID1> [<アカウントID2> ...]: 特定のアカウントのみを動作させたい場合に、アカウントIDをスペース区切りで指定します。
例: --accounts Maya19960330 ren_ai_coach
--target-users <ユーザーハンドル1> [<ユーザーハンドル2> ...]: 特定のターゲットユーザーに対してのみアクションを実行したい場合に、ユーザーハンドルをスペース区切りで指定します。
例: --target-users AIchan_lovelyAI
--headless: accounts.yaml で headless: false に設定されているアカウントでも、このフラグを付けると強制的にヘッドレスモードで実行されます。
並列動作の場合
複数の accounts.yaml ファイル（例: accounts_A.yaml, accounts_B.yaml）を用意し、それぞれ別々のターミナルで上記のコマンドを実行します。
```bash
# ターミナル1
python -m reply_bot.multi_main --config .\config\accounts_nyukimi_06.yaml --live-run

# ターミナル2
python -m reply_bot.multi_main --config .\config\accounts_nyukimi_08.yaml --live-run
```
これで、設定した自動操作を開始できます。

