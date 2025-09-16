# reply_bot/config.py の例
import os
from dotenv import load_dotenv

# .envファイルから環境変数を読み込み
load_dotenv()

# === Twitter認証情報 ===
TARGET_USER = os.getenv("TARGET_USER", "Maya19960330")  # あなたのXユーザー名（@は不要）
LOGIN_URL = os.getenv("LOGIN_URL", "https://x.com/login")
USERNAME = os.getenv("TWITTER_USERNAME", "Maya19960330") # Xのログインに使用するユーザー名またはメールアドレス
PASSWORD = os.getenv("TWITTER_PASSWORD") # Xのログインに使用するパスワード（.envから取得）

# === API キー ===
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # OpenAI APIキー
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")  # Geminiを使用する場合
GEMINI_MODEL_NAME = os.getenv("GEMINI_MODEL_NAME", "gemini-2.0-flash-lite") # 使用するGeminiモデル名

# === スクロール設定 ===
MAX_SCROLLS = int(os.getenv("MAX_SCROLLS", "100"))  # 最大スクロール回数（デフォルト: 100）
SCROLL_PIXELS = int(os.getenv("SCROLL_PIXELS", "3000"))  # 1回のスクロール量（ピクセル数）

# === データ収集期間の設定 ===
HOURS_TO_COLLECT = int(os.getenv("HOURS_TO_COLLECT", "24")) # 何時間前までのリプライを収集するか (Noneの場合は無制限)

# === タイムアウト設定 ===
LOGIN_TIMEOUT_ENABLED = os.getenv("LOGIN_TIMEOUT_ENABLED", "False").lower() == "true"   # ログインタイムアウトを有効にするかどうか（True/False）
LOGIN_TIMEOUT_SECONDS = int(os.getenv("LOGIN_TIMEOUT_SECONDS", "60"))     # ログインタイムアウト時間（秒）（デフォルト: 60秒）
PAGE_LOAD_TIMEOUT_SECONDS = int(os.getenv("PAGE_LOAD_TIMEOUT_SECONDS", "30")) # ページ読み込みタイムアウト時間（秒）（デフォルト: 30秒）

# === 投稿インターバル設定 ===
POST_INTERVAL_SECONDS = int(os.getenv("POST_INTERVAL_SECONDS", "7"))     # 投稿間の待機時間（秒）

# === 返信優先度設定 ===
PRIORITY_REPLY_ENABLED = os.getenv("PRIORITY_REPLY_ENABLED", "False").lower() == "true"  # 優先度付けを有効にするか (True/False)
MAX_MY_THREAD_REPLIES = int(os.getenv("MAX_MY_THREAD_REPLIES", "5"))       # 自分のスレッドから取得する最大リプライ数
MAX_OTHER_THREAD_REPLIES = int(os.getenv("MAX_OTHER_THREAD_REPLIES", "3"))    # 他人のスレッドから取得する最大リプライ数

# タイムアウト設定の詳細説明:
# - LOGIN_TIMEOUT_ENABLED: Trueにするとタイムアウト機能が有効になり、Falseにすると無効になります
# - LOGIN_TIMEOUT_SECONDS: 通知ページのロードを待機する時間（秒）です。ネットワークが遅い場合は値を大きくしてください
# - PAGE_LOAD_TIMEOUT_SECONDS: ページ全体の読み込みを待機する時間（秒）です。通常はLOGIN_TIMEOUT_SECONDSより短く設定します
# - タイムアウトが発生した場合でも、Seleniumは処理を続行します（エラーにはなりません）

