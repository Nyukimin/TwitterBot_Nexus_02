# Text Processing Utilities

感情コンテンツ抽出とテキスト処理のためのユーティリティパッケージ

## 📋 概要

`text_processing_utils`は、占星術テキストから感情的なコンテンツを抽出し、AI画像生成プロンプトなどに適用するためのPythonパッケージです。

### 主な機能

- **感情コンテンツ抽出**: 占星術記述を除去し、感情的・心理的内容のみを抽出
- **テキスト前処理**: 日本語テキストの高度な正規表現処理
- **感情キーワード分析**: 感情関連キーワードの自動検出と分類

## 🚀 インストール

### pip経由でのインストール

```bash
pip install text-processing-utils
```

### ソースからのインストール

```bash
git clone https://github.com/Nyukimin/TwitterBot_Nexus_02.git
cd TwitterBot_Nexus_02/extracted_modules/text_processing_utils
pip install -e .
```

## 💡 使用例

### 基本的な使用方法

```python
from text_processing_utils import extract_emotional_content

# 占星術テキストから感情コンテンツのみを抽出
text = "今日は月が魚座に入る。感受性が高まりやすい日。人の気持ちに寄り添って過ごそう。"
result = extract_emotional_content(text)

print(result)
# 出力: "感受性が高まりやすい日。人の気持ちに寄り添って過ごそう。"
```

### より複雑な例

```python
from text_processing_utils.emotion_extraction import extract_emotional_content

# 複数の占星術記述を含むテキスト
complex_text = """
今日は水星逆行開始。コミュニケーションに注意。
心を落ち着けて丁寧に対話しよう。
深呼吸して自分の心と向き合ってみて。
"""

emotional_content = extract_emotional_content(complex_text)
print(emotional_content)
# 出力: "心を落ち着けて丁寧に対話しよう。深呼吸して自分の心と向き合ってみて。"
```

### AI画像生成プロンプトとしての活用

```python
from text_processing_utils import extract_emotional_content

# 占星術ツイートから画像生成プロンプト用テキストを作成
astrology_tweet = "今日は満月のエネルギーが強い日。感情が高ぶりやすい時期。心穏やかに過ごそう。"
prompt_text = extract_emotional_content(astrology_tweet)

# AI画像生成に使用
image_prompt = f"A serene Japanese woman expressing: {prompt_text}"
print(image_prompt)
# 出力: "A serene Japanese woman expressing: 感情が高ぶりやすい時期。心穏やかに過ごそう。"
```

## 📚 API リファレンス

### `extract_emotional_content(text: str) -> str`

テキストから感情的なコンテンツを抽出します。

#### パラメータ

- `text` (str): 処理対象のテキスト

#### 戻り値

- `str`: 抽出された感情コンテンツ

#### 処理内容

1. **占星術記述の除去**: 「今日は〜座に」などの占星術特有の表現を除去
2. **感情キーワード検出**: 感情・心理関連のキーワードを含む文を優先抽出
3. **文章の再構築**: 自然な文章として再構築

#### 対応する占星術用語

- 星座名（牡羊座、牡牛座、双子座...）
- 天体名（月、太陽、水星、金星...）
- 占星術現象（逆行、順行、トランジット、新月、満月...）

#### 抽出される感情キーワード

- **感情表現**: 感情、気持ち、心、感受性、共感
- **癒し系**: 寄り添、優しさ、温かさ、癒し、安らぎ
- **心理状態**: 穏やか、静か、リラックス、落ち着き
- **ネガティブ**: 不安、心配、緊張、ストレス、疲れ
- **ポジティブ**: 喜び、幸せ、愛、思いやり、希望

## 🧪 テスト

```bash
# パッケージのテストを実行
python -m text_processing_utils.emotion_extraction

# または開発用テストの実行
pip install -e ".[test]"
pytest
```

## 🔧 開発

### 開発環境のセットアップ

```bash
# 開発用依存関係のインストール
pip install -e ".[dev]"

# コード品質チェック
flake8 text_processing_utils/
black text_processing_utils/
mypy text_processing_utils/
```

### プロジェクト構造

```
text_processing_utils/
├── text_processing_utils/
│   ├── __init__.py
│   └── emotion_extraction.py
├── tests/
│   └── test_emotion_extraction.py
├── setup.py
├── README.md
├── requirements.txt
└── LICENSE
```

## 📋 要件

- Python 3.7以上
- 標準ライブラリのみ（外部依存関係なし）

## 🔗 関連プロジェクト

このパッケージは[TwitterBot_Nexus_02](https://github.com/Nyukimin/TwitterBot_Nexus_02)プロジェクトから抽出されました。

### 関連モジュール

- **astrology_utils**: 占星術計算エンジン
- **image_generation_utils**: AI画像生成システム
- **chrome_automation_utils**: Chrome自動化ツール

## 🚀 用途例

### AI・機械学習分野

- **画像生成AI**: DALL-E、Midjourney、Stable Diffusionのプロンプト前処理
- **感情分析**: テキストの感情部分のみを抽出して分析精度向上
- **チャットボット**: 占星術アプリでの自然な応答生成

### コンテンツ制作

- **SNS投稿**: 占星術コンテンツから感情的な部分のみを抽出
- **ブログ記事**: 感情的な要素を強調したコンテンツ作成
- **マーケティング**: 感情に訴えるコピーライティング

### 学術・研究

- **言語学研究**: 日本語の感情表現パターン分析
- **心理学研究**: テキストベースの感情状態分析
- **占星術研究**: 占星術記述と感情表現の関係分析

## 📄 ライセンス

MIT License - 詳細は[LICENSE](LICENSE)ファイルを参照

## 🤝 コントリビューション

プルリクエストやイシューの報告を歓迎します。

1. このリポジトリをフォーク
2. 機能ブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m 'Add amazing feature'`)
4. ブランチにプッシュ (`git push origin feature/amazing-feature`)
5. プルリクエストを作成

## 📞 サポート

- GitHub Issues: [https://github.com/Nyukimin/TwitterBot_Nexus_02/issues](https://github.com/Nyukimin/TwitterBot_Nexus_02/issues)
- Email: contact@example.com

---

**Made with ❤️ by TwitterBot_Nexus_02 Project**