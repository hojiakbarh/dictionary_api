from django.contrib.auth.models import AbstractUser
from django.db.models import Model, CharField, URLField, OneToOneField, CASCADE, IntegerField, DateTimeField, \
    BooleanField, DateField, ForeignKey
from django.conf import settings
from django.db.models.fields import TextField
from django.utils import timezone
from django.utils.timezone import now




# Create your models here.

# ============= User ==============\

class User(AbstractUser):
    is_premium = BooleanField(default=False)

    def __str__(self):
        return self.username

#========= END ========================




# ========= Words search model ============
class Word(Model):
    uzbek = CharField(max_length=255)
    english = CharField(max_length=255)
    russian = CharField(max_length=255)
    pronunciation_url = URLField(blank=True, null=True)

    def __str__(self):
        return self.uzbek
# ============ END ===========================



# =========== AdView ===================

class AdView(Model):
    user = OneToOneField(settings.AUTH_USER_MODEL, CASCADE)
    count = IntegerField(default=0)
    updated_at = DateTimeField(auto_now=True)
    last_reward_at = DateField(null=True, blank=True)

    def reset_if_new_day(self):
        today = timezone.now().date()

        if self.last_reward_at != today:
            self.count = 0
            self.last_reward_at = today
            self.save()

            # 🔁 1 kunlik premium o‘tsa — premiumni o‘chir
            if self.user.is_premium:
                self.user.is_premium = False
                self.user.save()

# ============= ADMob END ======================



# ========= Word Search History ===============

class WordTranslation(Model):
    user = ForeignKey(settings.AUTH_USER_MODEL, CASCADE, related_name='translations')
    original_word = CharField(max_length=255, help_text='Original word')
    translated_word = CharField(max_length=255, help_text='Translated word')
    source_lang = CharField(max_length=255, help_text='Source language', default='unknown')
    target_lang = CharField(max_length=255, help_text='Target language', default='unknown')
    created_at = DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.original_word}"

    def get_translation_age(self):
        return (now() - self.created_at).days

# =========== End ====================




# ========= AI Translate Model =============

class SentenceTranslation(Model):
    user = ForeignKey(settings.AUTH_USER_MODEL, CASCADE, related_name='sentence_translations')
    original_text = TextField(help_text="Tarjima qilinadigan asl gap yoki matn")
    translated_text = TextField(help_text="Tarjima qilingan matn")
    source_lang = CharField(max_length=20, help_text="Tarjima qilinadigan til", default='unknown')
    target_lang = CharField(max_length=20, help_text="Tarjima qilingan til", default='unknown')
    created_at = DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.original_text}"

    def get_translated_age(self):
        return (now() - self.created_at).days

# ============ End =======================



# ============ Feedback (fikr-mulohaza) ===========

class Feedback(Model):
    user = ForeignKey(settings.AUTH_USER_MODEL, CASCADE, related_name='feedbacks')
    text = TextField(help_text="Foydalanuvchi tomonidan yuboriladigan fikr va mulohazalar...")
    rating = IntegerField(default=5, help_text="Baholang: 1 dan 5 gacha...")
    created_at = DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.rating}⭐"

# =============== End ==================