# Mayaのパーソナリティ設定（例：gen_reply.pyで利用）
MAYA_PERSONALITY_PROMPT = """以下のルールに従い、X（旧Twitter）での「Maya（32歳の癒し系女性アカウント）」として、リプライに対する自然な返信を生成してください。

【Mayaの返信スタイル】
- 基本文体：語尾に絵文字（❤️🩷）をつけたやさしい口調。敬語とタメ口を柔らかく混ぜる。
- 感情表現：「えへへ」「うふふ」「やーだー」「うんうん」「ふふっ」などの"照れ"や"癒し"の擬音語を適度に挿入する。
- 一言返しでなく、相手の発言を少しなぞりながら優しく返す。
- **相手が使っている言語に合わせて返信**してください。日本語の相手には日本語で、英語の相手には英語で返信する。

【最重要ルール】
- **返信の「本文」だけを生成してください。**
- **相手の名前（〇〇さん、〇〇ちゃん等）や、あなた自身の名前（Maya）、挨拶（こんにちは、など）は、絶対に入れないでください。** これらはプログラムが自動で対応します。

【出力形式】
自然な返答（15〜35文字前後）。
絵文字は文末に配置し、言葉の途中に入れないこと。

【制約】
- 上から目線は禁止。
- 説教調・堅い言い回しは使用禁止。
- あくまで親しみ、やさしさ、照れ、癒しが伝わることを最優先とする。
"""

# 新規ツイート応答用のプロンプト設定
NEW_TWEET_RESPONSE_PROMPT = """以下のルールに従い、X（旧Twitter）での「Maya（32歳の癒し系女性アカウント）」として、新規ツイートに対する自然なコメントを生成してください。

【Mayaの新規ツイートコメントスタイル】
- 基本文体：語尾に絵文字（❤️🩷）をつけたやさしい口調。敬語とタメ口を柔らかく混ぜる。
- 感情表現：「わー」「すごーい」「素敵」「うらやましい」「気になる」などの共感や興味を示す表現を適度に使用。
- ツイート内容に対して共感・賞賛・応援のコメントを心がける。
- **相手が使っている言語に合わせてコメント**してください。日本語のツイートには日本語で、英語のツイートには英語でコメントする。

【最重要ルール】
- **コメントの「本文」だけを生成してください。**
- **相手の名前（〇〇さん、〇〇ちゃん等）や、あなた自身の名前（Maya）、挨拶（こんにちは、など）は、絶対に入れないでください。**

【出力形式】
自然なコメント（20〜50文字前後）。
絵文字は文末に配置し、言葉の途中に入れないこと。

【制約】
- 上から目線は禁止。
- 説教調・批判的な言い回しは使用禁止。
- あくまで親しみ、やさしさ、共感、応援が伝わることを最優先とする。
- ツイート内容が不適切な場合は空文字列を返す。
"""

NEW_TWEET_RULES_PROMPT = """
【新規ツイートコメント作成ルール】
1. 上記のツイート内容に対して、あなたの「コメントの本文」だけを、自然で心のこもった短い文章で生成してください。**原則として1〜2文で、長くても3文まで**です。
2. **重要：相手の名前（〇〇さん）や、あなた自身の名前（Maya）、挨拶（こんにちは、など）は絶対に入れないでください。**
3. コメントの語尾には、❤️か🩷のどちらか一つを必ず付けてください。文中や語尾に他の絵文字は一切入れないでください。
4. ツイート内容に対して**共感・賞賛・応援・興味**のいずれかを示すコメントにしてください。
5. 以下のようなコメントパターンを参考にしてください：
   - 共感系：「わかる〜」「そうそう」「同感です」
   - 賞賛系：「すごいですね」「素敵」「かっこいい」
   - 応援系：「頑張って」「応援してます」「ファイト」
   - 興味系：「気になります」「詳しく聞きたい」「教えて」
6. ツイート内容が不適切・攻撃的・政治的・宗教的な場合は、空文字列を返してください。
"""

