from http import HTTPStatus
from django.contrib.auth import get_user_model
from django.db.models import Q, Count
from django.utils import timezone
from django.utils.crypto import get_random_string
from drf_spectacular.utils import extend_schema, OpenApiParameter
from langdetect import detect, LangDetectException
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from apps.fallback_translate import smart_translate
from apps.models import Word, AdView, SentenceTranslation, WordTranslation, Feedback
from apps.serializers import WordSerializer, SentenceTranslateSerializer, GuestLoginSerializer, AdViewRewardSerializer, \
    IsPremiumSerializer, SuggestionSerializer, WordTranslationSerializer, FeedbackSerializer
from root.settings import LANG_FIELD_MAP


# Create your views here.

# ===============  So'zni tarjima qilish bolimi ==========================
@extend_schema(
    tags=['search-word'],
    parameters=[
        OpenApiParameter(
            name='q',
            type=str,
            location=OpenApiParameter.QUERY,  # 👈 BUNI QO‘YISH MUHIM
            required=True,
            description='Search word in English'
        )
    ],
    responses={200: WordSerializer}
)



class SearchWordAPIView(APIView):
    permission_classes = (IsAuthenticated,)  # foydalanuvchi identifikatsiyalangan bo‘lishi kerak

    def get(self, request, *args, **kwargs):
        query = request.GET.get('q', '').strip()
        if not query:
            return Response({'status': 400, 'message': "So‘z yuborilmadi"})

        user = request.user

        try:
            # 1. Tilni aniqlash
            try:
                lang_code = detect(query)
            except LangDetectException:
                lang_code = None

            field_name = LANG_FIELD_MAP.get(lang_code)

            # 2. Fallback aniqlash
            if not field_name:
                for lang_key in LANG_FIELD_MAP:
                    if Word.objects.filter(**{f"{LANG_FIELD_MAP[lang_key]}__iexact": query}).exists():
                        field_name = LANG_FIELD_MAP[lang_key]
                        lang_code = lang_key
                        break

            if not field_name:
                # Aniqlanmasa, barcha tillardan taxminiy qidiruv qilamiz
                words = Word.objects.filter(
                    Q(english__icontains=query) | Q(russian__icontains=query) | Q(uzbek__icontains=query)
                ).order_by('english')[:10]
                if not words.exists():
                    return Response({'status': 404, 'message': "So‘z topilmadi"})
                serializer = WordSerializer(words, many=True, context={'request': request})
                return Response({'status': 200, 'detected_language': 'unknown', 'data': serializer.data})

            # 3. Aniq qidiruv (birinchi topilsa)
            word = Word.objects.filter(**{f"{field_name}__iexact": query}).first()
            if word:
                # Tarjima natijasini olish (foydalanuvchining tiliga qarab)
                translations = {
                    'english': word.english,
                    'russian': word.russian,
                    'uzbek': word.uzbek
                }

                target_lang_code = [lang for lang in LANG_FIELD_MAP.keys() if LANG_FIELD_MAP[lang] != field_name]
                for lang in target_lang_code:
                    to_field = LANG_FIELD_MAP[lang]
                    translated = getattr(word, to_field, None)
                    if translated:
                        # ✅ Tarixga yozish (asosiy nuqta)
                        WordTranslation.objects.create(
                            user=user,
                            original_word=query,
                            translated_word=translated,
                            source_lang=lang_code or 'unknown',
                            target_lang=lang
                        )
                        break

                serializer = WordSerializer(word, context={'request': request})
                return Response({'status': 200, 'detected_language': lang_code, 'data': serializer.data})

            # 4. Aniq topilmasa taxminiy qidiruv
            words = Word.objects.filter(**{f"{field_name}__icontains": query}).order_by('english')[:10]
            if not words.exists():
                return Response({'status': 404, 'message': "So‘z topilmadi"})

            serializer = WordSerializer(words, many=True, context={'request': request})
            return Response({'status': 200, 'detected_language': lang_code, 'data': serializer.data})

        except Exception as e:
            return Response({'status': 500, 'message': str(e)})



# ============= Word Translation History =============

@extend_schema(tags=['search-word'], responses={200: WordSerializer})
class WordTranslationsAPIView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = WordTranslationSerializer

    def get(self, request):
        user = request.user
        translations = WordTranslation.objects.filter(user=user).order_by('-created_at')

        # 1) So‘zlar ro‘yxati (oxirgi 20 ta)

        recent = translations[:]
        recent_list = [{
            'word' : t.original_word,
            'translated' : t.translated_word,
            'source_lang' : t.source_lang,
            'target_lang' : t.target_lang,
            'date' : t.created_at.strftime('%Y-%m-%d %H:%M')
        } for t in recent]

        # 2) Statistika

        total_count = translations.count()
        top_words = translations.values('original_word')\
                        .annotate(count=Count('original_word'))\
                        .order_by('-count')[:10]

        return Response({
            'status' : HTTPStatus.OK,
            'total_count' : total_count,
            'top_words' : len(top_words),
            'recent_history' : recent_list,
        })

    # 3) History delete

    def delete(self, request):
        user = request.user
        WordTranslation.objects.filter(user=user).delete()
        return Response({
            "status": HTTPStatus.OK,
            "message" : "✅ Tarix muvaffaqiyatli tozalandi"
        })


