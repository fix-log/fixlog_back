from django.db import models

from app.util.models import CreatedOnlyModel


class SearchHistory(CreatedOnlyModel):
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name="search_histories")
    keyword = models.CharField(max_length=100)

    class Meta:
        verbose_name = "검색 내역"
        verbose_name_plural = "검색 내역"
        ordering = ["-created_at"]  # 최신순 정렬

    def __str__(self):
        return f"{self.user.nickname} 검색어: {self.keyword}"
