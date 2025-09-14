#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
統合占星術システムのテスト
"""

from datetime import datetime
import sys
from pathlib import Path

# プロジェクトルートを追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from shared_modules.astrology.astro_system import (
    TransitInterpreter,
    BirthChartInterpreter
)

def test_transit_interpretation():
    """トランジット解釈のテスト"""
    print("=" * 60)
    print("🌟 トランジット解釈システム テスト")
    print("=" * 60)
    
    transit_system = TransitInterpreter()
    result = transit_system.interpret_current_transit()
    
    print(f"📅 解釈時刻: {result['datetime'].strftime('%Y年%m月%d日 %H時%M分')}")
    print("\n📍 惑星位置:")
    for planet, data in result['planet_positions'].items():
        print(f"  {planet}: {data['sign']} {data['degrees']}度{data['minutes']}分{data['seconds']}秒")
    
    print("\n🔮 解釈結果:")
    print(result['interpretation'])
    
    return result

def test_birth_chart_interpretation():
    """出生図解釈のテスト"""
    print("\n" + "=" * 60)
    print("🎂 出生図解釈システム テスト")
    print("=" * 60)
    
    birth_system = BirthChartInterpreter()
    
    # 例: 1990年3月15日 10:30 東京生まれ
    # 出生日時をタイムゾーン付きで作成
    import pytz
    jst = pytz.timezone('Asia/Tokyo')
    birth_datetime = jst.localize(datetime(1990, 3, 15, 10, 30))
    tokyo_location = (35.6762, 139.6503)  # 緯度, 経度
    
    result = birth_system.interpret_birth_chart(
        birth_datetime, tokyo_location
    )
    
    print(f"📅 出生日時: {result['birth_datetime'].strftime('%Y年%m月%d日 %H時%M分')}")
    print(f"📍 出生地: 東京 ({result['location']})")
    
    print("\n🌟 出生図惑星位置:")
    for planet, data in result['planet_positions'].items():
        print(f"  {planet}: {data['sign']} {data['degrees']}度{data['minutes']}分{data['seconds']}秒")
    
    print("\n🔮 出生図解釈:")
    print(result['interpretation'])
    
    return result

if __name__ == "__main__":
    print("🚀 統合占星術システム - 両機能テスト開始\n")
    
    try:
        # 1. トランジット解釈テスト
        transit_result = test_transit_interpretation()
        
        # 2. 出生図解釈テスト  
        birth_result = test_birth_chart_interpretation()
        
        print("\n" + "=" * 60)
        print("✅ 統合テスト完了 - 両システムが正常動作")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ エラー発生: {e}")
        import traceback
        traceback.print_exc()
