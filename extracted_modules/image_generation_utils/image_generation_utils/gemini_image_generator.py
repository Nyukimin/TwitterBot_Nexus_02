#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gemini-2.5-flash-image-preview 画像生成クラス (独立版)

元ファイル: shared_modules/image_generation/gemini_image_generator.py
ファイルサイズ0 bytes問題修正版 - 完全独立パッケージ化
"""

import os
import sys
import requests
import base64
import json
from datetime import datetime
from typing import Optional, List
import logging

class GeminiImageGenerator:
    """Gemini-2.5-flash-image-preview による画像生成 (独立版)"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        初期化
        
        Args:
            api_key: Gemini APIキー (省略時は環境変数から取得)
        """
        self.api_key = api_key or self._get_gemini_api_key()
        self.model_name = "gemini-2.5-flash-image-preview"
        self.endpoint_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent"
        
        # ログ設定
        self.logger = logging.getLogger(__name__)
        
        # APIキー検証
        if not self.api_key:
            raise ValueError("Gemini APIキーが設定されていません")
    
    def _get_gemini_api_key(self) -> Optional[str]:
        """Gemini APIキーを取得 (独立版 - 環境変数のみ)"""
        # 環境変数から取得
        api_key = os.getenv('GEMINI_API_KEY')
        if api_key:
            return api_key
        
        # .envファイルからの取得を試行
        try:
            env_file_path = os.path.join(os.getcwd(), '.env')
            if os.path.exists(env_file_path):
                with open(env_file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith('GEMINI_API_KEY='):
                            return line.split('=', 1)[1].strip('"\'')
        except Exception as e:
            self.logger.debug(f".envファイル読み込みエラー: {e}")
        
        return None
    
    def generate_image(self, prompt: str, save_path: str, 
                      face_reference_images: Optional[List[str]] = None) -> bool:
        """
        画像を生成して保存
        
        Args:
            prompt: 画像生成プロンプト
            save_path: 保存パス
            face_reference_images: 顔参照画像のパス（複数可）
            
        Returns:
            bool: 生成成功の場合True
        """
        
        if not self.api_key:
            print("❌ Gemini APIキーが設定されていません")
            return False
        
        # リクエストヘッダー
        headers = {
            "x-goog-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        
        # リクエストデータ
        data = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }
        
        # face_reference画像がある場合は追加
        if face_reference_images:
            self._add_face_reference_to_request(data, face_reference_images)
        
        print(f"🎨 Gemini画像生成開始: {prompt[:50]}...")
        
        try:
            # API リクエスト実行
            response = requests.post(self.endpoint_url, headers=headers, json=data)
            
            print(f"📡 HTTPステータス: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                
                # 画像データを抽出して保存
                if self._extract_and_save_image(result, save_path):
                    file_size = os.path.getsize(save_path)
                    print(f"✅ 画像保存完了: {save_path} ({file_size} bytes)")
                    return True
                else:
                    print("⚠️ 画像データの抽出に失敗")
                    return False
            else:
                print(f"❌ APIエラー: {response.status_code}")
                print(f"📄 レスポンス: {response.text[:200]}...")
                return False
                
        except Exception as e:
            print(f"❌ リクエストエラー: {str(e)}")
            return False
    
    def _extract_and_save_image(self, result: dict, save_path: str) -> bool:
        """
        APIレスポンスから画像データを抽出して保存（修正版）
        ファイルサイズ0 bytes問題を修正
        """
        
        if 'candidates' not in result or len(result['candidates']) == 0:
            print("⚠️ 候補が見つかりません")
            return False
        
        candidate = result['candidates'][0]
        
        if 'content' not in candidate or 'parts' not in candidate['content']:
            print("⚠️ コンテンツパートが見つかりません")
            return False
        
        parts = candidate['content']['parts']
        print(f"📋 パート数: {len(parts)}")
        
        for i, part in enumerate(parts):
            print(f"  Part {i}: {list(part.keys())}")
            
            # 画像データを探す（修正版：Base64デコード処理）
            if 'inlineData' in part:
                inline_data = part['inlineData']
                if 'data' in inline_data:
                    print("✅ 画像データ発見!")
                    print(f"📄 MIMEタイプ: {inline_data.get('mimeType', 'unknown')}")
                    
                    try:
                        # Base64デコードして保存（修正版）
                        image_data = base64.b64decode(inline_data['data'])
                        
                        # 保存ディレクトリ作成
                        os.makedirs(os.path.dirname(save_path), exist_ok=True)
                        
                        with open(save_path, 'wb') as f:
                            f.write(image_data)
                        
                        # ファイルサイズ確認
                        file_size = os.path.getsize(save_path)
                        if file_size > 0:
                            print(f"💾 画像保存完了: {save_path} ({file_size} bytes)")
                            return True
                        else:
                            print("⚠️ ファイルサイズが0です")
                            return False
                            
                    except Exception as e:
                        print(f"❌ 画像データの処理エラー: {str(e)}")
                        return False
            
            elif 'text' in part:
                text_content = part['text'][:100]
                print(f"  📝 テキスト: {text_content}...")
        
        print("⚠️ 画像データが見つかりませんでした")
        return False
    
    def _add_face_reference_to_request(self, data: dict, face_reference_images: List[str]):
        """face_reference画像をリクエストに追加"""
        
        for img_path in face_reference_images:
            if os.path.exists(img_path):
                try:
                    with open(img_path, 'rb') as f:
                        image_data = base64.b64encode(f.read()).decode('utf-8')
                    
                    data['contents'][0]['parts'].append({
                        "inlineData": {
                            "mimeType": "image/jpeg",
                            "data": image_data
                        }
                    })
                    print(f"🖼️ face_reference画像追加: {img_path}")
                    
                except Exception as e:
                    print(f"⚠️ face_reference画像の読み込み失敗: {img_path} - {str(e)}")
    
    def generate_emotion_link_image(self, prompt: str, output_folder: str = "images/emotion_link") -> Optional[str]:
        """
        emotion_link用画像生成（便利メソッド）
        
        Args:
            prompt: 画像生成プロンプト
            output_folder: 出力フォルダ
            
        Returns:
            str: 生成された画像のパス（失敗時はNone）
        """
        
        # ファイル名生成
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"emotion_link_{timestamp}.png"
        save_path = os.path.join(output_folder, filename)
        
        # face_reference画像の検索
        face_reference_folder = os.path.join(output_folder, "face_reference")
        face_reference_images = []
        
        if os.path.exists(face_reference_folder):
            for file in os.listdir(face_reference_folder):
                if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                    face_reference_images.append(os.path.join(face_reference_folder, file))
        
        print(f"🔍 face_reference画像: {len(face_reference_images)}枚発見")
        
        # 画像生成実行
        if self.generate_image(prompt, save_path, face_reference_images):
            return save_path
        else:
            return None
    
    def test_api_connection(self) -> bool:
        """
        API接続テスト
        
        Returns:
            bool: 接続成功時True
        """
        
        if not self.api_key:
            print("❌ APIキーが設定されていません")
            return False
        
        test_prompt = "simple red circle"
        test_folder = "temp_test"
        
        try:
            result = self.generate_emotion_link_image(test_prompt, test_folder)
            
            if result and os.path.exists(result):
                # テストファイル削除
                os.remove(result)
                if os.path.exists(test_folder) and not os.listdir(test_folder):
                    os.rmdir(test_folder)
                
                print("✅ API接続テスト成功")
                return True
            else:
                print("❌ API接続テスト失敗")
                return False
                
        except Exception as e:
            print(f"❌ API接続テストエラー: {str(e)}")
            return False
    
    @staticmethod
    def get_supported_image_formats() -> List[str]:
        """サポートされる画像形式一覧"""
        return ['PNG', 'JPEG', 'JPG', 'WEBP']
    
    @staticmethod 
    def get_model_info() -> dict:
        """モデル情報取得"""
        return {
            'name': 'gemini-2.5-flash-image-preview',
            'provider': 'Google',
            'capabilities': [
                'text-to-image',
                'face-reference',
                'base64-output',
                'high-resolution'
            ],
            'max_resolution': '1920x1080',
            'supported_formats': GeminiImageGenerator.get_supported_image_formats()
        }