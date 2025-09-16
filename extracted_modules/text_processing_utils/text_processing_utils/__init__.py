#!/usr/bin/env python3
"""
Text Processing Utilities
感情コンテンツ抽出とテキスト処理のためのユーティリティパッケージ

このパッケージは占星術テキストから感情的なコンテンツを抽出し、
AI画像生成プロンプトなどに適用するためのツールを提供します。

主な機能:
- 感情コンテンツ抽出
- 占星術記述の除去
- 感情キーワード分析
"""

from .emotion_extraction import extract_emotional_content

__version__ = "1.0.0"
__author__ = "TwitterBot_Nexus_02 Project"
__email__ = "contact@example.com"

# パッケージで公開する関数・クラスを定義
__all__ = [
    "extract_emotional_content",
]

# パッケージの説明
def get_package_info():
    """パッケージ情報を取得"""
    return {
        "name": "text_processing_utils",
        "version": __version__,
        "description": "感情コンテンツ抽出とテキスト処理のためのユーティリティパッケージ",
        "author": __author__,
        "email": __email__,
        "functions": __all__,
    }