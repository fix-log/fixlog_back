from django.contrib import admin

from .models import SearchHistory


@admin.register(SearchHistory)
class SearchHistoryAdmin(admin.ModelAdmin):
    list_display = ["user", "keyword"]
    list_filter = ["user"]
    search_fields = ["user__nickname", "keyword"]
    ordering = ["-created_at"]
