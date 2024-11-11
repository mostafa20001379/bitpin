from django.contrib import admin
from .models import Content, Rating


@admin.register(Content)
class ContentAdmin(admin.ModelAdmin):
    list_display = ['title', 'cached_avg_rating', 'cached_rating_count', 'last_cache_update']
    search_fields = ['title', 'text']


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ['user', 'content', 'score', 'created_at', 'is_verified']
    list_filter = ['is_verified', 'created_at']
    search_fields = ['user__username', 'content__title']
