#!/usr/bin/env python3
"""
Text Processing Utilities - Setup Configuration
感情コンテンツ抽出とテキスト処理のためのユーティリティパッケージ
"""

from setuptools import setup, find_packages
import os

# パッケージのメタデータを定義
PACKAGE_NAME = "text_processing_utils"
VERSION = "1.0.0"
DESCRIPTION = "感情コンテンツ抽出とテキスト処理のためのユーティリティパッケージ"
LONG_DESCRIPTION = """
# Text Processing Utilities

占星術テキストから感情的なコンテンツを抽出し、画像生成プロンプト用に処理するユーティリティパッケージです。

## 主な機能

- **感情コンテンツ抽出**: 占星術記述を除去し、感情的・心理的内容のみを抽出
- **テキスト前処理**: 日本語テキストの高度な正規表現処理
- **感情キーワード分析**: 感情関連キーワードの自動検出と分類

## 使用例

```python
from text_processing_utils.emotion_extraction import extract_emotional_content

# 占星術テキストから感情コンテンツのみを抽出
text = "今日は月が魚座に入る。感受性が高まりやすい日。人の気持ちに寄り添って過ごそう。"
result = extract_emotional_content(text)
print(result)  # "感受性が高まりやすい日。人の気持ちに寄り添って過ごそう。"
```

## 要件

- Python 3.7+
- 標準ライブラリのみ（外部依存なし）

## 利用シーン

- AI画像生成のプロンプト作成
- 感情分析前処理
- 占星術アプリケーションのテキスト処理
- チャットボットの応答生成
"""

# README.mdの内容を読み込み（存在する場合）
def get_long_description():
    try:
        with open("README.md", "r", encoding="utf-8") as fh:
            return fh.read()
    except FileNotFoundError:
        return LONG_DESCRIPTION

setup(
    name=PACKAGE_NAME,
    version=VERSION,
    author="TwitterBot_Nexus_02 Project",
    author_email="contact@example.com",
    description=DESCRIPTION,
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/Nyukimin/TwitterBot_Nexus_02",
    project_urls={
        "Bug Tracker": "https://github.com/Nyukimin/TwitterBot_Nexus_02/issues",
        "Documentation": "https://github.com/Nyukimin/TwitterBot_Nexus_02/blob/main/extracted_modules/text_processing_utils/README.md",
        "Source Code": "https://github.com/Nyukimin/TwitterBot_Nexus_02/tree/main/extracted_modules/text_processing_utils",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Text Processing :: Linguistic",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Natural Language :: Japanese",
    ],
    python_requires=">=3.7",
    install_requires=[
        # 標準ライブラリのみ使用のため、外部依存なし
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
        "test": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "extract-emotion=text_processing_utils.emotion_extraction:test_extract_emotional_content",
        ],
    },
    keywords=[
        "text-processing", "emotion-extraction", "japanese-nlp", 
        "astrology", "ai-prompt", "sentiment-analysis",
        "テキスト処理", "感情抽出", "占星術", "自然言語処理"
    ],
    package_data={
        "text_processing_utils": ["*.py"],
    },
    include_package_data=True,
    zip_safe=False,
)