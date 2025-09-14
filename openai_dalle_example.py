
# OpenAI DALL-E 3を使用した画像生成例
import openai
from openai import OpenAI

client = OpenAI(api_key="your-openai-api-key")

def generate_emotion_image(prompt, save_path):
    """OpenAI DALL-E 3で画像生成"""
    
    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024",
        quality="standard",
        n=1,
    )
    
    image_url = response.data[0].url
    
    # 画像をダウンロードして保存
    import requests
    img_response = requests.get(image_url)
    
    with open(save_path, 'wb') as f:
        f.write(img_response.content)
    
    return save_path

# emotion_link用プロンプト例
prompts = {
    "morning": "感情と心理をテーマにした温かく優しい抽象的なイラスト、パステルカラー",
    "afternoon": "日常の小さな幸せと心の成長、希望に満ちた自然の要素", 
    "evening": "夜の静けさと内省、穏やかで瞑想的な青と紫の色調"
}
