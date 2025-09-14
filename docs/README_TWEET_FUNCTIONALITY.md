# 🐦 TwitterBot Nexus 02 - ツイート投稿機能 完全ガイド

## 📋 目次
1. [概要](#概要)
2. [ツイート機能の種類](#ツイート機能の種類)
3. [設定ファイルの構造](#設定ファイルの構造)
4. [定型ツイート設定](#定型ツイート設定)
5. [AI生成ツイート設定](#ai生成ツイート設定)
6. [画像投稿機能](#画像投稿機能)
7. [実行方法](#実行方法)
8. [設定例](#設定例)
9. [トラブルシューティング](#トラブルシューティング)

---

## 📖 概要

TwitterBot Nexus 02には、以下の3種類のツイート投稿機能が実装されています：

1. **定型ツイート** - 指定時刻に固定テキスト + AI生成続き文章
2. **AI生成ツイート** - 完全にAIが生成する自由なツイート
3. **画像投稿機能** - 画像付きツイートの自動投稿

---

## 🎯 ツイート機能の種類

### 1. **定型ツイート（Fixed Tweets）**
- **特徴**: 決まった時間に、基本テキスト + AI生成の続き文章
- **用途**: 朝昼夕の挨拶、定期的なメッセージ
- **例**: 「おはよう❤\n今日も素敵な一日にしよう」

### 2. **AI生成ツイート（AI Generated Tweets）**
- **特徴**: AIが完全に内容を生成する自由なツイート
- **用途**: 日常の気づき、励ましメッセージ、季節の話題
- **例**: AIが「感謝」というトピックで自由に文章生成

### 3. **画像投稿（Image Posting）**
- **特徴**: 指定フォルダから画像を選択して投稿
- **用途**: 視覚的なコンテンツの共有
- **例**: `images/maya_content/`から画像を選択して投稿

---

## ⚙️ 設定ファイルの構造

### 基本設定 (`config/accounts_Maya19960330.yaml`)

```yaml
accounts:
  - id: Maya19960330
    handle: "Maya19960330"
    features: 
      like: true
      retweet: true
      comment: true
      bookmark: true
      tweet: true  # ツイート機能を有効化
    
    # ツイート投稿機能設定
    tweet_config:
      enabled: true
      schedule:
        # 定期ツイート設定
        regular_tweets:
          enabled: true
          interval_hours: 6
          time_slots: ["09:00", "15:00", "21:00"]
        
        # 定型ツイート設定
        fixed_tweets: [...]
        
        # AI生成ツイート設定
        ai_generated: [...]
        
        # 画像投稿設定
        image_posting: [...]
```

---

## 🕐 定型ツイート設定

### 設定構造
```yaml
fixed_tweets:
  - text: "基本テキスト\n"
    time: "HH:MM"
    days: ["monday", "tuesday", ...] または ["all"]
    ai_generate:
      enabled: true
      prompt: "AI生成用のプロンプト"
      max_length: 30
```

### 実装例

#### 1. **朝の挨拶（平日 6:00）**
```yaml
- text: "おはよう❤\n"
  time: "06:00"
  days: ["monday", "tuesday", "wednesday", "thursday", "friday"]
  ai_generate:
    enabled: true
    prompt: "「今日も一日頑張ろう」のニュアンスで、以下の例を参考に自然で前向きな続きの文章を生成してください。例：今日も素敵な一日にしよう、今日も笑顔で過ごそう、今日も元気に行こう、今日もがんばっていこう"
    max_length: 30
```

#### 2. **お昼の挨拶（毎日 12:00）**
```yaml
- text: "おひるだね❤\n"
  time: "12:00"
  days: ["all"]
  ai_generate:
    enabled: true
    prompt: "「ゆっくりしよう」のニュアンスで、以下の例を参考にリラックスした続きの文章を生成してください。例：お昼休みを楽しもう、少し休憩しよう、リラックスタイムだね、のんびりしよう"
    max_length: 30
```

#### 3. **夕方の挨拶（毎日 18:00）**
```yaml
- text: "おつかれさま❤\n"
  time: "18:00"
  days: ["all"]
  ai_generate:
    enabled: true
    prompt: "「今日はどんな一日でしたか？」のニュアンスで、以下の例を参考に労いの続きの文章を生成してください。例：今日はお疲れさまでした、一日お疲れさま、今日も一日ありがとう、お疲れさまでした"
    max_length: 30
```

#### 4. **金曜日の週末挨拶（金曜 18:00）**
```yaml
- text: "今週もお疲れさま❤"
  time: "18:00"
  days: ["friday"]
  ai_generate:
    enabled: true
    prompt: "「ゆっくり休んでね」のニュアンスで、以下の例を参考に週末への励ましの続きの文章を生成してください。例：週末はゆっくりしてね、いい週末を過ごしてね、お疲れさまでした、ゆっくり休息してね"
    max_length: 30
```

---

## 🤖 AI生成ツイート設定

### 設定構造
```yaml
ai_generated:
  enabled: true
  schedule:
    # ランダム投稿設定
    random_tweets:
      enabled: true
      frequency: "2-4_per_day"  # 1日の投稿回数
      avoid_times: ["06:00", "12:00", "18:00"]  # 避ける時間
      time_range: ["07:00", "23:00"]  # 投稿可能時間帯
    
    # 特定時間の投稿
    scheduled_times:
      - time: "10:00"
        frequency: "random"
      - time: "15:30"
        frequency: "random"
      - time: "20:00"
        frequency: "random"
  
  # コンテンツ設定
  topics: ["日常", "感謝", "励まし", "季節の話題", "ポジティブな思考", "応援メッセージ"]
  style: "friendly_positive"
  max_length: 140
  
  content_types:
    - "motivational_quotes"    # 励ましの言葉
    - "daily_thoughts"         # 日常の気づき
    - "seasonal_observations"  # 季節の話題
    - "gratitude_expressions"  # 感謝の表現
    - "positive_reminders"     # ポジティブなリマインダー
```

### 投稿タイミング
- **ランダム投稿**: 1日2-4回、7:00〜23:00の間
- **定型時間回避**: 6:00、12:00、18:00は避ける
- **追加投稿**: 10:00、15:30、20:00にランダムで追加

---

## 📷 画像投稿機能

### 設定構造
```yaml
image_posting:
  enabled: true
  image_folder: "images/maya_content"  # 画像フォルダのパス
  with_text: true                      # テキストも一緒に投稿
  schedule: "random"                   # random, daily, weekly
```

### 画像フォルダの準備
1. プロジェクトルートに `images/maya_content/` フォルダを作成
2. 投稿したい画像ファイルを配置
3. 対応形式: JPG, PNG, GIF（Twitter対応形式）

---

## 🚀 実行方法

### 1. **基本実行**
```bash
# ドライラン（実際には投稿しない）
python -m reply_bot.multi_main --accounts Maya19960330

# 実際に投稿
python -m reply_bot.multi_main --accounts Maya19960330 --live-run
```

### 2. **設定ファイル指定**
```bash
python -m reply_bot.multi_main --accounts Maya19960330 --live-run --config config/accounts_Maya19960330.yaml
```

### 3. **バッチファイル実行**
```bash
# Windows
run_bot.bat

# または直接
python -m reply_bot.multi_main --accounts Maya19960330 --live-run
```

---

## 📋 設定例

### 完全な設定例
```yaml
accounts:
  - id: Maya19960330
    handle: "Maya19960330"
    browser: 
      user_data_dir: "profile/Maya19960330"
      headless: true
    features: 
      like: true
      retweet: true
      comment: true
      bookmark: true
      tweet: true
    
    tweet_config:
      enabled: true
      schedule:
        regular_tweets:
          enabled: true
          interval_hours: 6
          time_slots: ["09:00", "15:00", "21:00"]
        
        fixed_tweets:
          - text: "おはよう❤\n"
            time: "06:00"
            days: ["monday", "tuesday", "wednesday", "thursday", "friday"]
            ai_generate:
              enabled: true
              prompt: "「今日も一日頑張ろう」のニュアンスで前向きな続きを生成"
              max_length: 30
        
        ai_generated:
          enabled: true
          schedule:
            random_tweets:
              enabled: true
              frequency: "2-4_per_day"
              avoid_times: ["06:00", "12:00", "18:00"]
              time_range: ["07:00", "23:00"]
          topics: ["日常", "感謝", "励まし", "季節の話題"]
          style: "friendly_positive"
          max_length: 140
        
        image_posting:
          enabled: true
          image_folder: "images/maya_content"
          with_text: true
          schedule: "random"
    
    rate_limits:
      tweet_per_hour: 10
      min_interval_seconds: 300
```

---

## 🔧 トラブルシューティング

### よくある問題と解決方法

#### 1. **ツイートが投稿されない**
- `features.tweet: true` が設定されているか確認
- `tweet_config.enabled: true` が設定されているか確認
- `--live-run` フラグを付けて実行しているか確認

#### 2. **AI生成が動作しない**
- Gemini API キーが正しく設定されているか確認
- `ai_generated.enabled: true` が設定されているか確認
- プロンプトが適切に設定されているか確認

#### 3. **画像投稿が失敗する**
- `images/maya_content/` フォルダが存在するか確認
- 画像ファイルが適切な形式（JPG, PNG, GIF）か確認
- ファイルサイズがTwitterの制限内か確認

#### 4. **時間指定が動作しない**
- 時間形式が "HH:MM" (24時間形式) になっているか確認
- システムの時刻設定が正しいか確認
- タイムゾーンの設定が正しいか確認

### ログ確認
```bash
# ログファイルの確認
tail -f logs/Maya19960330_*.log

# エラーログの確認
grep ERROR logs/Maya19960330_*.log
```

---

## 📞 サポート

問題が解決しない場合は、以下の情報を含めてサポートにお問い合わせください：

1. 使用している設定ファイル (`config/accounts_Maya19960330.yaml`)
2. エラーメッセージの全文
3. 実行コマンド
4. ログファイルの該当部分

---

## 📝 更新履歴

- **v1.0.0**: ツイート投稿機能の初期実装
- **v1.1.0**: AI生成ツイート機能追加
- **v1.2.0**: 画像投稿機能追加
- **v1.3.0**: 定型ツイート + AI生成続き文章機能追加

---

**TwitterBot Nexus 02** で充実したTwitterライフを！🐦✨