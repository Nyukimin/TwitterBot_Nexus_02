# Phase 4-01a: 環境構築手順（TDD基盤）

**作成日**: 2025-11-24  
**バージョン**: 3.0 (TDD重視・実装可能版)  
**対象者**: 新人エンジニア・中級エンジニア  
**実装時間**: 1.5-2時間  
**TDD段階**: 環境準備（Red-Green-Refactorの基盤構築）

---

## 📋 目次

1. [TDD環境構築の重要性](#tdd環境構築の重要性)
2. [Python仮想環境構築](#python仮想環境構築)
3. [依存パッケージインストール](#依存パッケージインストール)
4. [テスト用パッケージインストール](#テスト用パッケージインストール)
5. [環境構築完了確認](#環境構築完了確認)

---

## 🎯 TDD環境構築の重要性

### **なぜTDD環境構築が最初なのか**

```
【TDD開発サイクル】
┌─────────────────────────────────────────┐
│ 1. Red: テストを書く（失敗させる）       │ ← 環境がないと書けない
│        ↓                                │
│ 2. Green: 最小限の実装で通す             │ ← 実装より先にテスト
│        ↓                                │
│ 3. Refactor: コードをリファクタ          │ ← テストがあるから安心
│        ↓                                │
│ 4. 次の機能へ（1に戻る）                 │ ← サイクルを回し続ける
└─────────────────────────────────────────┘
```

**TDD環境構築 = テストファーストの準備**

- ✅ **テストが実行できないと開発が始まらない**
- ✅ **テスト環境が整っていないとTDDサイクルが回らない**
- ✅ **環境構築を後回しにすると結局テストを書かなくなる**

### **このフェーズのゴール**

```yaml
phase4_01a_goals:
  primary_goal: "TDDサイクルを回せる環境を構築する"
  
  success_criteria:
    - "pytestコマンドが実行できる"
    - "テストファイルが認識される"
    - "カバレッジが計測できる"
    - "Lint/フォーマットツールが動作する"
  
  tdd_mindset:
    - "テストファースト: 実装前にテストを書く習慣"
    - "高速フィードバック: テスト実行が5秒以内"
    - "自動化: 手動確認を極力減らす"
```

---

## 🔧 Python仮想環境構築

### **Step 1: 仮想環境作成（5分）**

#### **1-1. プロジェクトディレクトリに移動**

```bash
# Windowsコマンドプロンプト
cd c:\GenerativeAI\TwitterBot_Nexus_02

# 現在のディレクトリ確認
cd
# 期待出力: c:\GenerativeAI\TwitterBot_Nexus_02
```

**トラブルシューティング:**

```bash
# ディレクトリが存在しない場合
# エラー例: "指定されたパスが見つかりません"
# 対処法: プロジェクトルートを確認
dir c:\GenerativeAI\

# TwitterBot_Nexus_02が見つからない場合
# → プロジェクトのクローン/展開が必要
git clone <repository_url>
```

#### **1-2. Python仮想環境作成**

```bash
# 仮想環境作成
python -m venv venv

# 作成確認
dir venv
# 期待出力:
# venv\Scripts\    ← ここにpython.exe、activate.batなどが入る
# venv\Lib\        ← パッケージインストール先
# venv\pyvenv.cfg  ← 仮想環境設定ファイル
```

**期待される出力:**

```
Directory of c:\GenerativeAI\TwitterBot_Nexus_02\venv

2025/11/24  17:00    <DIR>          .
2025/11/24  17:00    <DIR>          ..
2025/11/24  17:00    <DIR>          Include
2025/11/24  17:00    <DIR>          Lib
2025/11/24  17:00    <DIR>          Scripts
2025/11/24  17:00               119 pyvenv.cfg
```

**トラブルシューティング:**

```bash
# Python未インストール
# エラー例: "'python' は、内部コマンドまたは外部コマンド..."
# 対処法: Python公式サイトからインストール
# https://www.python.org/downloads/

# Python 3.10以上を確認
python --version
# 期待: Python 3.11.x または 3.10.x

# Pythonパス確認
where python
# 期待: C:\Users\<user>\AppData\Local\Programs\Python\Python311\python.exe

# 古いバージョンの場合
# → Python 3.10以上をインストールして再実行
```

#### **1-3. 仮想環境有効化**

```bash
# Windows（コマンドプロンプト）
venv\Scripts\activate

# 有効化確認: プロンプトに (venv) が表示される
# (venv) c:\GenerativeAI\TwitterBot_Nexus_02>

# Pythonパス確認
where python
# 期待出力: c:\GenerativeAI\TwitterBot_Nexus_02\venv\Scripts\python.exe
```

**PowerShellの場合:**

```powershell
# PowerShell実行ポリシー確認
Get-ExecutionPolicy
# 期待: RemoteSigned または Unrestricted

# Restrictedの場合
# → 管理者PowerShellで実行
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser

# 仮想環境有効化
venv\Scripts\Activate.ps1
```

**トラブルシューティング:**

```bash
# 有効化失敗（PowerShell）
# エラー例: "このシステムではスクリプトの実行が無効になっているため..."
# 対処法: 実行ポリシー変更（上記参照）

# 有効化確認方法
python -c "import sys; print(sys.prefix)"
# 期待: c:\GenerativeAI\TwitterBot_Nexus_02\venv
# NGパターン: C:\Users\<user>\AppData\... （システムPython）
```

#### **1-4. pip/setuptoolsアップグレード**

```bash
# pip自体をアップグレード
python -m pip install --upgrade pip

# 期待出力:
# Successfully installed pip-23.3.1

# setuptools/wheelもアップグレード
pip install --upgrade setuptools wheel

# バージョン確認
pip --version
# 期待: pip 23.3.1 from c:\...\venv\Lib\site-packages\pip (python 3.11)
```

---

## 📦 依存パッケージインストール

### **Step 2: 既存requirements.txtインストール（10分）**

#### **2-1. requirements.txt確認**

```bash
# reply_bot/requirements.txt の内容確認
type reply_bot\requirements.txt

# 期待内容（例）:
# selenium==4.15.2
# beautifulsoup4==4.12.2
# google-generativeai==0.3.1
# pyyaml==6.0.1
# python-dotenv==1.0.0
# pytz==2023.3
# ...
```

**トラブルシューティング:**

```bash
# requirements.txtが存在しない
# エラー例: "指定されたファイルが見つかりません"
# 対処法: プロジェクト構造確認
dir reply_bot\

# reply_botディレクトリがない場合
# → プロジェクト構造の問題。READMEを確認
```

#### **2-2. パッケージインストール実行**

```bash
# インストール実行（時間がかかる場合あり: 5-10分）
pip install -r reply_bot\requirements.txt

# 進行状況表示例:
# Collecting selenium==4.15.2
#   Downloading selenium-4.15.2-py3-none-any.whl (10.0 MB)
#      ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 10.0/10.0 MB 2.3 MB/s eta 0:00:00
# Installing collected packages: selenium, beautifulsoup4, ...
# Successfully installed beautifulsoup4-4.12.2 selenium-4.15.2 ...
```

**期待される最終出力:**

```
Successfully installed:
  beautifulsoup4-4.12.2
  google-generativeai-0.3.1
  pyyaml-6.0.1
  python-dotenv-1.0.0
  selenium-4.15.2
  ...
```

**トラブルシューティング:**

```bash
# ネットワークエラー
# エラー例: "Could not find a version that satisfies the requirement..."
# 対処法: ネットワーク確認、PyPIミラー使用

# プロキシ環境の場合
set HTTP_PROXY=http://proxy.example.com:8080
set HTTPS_PROXY=https://proxy.example.com:8080
pip install -r reply_bot\requirements.txt

# 特定パッケージのインストール失敗
# → 個別にインストール試行
pip install selenium==4.15.2 --verbose

# バージョン互換性エラー
# → requirements.txtのバージョン指定を緩和（検討）
# selenium>=4.15.0 （==から>=に変更）
```

#### **2-3. インストール確認**

```bash
# インストール済みパッケージ一覧
pip list

# 重要パッケージの確認
pip list | findstr "selenium google-generativeai beautifulsoup4"

# 期待出力:
# beautifulsoup4           4.12.2
# google-generativeai      0.3.1
# selenium                 4.15.2
```

**詳細確認:**

```bash
# 特定パッケージの詳細情報
pip show selenium

# 期待出力:
# Name: selenium
# Version: 4.15.2
# Summary: Python bindings for Selenium
# Home-page: https://www.selenium.dev
# Author: Selenium Project
# Location: c:\...\venv\Lib\site-packages
# Requires: urllib3, trio, certifi, ...
```

---

## 🧪 テスト用パッケージインストール

### **Step 3: TDD環境パッケージインストール（5分）**

#### **3-1. requirements-dev.txt作成**

```bash
# requirements-dev.txt作成（コピペ可能）
(
echo # ========================================
echo # TDD テストフレームワーク
echo # ========================================
echo pytest==7.4.3
echo pytest-cov==4.1.0
echo pytest-xdist==3.5.0
echo pytest-timeout==2.2.0
echo pytest-mock==3.12.0
echo.
echo # ========================================
echo # 【必須】コード品質ツール（常時使用）
echo # ========================================
echo black==23.12.0
echo flake8==6.1.0
echo flake8-docstrings==1.7.0
echo mypy==1.7.1
echo.
echo # ========================================
echo # オプションツール
echo # ========================================
echo pre-commit==3.6.0
echo pytest-benchmark==4.0.0
echo pytest-html==4.1.1
) > requirements-dev.txt

# 作成確認
type requirements-dev.txt
```

**requirements-dev.txt 内容説明:**

```yaml
# 各パッケージの役割
pytest:
  purpose: "TDDテストフレームワーク本体"
  usage: "全テスト実行の中心"

pytest-cov:
  purpose: "コードカバレッジ測定"
  usage: "TDDでのカバレッジ70%目標達成に必須"
  
pytest-xdist:
  purpose: "並列テスト実行"
  usage: "テスト実行速度を2-3倍高速化"
  
pytest-timeout:
  purpose: "テストタイムアウト制御"
  usage: "無限ループテストの防止"
  
pytest-mock:
  purpose: "モック機能拡張"
  usage: "外部API・DBのモック作成"

black:
  purpose: "【必須】コード自動フォーマット"
  usage: "保存時に自動実行（VSCode設定）"
  importance: "TDDリファクタリング時の整形"
  
flake8:
  purpose: "【必須】コード品質チェック"
  usage: "保存時に自動実行（VSCode設定）"
  importance: "TDD Red→Green時のコード品質保証"
  
mypy:
  purpose: "型チェック（オプション）"
  usage: "型安全性の保証"
  
pre-commit:
  purpose: "Git commitフック（オプション）"
  usage: "コミット前の自動チェック"
```

#### **3-2. テスト用パッケージインストール**

```bash
# インストール実行
pip install -r requirements-dev.txt

# 進行状況表示例:
# Collecting pytest==7.4.3
#   Downloading pytest-7.4.3-py3-none-any.whl (325 kB)
# ...
# Successfully installed pytest-7.4.3 pytest-cov-4.1.0 black-23.12.0 ...
```

**期待される最終出力:**

```
Successfully installed:
  pytest-7.4.3
  pytest-cov-4.1.0
  pytest-xdist-3.5.0
  pytest-timeout-2.2.0
  pytest-mock-3.12.0
  black-23.12.0
  flake8-6.1.0
  mypy-1.7.1
  pre-commit-3.6.0
```

#### **3-3. インストール確認**

```bash
# pytestバージョン確認
pytest --version
# 期待: pytest 7.4.3

# black確認
black --version
# 期待: black, 23.12.0 (compiled: yes)

# flake8確認
flake8 --version
# 期待: 6.1.0 (mccabe: 0.7.0, pycodestyle: 2.11.0, pyflakes: 3.1.0)

# 全ツール動作確認
pytest --version && black --version && flake8 --version
# → 3つとも正常にバージョン表示されればOK
```

**トラブルシューティング:**

```bash
# コマンドが見つからない
# エラー例: "'pytest' は、内部コマンドまたは外部コマンド..."
# 対処法: 仮想環境の有効化確認

# 仮想環境確認
python -c "import sys; print(sys.prefix)"
# 期待: c:\...\venv （プロジェクト内）
# NGパターン: C:\Users\... （システムPython）

# 再度有効化
venv\Scripts\activate

# パス確認
where pytest
# 期待: c:\...\venv\Scripts\pytest.exe
```

---

## ✅ 環境構築完了確認

### **Step 4: TDD環境動作確認（5分）**

#### **4-1. テストディレクトリ作成**

```bash
# テストディレクトリ構造作成
mkdir tests
mkdir tests\unit
mkdir tests\integration
mkdir tests\e2e
mkdir tests\fixtures
mkdir tests\mocks
mkdir tests\logs

# __init__.py作成（Pythonパッケージ化）
type nul > tests\__init__.py
type nul > tests\unit\__init__.py
type nul > tests\integration\__init__.py
type nul > tests\e2e\__init__.py

# ディレクトリ確認
tree /F tests
```

**期待出力:**

```
tests
│   __init__.py
│
├───unit
│       __init__.py
│
├───integration
│       __init__.py
│
├───e2e
│       __init__.py
│
├───fixtures
└───mocks
└───logs
```

#### **4-2. サンプルテスト作成**

```bash
# 簡単なサンプルテスト作成
(
echo import pytest
echo.
echo def test_environment_setup^(^):
echo     """環境構築確認テスト"""
echo     assert True, "環境構築成功！"
echo.
echo def test_python_version^(^):
echo     """Python 3.10以上の確認"""
echo     import sys
echo     assert sys.version_info ^>= ^(3, 10^), "Python 3.10以上が必要"
echo.
echo def test_pytest_works^(^):
echo     """pytestが動作することを確認"""
echo     assert 1 + 1 == 2, "基本演算が正常"
) > tests\unit\test_environment.py

# 作成確認
type tests\unit\test_environment.py
```

#### **4-3. テスト実行**

```bash
# pytest実行
pytest tests\unit\test_environment.py -v

# 期待出力:
# ============================== test session starts ==============================
# collected 3 items
#
# tests/unit/test_environment.py::test_environment_setup PASSED           [ 33%]
# tests/unit/test_environment.py::test_python_version PASSED              [ 66%]
# tests/unit/test_environment.py::test_pytest_works PASSED                [100%]
#
# =============================== 3 passed in 0.02s ===============================
```

**成功条件:**
- ✅ `3 passed in 0.02s` と表示される
- ✅ エラーが発生しない
- ✅ 実行時間が0.1秒以内

**トラブルシューティング:**

```bash
# テストが見つからない
# エラー例: "no tests ran in 0.00s"
# 対処法: ファイル名がtest_*.pyになっているか確認

# テスト失敗
# エラー例: "AssertionError: Python 3.10以上が必要"
# 対処法: Pythonバージョンアップグレード

# ModuleNotFoundError
# エラー例: "ModuleNotFoundError: No module named 'pytest'"
# 対処法: pip install -r requirements-dev.txt 再実行
```

#### **4-4. カバレッジ測定確認**

```bash
# カバレッジ付きテスト実行
pytest tests\unit\test_environment.py --cov=tests --cov-report=term

# 期待出力:
# ============================== test session starts ==============================
# collected 3 items
#
# tests/unit/test_environment.py ...                                        [100%]
#
# ----------- coverage: platform win32, python 3.11.5 -----------
# Name                                Stmts   Miss  Cover
# -------------------------------------------------------
# tests\__init__.py                       0      0   100%
# tests\unit\__init__.py                  0      0   100%
# tests\unit\test_environment.py          9      0   100%
# -------------------------------------------------------
# TOTAL                                   9      0   100%
#
# =============================== 3 passed in 0.15s ===============================
```

**成功条件:**
- ✅ `TOTAL Cover` が100%と表示される
- ✅ `Miss` が0になっている

---

## 📊 完了チェックリスト

```yaml
phase4_01a_completion_checklist:
  python_environment:
    - [ ] Python 3.10以上がインストール済み
    - [ ] 仮想環境（venv）作成完了
    - [ ] 仮想環境有効化成功（プロンプトに(venv)表示）
    - [ ] pip --version でバージョン確認成功
  
  dependencies:
    - [ ] reply_bot/requirements.txt インストール成功
    - [ ] selenium/beautifulsoup4/google-generativeai確認
    - [ ] pip list で全パッケージ表示
  
  test_packages:
    - [ ] requirements-dev.txt 作成
    - [ ] pytest/pytest-cov/black/flake8インストール成功
    - [ ] pytest --version で7.4.3表示
    - [ ] black --version で23.12.0表示
  
  test_execution:
    - [ ] testsディレクトリ構造作成
    - [ ] サンプルテスト（test_environment.py）作成
    - [ ] pytest実行成功（3 passed）
    - [ ] カバレッジ測定成功（100%表示）
  
  tdd_readiness:
    - [ ] pytest実行時間が0.1秒以内（高速フィードバック）
    - [ ] テストが自動検出される
    - [ ] エラーメッセージが明確に表示される
  
  next_step:
    - [ ] Phase4_01bへ進む準備完了
```

---

## 🚀 TDDマインドセット確認

**このフェーズで身につけるべきTDD習慣:**

```yaml
tdd_habits_phase01a:
  habit_1:
    name: "テスト環境を常に整える"
    practice: "開発開始前に必ずpytest実行"
    benefit: "環境問題の早期発見"
  
  habit_2:
    name: "高速フィードバックループ"
    practice: "テスト実行は3秒以内を目指す"
    benefit: "TDDサイクルが回りやすくなる"
  
  habit_3:
    name: "自動化ファースト"
    practice: "手動確認を減らす"
    benefit: "人的ミスの削減"
```

---

## 📝 次のステップ

✅ **Phase 4-01a 完了！**

次は [`12_Phase4_01b_テストフレームワーク設定.md`](12_Phase4_01b_テストフレームワーク設定.md) へ進んでください。

**Phase4-01b の内容:**
- pytest.ini 詳細設定
- conftest.py フィクスチャ作成
- TDDサイクル実践準備

---

**最終更新**: 2025-11-24  
**TDD重要度**: ★★★★★ (環境構築は全ての基盤)