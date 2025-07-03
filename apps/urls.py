from django.urls import path
from .views import GuestLoginAPIView, IsPremiumAPIView, SentenceTranslateAPIView, WordSuggestionAPIView, \
    WordTranslationsAPIView, SentenceTranslationsAPIView, FeedbackAPIView
from apps.views import SearchWordAPIView, AdViewRewardAPIView

# =========== Search Word ===========
urlpatterns = [
    path('search-word/', SearchWordAPIView.as_view(), name='search-word'),
    path('search-word/word-suggestion/', WordSuggestionAPIView.as_view(), name='word-suggestion'),
    path('search-word/word-translations/', WordTranslationsAPIView.as_view(), name='word-translations'),


]

# ========== End Search word ==========



# =============== AdMob View =========

urlpatterns += [
    path('ad-viewed/', AdViewRewardAPIView.as_view(), name='ad-viewed'),
]

# ============== END =============



# ============ IsPremium =========

urlpatterns += [
    path('is-premium/', IsPremiumAPIView.as_view(), name='is-premium'),
]

# =========== End ============



# ======= JWT token =========

urlpatterns += [
    path('auth/guest-login/', GuestLoginAPIView.as_view(), name='guest-login'),
]

# ============ End =================



# ========= Sentence Translate =============

urlpatterns += [
    path('sentence-translate/', SentenceTranslateAPIView.as_view(), name='sentence-translate'),
    path('sentence-translate/history/', SentenceTranslationsAPIView.as_view(), name='sentence-translation-history'),
]

# =========== End ===============




# =============== Feedback User ===========

urlpatterns += [
    path('feedback-user/', FeedbackAPIView.as_view(), name='feedback-user'),
]

# =================== End ================









