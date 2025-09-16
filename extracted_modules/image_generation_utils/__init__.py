#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Image Generation Utils - AI画像生成・Face Reference統合ライブラリ

TwitterBot_Nexus_02プロジェクトから抽出された高品質AI画像生成システム

主要クラス:
- GeminiImageGenerator: Gemini-2.5-flash-image-preview統合画像生成

主要機能:
- 🎨 AI画像生成: Google Gemini API統合
- 👤 Face Reference: 顔ID保持機能（複数参照画像）  
- 📦 Base64処理: 高品質画像データ処理
- 🔗 emotion_link対応: TwitterBot専用便利メソッド
- 🛡️ エラーハンドリング: 包括的例外処理
"""

from .image_generation_utils.gemini_image_generator import GeminiImageGenerator

# パッケージ情報
__version__ = "1.0.0"
__author__ = "TwitterBot_Nexus_02 Team"
__email__ = "contact@example.com"
__description__ = "AI画像生成とFace Reference機能を提供する統合ライブラリ"

# エクスポート対象
__all__ = [
    "GeminiImageGenerator",
]

# パッケージレベル設定
def get_version() -> str:
    """パッケージバージョンを取得"""
    return __version__

def get_supported_models() -> list:
    """サポートされているAIモデル一覧"""
    return [
        "gemini-2.5-flash-image-preview",  # メイン
        "gemini-pro-vision",               # フォールバック
    ]

def get_supported_formats() -> list:
    """サポートされている画像形式"""
    return [
        "PNG", "JPEG", "JPG", "WEBP"
    ]

# モジュール初期化メッセージ（開発時のみ）
import os
if os.getenv("IMAGEUTILS_DEBUG"):
    print(f"🎨 Image Generation Utils v{__version__} loaded")
    print(f"📦 Available classes: {', '.join(__all__)}")