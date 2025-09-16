#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Image Generation Utils - Setup Configuration

高品質AI画像生成とFace Reference機能を提供する独立Pythonパッケージ
"""

from setuptools import setup, find_packages

# パッケージの基本情報
PACKAGE_NAME = "image_generation_utils"
VERSION = "1.0.0"
DESCRIPTION = "AI画像生成とFace Reference機能を提供する統合ライブラリ"
LONG_DESCRIPTION = """
# Image Generation Utils

Gemini-2.5-flash-image-preview統合による高品質AI画像生成システム

## 主要機能

- **Gemini Image Generator**: Google Gemini API統合画像生成
- **Face Reference**: 顔ID保持機能（複数参照画像対応）
- **Base64処理**: 高品質画像データ処理（0bytes問題修正済み）
- **emotion_link対応**: TwitterBot専用便利メソッド
- **エラーハンドリング**: 包括的例外処理とログ機能

TwitterBot_Nexus_02プロジェクトから抽出された企業レベル品質の独立パッケージです。
"""

# 必須依存関係
REQUIRED_PACKAGES = [
    "requests>=2.25.0",
    "Pillow>=8.0.0",  # 画像処理
]

# オプション依存関係
OPTIONAL_PACKAGES = {
    "full": [
        "google-generativeai>=0.3.0",  # Gemini API
        "opencv-python>=4.5.0",        # 高度画像処理
        "numpy>=1.21.0",                # 数値計算
    ],
    "dev": [
        "pytest>=6.0.0",
        "pytest-cov>=2.12.0",
        "black>=21.0.0",
        "flake8>=3.9.0",
    ]
}

# 長期間サポート用Python環境
PYTHON_REQUIRES = ">=3.8"

# パッケージ分類
CLASSIFIERS = [
    "Development Status :: 5 - Production/Stable",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Topic :: Multimedia :: Graphics",
    "Topic :: Scientific/Engineering :: Artificial Intelligence",
    "Operating System :: OS Independent",
]

# エントリーポイント
ENTRY_POINTS = {
    "console_scripts": [
        "generate-image=image_generation_utils.cli:main",
    ],
}

# セットアップ実行
setup(
    name=PACKAGE_NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    
    # 作者情報
    author="TwitterBot_Nexus_02 Team",
    author_email="contact@example.com",
    
    # プロジェクト情報
    url="https://github.com/your-repo/TwitterBot_Nexus_02",
    project_urls={
        "Bug Reports": "https://github.com/your-repo/TwitterBot_Nexus_02/issues",
        "Source": "https://github.com/your-repo/TwitterBot_Nexus_02",
        "Documentation": "https://github.com/your-repo/TwitterBot_Nexus_02/wiki",
    },
    
    # パッケージ構成
    packages=find_packages(),
    python_requires=PYTHON_REQUIRES,
    
    # 依存関係
    install_requires=REQUIRED_PACKAGES,
    extras_require=OPTIONAL_PACKAGES,
    
    # メタデータ
    classifiers=CLASSIFIERS,
    keywords=[
        "ai", "image-generation", "gemini", "face-reference", 
        "twitter-bot", "automation", "computer-vision"
    ],
    
    # エントリーポイント
    entry_points=ENTRY_POINTS,
    
    # パッケージデータ
    include_package_data=True,
    package_data={
        PACKAGE_NAME: [
            "*.md",
            "*.txt",
            "*.yml",
            "examples/*",
        ],
    },
    
    # Zip安全性
    zip_safe=False,
    
    # テスト設定
    test_suite="tests",
    tests_require=OPTIONAL_PACKAGES["dev"],
)

# インストール完了メッセージ
print(f"""
🎨 {PACKAGE_NAME} v{VERSION} インストール完了！

📦 基本使用法:
    from image_generation_utils import GeminiImageGenerator
    
    generator = GeminiImageGenerator()
    result = generator.generate_image("beautiful sunset", "output.png")

🔧 開発環境セットアップ:
    pip install -e ".[dev,full]"

📋 主要機能:
    ✅ Gemini-2.5-flash-image-preview統合
    ✅ Face Reference機能（顔ID保持）
    ✅ Base64処理（0bytes問題修正）
    ✅ emotion_link対応
    ✅ 包括的エラーハンドリング

🚀 他プロジェクトでの利用も可能な独立パッケージです！
""")