# Phase 4-03: データ管理TDD実装

**作成日**: 2025-11-24  
**バージョン**: 3.0 (TDD完全版・統合ドキュメント)  
**対象者**: 中級エンジニア  
**実装時間**: 8-12時間  
**完成度**: ★★★★★ (実装可能)

---

## 📋 目次

1. [概要とアーキテクチャ](#概要とアーキテクチャ)
2. [実装ファイル構成](#実装ファイル構成)
3. [詳細実装ドキュメント](#詳細実装ドキュメント)
4. [TDD実装フロー](#tdd実装フロー)
5. [テスト実行方法](#テスト実行方法)
6. [トラブルシューティング](#トラブルシューティング)
7. [完了チェックリスト](#完了チェックリスト)

---

## 🎯 概要とアーキテクチャ

このフェーズでは、**ファイルベースのデータ管理機能**をTDD形式で実装します。

### **システムアーキテクチャ**

```
┌─────────────────────────────────────────────────┐
│ アプリケーション層                              │
│ (multi_main.py, reply_processor.py)             │
└─────────────────────────────────────────────────┘
         ↓ (データ操作)
┌─────────────────────────────────────────────────┐
│ データ管理層 (Phase 4-03の実装対象)            │
│                                                 │
│ ┌─────────────┐  ┌─────────────┐              │
│ │YAML設定管理 │  │JSON          │              │
│ │             │  │キャッシュ管理│              │
│ └─────────────┘  └─────────────┘              │
│ ┌─────────────┐  ┌─────────────┐              │
│ │ログファイル │  │データ        │              │
│ │管理         │  │整合性保証    │              │
│ └─────────────┘  └─────────────┘              │
└─────────────────────────────────────────────────┘
         ↓ (ファイルシステム)
┌─────────────────────────────────────────────────┐
│ ストレージ層                                    │
│ (config/, cache/, logs/, backups/)              │
└─────────────────────────────────────────────────┘
```

### **実装対象モジュール**

```
データ管理システム (Phase 4-03)
├── 【Phase 4-03a】 設定・キャッシュ管理
│   ├── config_manager.py         - YAML設定管理
│   ├── cache_manager.py          - JSONキャッシュ基盤
│   └── greeting_tracker.py       - 挨拶記録トラッカー
│
└── 【Phase 4-03b】 ログ・整合性管理
    ├── structured_logger.py      - 構造化ログ
    ├── action_logger.py          - アクション記録
    ├── file_lock.py              - ファイルロック
    └── backup_manager.py         - バックアップ管理
```

---

## 📂 実装ファイル構成

### **プロダクションコード配置**

```
reply_bot/
├── config_manager.py           # YAML設定管理
├── cache_manager.py            # JSONキャッシュ管理
├── greeting_tracker.py         # 挨拶記録トラッカー
├── structured_logger.py        # 構造化ログ
├── action_logger.py            # アクション記録
├── file_lock.py                # ファイルロック機構
└── backup_manager.py           # バックアップ管理
```

### **テストコード配置**

```
tests/
└── unit/
    ├── test_config_manager.py          # 設定管理テスト
    ├── test_cache_manager.py           # キャッシュ管理テスト
    ├── test_greeting_tracker.py        # 挨拶トラッカーテスト
    ├── test_structured_logger.py       # 構造化ログテスト
    ├── test_action_logger.py           # アクションログテスト
    ├── test_file_lock.py               # ファイルロックテスト
    └── test_backup_manager.py          # バックアップテスト
```

### **データファイル配置**

```
(プロジェクトルート)/
├── config/
│   ├── accounts.yaml           # アカウント設定
│   └── bot_settings.yaml       # Bot全体設定
├── cache/
│   ├── greeting_tracker.json   # 挨拶記録
│   ├── ai_response_cache.json  # AI応答キャッシュ
│   └── session_data.json       # セッション情報
├── logs/
│   ├── bot_actions.jsonl       # アクションログ
│   ├── structured.log          # 構造化ログ
│   └── error.log               # エラーログ
└── backups/
    └── (自動バックアップファイル)
```

---

## 📚 詳細実装ドキュメント

Phase 4-03は2つの詳細ドキュメントに分割されています：

### **Phase 4-03a: 設定・キャッシュ管理TDD**

[`12_Phase4_03a_設定・キャッシュ管理TDD.md`](./12_Phase4_03a_設定・キャッシュ管理TDD.md)

**実装内容:**
- ✅ ConfigManager（YAML設定管理）
- ✅ CacheManager（JSONキャッシュ基盤）
- ✅ GreetingTracker（挨拶記録トラッカー）

**実装時間:** 4-6時間  
**テスト数:** 17件  
**カバレッジ目標:** 85%以上

---

### **Phase 4-03b: ログ・整合性管理TDD**

[`12_Phase4_03b_ログ・整合性管理TDD.md`](./12_Phase4_03b_ログ・整合性管理TDD.md)

**実装内容:**
- ✅ StructuredLogger（構造化ログ）
- ✅ ActionLogger（アクション記録）
- ✅ FileLock（ファイルロック機構）
- ✅ BackupManager（バックアップ管理）

**実装時間:** 4-6時間  
**テスト数:** 9件  
**カバレッジ目標:** 85%以上

---

## 🔄 TDD実装フロー

### **推奨実装順序**

```
【Day 1: 午前】 Phase 4-03a - 設定管理
├─ Step 1: test_config_manager.py 作成 (Red)
├─ Step 2: config_manager.py 実装 (Green)
└─ Step 3: リファクタリング (Refactor)

【Day 1: 午後】 Phase 4-03a - キャッシュ管理
├─ Step 1: test_cache_manager.py 作成 (Red)
├─ Step 2: cache_manager.py 実装 (Green)
├─ Step 3: test_greeting_tracker.py 作成 (Red)
└─ Step 4: greeting_tracker.py 実装 (Green)

【Day 2: 午前】 Phase 4-03b - ログ管理
├─ Step 1: test_structured_logger.py 作成 (Red)
├─ Step 2: structured_logger.py 実装 (Green)
├─ Step 3: test_action_logger.py 作成 (Red)
└─ Step 4: action_logger.py 実装 (Green)

【Day 2: 午後】 Phase 4-03b - 整合性管理
├─ Step 1: test_file_lock.py 作成 (Red)
├─ Step 2: file_lock.py 実装 (Green)
├─ Step 3: test_backup_manager.py 作成 (Red)
├─ Step 4: backup_manager.py 実装 (Green)
└─ Step 5: 総合テスト・リファクタリング
```

### **各ステップの時間配分**

| ステップ | 時間 | 内容 |
|---------|------|------|
| Red Phase | 5-10分 | テストコード作成 |
| Green Phase | 15-30分 | 最小実装 |
| Refactor Phase | 10-15分 | コード整理 |

---

## 🧪 テスト実行方法

### **Phase 4-03a: 設定・キャッシュ管理のテスト**

```bash
# 全テスト実行
pytest tests/unit/test_config_manager.py -v
pytest tests/unit/test_cache_manager.py -v
pytest tests/unit/test_greeting_tracker.py -v

# カバレッジ計測
pytest tests/unit/test_config_manager.py --cov=reply_bot.config_manager --cov-report=term-missing

# 特定テストのみ実行
pytest tests/unit/test_config_manager.py::TestConfigManager::test_load_valid_config -v
```

### **Phase 4-03b: ログ・整合性管理のテスト**

```bash
# 全テスト実行
pytest tests/unit/test_structured_logger.py -v
pytest tests/unit/test_action_logger.py -v
pytest tests/unit/test_file_lock.py -v
pytest tests/unit/test_backup_manager.py -v

# カバレッジ計測
pytest tests/unit/ --cov=reply_bot --cov-report=html
```

### **Phase 4-03全体のテスト**

```bash
# データ管理層の全テスト実行
pytest tests/unit/test_config_manager.py \
       tests/unit/test_cache_manager.py \
       tests/unit/test_greeting_tracker.py \
       tests/unit/test_structured_logger.py \
       tests/unit/test_action_logger.py \
       tests/unit/test_file_lock.py \
       tests/unit/test_backup_manager.py \
       -v --cov=reply_bot --cov-report=term-missing

# HTMLカバレッジレポート生成
pytest tests/unit/ --cov=reply_bot --cov-report=html
# ブラウザでhtmlcov/index.htmlを開く
```

### **テスト成功の確認基準**

```yaml
phase4_03_success_criteria:
  test_results:
    total_tests: 26件以上
    passed: 100%
    failed: 0件
  
  coverage:
    overall: 85%以上
    config_manager: 85%以上
    cache_manager: 85%以上
    log_managers: 85%以上
    file_lock: 90%以上
  
  code_quality:
    flake8: 警告0件
    black: フォーマット済み
    mypy: 型エラー0件
```

---

## 🔧 トラブルシューティング

### **よくあるエラーと解決策**

#### **1. ModuleNotFoundError: No module named 'reply_bot'**

**原因:** Pythonパスが通っていない

**解決策:**
```bash
# プロジェクトルートから実行
cd c:/GenerativeAI/TwitterBot_Nexus_02
python -m pytest tests/unit/test_config_manager.py -v
```

または

```bash
# PYTHONPATHを設定
set PYTHONPATH=c:\GenerativeAI\TwitterBot_Nexus_02
pytest tests/unit/test_config_manager.py -v
```

---

#### **2. FileNotFoundError: Config file not found**

**原因:** テスト用の一時ファイルパスの問題

**解決策:**
```python
# tmp_pathフィクスチャを使用
def test_example(tmp_path):
    config_path = tmp_path / "test.yaml"
    # ... テストコード
```

---

#### **3. TimeoutError: Lock timeout**

**原因:** ファイルロックが解放されていない

**解決策:**
```python
# context managerを使用（自動解放）
with FileLock("test.lock"):
    # 処理
# ここで自動的にロック解放
```

---

#### **4. yaml.YAMLError: Invalid YAML**

**原因:** YAML形式が不正

**解決策:**
```python
# 正しいYAML形式
config_data = {
    "accounts": [
        {"id": "test001", "handle": "@user"}
    ]
}
# yaml.dump()で出力
```

---

### **デバッグ方法**

#### **詳細ログ出力**

```bash
# pytest詳細出力
pytest tests/unit/test_config_manager.py -vv -s

# ロギング有効化
pytest tests/unit/ --log-cli-level=DEBUG
```

#### **特定テストのみ実行**

```bash
# クラス単位
pytest tests/unit/test_config_manager.py::TestConfigManager -v

# メソッド単位
pytest tests/unit/test_config_manager.py::TestConfigManager::test_load_valid_config -v
```

#### **失敗時に停止**

```bash
pytest tests/unit/ -x  # 最初の失敗で停止
pytest tests/unit/ --maxfail=3  # 3回失敗で停止
```

---

## ✅ 完了チェックリスト

### **Phase 4-03a: 設定・キャッシュ管理**

```yaml
config_management:
  - [ ] ConfigManager クラス実装完了
  - [ ] test_config_manager.py 全テスト成功（10件）
  - [ ] カバレッジ85%以上達成
  - [ ] スキーマバリデーション実装完了
  - [ ] 原子的書き込み実装完了

cache_management:
  - [ ] CacheManager クラス実装完了
  - [ ] test_cache_manager.py 全テスト成功（4件）
  - [ ] TTL機能実装完了
  - [ ] カバレッジ85%以上達成

greeting_tracker:
  - [ ] GreetingTracker クラス実装完了
  - [ ] test_greeting_tracker.py 全テスト成功（3件）
  - [ ] 日次制限チェック実装完了
  - [ ] カバレッジ85%以上達成
```

### **Phase 4-03b: ログ・整合性管理**

```yaml
structured_logging:
  - [ ] StructuredLogger クラス実装完了
  - [ ] test_structured_logger.py 全テスト成功（2件）
  - [ ] JSON形式ログ出力実装完了
  - [ ] カバレッジ90%以上達成

action_logging:
  - [ ] ActionLogger クラス実装完了
  - [ ] test_action_logger.py 全テスト成功（2件）
  - [ ] JSON Lines形式実装完了
  - [ ] カバレッジ85%以上達成

file_lock:
  - [ ] FileLock クラス実装完了
  - [ ] test_file_lock.py 全テスト成功（3件）
  - [ ] タイムアウト機能実装完了
  - [ ] 例外時クリーンアップ実装完了
  - [ ] カバレッジ95%以上達成

backup:
  - [ ] BackupManager クラス実装完了
  - [ ] test_backup_manager.py 全テスト成功（2件）
  - [ ] バックアップ作成実装完了
  - [ ] 復元機能実装完了
  - [ ] カバレッジ85%以上達成
```

### **Phase 4-03全体**

```yaml
phase4_03_overall:
  testing:
    - [ ] 全26テスト成功
    - [ ] カバレッジ85%以上達成
    - [ ] flake8警告ゼロ
    - [ ] black適用済み
    - [ ] mypy型チェック成功
  
  documentation:
    - [ ] Phase4-03メインドキュメント完成
    - [ ] Phase4-03a詳細ドキュメント完成
    - [ ] Phase4-03b詳細ドキュメント完成
    - [ ] コード内docstring完備
  
  integration:
    - [ ] 7モジュール全て実装完了
    - [ ] モジュール間連携テスト成功
    - [ ] 実プロジェクトへの組み込み準備完了
  
  next_step:
    - [ ] Phase4-04へ進む（セキュリティTDD実装）
```

---

## 📊 Phase 4-03 完成後の成果物

### **実装モジュール数**

- ✅ プロダクションコード: 7ファイル
- ✅ テストコード: 7ファイル
- ✅ 合計: 14ファイル

### **テストカバレッジ**

- ✅ 総合カバレッジ: 85%以上
- ✅ テスト数: 26件以上
- ✅ 成功率: 100%

### **コード品質**

- ✅ flake8: 警告0件
- ✅ black: フォーマット済み
- ✅ mypy: 型ヒント100%
- ✅ docstring: 全関数・クラスに完備

---

## 🚀 次のステップ

Phase 4-03完了後は、以下のフェーズに進みます：

**Phase 4-04: セキュリティTDD実装**
- API認証管理
- 環境変数管理
- シークレット暗号化
- レート制限機能

[Phase4_04_セキュリティTDD実装.md](./12_Phase4_04_セキュリティTDD実装.md)

---

## 📖 関連ドキュメント

- [Phase4-01: 環境構築とTDD準備](./12_Phase4_01_環境構築とTDD準備.md)
- [Phase4-02: プロジェクト基盤TDD実装](./12_Phase4_02_プロジェクト基盤TDD実装.md)
- [Phase4-03a: 設定・キャッシュ管理TDD](./12_Phase4_03a_設定・キャッシュ管理TDD.md) ⬅️ **詳細実装**
- [Phase4-03b: ログ・整合性管理TDD](./12_Phase4_03b_ログ・整合性管理TDD.md) ⬅️ **詳細実装**

---

**最終更新**: 2025-11-25  
**ドキュメント状態**: ✅ 完成・実装可能  
**TDD実践度**: ★★★★★ (100%)  
**推定実装時間**: 8-12時間（中級エンジニア）