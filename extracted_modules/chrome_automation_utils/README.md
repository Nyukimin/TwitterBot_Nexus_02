# Chrome Automation Utils

Chrome自動化とプロファイル管理のための統合ユーティリティライブラリ

## 🚀 概要

TwitterBot等のWebスクレイピングプロジェクトで必要な**Chromeプロファイルの作成**、**Chrome起動**、**ステルス設定**を統合した再利用可能なモジュールです。

## 📦 インストール

### 方法1: パッケージインストール
```bash
cd extracted_modules/chrome_automation_utils
pip install .
```

### 方法2: 直接コピー
```bash
cp -r extracted_modules/chrome_automation_utils your_project/
cd your_project
pip install -r chrome_automation_utils/requirements.txt
```

## 🔧 基本的な使用方法

```python
from chrome_automation_utils import ProfiledChromeManager

# 初期化
manager = ProfiledChromeManager(base_profiles_dir="./profiles")

# プロファイル作成 + Chrome起動（一括）
driver = manager.create_and_launch(
    profile_name="my_profile",
    window_size=(1200, 800),
    headless=False
)

# Webページ操作
driver.get("https://example.com")
print("Current URL:", driver.current_url)

# 終了
driver.quit()
```

## ⚙️ 高度な設定

### カスタムオプション
```python
driver = manager.create_and_launch(
    profile_name="custom_profile",
    headless=True,                    # ヘッドレスモード
    window_size=(1920, 1080),         # ウィンドウサイズ
    user_agent="Custom UserAgent",    # カスタムUserAgent
    proxy="socks5://127.0.0.1:1080",  # プロキシ設定
    disable_images=True,              # 画像読み込み無効化
)
```

### 既存プロファイルの利用
```python
# 既存プロファイルでChrome起動
driver = manager.launch_existing("my_profile")
```

### プロファイル管理
```python
# 利用可能なプロファイル一覧
profiles = manager.list_profiles()
print("Available profiles:", profiles)

# プロファイルのバックアップ
backup_path = manager.backup_profile("my_profile")

# プロファイルの削除
manager.delete_profile("old_profile")
```

## 🎯 実用例

### TwitterBot連携
```python
def twitter_automation():
    manager = ProfiledChromeManager(base_profiles_dir="./twitter_profiles")
    
    accounts = ["account1", "account2", "account3"]
    
    for account in accounts:
        print(f"Processing account: {account}")
        
        driver = manager.create_and_launch(
            profile_name=f"twitter_{account}",
            window_size=(1920, 1080),
            disable_images=True,  # 高速化
            headless=False
        )
        
        try:
            driver.get("https://twitter.com")
            # ... ログイン確認、投稿処理など ...
            
        finally:
            driver.quit()
```

### マルチアカウント管理
```python
def multi_account_scraping():
    manager = ProfiledChromeManager()
    
    # 複数アカウントでの並行処理
    accounts = [
        {"name": "user1", "proxy": "127.0.0.1:8080"},
        {"name": "user2", "proxy": "127.0.0.1:8081"},
        {"name": "user3", "proxy": "127.0.0.1:8082"},
    ]
    
    for account in accounts:
        driver = manager.create_and_launch(
            profile_name=account["name"],
            proxy=account["proxy"],
            headless=True
        )
        # ... 処理 ...
        driver.quit()
```

## 📁 ディレクトリ構造

```
chrome_automation_utils/
├── __init__.py              # パッケージエントリーポイント
├── manager.py               # ProfiledChromeManager
├── exceptions.py            # 専用例外クラス
└── examples/
    └── basic_usage.py       # 基本的な使用例
```

## 🔧 依存関係

- Python 3.8+
- selenium>=4.0.0
- webdriver-manager>=3.8.0

## 💡 機能一覧

- ✅ **プロファイル自動作成**: 必要に応じてChromeプロファイルを自動生成
- ✅ **Chrome起動統合**: プロファイル作成とChrome起動を一括実行
- ✅ **豊富なオプション**: ヘッドレス、プロキシ、UserAgent等の設定対応
- ✅ **プロファイル管理**: 一覧表示、バックアップ、削除機能
- ✅ **再利用性**: 他プロジェクトでも簡単に利用可能
- ✅ **ステルス設定**: bot検出回避のための基本設定を自動適用

## 🚀 他プロジェクトでの利用

### プロジェクト間でのコピー
```bash
# 他のプロジェクトに移植
cp -r extracted_modules/chrome_automation_utils other_project/
cd other_project
pip install -r chrome_automation_utils/requirements.txt

# 利用開始
from chrome_automation_utils import ProfiledChromeManager
```

### pip パッケージとして利用
```bash
# パッケージ化
cd extracted_modules/chrome_automation_utils
python setup.py sdist

# 他プロジェクトでインストール
pip install path/to/chrome-automation-utils-1.0.0.tar.gz
```

## 📝 ライセンス

MIT License

## 🤝 コントリビューション

バグ報告や機能要望は Issues でお知らせください。

## 📞 サポート

このモジュールは TwitterBot_Nexus_02 プロジェクトから切り出された汎用Chrome自動化ユーティリティです。
質問や問題がある場合は、プロジェクトの Issues までお気軽にお問い合わせください。

## ⚡ 特別機能

- **ステルス設定**: bot検出回避のための高度な設定を自動適用
- **マルチアカウント対応**: 複数のChromeプロファイルを効率的に管理
- **エラーハンドリング**: 堅牢なエラー処理と自動回復機能
- **企業レベル品質**: プロダクション環境での使用に適した設計