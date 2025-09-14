#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
星座別恋愛運システム
各星座の今日の恋愛運を生成
"""

from datetime import datetime
from typing import Dict, List
import pytz

# 統合占星術システムから基盤クラスをインポート
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from shared_modules.astrology.astro_system import AstroCalculator, GeminiInterpreter

class ZodiacLoveFortune:
    """星座別恋愛運システム"""
    
    def __init__(self):
        self.calculator = AstroCalculator()
        self.interpreter = GeminiInterpreter()
        
        # 十二星座リスト
        self.zodiac_signs = [
            "牡羊座", "牡牛座", "双子座", "蟹座", "獅子座", "乙女座",
            "天秤座", "蠍座", "射手座", "山羊座", "水瓶座", "魚座"
        ]
    
    def get_love_fortune_by_sign(self, zodiac_sign: str) -> Dict:
        """指定した星座の今日の恋愛運を取得"""
        
        if zodiac_sign not in self.zodiac_signs:
            raise ValueError(f"無効な星座名: {zodiac_sign}. 有効な星座: {self.zodiac_signs}")
        
        # 現在時刻（日本時間）
        jst = pytz.timezone('Asia/Tokyo')
        now = datetime.now(jst)
        
        # 惑星位置計算
        planet_positions = self.calculator.calculate_planet_positions(now)
        
        # 星座別恋愛運プロンプト
        prompt_template = f"""
        以下は{now.strftime("%Y年%m月%d日")}のトランジットデータです：
        
        {self._format_planet_positions(planet_positions)}
        
        この惑星配置から、{zodiac_sign}の人の今日の恋愛運を詳細に分析してください。
        
        以下の項目について具体的にアドバイスしてください：
        1. 今日の恋愛運の総合評価（5段階）
        2. 恋人がいる人へのアドバイス
        3. シングルの人へのアドバイス
        4. 恋愛での注意点
        5. ラッキーアクション
        6. 相性の良い星座（今日限定）
        
        温かく親しみやすい文体で、読む人が前向きになれるような内容で書いてください。
        """
        
        # 恋愛運解釈生成
        interpretation = self.interpreter.generate_interpretation(
            prompt_template, planet_positions, "love_fortune"
        )
        
        return {
            'date': now,
            'zodiac_sign': zodiac_sign,
            'planet_positions': planet_positions,
            'love_fortune': interpretation
        }
    
    def get_all_signs_love_fortune(self) -> Dict:
        """全星座の今日の恋愛運を一括取得"""
        
        results = {}
        for sign in self.zodiac_signs:
            try:
                results[sign] = self.get_love_fortune_by_sign(sign)
            except Exception as e:
                results[sign] = {'error': str(e)}
        
        return results
    
    def _format_planet_positions(self, planet_data: Dict) -> str:
        """惑星位置をテキスト形式に変換"""
        lines = []
        for planet, data in planet_data.items():
            line = f"{planet}：{data['sign']}{data['degrees']}度{data['minutes']}分{data['seconds']}秒"
            lines.append(line)
        return "\n".join(lines)

# 使用例とテスト
if __name__ == "__main__":
    love_system = ZodiacLoveFortune()
    
    # 特定の星座の恋愛運を取得
    print("=== 蠍座の今日の恋愛運 ===")
    scorpio_fortune = love_system.get_love_fortune_by_sign("蠍座")
    print(scorpio_fortune['love_fortune'])
    
    print("\n" + "="*50)
    print("✅ 星座別恋愛運システム テスト完了")
