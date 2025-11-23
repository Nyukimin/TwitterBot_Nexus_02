# TwitterBot_Nexus_02 インストールガイド

このドキュメントでは、TwitterBot_Nexus_02の環境構築手順を説明します。

---

## 📋 目次

1. [システム要件](#システム要件)
2. [インストール手順](#インストール手順)
3. [環境設定](#環境設定)
4. [動作確認](#動作確認)
5. [トラブルシューティング](#トラブルシューティング)

---

## 💻 システム要件

### **必須環境**

- **OS**: Windows 10/11, macOS 10.14+, Linux (Ubuntu 20.04+)
- **Python**: 3.8以上
- **Google Chrome**: 最新版
- **メモリ**: 4GB以上推奨
- **ディスク空き容量**: 2GB以上

### **必須アカウント**

- **Twitterアカウント**: 運用するアカウント
- **Google Cloud Platform**: Gemini API利用のため
  - Gemini API キー取得済み

---

## 🚀 インストール手順

### **STEP 1: リポジトリのクローン**

```bash
# GitHubからクローン
git clone https://github.com/your-username/TwitterBot_Nexus_02.git
cd TwitterBot_Nexus_02
```

### **STEP 2: Python仮想環境の作成**

```bash
# Windowsの場合
python -m venv venv
venv\Scripts\activate

# macOS/Linuxの場合
python3 -m venv venv
source venv/bin/activate
```

### **STEP 3: 依存パッケージのインストール**

#### **基本パッケージ（必須）**

```bash
# reply_botの依存パッケージをインストール
pip install -r reply_bot/requirements.txt
```

**requirements.txt の内容:**
- BeautifulSoup4 - HTML/XMLパーサー
- emoji - 絵文字処理
- google-generativeai - Google Gemini API
- pandas - データ処理
- pyperclip - クリップボード操作
- pytz - タイムゾーン処理
- selenium - ブラウザ自動化
- snscrape - Twitter情報収集
- webdriver-manager - ChromeDriver管理
- psutil - プロセス管理
- python-dotenv - 環境変数管理
- PyYAML - YAML設定ファイル処理

#### **オプションパッケージ（拡張機能用）**

```bash
# 占星術機能を使用する場合
cd extracted_modules/astrology_utils
pip install -e .

# 画像生成機能を使用する場合
cd extracted_modules/image_generation_utils
pip install -e .

# テキスト処理機能を使用する場合
cd extracted_modules/text_processing_utils
pip install -e .

# ブラウザ自動化機能を使用する場合
cd extracted_modules/chrome_automation_utils
pip install -e .
```

### **STEP 4: 固定Chrome環境のセットアップ（必須）**

⚠️ **重要**: このプロジェクトは `fixed_chrome` ディレクトリの固定バージョンChromeを使用します。

#### **固定Chromeのダウンロード**

**Chrome 140.0.7339.80 と ChromeDriver 140.0.7339.80 を使用（固定）**

1. **Chrome本体のダウンロード**
   ```bash
   # Chrome for Testing (公式配布版) をダウンロード
   # https://googlechromelabs.github.io/chrome-for-testing/
   
   # Windows版のダウンロード例
   # Chrome 140.0.7339.80 win64版を取得
   ```

2. **ChromeDriverのダウンロード**
   ```bash
   # ChromeDriver 140.0.7339.80 をダウンロード
   # https://googlechromelabs.github.io/chrome-for-testing/
   
   # Windows版のダウンロード例
   # ChromeDriver 140.0.7339.80 win64版を取得
   ```

#### **fixed_chromeディレクトリの構成**

```
fixed_chrome/
├── chrome/
│   └── chrome-win64/
│       ├── chrome.exe              # Chrome本体
│       └── 140.0.7339.80.manifest  # バージョン確認用
├── chromedriver/
│   └── chromedriver-win64/
│       └── chromedriver.exe        # ChromeDriver
├── check_versions.bat              # バージョンチェック用
├── README.md                       # 固定Chrome環境の説明
└── version_check.md                # バージョン確認方法
```

#### **配置手順**

```bash
# 1. Chromeの配置
# ダウンロードしたchrome-win64.zipを解凍
# fixed_chrome/chrome/ 配下に配置

# 2. ChromeDriverの配置
# ダウンロードしたchromedriver-win64.zipを解凍
# fixed_chrome/chromedriver/ 配下に配置

# 3. バージョン確認
check_versions.bat
```

#### **バージョンチェック**

```bash
# ChromeDriverのバージョン確認
fixed_chrome\chromedriver\chromedriver-win64\chromedriver.exe --version
# 出力: ChromeDriver 140.0.7339.80

# Chromeのバージョン確認
powershell -Command "(Get-ItemProperty 'fixed_chrome\chrome\chrome-win64\chrome.exe').VersionInfo.FileVersion"
# 出力: 140.0.7339.80
```

#### **重要な運用方針**

⚠️ **固定バージョン使用の徹底:**
1. ✅ `fixed_chrome` ディレクトリのChromeのみを使用
2. ❌ システムにインストール済みのChromeは使用禁止
3. ❌ ChromeとChromeDriverのアップデート禁止
4. ✅ バージョン 140.0.7339.80 に固定

この方針により、環境の一貫性を保ち、予期しない動作変更を防ぎます。

---

## ⚙️ 環境設定

### **STEP 1: 環境変数ファイルの作成**

プロジェクトルートに `.env` ファイルを作成：

```bash
# .env ファイルの内容
GEMINI_API_KEY=your_gemini_api_key_here
```

### **STEP 2: アカウント設定ファイルの作成**

`config/accounts.yaml` を作成：

```yaml
# config/accounts.yaml の例
accounts:
  - username: "your_twitter_username"
    profile_name: "twitter_bot_profile"
    enabled: true
    
  - username: "another_account"
    profile_name: "another_profile"
    enabled: false
```

### **STEP 3: スケジュール設定（オプション）**

`config/schedule.yaml` を作成：

```yaml
# config/schedule.yaml の例
schedule:
  - time: "08:00"
    days: ["monday", "wednesday", "friday"]
    content: "AI占星術解釈"
    enabled: true
    
  - time: "20:00"
    days: ["all"]
    content: "画像付きツイート"
    enabled: true
```

### **STEP 4: ディレクトリの作成**

```bash
# 必要なディレクトリを作成
mkdir -p logs
mkdir -p images
mkdir -p profile
mkdir -p config
```

---

## ✅ 動作確認

### **基本動作テスト**

```bash
# Pythonパスの確認
python --version  # Python 3.8以上であることを確認

# 依存パッケージの確認
pip list

# ログイン状態の確認
python -m reply_bot.check_login_status
```

### **モジュール個別テスト**

```bash
# ブラウザ自動化テスト
cd test
python test_chrome_automation.py

# 占星術機能テスト
python test_integrated_astro.py

# 画像生成テスト
python test_actual_image_generation.py
```

### **本番実行テスト**

```bash
# メインボット起動
python -m reply_bot.main

# スケジュール投稿テスト
python -m reply_bot.schedule_tweet_main
```

---

## 🔧 トラブルシューティング

### **問題1: ChromeDriverのバージョン不一致**

```bash
# エラー: "This version of ChromeDriver only supports Chrome version XX"

# 解決方法: webdriver-managerで自動更新
pip install --upgrade webdriver-manager
```

### **問題2: Gemini API接続エラー**

```bash
# エラー: "API key not valid"

# 解決方法:
# 1. .envファイルにAPIキーが正しく設定されているか確認
# 2. Google Cloud Consoleで APIが有効化されているか確認
# 3. APIキーの使用制限を確認
```

### **問題3: Selenium起動エラー**

```bash
# エラー: "selenium.common.exceptions.WebDriverException"

# 解決方法:
# 1. fixed_chromeのバージョンを確認
check_versions.bat

# 2. Chrome 140.0.7339.80 と ChromeDriver 140.0.7339.80 が正しく配置されているか確認
dir fixed_chrome\chrome\chrome-win64\chrome.exe
dir fixed_chrome\chromedriver\chromedriver-win64\chromedriver.exe

# 3. バージョン不一致の場合は再ダウンロード
# https://googlechromelabs.github.io/chrome-for-testing/
# から Chrome 140.0.7339.80 と ChromeDriver 140.0.7339.80 を取得
```

### **問題6: fixed_chrome ダウンロード方法**

```bash
# Chrome for Testing からダウンロード
# https://googlechromelabs.github.io/chrome-for-testing/

# Windows版のダウンロードリンク例:
# Chrome 140.0.7339.80:
# https://storage.googleapis.com/chrome-for-testing-public/140.0.7339.80/win64/chrome-win64.zip

# ChromeDriver 140.0.7339.80:
# https://storage.googleapis.com/chrome-for-testing-public/140.0.7339.80/win64/chromedriver-win64.zip

# ダウンロード後、解凍して配置:
# - chrome-win64.zip → fixed_chrome/chrome/
# - chromedriver-win64.zip → fixed_chrome/chromedriver/
```

### **問題4: Twitter ログインエラー**

```bash
# エラー: "Login failed"

# 解決方法:
# 1. ログインアシストツールを使用
python -m reply_bot.login_assist

# 2. プロファイルを削除して再作成
rm -rf profile/twitter_bot_profile
```

### **問題5: モジュールインポートエラー**

```bash
# エラー: "ModuleNotFoundError: No module named 'xxx'"

# 解決方法:
# 1. 仮想環境が有効化されているか確認
which python  # 仮想環境のパスが表示されるはず

# 2. requirements.txtを再インストール
pip install -r reply_bot/requirements.txt --force-reinstall
```

---

## 📚 次のステップ

インストールが完了したら、以下のドキュメントを参照してください：

- **[プロジェクト概要](docs/00_プロジェクト概要.md)** - システムの全体像を把握
- **[コーディング開発ガイド](docs/01_コーディング開発ガイド.md)** - 開発ルール・バッチ設定
- **[完全実装仕様書](docs/08_完全実装仕様書.md)** - 詳細な実装手順

---

## 🆘 サポート

問題が解決しない場合：

1. **ログファイルの確認**: `logs/` ディレクトリ内のログを確認
2. **Issueの作成**: GitHubリポジトリでIssueを作成
3. **ドキュメント参照**: `docs/` フォルダ内の関連ドキュメントを確認

---

*最終更新: 2025-11-23*  
*バージョン: 2.0.0*