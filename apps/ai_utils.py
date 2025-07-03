"""import openai
from django.conf import settings
from openai import OpenAIError

# API kalitni xavfsiz joydan olish
openai.api_key = getattr(settings, 'OPENAI_API_KEY', None)

def ai_translate(text: str, target_lang: str = "uzbek") -> str:
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": f"You are a helpful translator. Translate everything the user sends into {target_lang}."
                },
                {
                    "role": "user",
                    "content": text
                }
            ],
            temperature=0.3,
            max_tokens=250,
        )
        return response['choices'][0]['message']['content'].strip()

    except OpenAIError as e:
        return f"❌ Tarjima amalga oshmadi: {str(e)}"

"""



"""from googletrans import Translator
from langdetect import detect, LangDetectException

translator = Translator()

def ai_translate(text: str, dest_lang: str = "uz") -> str:
    try:
        # Avval tilni aniqlash
        try:
            detected_lang = detect(text)
        except LangDetectException:
            detected_lang = "en"  # Default til

        # Tarjima qilish
        result = translator.translate(text, src=detected_lang, dest=dest_lang)
        return result.text.strip(), detected_lang
    except Exception as e:
        return f"❌ Tarjima amalga oshmadi: {str(e)}", None"""



import openai
from langdetect import detect
from root import settings

openai.api_key = settings.OPENAI_API_KEY

def ai_translate(text: str) -> str:
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # gpt-4 bo‘lmasa, ushbu modelni ishlatish tavsiya etiladi
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful translator. Translate the following sentence clearly into Uzbek."
                },
                {
                    "role": "user",
                    "content": text
                }
            ],
            temperature=0.3,
            max_tokens=250,
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        return f"❌ Tarjima amalga oshmadi: {str(e)}"
