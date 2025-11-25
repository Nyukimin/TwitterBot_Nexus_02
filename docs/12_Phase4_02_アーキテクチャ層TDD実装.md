# Phase 4-02: アーキテクチャ層TDD実装

**作成日**: 2025-11-24  
**バージョン**: 2.0 (TDD対応版・概要版)  
**対象者**: 中級〜上級エンジニア  
**実装時間**: 16-24時間

---

## 📋 目次

1. [概要](#概要)
2. [4層アーキテクチャ構成](#4層アーキテクチャ構成)
3. [Layer 1: オーケストレーション層TDD実装](#layer-1-オーケストレーション層tdd実装)
4. [Layer 2: ビジネスロジック層TDD実装](#layer-2-ビジネスロジック層tdd実装)
5. [Layer 3: 共有モジュール層TDD実装](#layer-3-共有モジュール層tdd実装)
6. [Layer 4: インフラ層TDD実装](#layer-4-インフラ層tdd実装)
7. [層間統合テスト](#層間統合テスト)
8. [完了チェックリスト](#完了チェックリスト)

---

## 🎯 概要

このフェーズでは、TwitterBot_Nexus_02の**4層アーキテクチャ**をTDD形式で段階的に実装します。

### **実装対象**

```
┌─────────────────────────────────────────┐
│ Layer 1: オーケストレーション層          │
│ (multi_main.py)                         │
│ - アカウント管理・並列実行制御           │
└─────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────┐
│ Layer 2: ビジネスロジック層              │
│ (reply_processor.py)                    │
│ - AI応答生成・スレッド解析               │
└─────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────┐
│ Layer 3: 共有モジュール層                │
│ (shared_modules/)                       │
│ - 占星術・テキスト処理・Chrome管理       │
└─────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────┐
│ Layer 4: インフラ層                      │
│ (webdriver_stabilizer.py, logging)      │
│ - WebDriver安定化・ログ管理              │
└─────────────────────────────────────────┘
```

### **TDD実装順序**

1. **Layer 1テスト作成** → 最小実装（Green） → リファクタ
2. **Layer 2テスト作成** → 最小実装（Green） → リファクタ
3. **Layer 3テスト作成** → 最小実装（Green） → リファクタ
4. **Layer 4テスト作成** → 最小実装（Green） → リファクタ
5. **層間統合テスト** → バグ修正 → リファクタ

---

## 🏗️ 4層アーキテクチャ構成

### **Layer 1: オーケストレーション層**

**責務**: 複数アカウントの並列実行管理

**主要ファイル**:
- `reply_bot/multi_main.py`

**主要機能**:
- アカウント設定読み込み（`load_accounts_config()`）
- アカウント選択（`select_accounts()`）
- 個別アカウント実行（`run_for_account()`）
- コマンドライン引数処理（`argparse`）

---

### **Layer 2: ビジネスロジック層**

**責務**: AI応答生成・スレッド解析・返信判定

**主要ファイル**:
- `reply_bot/reply_processor.py`

**主要機能**:
- スレッド解析（`fetch_and_analyze_thread()`）
- AI応答生成（`generate_reply()`）
- 返信判定（`reply_detection_unified.py`）
- いいね・リツイート処理

---

### **Layer 3: 共有モジュール層**

**責務**: 再利用可能な共通機能

**主要ディレクトリ**:
- `shared_modules/astrology/` - 占星術計算
- `shared_modules/text_processing/` - テキスト処理
- `shared_modules/chrome_profile_manager/` - Chrome管理

**主要機能**:
- 天体計算・AI解釈（`astro_system.py`）
- 感情分析（`emotion_extraction.py`）
- Chromeプロファイル管理

---

### **Layer 4: インフラ層**

**責務**: 低レベルインフラ・安定化機能

**主要ファイル**:
- `reply_bot/webdriver_stabilizer.py`
- `reply_bot/utils.py`
- Python `logging`

**主要機能**:
- WebDriver起動・再接続
- エラーリトライ
- ログ管理

---

## 🧪 Layer 1: オーケストレーション層TDD実装

### **Step 1: テスト作成（Red）**

**tests/unit/test_multi_main.py:**
```python
"""multi_main.py のTDDテスト"""

import pytest
from unittest.mock import Mock, patch
from reply_bot.multi_main import (
    load_accounts_config,
    select_accounts,
    run_for_account
)


class TestLoadAccountsConfig:
    """アカウント設定読み込みのテスト"""
    
    def test_load_valid_yaml(self, mock_accounts_yaml):
        """正常なYAMLファイル読み込み"""
        # Arrange
        yaml_path = str(mock_accounts_yaml)
        
        # Act
        accounts = load_accounts_config(yaml_path)
        
        # Assert
        assert len(accounts) == 2
        assert accounts[0]["id"] == "test_account_001"
    
    def test_load_nonexistent_file(self):
        """存在しないファイルの読み込みエラー"""
        with pytest.raises(FileNotFoundError):
            load_accounts_config("/invalid/path.yaml")


class TestSelectAccounts:
    """アカウント選択のテスト"""
    
    def test_select_all_accounts(self, sample_account_config):
        """全アカウント選択"""
        # Arrange
        cfg_data = {"accounts": [sample_account_config]}
        
        # Act
        selected = select_accounts(cfg_data, args_accounts=None)
        
        # Assert
        assert len(selected) == 1
    
    def test_select_by_id(self, sample_account_config):
        """ID指定でアカウント選択"""
        # Arrange
        cfg_data = {"accounts": [sample_account_config]}
        
        # Act
        selected = select_accounts(cfg_data, args_accounts=["test_account_001"])
        
        # Assert
        assert len(selected) == 1
        assert selected[0]["id"] == "test_account_001"
    
    def test_select_nonexistent_account(self, sample_account_config):
        """存在しないアカウント指定"""
        # Arrange
        cfg_data = {"accounts": [sample_account_config]}
        
        # Act
        selected = select_accounts(cfg_data, args_accounts=["nonexistent"])
        
        # Assert
        assert len(selected) == 0


class TestRunForAccount:
    """個別アカウント実行のテスト"""
    
    @patch('reply_bot.multi_main.setup_driver')
    @patch('reply_bot.multi_main.main_process')
    def test_run_account_success(self, mock_main_process, mock_setup_driver, sample_account_config):
        """アカウント実行成功"""
        # Arrange
        mock_driver = Mock()
        mock_setup_driver.return_value = mock_driver
        mock_main_process.return_value = True
        
        # Act
        result = run_for_account(sample_account_config, live_run=False)
        
        # Assert
        assert result is True
        mock_setup_driver.assert_called_once()
        mock_main_process.assert_called_once()
    
    @patch('reply_bot.multi_main.setup_driver')
    def test_run_account_driver_failure(self, mock_setup_driver, sample_account_config):
        """WebDriver起動失敗"""
        # Arrange
        mock_setup_driver.side_effect = Exception("Driver failed")
        
        # Act & Assert
        with pytest.raises(Exception, match="Driver failed"):
            run_for_account(sample_account_config, live_run=False)
```

### **Step 2: 最小実装（Green）**

**reply_bot/multi_main.py（修正）:**
```python
"""マルチアカウント実行管理（TDDで段階的に実装）"""

import yaml
from pathlib import Path
from typing import Dict, List, Optional


def load_accounts_config(yaml_path: str) -> List[Dict]:
    """アカウント設定をYAMLから読み込む
    
    Args:
        yaml_path: YAML設定ファイルパス
    
    Returns:
        アカウント設定リスト
    
    Raises:
        FileNotFoundError: ファイルが存在しない
    """
    path = Path(yaml_path)
    
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {yaml_path}")
    
    with open(path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    return data.get("accounts", [])


def select_accounts(cfg_data: Dict, args_accounts: Optional[List[str]] = None) -> List[Dict]:
    """実行対象アカウントを選択
    
    Args:
        cfg_data: YAML設定データ
        args_accounts: 指定アカウントID/ハンドルリスト（Noneなら全選択）
    
    Returns:
        選択されたアカウント設定リスト
    """
    all_accounts = cfg_data.get("accounts", [])
    
    # 全選択
    if args_accounts is None:
        return all_accounts
    
    # ID/ハンドル指定
    selected = []
    for account in all_accounts:
        if account["id"] in args_accounts or account["handle"] in args_accounts:
            selected.append(account)
    
    return selected


def run_for_account(account: Dict, live_run: bool = False, **kwargs) -> bool:
    """個別アカウントを実行
    
    Args:
        account: アカウント設定
        live_run: 本実行モード（Falseならドライラン）
    
    Returns:
        実行成功ならTrue
    
    Raises:
        Exception: WebDriver起動失敗など
    """
    from reply_bot.utils import setup_driver
    from reply_bot.reply_processor import main_process
    
    # WebDriver起動
    driver = setup_driver(account)
    
    try:
        # メイン処理実行
        result = main_process(driver, account, live_run=live_run, **kwargs)
        return result
    finally:
        driver.quit()
```

### **Step 3: テスト実行・リファクタ**

```bash
# テスト実行
pytest tests/unit/test_multi_main.py -v

# カバレッジ確認
pytest tests/unit/test_multi_main.py --cov=reply_bot.multi_main --cov-report=term

# Lint実行
flake8 reply_bot/multi_main.py
black reply_bot/multi_main.py
```

---

## 🧪 Layer 2: ビジネスロジック層TDD実装

### **Step 1: テスト作成（Red）**

**tests/unit/test_reply_processor.py:**
```python
"""reply_processor.py のTDDテスト"""

import pytest
from unittest.mock import Mock, patch
from reply_bot.reply_processor import (
    fetch_and_analyze_thread,
    generate_reply,
    main_process
)


class TestFetchAndAnalyzeThread:
    """スレッド解析のテスト"""
    
    @patch('reply_bot.reply_processor.BeautifulSoup')
    def test_analyze_simple_thread(self, mock_bs, mock_webdriver):
        """単純なスレッド解析"""
        # Arrange
        mock_bs.return_value.find_all.return_value = [
            Mock(text="元ツイート"),
            Mock(text="返信1")
        ]
        
        # Act
        thread = fetch_and_analyze_thread(mock_webdriver, "https://twitter.com/test/status/123")
        
        # Assert
        assert len(thread) == 2
        assert thread[0]["text"] == "元ツイート"


class TestGenerateReply:
    """AI応答生成のテスト"""
    
    @patch('reply_bot.reply_processor.genai.GenerativeModel')
    def test_generate_simple_reply(self, mock_genai_model, mock_ai_response):
        """簡単な返信生成"""
        # Arrange
        mock_model = Mock()
        mock_model.generate_content.return_value.text = "AIからの返信です。"
        mock_genai_model.return_value = mock_model
        
        thread_context = [{"author": "user1", "text": "こんにちは"}]
        
        # Act
        reply = generate_reply(thread_context, personality_prompt="丁寧に返信")
        
        # Assert
        assert "返信" in reply
        mock_model.generate_content.assert_called_once()


class TestMainProcess:
    """メインプロセスのテスト"""
    
    @patch('reply_bot.reply_processor.fetch_and_analyze_thread')
    @patch('reply_bot.reply_processor.generate_reply')
    @patch('reply_bot.reply_processor.post_reply')
    def test_full_reply_workflow(self, mock_post, mock_gen_reply, mock_fetch, mock_webdriver):
        """返信ワークフロー全体"""
        # Arrange
        mock_fetch.return_value = [{"author": "user1", "text": "質問です"}]
        mock_gen_reply.return_value = "回答します。"
        mock_post.return_value = True
        
        account_config = {"PERSONALITY_PROMPT": "丁寧に", "features": {"comment": True}}
        
        # Act
        result = main_process(mock_webdriver, account_config, live_run=True)
        
        # Assert
        assert result is True
        mock_fetch.assert_called()
        mock_gen_reply.assert_called()
        mock_post.assert_called()
```

### **Step 2: 最小実装（Green）**

**reply_bot/reply_processor.py（修正）:**
```python
"""ビジネスロジック層（TDDで段階的に実装）"""

from typing import List, Dict
from bs4 import BeautifulSoup
import google.generativeai as genai


def fetch_and_analyze_thread(driver, tweet_url: str) -> List[Dict]:
    """スレッド全体を解析
    
    Args:
        driver: WebDriverインスタンス
        tweet_url: ツイートURL
    
    Returns:
        スレッド情報リスト
    """
    driver.get(tweet_url)
    
    # HTML解析
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    tweets = soup.find_all('article')
    
    thread = []
    for tweet in tweets:
        thread.append({
            "author": _extract_author(tweet),
            "text": tweet.get_text(strip=True)
        })
    
    return thread


def generate_reply(thread_context: List[Dict], personality_prompt: str) -> str:
    """AI応答生成
    
    Args:
        thread_context: スレッド文脈
        personality_prompt: 性格設定プロンプト
    
    Returns:
        生成された返信テキスト
    """
    # Gemini API呼び出し
    model = genai.GenerativeModel("gemini-pro")
    
    prompt = f"{personality_prompt}\n\nThread:\n"
    for msg in thread_context:
        prompt += f"{msg['author']}: {msg['text']}\n"
    
    response = model.generate_content(prompt)
    return response.text


def main_process(driver, account_config: Dict, live_run: bool = False, **kwargs) -> bool:
    """メイン処理
    
    Args:
        driver: WebDriverインスタンス
        account_config: アカウント設定
        live_run: 本実行モード
    
    Returns:
        処理成功ならTrue
    """
    # スレッド取得
    thread = fetch_and_analyze_thread(driver, kwargs.get("target_url"))
    
    # AI応答生成
    reply_text = generate_reply(thread, account_config["PERSONALITY_PROMPT"])
    
    # 返信投稿（live_runがTrueの場合のみ）
    if live_run and account_config["features"]["comment"]:
        from reply_bot.post_reply import post_reply
        return post_reply(driver, reply_text)
    
    return True


def _extract_author(tweet_element) -> str:
    """ツイート投稿者抽出（内部関数）"""
    return tweet_element.get("data-author", "unknown")
```

---

## 🧪 Layer 3: 共有モジュール層TDD実装

### **占星術モジュールテスト例**

**tests/unit/test_astrology.py:**
```python
"""占星術モジュールのTDDテスト"""

import pytest
from datetime import datetime
from shared_modules.astrology.astro_system import AstroCalculator


class TestAstroCalculator:
    """占星術計算のテスト"""
    
    def test_calculate_sun_position(self):
        """太陽位置計算"""
        # Arrange
        calc = AstroCalculator(
            birth_date=datetime(1990, 1, 1, 12, 0),
            location=(35.6762, 139.6503)  # 東京
        )
        
        # Act
        sun_pos = calc.get_sun_position()
        
        # Assert
        assert "degree" in sun_pos
        assert 0 <= sun_pos["degree"] < 360
    
    def test_zodiac_sign_from_degree(self):
        """度数から星座を取得"""
        # Arrange
        calc = AstroCalculator(datetime(1990, 1, 1), (0, 0))
        
        # Act
        sign = calc.get_zodiac_sign(0)  # 牡羊座0度
        
        # Assert
        assert sign == "牡羊座"
```

---

## 🧪 Layer 4: インフラ層TDD実装

### **WebDriver安定化テスト例**

**tests/unit/test_webdriver_stabilizer.py:**
```python
"""WebDriver安定化のTDDテスト"""

import pytest
from unittest.mock import Mock, patch
from reply_bot.webdriver_stabilizer import stabilize_chrome_startup


class TestWebDriverStabilizer:
    """WebDriver安定化のテスト"""
    
    @patch('selenium.webdriver.Chrome')
    def test_startup_success_on_first_try(self, mock_chrome):
        """1回目で起動成功"""
        # Arrange
        mock_driver = Mock()
        mock_chrome.return_value = mock_driver
        
        # Act
        driver = stabilize_chrome_startup(max_retries=3)
        
        # Assert
        assert driver == mock_driver
        assert mock_chrome.call_count == 1
    
    @patch('selenium.webdriver.Chrome')
    def test_startup_success_after_retries(self, mock_chrome):
        """リトライ後に成功"""
        # Arrange
        mock_driver = Mock()
        mock_chrome.side_effect = [
            Exception("Failed 1"),
            Exception("Failed 2"),
            mock_driver
        ]
        
        # Act
        driver = stabilize_chrome_startup(max_retries=3)
        
        # Assert
        assert driver == mock_driver
        assert mock_chrome.call_count == 3
```

---

## 🔗 層間統合テスト

**tests/integration/test_layer_integration.py:**
```python
"""層間統合テスト"""

import pytest
from unittest.mock import Mock, patch


class TestLayerIntegration:
    """4層統合テスト"""
    
    @patch('reply_bot.multi_main.setup_driver')
    @patch('reply_bot.reply_processor.generate_reply')
    def test_full_stack_integration(self, mock_gen_reply, mock_setup_driver):
        """Layer 1 → Layer 2 → Layer 3 → Layer 4 統合"""
        # Arrange
        mock_driver = Mock()
        mock_setup_driver.return_value = mock_driver
        mock_gen_reply.return_value = "統合テスト返信"
        
        account_config = {
            "id": "test001",
            "PERSONALITY_PROMPT": "テスト",
            "features": {"comment": True}
        }
        
        # Act
        from reply_bot.multi_main import run_for_account
        result = run_for_account(account_config, live_run=False)
        
        # Assert
        assert result is True
```

---

## ✅ 完了チェックリスト

```yaml
phase4_02_completion:
  layer1_orchestration:
    - [ ] load_accounts_config テスト成功
    - [ ] select_accounts テスト成功
    - [ ] run_for_account テスト成功
    - [ ] カバレッジ60%以上
  
  layer2_business_logic:
    - [ ] fetch_and_analyze_thread テスト成功
    - [ ] generate_reply テスト成功
    - [ ] main_process テスト成功
    - [ ] カバレッジ60%以上
  
  layer3_shared_modules:
    - [ ] astrology テスト成功
    - [ ] text_processing テスト成功
    - [ ] chrome_profile_manager テスト成功
    - [ ] カバレッジ50%以上
  
  layer4_infrastructure:
    - [ ] webdriver_stabilizer テスト成功
    - [ ] logging テスト成功
    - [ ] カバレッジ70%以上
  
  integration:
    - [ ] 層間統合テスト成功
    - [ ] 全体カバレッジ60%以上
    - [ ] Lint警告ゼロ
  
  next_step:
    - [ ] Phase4_03へ進む（データ管理TDD実装）
```

---

**次のフェーズ:**  
[Phase4_03_データ管理TDD実装.md](12_Phase4_03_データ管理TDD実装.md)

---

**最終更新**: 2025-11-24