"""# import requests
#
# def fallback_translate(text: str, target_lang='en'):
#     url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl={target_lang}&dt=t&q={text}"
#     response = requests.get(url)
#     if response.status_code == 200:
#         try:
#             return response.json()[0][0][0]
#         except Exception:
#             return "Tarjima olishda xatolik"
#     return "Tarjima xizmati ishlamadi."
import openai
import requests
import urllib.parse


from langdetect import detect, LangDetectException

def detect_language(text: str) -> str:
    try:
        lang = detect(text)
        if lang == 'so':  # Somali tiliga o‘xshab ketmasligi uchun
            return 'uz'
        return lang
    except LangDetectException:
        return "auto"



def fallback_translate(text: str, source_lang: str = "auto", target_lang: str = "uz") -> str:
    if not text.strip():
        return "❌ Matn bo‘sh"

    encoded_text = urllib.parse.quote(text)
    url = (
        f"https://translate.googleapis.com/translate_a/single"
        f"?client=gtx&sl={source_lang}&tl={target_lang}&dt=t&q={encoded_text}"
    )
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            result = response.json()
            return result[0][0][0].strip()
        else:
            return "❌ Google Translate javob qaytarmadi"
    except Exception:
        return "❌ Google Translate ishlamayapti"

def ai_translate(text: str, source_lang: str = 'auto', target_lang: str = "uz") -> str:
    prompt = (
        f"Translate the following sentence from {source_lang} to {target_lang}, "
        f"preserving punctuation and meaning:\n\n{text}"
    )
    try:
        response = openai.ChatCompletion.create(
            model = "gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful translator."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=250
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        return f"❌ AI tarjima xatoligi: {str(e)}"

def smart_translate(text: str, target_lang: str = "uz") -> tuple[str, str]:
    detected_lang = detect_language(text)

    # Avval OpenAI orqali harakat qilib ko‘ramiz
    ai_result = ai_translate(text, source_lang=detected_lang, target_lang=target_lang)
    if ai_result.startswith("❌"):
        fallback_result = fallback_translate(text, source_lang=detected_lang, target_lang=target_lang)
        return fallback_result, detected_lang

    return ai_result, detected_lang

import requests
import urllib.parse
import openai
from langdetect import detect, LangDetectException
from root import settings

openai.api_key = settings.OPENAI_API_KEY  # openai api key

def detect_language(text: str) -> str:
    try:
        lang = detect(text)
        # Somali va Swahili noto‘g‘ri aniqlansa, 'uz' deb olish
        return 'uz' if lang in ['so', 'sw', 'tl', 'tr', 'fi', 'id', 'sq', 'et'] else lang
    except LangDetectException:
        return "auto"

def fallback_translate(text: str, source_lang: str = "auto", target_lang: str = "uz") -> str:
    if not text.strip():
        return "❌ Matn bo‘sh"

    encoded_text = urllib.parse.quote(text)
    url = (
        f"https://translate.googleapis.com/translate_a/single"
        f"?client=gtx&sl={source_lang}&tl={target_lang}&dt=t&q={encoded_text}"
    )
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            result = response.json()
            return result[0][0][0].strip()
        return "❌ Google Translate javob qaytarmadi"
    except Exception:
        return "❌ Google Translate ishlamayapti"

def ai_translate(text: str, source_lang: str = "auto", target_lang: str = "uz") -> str:
    prompt = (
        f"Translate the following sentence from {source_lang} to {target_lang}, "
        f"preserving punctuation and meaning:\n\n{text}"
    )
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful translator."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=250
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        return f"❌ AI tarjima xatoligi: {str(e)}"

def smart_translate(text: str, target_lang: str = "uz") -> tuple[str, str]:
    detected_lang = detect_language(text)
    ai_result = ai_translate(text, source_lang=detected_lang, target_lang=target_lang)
    if ai_result.startswith("❌"):
        fallback_result = fallback_translate(text, source_lang=detected_lang, target_lang=target_lang)
        return fallback_result, detected_lang
    return ai_result, detected_lang"""

import requests
import urllib.parse
import openai
from root import settings

openai.api_key = settings.OPENAI_API_KEY


def fallback_translate(text: str, source_lang: str, target_lang: str) -> str:
    encoded_text = urllib.parse.quote(text)
    url = (
        f"https://translate.googleapis.com/translate_a/single"
        f"?client=gtx&sl={source_lang}&tl={target_lang}&dt=t&q={encoded_text}"
    )
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return response.json()[0][0][0].strip()
        return "❌ Google Translate javob bermadi."
    except Exception:
        return "❌ Google Translate ishlamayapti"

def ai_translate(text: str, source_lang: str, target_lang: str) -> str:
    prompt = f"Translate from {source_lang} to {target_lang}, keeping punctuation:\n\n{text}"
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful translator."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=300
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"❌ AI tarjima xatoligi: {str(e)}"

def smart_translate(text: str, source_lang: str, target_lang: str) -> str:
    ai_result = ai_translate(text, source_lang, target_lang)
    if ai_result.startswith("❌"):
        return fallback_translate(text, source_lang, target_lang)
    return ai_result

