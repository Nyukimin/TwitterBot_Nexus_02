# Twitter自動返信ボット (v0.94)

## 概要
このシステムは、あなた（@nyukimi_AI）のX（旧Twitter）アカウントのツイートに対する他ユーザーからのリプライを自動的に検出し、AI（「Maya」）が文脈を理解した応答文を生成・投稿することを目的としています。**システムのコアは `reply_processor.py` に集約されており、単なる返信だけでなく、会話の文脈全体を考慮したインテリジェントな対話を実現します。**

---

## バージョン履歴

### **v0.94 (現在)**: インテリジェント返信処理への進化
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

## 主な機能
- **X API不使用**: `selenium` を活用し、コストをかけずに運用します。
- **リプライ・ツイート取得**: 通知ページからメンションを抽出し、分析のベースとなるデータを作成します。
- **インテリジェントな返信生成 (`reply_processor.py`)**:
    - **スレッド文脈理解**: 会話全体の流れを読み解き、AIが自然な応答を生成します。
    - **多様な返信ロジック**:
        - **ニックネーム呼びかけ**: DB登録済みの「顔なじみ」ユーザーにはニックネームで呼びかけます。
        - **多言語対応の定型文**: 短い挨拶や絵文字のみのツイートには、言語を判定し、`config.py`に定義された複数の定型フレーズからランダムに返信します。
        - **自己模倣防止**: 過去の返信で多用した表現を避け、常に新鮮な言葉で応答します。
- **堅牢な自動投稿 (`post_reply.py`)**:
    - **ライブ情報に基づく重複投稿チェック**: ページの**ライブ情報**を元に、会話への割り込みを厳密に判定し、不要な投稿をスキップします。
    - **最優先ルールの適用**: 「自分のスレッドへの初リプライ」という最重要ケースを見逃さずに返信します。
    - **状態管理による重複「いいね」防止**: 「いいね」の状態をCSVで管理し、重複アクションを防ぎます。
- **ユーザー設定**: DBは廃止。ニックネームなどは `accounts.yaml` の `policies.per_target` で管理します。
- **定期実行**: `cron`等で1時間ごとに自動実行される設計です。

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

