from django.contrib import admin

from .models import Fixred, FixredBlock, FixredComment, FixredImage, FixredReport


class FixredImageInline(admin.TabularInline):
    model = FixredImage
    extra = 0


class FixredCommentInline(admin.TabularInline):
    model = FixredComment
    extra = 0
    readonly_fields = ("created_at",)


# Fixred
@admin.register(Fixred)
class FixredAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "content_preview", "like_count", "comment_count", "read_permission", "created_at")
    list_display_links = ("content_preview",)
    search_fields = ("content", "user__nickname")
    readonly_fields = ("created_at", "updated_at")
    inlines = [FixredCommentInline, FixredImageInline]

    def content_preview(self, obj):
        return obj.content[:20]

    content_preview.short_description = "내용 미리보기"


# FixredImage
@admin.register(FixredImage)
class FixredImageAdmin(admin.ModelAdmin):
    list_display = ("id", "post", "image")


# FixredComment
@admin.register(FixredComment)
class FixredCommentAdmin(admin.ModelAdmin):
    list_display = ("id", "fixred", "user", "comment", "created_at")
    search_fields = ("comment", "user__nickname")


# FixredReport
@admin.register(FixredReport)
class FixredReportAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "fixred_post", "reason", "created_at")
    list_filter = ("reason",)
    search_fields = ("fixred_post__content", "user__nickname")


# FixredBlock
@admin.register(FixredBlock)
class FixredBlockAdmin(admin.ModelAdmin):
    list_display = ("id", "blocker", "blocked", "created_at")
    search_fields = ("blocker__nickname", "blocked__nickname")
