# 📚 TwitterBot_Nexus_02 ドキュメント索引

このドキュメントは、`docs/`フォルダ内の全ドキュメントを3つのカテゴリに分類して整理した索引です。

---

## 📋 目次

1. [技術メモ](#技術メモ)
2. [仕様](#仕様)
3. [実装状況](#実装状況)

---

## 🔧 技術メモ

開発・運用に関する技術的な情報、ガイド、分析レポートをまとめています。

### コーディング・開発ガイド

| ファイル名 | 説明 | サイズ |
|-----------|------|--------|
| `coding_rules.md` | ペアプログラミングのコア原則、コード修正における思考憲法、データ処理アプローチの選択原則 | 6.9KB |
| `README_run_bot.md` | 自動実行バッチファイル（`run_bot.bat`）の設定と使い方、Windowsタスクスケジューラでの定期実行方法 | 4.0KB |
| `README_TWEET_FUNCTIONALITY.md` | ツイート投稿機能の完全ガイド（定型ツイート、AI生成ツイート、画像投稿機能） | 10KB |

### 問題・改善・分析レポート

| ファイル名 | 説明 | サイズ |
|-----------|------|--------|
| `current_issues.md` | 完了したタスク、今後の課題、現状の問題点、重要なルール、タイムアウト設定 | 3.8KB |
| `IMPROVEMENTS.md` | Twitter返信判定システムの改善ドキュメント（返信判定ロジック、統合返信判定システム、テスト・検証システム） | 6.0KB |
| `COMPLETE_PROJECT_ANALYSIS_REPORT.md` | プロジェクトの完全分析レポート | 31KB |
| `COMPREHENSIVE_SYSTEM_OVERVIEW.md` | システム全体の包括的な概要 | 20KB |
| `PROJECT_VERIFICATION_REPORT.md` | プロジェクト検証レポート | 19KB |

### モジュール関連

| ファイル名 | 説明 | サイズ |
|-----------|------|--------|
| `MODULE_EXTRACTION_GUIDE.md` | モジュール抽出ガイド（独立パッケージ化の手順） | 8.9KB |

---

## 📐 仕様

システムの設計仕様、要件定義、実装設計に関するドキュメントです。

### 基本仕様

| ファイル名 | 説明 | サイズ |
|-----------|------|--------|
| `specification.md` | 全体仕様（v1.0）- 目的と要件、アーキテクチャ、設定ファイル構造、データベース、モジュール構成 | 25KB |
| `SPEC_OVERVIEW.md` | 仕様概要 - 目的と要件、アーキテクチャ、設定ファイル構造、データベース、モジュール構成 | 5.5KB |
| `TwitterBot_Nexus_02_完全実装仕様書.md` | 完全構築ガイド・仕様書（v2.0.0）- プロジェクト概要、システム構成、構築手順、運用方法、テスト・品質保証 | 96KB |

### Phase別仕様書

| ファイル名 | 説明 | サイズ |
|-----------|------|--------|
| `specification_phase1_value_definition.md` | Phase1: 価値定義 - プロジェクトの価値、目的、目標の定義 | 27KB |
| `specification_phase2_technology_foundation.md` | Phase2: 技術基盤 - 技術スタック、アーキテクチャ、技術選定の根拠 | 37KB |
| `specification_phase3_requirements_analysis.md` | Phase3: 要件分析 - 機能要件、非機能要件、制約条件の詳細分析 | 46KB |
| `specification_phase4_implementation_design.md` | Phase4: 実装設計 - 詳細設計、データベース設計、API設計、モジュール設計 | 41KB |
| `specification_phase5_quality_assurance.md` | Phase5: 品質保証 - テスト戦略、品質基準、品質管理プロセス | 36KB |
| `specification_phase6_operations_design.md` | Phase6: 運用設計 - デプロイメント、監視、運用プロセス、障害対応 | 37KB |

### 仕様作成ガイド

| ファイル名 | 説明 | サイズ |
|-----------|------|--------|
| `complete_specification_creation_guide_v1.0.md` | 完全仕様書作成ガイド（v1.0） | 19KB |
| `complete_specification_creation_guide_v1.1.md` | 完全仕様書作成ガイド（v1.1）- 仕様書作成の詳細な手順とテンプレート | 87KB |

### モジュール設計仕様

| ファイル名 | 説明 | サイズ |
|-----------|------|--------|
| `MODULAR_DECOMPOSITION_SPECIFICATION.md` | モジュール分解仕様 - モジュール化の設計方針と構造 | 11KB |

---

## 📊 実装状況

実装の進捗状況、拡張計画、今後のロードマップに関するドキュメントです。

| ファイル名 | 説明 | サイズ |
|-----------|------|--------|
| `IMPLEMENTATION_STATUS.md` | 実装状況（2025-08-19時点）- 進捗サマリ、完了項目、未実装/残課題、実行と検証 | 4.0KB |
| `EXPANSION_PLAN.md` | システム拡張方針（v1.0）- 目的と要件、決定事項、設計変更の詳細、実装ステップ、リスクと対策 | 6.8KB |

---

## 📖 ドキュメントの使い方

### 新規開発者向け

1. **まず読むべきドキュメント**:
   - `COMPREHENSIVE_SYSTEM_OVERVIEW.md` - システム全体の概要を把握
   - `specification.md` または `SPEC_OVERVIEW.md` - 基本仕様を理解
   - `README_run_bot.md` - 実行方法を確認

2. **開発を始める前に**:
   - `coding_rules.md` - コーディング原則を理解
   - `IMPLEMENTATION_STATUS.md` - 現在の実装状況を確認
   - `current_issues.md` - 既知の問題点を把握

### 機能追加・拡張時

1. **設計段階**:
   - `EXPANSION_PLAN.md` - 拡張方針を確認
   - Phase別仕様書（phase1-6） - 該当するPhaseの仕様を参照
   - `MODULAR_DECOMPOSITION_SPECIFICATION.md` - モジュール設計を確認

2. **実装段階**:
   - `TwitterBot_Nexus_02_完全実装仕様書.md` - 詳細な実装手順を参照
   - `MODULE_EXTRACTION_GUIDE.md` - モジュール化が必要な場合

### 問題解決・改善時

1. **問題の把握**:
   - `current_issues.md` - 既知の問題点を確認
   - `IMPROVEMENTS.md` - 過去の改善事例を参照

2. **分析・検証**:
   - `COMPLETE_PROJECT_ANALYSIS_REPORT.md` - プロジェクト全体の分析
   - `PROJECT_VERIFICATION_REPORT.md` - 検証結果を確認

---

## 🔄 ドキュメントの更新履歴

- **2025-11-21**: ドキュメント索引作成
- 各ドキュメントの最終更新日は各ファイル内を参照してください

---

## 📝 注意事項

- ドキュメントは随時更新される可能性があります
- 最新の情報は各ドキュメントファイルを直接確認してください
- 仕様と実装に差異がある場合は、実装コードを優先してください

---

**最終更新**: 2025-11-21