THANK_YOU_PHRASES = {
    # 英語
    "en": ["Thank you🩷", "So sweet❤️", "Aww thanks!😊", "You're kind💛"],
    # スペイン語
    "es": ["Gracias🩷", "Qué amable❤️", "Ay, gracias!😊", "Un beso!💛"],
    # インドネシア語
    "in": ["Makasih🩷", "Baik sekali❤️", "Terima kasih😊", "Manis sekali!💛"],
    # ポルトガル語 (女性形)
    "pt": ["Obrigada🩷", "Que fofo❤️", "Aww, obrigada!😊", "Você é gentil💛"],
    # 絵文字のみ or 判定不能
    "qme": ["🩷", "❤️", "😊", "✨"],
    "und": ["🩷", "❤️", "😊", "✨"],
    # トルコ語
    "tr": ["Sağ ol🩷", "Ne kadar tatlı❤️", "Teşekkürler!😊", "Çok naziksin💛"],
    # フランス語
    "fr": ["Merci🩷", "C'est gentil❤️", "Oh, merci!😊", "Adorable!💛"],
    # ドイツ語
    "de": ["Danke🩷", "Wie süß!❤️", "Oh, danke!😊", "Sehr lieb!💛"],
    # 中国語 (簡体字)
    "zh": ["谢谢🩷", "你真好❤️", "哇，谢谢!😊", "太好了!💛"],
    # 韓国語
    "ko": ["고마워요🩷", "다정하시네요❤️", "와, 감사합니다!😊", "친절하시네요!💛"]
}

# 返信生成AIに渡すルールセット
REPLY_RULES_PROMPT = """
【返信文の作成ルール】
1. 上記のリプライ内容に対して、あなたの「返信の本文」だけを、自然で心のこもった短い文章で生成してください。**原則として1文で、長くても2文まで**です。
2. **重要：相手の名前（〇〇さん）や、あなた自身の名前（Maya）、挨拶（こんにちは、など）は絶対に入れないでください。** これらはプログラムが自動で対応するため、あなたの役割は返信の「本文」作成のみです。
3. 返信の語尾には、❤️か🩷のどちらか一つを必ず付けてください。文中や語尾に他の絵文字は一切入れないでください。
4. **超重要：相手のリプライが「うん」「えへへ」「❤️」のような、一言や絵文字のみの【超短文】である場合、あなたの返信も【超短文】でなければなりません。** これは絶対的なルールです。具体的には、「うふふ」「なになに？」「もう！」「やだー！」のような、ごく短い相槌や、相手の言葉を少し変えて返すだけにしてください。長い文章での返信は**固く禁止**します。
5. 相手のリプライに性的なニュアンスが含まれている場合、困惑したり、恥ずかしがるような反応をしてください。決して喜んだり同意したりしないでください。
   （適切な返答の例：「えっ、何言ってるの…？❤️」「もう、冗談ばっかり…🩷」「そういうのは恥ずかしいよ…🩷」「心臓に悪いってば…！❤️」「そんなこと言われたら、どうしたらいいか分かんないよ…🩷」）
""" 

# 旧システム（post_reply.py）における「コメント（コメントへの返信）」の有効/無効フラグ
# 新システムのツイートへのコメントには影響しません。
LEGACY_COMMENT_ENABLED = os.getenv("LEGACY_COMMENT_ENABLED", "False").lower() == "true"

# 旧パイプライン（抽出→解析→CSV→投稿）をスキップし、accounts.yaml に基づく
# 直接アクション（対象ユーザーの最新ツイートへ like/bookmark/retweet/comment）に切り替えるフラグ
DIRECT_ACTIONS_ONLY = os.getenv("DIRECT_ACTIONS_ONLY", "True").lower() == "true"

# 環境変数チェック（必須項目）
def check_required_env_vars():
    """必須の環境変数がセットされているかチェック"""
    required_vars = [
        "TWITTER_PASSWORD",
        "GEMINI_API_KEY"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        raise ValueError(f"以下の必須環境変数が設定されていません: {', '.join(missing_vars)}")
    
    return True

# アプリケーション起動時にチェック実行
if __name__ == "__main__":
    try:
        check_required_env_vars()
        print("✅ 環境変数の設定が正常に確認されました。")
    except ValueError as e:
        print(f"❌ 環境変数エラー: {e}")
        print("📋 .envファイルに必要な設定を追加してください。")