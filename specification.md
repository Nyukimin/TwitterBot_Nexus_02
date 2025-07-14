# Maya自動返信ボット 仕様書 (v0.96)

## 1. 目的
本システムは、X（旧Twitter）上で「Maya（@Maya19960330）」アカウントに届いたメンション（リプライ）に対し、**スレッド全体の文脈を理解した**AIによる返信を生成し、適切なルールに基づいて自動投稿することを目的とします。

## 2. システムアーキテクチャ (v0.96)
v0.95のアーキテクチャを維持しつつ、返信判定アルゴリズムと投稿処理ロジックを改善しました。**全ツイートへの確実な「いいね」処理**と**返信コメント存在時の必須返信**を実現します。

```mermaid
graph TD;
    subgraph "事前準備"
        AA(add_user_preferences.py) --> DB[(user_preferences DB)];
    end

    A[Start] --> B(1. csv_generator.py);
    B -- DataFrame --> C(2. reply_processor.py);
    DB -.-> C;
    C -- DataFrame --> D(3. post_reply.py);
    D -- DataFrame --> E(4. utils.save_results_to_csv);
    E --> F[End];

    subgraph "制御"
        G(main.py)
    end

    G -.-> B;
    G -.-> C;
    G -.-> D;
    G -.-> E;
```

---

## 3. モジュール詳細

### ステップ0: ユーザー情報登録 (`add_user_preferences.py`)
- **役割**: 特定ユーザーのニックネーム等を事前にDBに登録します。
- **変更点**: 変更なし。

### ステップ1: リプライ収集 (`csv_generator.py`)
- **役割**: Seleniumで通知ページからメンションを収集します。
- **出力**: `extracted_tweets_{タイムスタンプ}.csv` は廃止され、収集結果をPandas DataFrameとして後続の`reply_processor`に直接返します。
- **設定変更**: `HOURS_TO_COLLECT = 24` (24時間前までのリプライを収集)

### ステップ2: 返信処理 (`reply_processor.py`) - ★改善・コアモジュール
- **役割**: スレッド分析、ルール適用、AIによる返信文生成までの一連の処理を担います。
- **入力**: `csv_generator.py`から受け取ったDataFrame、`replies.db`
- **処理フロー**:
    1. **★改善された返信判定**: `_is_tweet_a_reply`関数の精度向上
        - **問題解決**: `[data-testid*="reply"]`セレクタが返信ボタンを誤検出していた問題を修正
        - **厳密化**: `[data-testid="inReplyTo"]`による正確な返信先表示のみを検出
        - **@メンション検出の制限**: ツイート本文外かつ返信関連キーワードと組み合わされた場合のみ
        - **結果**: 全ツイートが返信として誤判定される問題を解決
    2. **スレッド起点判定**: 改善された返信判定により、`is_my_thread`の精度が向上
    3. **返信生成ロジック**: `is_my_thread` が `True` のリプライに対してのみ返信生成
        - **AIモデル**: Gemini 2.0 Flash Lite
        - **短い返信方針**: 複雑な感情表現を排除し、Mayaらしい短文返信を生成
        - **言語一致**: 相手が使っている言語に合わせて返信
    4. **いいね対象の拡張**: `is_my_thread=False`のツイートは返信生成せず空文字を設定
- **出力**: 処理結果を2つのCSVファイルに分割出力
    - **成功ファイル**: `processed_replies_{タイムスタンプ}.csv`
    - **失敗ファイル**: `failed_selfcheck_{タイムスタンプ}.csv`

### ステップ2.5: 返信品質のセルフチェック
返信生成対象ツイート（`is_my_thread=True`）について、以下のチェックを実行：

#### チェック項目
1. **言語チェック**: 生成された返信が元ツイートの言語と一致しているか
2. **ニックネームチェック**: DBに登録されたニックネームが正しく付与されているか
3. **禁止フレーズチェック**: 動的禁止フレーズが含まれていないか
4. **フォーマットチェック**: 空文字列でなく、末尾に🩷が付与されているか
5. **AIによる自己評価**: ルール遵守の再確認

### ステップ3: 投稿処理 (`post_reply.py`) - ★大幅改善
- **入力**: `reply_processor.py`から受け取った`processed_replies_{タイムスタンプ}.csv`のパス
- **★重要な変更点**:
    
    **改善前の問題**:
    ```python
    # 問題のあった絞り込み（is_my_thread=Falseが除外される）
    replies_to_process = df[df['generated_reply'].notna()].copy()
    ```
    
    **改善後の解決策**:
    ```python
    # 全ツイートを処理対象とする
    replies_to_process = df.copy()
    ```

- **処理ロジック**:
    - **全ツイートに対する「いいね」処理**: 
        - `is_my_thread`の値に関係なく、未いいねの場合は必ず実行
        - 既にいいね済みの場合はスキップ
    - **返信処理**: 
        - `generated_reply`が存在する（空でない）場合のみ実行
        - 重複チェック後に投稿
