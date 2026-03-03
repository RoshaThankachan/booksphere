from django.contrib import admin
from .models import UserPreference, Recommendation


@admin.register(UserPreference)
class UserPreferenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'reading_level', 'last_updated')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('last_updated',)


@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = ('user', 'book', 'reason', 'score', 'created_at')
    list_filter = ('reason', 'created_at')
    search_fields = ('user__username', 'book__title')
    readonly_fields = ('created_at',)
    ordering = ('-score', '-created_at')
