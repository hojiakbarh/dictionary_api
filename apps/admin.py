from django.contrib import admin

from apps.models import Word, Feedback

# Register your models here.


from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    pass


@admin.register(Word)
class WordAdmin(admin.ModelAdmin):
    list_display = ['english', 'uzbek', 'russian']
    search_fields = ['english', 'uzbek', 'russian']

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('user', 'rating', 'text', 'created_at')
    search_fields = ('user__username', 'text')
    list_filter = ('rating', 'created_at')