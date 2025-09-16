# Astrology Utils

高精度な占星術計算と恋愛占いを提供する独立Pythonパッケージ

## 🔮 概要

Astrology Utilsは、TwitterBot_Nexus_02プロジェクトから抽出された占星術システムです。Skyfieldベースの高精度天体計算とGemini AI統合による解釈生成機能を提供します。

## ✨ 主要機能

### 天体計算システム
- **AstroCalculator**: 高精度天体位置計算
- **Skyfield統合**: de421.bspファイルによる精密天体暦
- **リアルタイム計算**: 現在時刻ベース惑星位置

### AI解釈システム
- **GeminiInterpreter**: Google Gemini API統合
- **TransitInterpreter**: トランジット解釈生成
- **BirthChartInterpreter**: 出生図解釈

### 恋愛占いシステム
- **ZodiacLoveFortune**: 12星座別恋愛運生成
- **個別星座対応**: 各星座の特性に基づく占い
- **日本語対応**: 完全日本語占星術解釈

## 🚀 インストール

```bash
# 開発環境でのインストール
cd extracted_modules/astrology_utils
pip install -e .

# 依存関係のインストール
pip install skyfield pytz requests
pip install google-generativeai  # Gemini AI機能用（オプション）
```

## 📦 依存関係

### 必須
- Python 3.8+
- skyfield
- pytz
- requests

### オプション
- google-generativeai (AI解釈機能)
- swisseph (Swiss Ephemeris高精度計算)
- pyephem (追加天体計算)

## 💻 基本使用法

### 天体計算
```python
from astrology_utils import AstroCalculator
from datetime import datetime

# 計算エンジン初期化
calc = AstroCalculator()

# 現在の惑星位置計算
now = datetime.now()
positions = calc.calculate_planet_positions(now)
print(f"太陽位置: {positions['sun']}")
```

### 恋愛占い
```python
from astrology_utils import ZodiacLoveFortune

# 恋愛占いシステム
love_fortune = ZodiacLoveFortune()

# 特定星座の恋愛運取得
result = love_fortune.get_love_fortune_by_sign("牡羊座")
print(result)
```

### AI解釈生成
```python
from astrology_utils import GeminiInterpreter
import os

# Gemini APIキー設定
os.environ['GEMINI_API_KEY'] = 'your-api-key'

# AI解釈システム
interpreter = GeminiInterpreter()

# トランジット解釈生成
transit_data = "今日は月が魚座に入ります..."
interpretation = interpreter.generate_interpretation(transit_data)
print(interpretation)
```

## 🧪 テスト実行

```bash
cd extracted_modules/astrology_utils
python test_package.py
```

### テスト結果例
```
🔮 Astrology Utils 包括的動作確認テスト
================================
✅ PASS     基本インポート
✅ PASS     クラス初期化  
✅ PASS     依存関係
✅ PASS     AstroCalculator
✅ PASS     恋愛占いシステム
✅ PASS     パッケージ構造

総テスト数: 6
成功: 6
成功率: 100.0%
🎉 全テスト成功！
```

## 🏗️ アーキテクチャ

```
astrology_utils/
├── setup.py              # パッケージ設定
├── README.md             # このファイル
├── test_package.py       # 包括的テスト
├── __init__.py          # エントリーポイント
└── astrology_utils/     # メインパッケージ
    ├── __init__.py
    ├── astro_system.py  # 天体計算・AI解釈
    └── zodiac_love_fortune.py  # 恋愛占いシステム
```

## 📋 利用可能クラス

| クラス名 | 機能 | 説明 |
|---------|------|------|
| `AstroCalculator` | 天体計算 | Skyfieldベース高精度計算 |
| `GeminiInterpreter` | AI解釈 | Gemini API統合解釈生成 |
| `TransitInterpreter` | トランジット | 現在の惑星配置解釈 |
| `BirthChartInterpreter` | 出生図 | 個人の出生図解釈 |
| `ZodiacLoveFortune` | 恋愛占い | 12星座別恋愛運生成 |

## 🔧 設定

### Gemini API設定
```bash
export GEMINI_API_KEY="your-gemini-api-key"
```

### 天体暦ファイル
- `de421.bsp`: Skyfield用天体暦ファイル（自動ダウンロード）
- プロジェクトルートに配置される

## 🚨 エラーハンドリング

```python
# 依存関係未インストール時のグレースフル処理
try:
    from astrology_utils import AstroCalculator
    calc = AstroCalculator()
except ImportError:
    print("Skyfieldが見つかりません。基本機能のみ利用可能です。")
```

## 📊 パフォーマンス

- **天体計算**: Skyfield最適化による高速処理
- **メモリ効率**: 必要最小限の依存関係
- **API制限**: Gemini API制限内での効率的利用

## 🔒 セキュリティ

- **APIキー管理**: 環境変数による秘匿情報管理
- **入力検証**: 適切なパラメータ検証
- **エラー処理**: セキュアなエラー情報管理

## 🤝 他プロジェクトでの利用

この独立パッケージは以下の用途で再利用可能：

- **占星術アプリ**: モバイル・Web占星術アプリケーション
- **AIボット**: Discord/Slack占星術ボット
- **データ分析**: 天体位置データの統計分析
- **教育ツール**: 占星術学習システム

## 📝 ライセンス

TwitterBot_Nexus_02プロジェクトと同じライセンス

## 🔄 バージョン

- **v1.0.0**: 初回リリース（TwitterBot_Nexus_02から抽出）
  - 天体計算システム完成
  - AI解釈システム統合  
  - 恋愛占いシステム実装
  - 完全独立パッケージ化

---

*このパッケージはTwitterBot_Nexus_02の`shared_modules/astrology/`から抽出・独立化されました。*