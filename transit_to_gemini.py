#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
現在時刻の惑星位置を計算し、占星術的解釈をGeminiに依頼するスクリプト
emotion_linkアカウント用の占星術ツイート機能
"""

import os
import sys
from datetime import datetime
import pytz
from math import floor

from skyfield.api import load
from skyfield.api import N, W, wgs84
from dotenv import load_dotenv

# プロジェクトのconfigからAPIキーを取得
sys.path.append(os.path.dirname(__file__))
try:
    from reply_bot.config import GEMINI_API_KEY
    print(f"✅ プロジェクト設定からAPIキーを取得: {GEMINI_API_KEY[:20]}...")
except ImportError as e:
    print(f"❌ エラー: reply_bot.configからAPIキーを取得できません: {e}")
    GEMINI_API_KEY = None

# ========== 設定 ==========
TARGET_TZ = "Asia/Tokyo"

# 12星座（0=牡羊座…）
ZODIAC_SIGNS = [
    "牡羊座","牡牛座","双子座","蟹座","獅子座","乙女座",
    "天秤座","蠍座","射手座","山羊座","水瓶座","魚座"
]

# Skyfieldで使う惑星キー（barycenterは木星以遠の重心）
PLANET_KEYS = [
    ("sun", "太陽"),
    ("moon", "月"),
    ("mercury", "水星"),
    ("venus", "金星"),
    ("mars", "火星"),
    ("jupiter barycenter", "木星"),
    ("saturn barycenter", "土星"),
    ("uranus barycenter", "天王星"),
    ("neptune barycenter", "海王星"),
    ("pluto barycenter", "冥王星"),
]

def deg_to_sign_and_dms(lon_deg: float):
    """黄経(0-360)を星座と度分秒に変換"""
    lon_deg = lon_deg % 360.0
    sign_idx = int(lon_deg // 30)
    sign = ZODIAC_SIGNS[sign_idx]
    deg_in_sign = lon_deg - 30 * sign_idx
    d = floor(deg_in_sign)
    m = floor((deg_in_sign - d) * 60)
    s = round(((deg_in_sign - d) * 60 - m) * 60)
    # 秒繰り上がり処理（まれに60になる）
    if s == 60:
        s = 0
        m += 1
    if m == 60:
        m = 0
        d += 1
        if d == 30:  # 30度に達したら次の星座へ
            d = 0
            sign_idx = (sign_idx + 1) % 12
            sign = ZODIAC_SIGNS[sign_idx]
    return sign, d, m, s

def now_in_utc():
    tz = pytz.timezone(TARGET_TZ)
    local_now = tz.localize(datetime.now().replace(microsecond=0))
    return local_now.astimezone(pytz.utc), local_now

def compute_transit_text():
    """現在の惑星位置を計算してテキスト化"""
    # 天文データ（最初の実行時に de421.bsp をDLしてキャッシュ）
    planets = load("de421.bsp")
    earth = planets["earth"]

    t_utc, t_local = now_in_utc()
    ts = load.timescale()
    t = ts.from_datetime(t_utc)

    lines = []
    for key, label in PLANET_KEYS:
        body = planets[key]
        # 黄道座標（緯度・経度）
        ecl = earth.at(t).observe(body).ecliptic_latlon()
        lon = ecl[1].degrees  # 黄経（度）
        sign, d, m, s = deg_to_sign_and_dms(lon)
        lines.append(f"{label}：{sign}{d}度{m}分{s}秒")

    header = f"{t_local.strftime('%Y-%m-%d %H:%M:%S')} ({TARGET_TZ}) のトランジット"
    return header, "\n".join(lines)

def build_prompt(transit_text: str):
    """占星術解釈用のプロンプトを生成"""
    return (
        "以下は現在時刻のトランジット（惑星の黄道十二宮上の位置）です。\n"
        "占星術の一般的な解釈として、全体傾向と注意点・活かし方を日本語で簡潔にまとめてください。\n"
        "専門用語は使いすぎず、日常生活の行動指針に落とし込んでください。\n"
        "感情と心理の観点から、今日の心の状態やコミュニケーションのヒントも含めてください。\n\n"
        f"{transit_text}\n"
    )

def get_gemini_interpretation(transit_text: str):
    """Gemini APIで占星術解釈を取得"""
    if not GEMINI_API_KEY:
        return "APIキーが設定されていないため、占星術解釈をスキップしました。"
    
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        
        model = genai.GenerativeModel('gemini-2.0-flash')
        prompt = build_prompt(transit_text)
        
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.7,
                max_output_tokens=800,
            )
        )
        
        return response.text.strip()
        
    except Exception as e:
        return f"Gemini解釈エラー: {str(e)}"

def generate_astrology_tweet():
    """占星術ツイート用のテキストを生成"""
    print("🌟 惑星位置計算開始...")
    header, body = compute_transit_text()
    transit_text = header + "\n" + body
    
    print("=== 計算結果 ===")
    print(transit_text)
    
    print("\n🔮 Gemini解釈リクエスト...")
    interpretation = get_gemini_interpretation(transit_text)
    
    print("\n=== 占星術解釈 ===")
    print(interpretation)
    
    # ツイート用に整形（120文字以内）
    tweet_text = f"🌟今日の星の流れ🌟\n{interpretation[:100]}..."
    
    return tweet_text, interpretation

def main():
    """メイン関数"""
    print("=" * 70)
    print("🌟 占星術的トランジット解釈システム")
    print("=" * 70)
    
    # 依存パッケージ確認
    required_packages = [
        ("skyfield", "skyfield"),
        ("pytz", "pytz"),
        ("google-generativeai", "google.generativeai")
    ]
    missing_packages = []
    
    for package_name, import_name in required_packages:
        try:
            __import__(import_name)
            print(f"✅ {package_name}: インストール済み")
        except ImportError:
            missing_packages.append(package_name)
            print(f"❌ {package_name}: 未インストール")
    
    if missing_packages:
        print(f"\n⚠️ 以下のパッケージをインストールしてください:")
        print(f"pip install {' '.join(missing_packages)}")
        return
    
    # 占星術ツイート生成
    tweet_text, full_interpretation = generate_astrology_tweet()
    
    print("\n" + "=" * 70)
    print("📝 生成されたツイートテキスト:")
    print("=" * 70)
    print(tweet_text)

if __name__ == "__main__":
    main()