@extend_schema(tags=['search-word'], request=WordSerializer, responses={200: WordSerializer})
class WordSuggestionAPIView(APIView):
    permission_classes = [AllowAny]  # Login bo'lmaganlarga ham ochiq bo'lishi mumkin
    serializer_class = SuggestionSerializer

    def get(self, request):
        serializer = SuggestionSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        query = serializer.validated_data['query'].strip().lower()
        lang = serializer.validated_data['lang'].strip().lower()

        if len(query) < 1:
            return Response({"suggestions": []})

        suggestions = Word.objects.filter(
            lang=lang,
            word__icontains=query
        ).order_by('word').values_list('word', flat=True).distinct()[:10]

        return Response({
            "suggestions": list(suggestions)
        })


# ===================== End ======================




# ============= JWT token =========================
User = get_user_model()

class GuestLoginAPIView(APIView):
    permission_classes = [AllowAny]
    serializer_class = GuestLoginSerializer

    def post(self, request):
        guest_username = request.data.get('username', 'guest_user')
        user, created = User.objects.get_or_create(username=guest_username)

        if created:
            # Parol yaratish shu yerda bo‘ladi
            password = get_random_string(12)
            user.set_password(password)
            user.save()

        refresh = RefreshToken.for_user(user)
        return Response({
            "status": 200,
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "message": "Guest login successful"
        })
# ================= End =========================


# ==================== AdMob bolimi =============================

@extend_schema(tags=['admob-view'])
class AdViewRewardAPIView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AdViewRewardSerializer

    def post(self, request):
        ad_view, _ = AdView.objects.get_or_create(user=request.user)
        ad_view.reset_if_new_day()  # 💡 Har kuni qayta nolga tushuriladi

        ad_view.count += 1
        ad_view.save()

        if ad_view.count >= 2:
            request.user.is_premium = True
            request.user.save()
            ad_view.count = 0
            ad_view.last_reward_at = timezone.now().date()
            ad_view.save()
            return Response({'status': 200, 'message': "🎉 Premium ochildi (1 kunlik)"})

        return Response({
            'status': 200,
            'message': f"👁 Reklama ko‘rilgan: {ad_view.count}/2"
        })

# ================== AdMob END ==================


# ============== IsPremium ===============

@extend_schema(tags=['is-premium'])
class IsPremiumAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = IsPremiumSerializer

    def get(self, request, *args, **kwargs):
        user = request.user
        try:
            ad_view = AdView.objects.get(user=user)
            ad_view.reset_if_new_day()
        except AdView.DoesNotExist:
            pass

        return Response({
            'status' : HTTPStatus.OK,
            'message' : user.is_premium,
        })

# ============ End ==================



# ============== AI Translate =============

@extend_schema(
    tags=["sentence-translate"],
    request=SentenceTranslateSerializer,
    responses={200: SentenceTranslateSerializer}
)
class SentenceTranslateAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        if not request.user.is_premium:
            return Response({
                "status": HTTPStatus.FORBIDDEN,
                "message": "❌ Tarjima faqat premium foydalanuvchilar uchun"
            })

        serializer = SentenceTranslateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        text = serializer.validated_data.get("text").strip()
        source_lang = serializer.validated_data['source_lang'].strip().lower()
        target_lang = serializer.validated_data['target_lang'].strip().lower()

        if not text:
            return Response({
                "status": HTTPStatus.BAD_REQUEST,
                "message": "❌ Matn yuborilmadi."
            })

        translated_text = smart_translate(text, source_lang=source_lang,target_lang=target_lang)

        if not translated_text or translated_text.strip().lower() == text.lower():
            return Response({
                "status": HTTPStatus.BAD_REQUEST,
                "message": "❌ Tarjima amalga oshmadi.",
            })


        SentenceTranslation.objects.create(
            user=request.user,
            original_text=text,
            translated_text=translated_text,
            source_lang=source_lang,
            target_lang=target_lang
        )

        return Response({
            "status": HTTPStatus.OK,
            "message": translated_text,
            "source_lang": source_lang,
            "target_lang": target_lang
        })




# ================== Sentence Histories =============

@extend_schema(tags=['sentence-translate'], responses=SentenceTranslateSerializer)
class SentenceTranslationsAPIView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SentenceTranslateSerializer

    def get(self, request):
        user = request.user
        translations = SentenceTranslation.objects.filter(user=user).order_by('-created_at')

        # 1) Oxirgi 20 ta tarjima tarixi
        recent = translations[:]
        recent_list = [{
            'text': t.original_text,
            'translated': t.translated_text,
            'source_lang': t.source_lang,
            'target_lang': t.target_lang,
            'date': t.created_at.strftime('%Y-%m-%d %H:%M')
        } for t in recent]

        # 2) Statistika
        total_count = translations.count()
        top_sentence = translations.values('original_text')\
                            .annotate(count=Count('original_text'))\
                            .order_by('-count')[:10]

        return Response({
            'status' : HTTPStatus.OK,
            'total_count' : total_count,
            'top_sentences' : len(top_sentence),
            'recent_history' : recent_list,
        })
    def delete(self, request):
        user = request.user
        SentenceTranslation.objects.filter(user=user).delete()
        return Response({
            "status": HTTPStatus.OK,
            'message': "✅ Gaplar tarixi tozalandi"
        })
# ================= End ====================



# =============== Feedback API ===============
@extend_schema(tags=['feedback-user'], responses=FeedbackSerializer, request=FeedbackSerializer)
class FeedbackAPIView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FeedbackSerializer

    def post(self, request):
        user = request.user
        data = request.data
        serializer = FeedbackSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        Feedback.objects.create(
            user=user,
            text=serializer.validated_data.get('text'),
            rating=serializer.validated_data.get('rating'),
            created_at=serializer.validated_data.get('created_at'),
        )
        return Response({
            "status": HTTPStatus.OK,
            "message" : "✅ Fikr uchun rahmat!"
        })

# ============ End ===============





































