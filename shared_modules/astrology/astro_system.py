#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
統合占星術システム
トランジット解釈と出生図解釈の共通基盤
"""

import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from skyfield.api import load, Topos
from skyfield.data import hipparcos
import pytz
import yaml
from typing import Dict, List, Optional, Tuple

# プロジェクトルートを追加
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import google.generativeai as genai

# テキスト処理機能をインポート
try:
    from shared_modules.text_processing import extract_emotional_content
except ImportError:
    # フォールバック用の簡易実装
    import re
    def extract_emotional_content(text: str) -> str:
        pattern = r'^今日は.*?。'
        return re.sub(pattern, '', text, count=1).strip()

class AstroCalculator:
    """占星術計算エンジン（共通）"""
    
    def __init__(self):
        self.ts = load.timescale()
        self.planets = load('de421.bsp')
        
        # 惑星定義
        self.planet_names = {
            'sun': '太陽',
            'moon': '月', 
            'mercury': '水星',
            'venus': '金星',
            'mars': '火星',
            'jupiter': '木星',
            'saturn': '土星',
            'uranus': '天王星',
            'neptune': '海王星',
            'pluto': '冥王星'
        }
        
        # 黄道十二宮
        self.zodiac_signs = [
            '牡羊座', '牡牛座', '双子座', '蟹座', '獅子座', '乙女座',
            '天秤座', '蠍座', '射手座', '山羊座', '水瓶座', '魚座'
        ]
    
    def calculate_planet_positions(self, dt: datetime, location: Optional[Tuple[float, float]] = None) -> Dict:
        """惑星位置を計算（共通メソッド）"""
        t = self.ts.from_datetime(dt)
        
        # 観測地点設定（出生図で使用）
        if location:
            observer = self.planets['earth'] + Topos(location[0], location[1])
        else:
            observer = self.planets['earth']
        
        results = {}
        
        for eng_name, jp_name in self.planet_names.items():
            if eng_name == 'sun':
                planet = self.planets['sun']
            elif eng_name == 'moon':
                planet = self.planets['moon']
            elif eng_name == 'pluto':
                planet = self.planets['pluto barycenter']
            else:
                planet = self.planets[f'{eng_name} barycenter']
            
            astrometric = observer.at(t).observe(planet)
            ra, dec, distance = astrometric.radec()
            
            # 黄経計算
            ecliptic_lon = self._ra_dec_to_ecliptic_longitude(ra.hours, dec.degrees, t)
            
            # 星座とリード分秒
            sign_index = int(ecliptic_lon // 30)
            degree_in_sign = ecliptic_lon % 30
            degrees = int(degree_in_sign)
            minutes = int((degree_in_sign - degrees) * 60)
            seconds = int(((degree_in_sign - degrees) * 60 - minutes) * 60)
            
            results[jp_name] = {
                'sign': self.zodiac_signs[sign_index],
                'degrees': degrees,
                'minutes': minutes,
                'seconds': seconds,
                'longitude': ecliptic_lon
            }
        
        return results
    
    def _ra_dec_to_ecliptic_longitude(self, ra_hours, dec_degrees, t):
        """赤道座標から黄経に変換"""
        # 簡略化された変換（実際にはより複雑な計算が必要）
        ra_degrees = ra_hours * 15
        # 黄道傾斜角を考慮した変換
        obliquity = 23.4367  # 簡略化
        import math
        ra_rad = math.radians(ra_degrees)
        dec_rad = math.radians(dec_degrees)
        obl_rad = math.radians(obliquity)
        
        ecliptic_lon = math.atan2(
            math.sin(ra_rad) * math.cos(obl_rad) + math.tan(dec_rad) * math.sin(obl_rad),
            math.cos(ra_rad)
        )
        
        return math.degrees(ecliptic_lon) % 360

class GeminiInterpreter:
    """Gemini解釈エンジン（共通）"""
    
    def __init__(self):
        # APIキーの設定（既存のプロジェクト設定から取得）
        import os
        api_key = self._get_gemini_api_key()
        genai.configure(api_key=api_key)
    
    def _get_gemini_api_key(self) -> str:
        """プロジェクト設定からGemini APIキーを取得"""
        try:
            from reply_bot.config import GEMINI_API_KEY
            return GEMINI_API_KEY
        except ImportError:
            # 環境変数からの取得
            import os
            api_key = os.getenv('GEMINI_API_KEY')
            if api_key:
                return api_key
            raise ValueError("Gemini APIキーが見つかりません")
    
    def generate_interpretation(self, prompt_template: str, planet_data: Dict,
                             interpretation_type: str = "transit", personality_prompt: str = "", 
                             extract_emotional_only: bool = False) -> str:
        """占星術解釈を生成 - PERSONALITY_PROMPT対応"""
        
        # 惑星位置をテキスト化
        planet_text = self._format_planet_positions(planet_data)
        
        # プロンプト作成（PERSONALITY_PROMPT対応）
        if personality_prompt:
            # PERSONALITY_PROMPTプレースホルダーを置換
            if '{PERSONALITY_PROMPT}' in prompt_template:
                prompt_with_personality = prompt_template.replace('{PERSONALITY_PROMPT}', personality_prompt)
            else:
                prompt_with_personality = f"{personality_prompt}\n\n{prompt_template}"
            # 惑星位置を置換
            full_prompt = prompt_with_personality.format(
                planet_positions=planet_text,
                type=interpretation_type
            )
        else:
            full_prompt = prompt_template.format(
                planet_positions=planet_text,
                type=interpretation_type
            )
        
        # Gemini APIで解釈生成
        model = genai.GenerativeModel('gemini-2.0-flash')
        try:
            response = model.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=1000
                )
            )
            
            # セーフティフィルターチェック
            if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
                result_text = response.text
                # 感情的内容のみを抽出する場合
                if extract_emotional_only:
                    result_text = extract_emotional_content(result_text)
                return result_text
            else:
                # セーフティフィルターまたはエラーで内容が生成されなかった場合
                finish_reason = response.candidates[0].finish_reason if response.candidates else 'UNKNOWN'
                return f"申し訳ございませんが、現在の占星術解釈を生成できませんでした。（理由: {finish_reason}）"
                
        except Exception as e:
            return f"占星術解釈の生成中にエラーが発生しました: {str(e)}"
    
    def _format_planet_positions(self, planet_data: Dict) -> str:
        """惑星位置をテキスト形式に変換"""
        lines = []
        for planet, data in planet_data.items():
            line = f"{planet}：{data['sign']}{data['degrees']}度{data['minutes']}分{data['seconds']}秒"
            lines.append(line)
        return "\n".join(lines)

class TransitInterpreter:
    """トランジット解釈システム"""
    
    def __init__(self):
        self.calculator = AstroCalculator()
        self.interpreter = GeminiInterpreter()
    
    def interpret_current_transit(self) -> Dict:
        """現在のトランジットを解釈"""
        
        # 現在時刻（日本時間）
        jst = pytz.timezone('Asia/Tokyo')
        now = datetime.now(jst)
        
        # 惑星位置計算
        planet_positions = self.calculator.calculate_planet_positions(now)
        
        # トランジット解釈プロンプト
        prompt_template = """
        以下は{now}のトランジットデータです：
        
        {planet_positions}
        
        このトランジットから、今日の全体的な傾向、注意点、活かし方、
        感情と心理、コミュニケーションのヒントを分析してください。
        
        具体的で実用的なアドバイスを含めて、日本語で詳細に解釈してください。
        """.format(now=now.strftime("%Y年%m月%d日 %H時%M分"), 
                   planet_positions="{planet_positions}")
        
        # 解釈生成 - PERSONALITY_PROMPTを渡す
        interpretation = self.interpreter.generate_interpretation(
            prompt_template, planet_positions, "transit", personality_prompt=""
        )
        
        return {
            'datetime': now,
            'planet_positions': planet_positions,
            'interpretation': interpretation
        }

class BirthChartInterpreter:
    """出生図解釈システム"""
    
    def __init__(self):
        self.calculator = AstroCalculator()
        self.interpreter = GeminiInterpreter()
    
    def interpret_birth_chart(self, birth_datetime: datetime, 
                            location: Tuple[float, float] = None) -> Dict:
        """出生図を解釈"""
        
        # 惑星位置計算（出生時刻・場所）
        planet_positions = self.calculator.calculate_planet_positions(
            birth_datetime, location
        )
        
        # 出生図解釈プロンプト
        prompt_template = """
        以下は{birth_date}の出生図データです：
        
        {planet_positions}
        
        この出生図から、この人の基本的な性格、才能、人生の課題、
        恋愛傾向、仕事適性、成長のポイントを分析してください。
        
        深い洞察と具体的なアドバイスを含めて、日本語で詳細に解釈してください。
        """.format(birth_date=birth_datetime.strftime("%Y年%m月%d日 %H時%M分"),
                   planet_positions="{planet_positions}")
        
        # 解釈生成
        interpretation = self.interpreter.generate_interpretation(
            prompt_template, planet_positions, "birth_chart"
        )
        
        return {
            'birth_datetime': birth_datetime,
            'location': location,
            'planet_positions': planet_positions,
            'interpretation': interpretation
        }

# 使用例
if __name__ == "__main__":
    # トランジット解釈
    transit_system = TransitInterpreter()
    transit_result = transit_system.interpret_current_transit()
    print("=== トランジット解釈 ===")
    print(transit_result['interpretation'])
    
    # 出生図解釈（例：1990年3月15日 10:30 東京）
    birth_system = BirthChartInterpreter()
    birth_dt = datetime(1990, 3, 15, 10, 30)
    tokyo_location = (35.6762, 139.6503)  # 緯度, 経度
    
    birth_result = birth_system.interpret_birth_chart(
        birth_dt, tokyo_location
    )
    print("\n=== 出生図解釈 ===")
    print(birth_result['interpretation'])
