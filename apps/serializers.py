from drf_spectacular.utils import extend_schema_field
from rest_framework.exceptions import ValidationError
from rest_framework.fields import SerializerMethodField, CharField, IntegerField
from rest_framework.serializers import ModelSerializer, Serializer

from apps.models import Word, SentenceTranslation, WordTranslation, Feedback


class WordSerializer(ModelSerializer):
    pronunciation_url = SerializerMethodField()

    class Meta:
        model = Word
        fields = ('english', 'uzbek', 'russian', 'pronunciation_url')

    @extend_schema_field(str)
    def get_pronunciation_url(self, obj):
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        if user.is_authenticated and user.is_premium:
            return obj.pronunciation_url
        return None



class SentenceTranslateSerializer(Serializer):
    text = CharField(required=True)
    source_lang = CharField(required=True)
    target_lang = CharField(required=True)

    def validate(self, attrs):
        if attrs['source_lang'] == attrs['target_lang']:
            raise ValidationError("❌ Manba tili va tarjima tili bir xil bo‘lmasligi kerak.")
        return attrs


class GuestLoginSerializer(Serializer):
    pass

class AdViewRewardSerializer(Serializer):
    pass

class IsPremiumSerializer(Serializer):
    pass


class WordTranslationSerializer(ModelSerializer):
    class Meta:
        model = WordTranslation
        fields = ['id', 'original_word', 'translated_word', 'source_lang', 'target_lang', 'created_at']
        read_only_fields = ['id','translated_word','created_at']



class SuggestionSerializer(Serializer):
    query = CharField(required=True)
    lang = CharField(required=True)



#============ Feedback Serializer ==========

class FeedbackSerializer(Serializer):
    text = CharField(required=True)
    rating = IntegerField(required=True) # default = 5