- **出力**: `liked`, `posted`, `status`などの実行結果を追記したDataFrameを返します。

### ステップ4: 結果保存
`reply_processor.py`は、処理の最後に以下の2種類のCSVファイルを`output/`ディレクトリに出力：

1. **`processed_replies_{タイムスタンプ}.csv`（処理結果ログ）**
   - セルフチェック通過済みの返信コメント
   - `is_my_thread=False`のツイート（返信コメントなし、いいね対象）

2. **`failed_selfcheck_{タイムスタンプ}.csv`（失敗分析用データ）**
   - セルフチェックで不合格となったツイートのみ

---

## 4. 設定ファイルとデータベース

### 設定ファイル (`config.py`)
- `TARGET_USER = "Maya19960330"`: 対象アカウント
- `GEMINI_MODEL_NAME = "gemini-2.0-flash-lite"`: 使用AIモデル
- `HOURS_TO_COLLECT = 24`: 収集対象期間（24時間）
- `POST_INTERVAL_SECONDS = 7`: 投稿間隔（7秒）
- **`MAYA_PERSONALITY_PROMPT`**: 短文・自然な返信を重視したプロンプト
  - 相手の言語に合わせた返信
  - 15-35文字前後の短文
  - 感情表現は適度に、説教調禁止

### データベース (`replies.db`)
- **`user_preferences`テーブル**: ユーザーニックネーム管理

---

## 5. v0.96の主要改善点

### 🔧 返信判定アルゴリズムの精密化

#### **旧ロジックの問題 (v0.95まで)**
```python
# 問題のあった実装
reply_indicators = ['[data-testid*="reply"]']  # 返信ボタンを誤検出
parent_indicators = article.find_all(['span', 'div'], string=re.compile(r'@\w+'))
if len(parent_indicators) > 1: return True  # 過度に広範囲な@メンション検出
```
- 全ツイートが返信として誤判定される
- スレッド先頭検出の失敗
- 返信生成の高い失敗率

#### **新ロジックの解決策 (v0.96)**
```python
# 改善された実装
reply_indicators = [
    '[data-testid="inReplyTo"]',        # 正確な返信先表示のみ
    '[aria-label*="Replying to"]'       # 返信先を示すaria-label
]

# ツイート本文外かつ返信関連キーワード併用時のみ@メンション検出
if (tweet_text_div and elem in tweet_text_div.descendants): continue
if any(keyword in parent_text.lower() for keyword in ['replying', '返信', ...]):
    parent_indicators.append(elem)
```

### 🎯 投稿処理ロジックの全面改善

#### **旧ロジックの問題**
- `generated_reply`が空の場合、処理対象から完全除外
- `is_my_thread=False`のツイートに「いいね」されない

#### **新ロジックの解決策**
- **全ツイート処理**: `is_my_thread`の値に関係なく全ツイートを処理対象
- **条件分岐処理**: 
  - **いいね**: 全ツイートで未実施の場合実行
  - **返信**: `generated_reply`存在時のみ実行

### 🔍 期待される効果
1. **返信判定精度の向上**: 誤った返信判定を大幅に削減
2. **確実ないいね処理**: 全対象ツイートへの適切ないいね実行
3. **返信成功率の向上**: 正確なスレッド分析による適切な返信生成
4. **処理の透明性**: 詳細なログによる動作の可視化

---

## 6. フォルダ構成
```
Twitter_reply/
├── reply_bot/
│   ├── main.py
│   ├── csv_generator.py
│   ├── reply_processor.py  # (Improved) Core module
│   ├── post_reply.py       # (Major update) Fixed logic
│   ├── add_user_preferences.py
│   ├── utils.py
│   ├── config.py           # (Updated) Model and settings
│   └── db.py
├── cookie/
├── output/
│   ├── processed_replies_YYYYMMDD_HHMMSS.csv  # 成功ファイル
│   └── failed_selfcheck_YYYYMMDD_HHMMSS.csv   # 失敗ファイル
├── log/                    # (New) Debug log directory
│   ├── thread_debug.log
│   ├── reply_judgment.log
│   ├── thread_owner_judgment.log
│   └── main_process.log
└── requirements.txt
```

---

## 7. 運用フロー

### 基本的な実行手順
1. **データ収集**: `csv_generator.py`で24時間以内のメンション収集
2. **返信生成**: `reply_processor.py`でスレッド分析・返信生成・セルフチェック
3. **投稿実行**: `post_reply.py`でいいね・返信投稿
4. **結果確認**: ログファイルと出力CSVで処理結果を確認

### トラブルシューティング
- **いいねされない**: `post_reply.py`の処理対象絞り込みを確認
- **返信生成失敗**: `log/`ディレクトリの詳細ログを確認
- **スレッド分析エラー**: `thread_debug.log`でスレッド取得状況を確認