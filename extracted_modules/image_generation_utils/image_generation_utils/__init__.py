#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Image Generation Utils - 内部パッケージ

AI画像生成とFace Reference機能の実装モジュール
"""

from .gemini_image_generator import GeminiImageGenerator

__version__ = "1.0.0"

def get_version():
    """パッケージバージョンを取得"""
    return __version__

def get_supported_models():
    """サポートされているAIモデル一覧"""
    return [
        "gemini-2.5-flash-image-preview",  # メイン
        "gemini-pro-vision",               # フォールバック
    ]

def get_supported_formats():
    """サポートされている画像形式"""
    return [
        "PNG", "JPEG", "JPG", "WEBP"
    ]

__all__ = ['GeminiImageGenerator', 'get_version', 'get_supported_models', 'get_supported_formats']