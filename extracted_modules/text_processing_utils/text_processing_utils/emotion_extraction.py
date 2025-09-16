#!/usr/bin/env python3
"""
感情コンテンツ抽出モジュール
ツイートから感情的な内容を抽出し、画像生成プロンプト用に処理する
"""

import re


def extract_emotional_content(text: str) -> str:
    """
    テキストから感情的なコンテンツを抽出
    
    Args:
        text: 元のテキスト（例: "今日は月が魚座に入る。感受性が高まりやすい日。人の気持ちに寄り添って過ごそう。"）
    
    Returns:
        str: 抽出された感情コンテンツ（例: "感受性が高まりやすい日。人の気持ちに寄り添って過ごそう。"）
    """
    if not text:
        return ""
    
    # 占星術情報の冒頭部分を除去（「今日は〜。」の最初の文を削除）
    # パターン1: "今日は...。" の形式を削除
    pattern1 = r'^今日は[^。]*。\s*'
    processed_text = re.sub(pattern1, '', text.strip())
    
    # パターン2: 占星術用語を含む冒頭文を削除
    astro_terms = [
        '月が.*?に入る', '水星逆行', 'トランジット', '新月', '満月', 
        '金星が.*?に', '火星が.*?に', '木星が.*?に', '土星が.*?に',
        '天王星が.*?に', '海王星が.*?に', '冥王星が.*?に'
    ]
    
    for term in astro_terms:
        pattern = rf'^[^。]*{term}[^。]*。\s*'
        processed_text = re.sub(pattern, '', processed_text, flags=re.IGNORECASE)
    
    # パターン3: 時間・日付表現を含む冒頭文を削除
    time_patterns = [
        r'^[^。]*今日[^。]*。\s*',
        r'^[^。]*明日[^。]*。\s*',
        r'^[^。]*週末[^。]*。\s*',
        r'^[^。]*午前[^。]*。\s*',
        r'^[^。]*午後[^。]*。\s*'
    ]
    
    for pattern in time_patterns:
        processed_text = re.sub(pattern, '', processed_text)
    
    # 感情・心理関連のキーワードを含む文を優先的に抽出
    emotional_keywords = [
        '感情', '気持ち', '心', '感受性', '共感', '寄り添', '優しさ', '温かさ',
        '癒し', '安らぎ', '穏やか', '静か', '深呼吸', 'リラックス', '落ち着き',
        '不安', '心配', '緊張', 'ストレス', '疲れ', '悲しみ', '喜び', '幸せ',
        '愛', '思いやり', '信頼', '希望', '勇気', '自信', '成長', '変化'
    ]
    
    # 感情関連キーワードを含む文を抽出
    sentences = re.split(r'[。！？]', processed_text)
    emotional_sentences = []
    
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
            
        # 感情キーワードが含まれている文を優先
        for keyword in emotional_keywords:
            if keyword in sentence:
                emotional_sentences.append(sentence + '。')
                break
        else:
            # キーワードがなくても、短めの文は感情的な可能性が高い
            if len(sentence) < 50 and sentence:
                emotional_sentences.append(sentence + '。')
    
    # 抽出された感情文がある場合はそれを返す
    if emotional_sentences:
        result = ' '.join(emotional_sentences)
    else:
        # フォールバック: 処理済みテキストをそのまま返す
        result = processed_text
    
    # 最終的な整理
    result = result.strip()
    if not result:
        result = "心穏やかに過ごしましょう。"
    
    return result


# テスト用の関数
def test_extract_emotional_content():
    """テスト関数"""
    test_cases = [
        "今日は月が魚座に入る。感受性が高まりやすい日。人の気持ちに寄り添って過ごそう。",
        "今日は水星逆行開始。コミュニケーションに注意。心を落ち着けて丁寧に対話しよう。",
        "満月の夜。感情が高ぶりやすい時期。深呼吸して自分の心と向き合ってみて。",
        "今日も一日お疲れさま。小さな幸せを見つけて心温かく過ごそう。"
    ]
    
    for i, test_text in enumerate(test_cases, 1):
        result = extract_emotional_content(test_text)
        print(f"テスト{i}:")
        print(f"入力: {test_text}")
        print(f"出力: {result}")
        print("-" * 50)


if __name__ == "__main__":
    test_extract_emotional_content()