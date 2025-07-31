from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from app.search.models import SearchHistory

from .models import RefreshToken, SocialAccount, User


class SearchHistoryInline(admin.TabularInline):  # or admin.StackedInline
    model = SearchHistory
    extra = 0
    readonly_fields = ("keyword", "created_at")
    can_delete = True


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("email", "nickname", "is_staff", "is_active", "date_joined")
    list_filter = ("is_staff", "is_active", "created_at")
    search_fields = ("email", "nickname", "phone_number")
    ordering = ("-date_joined",)
    filter_horizontal = (
        "groups",
        "user_permissions",
        "position",
        "language",
        "stack",
        "coop_tool",
        "interest_field",
        "interest_trend",
        "career",
    )
    inlines = [SearchHistoryInline]
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            _("Personal info"),
            {"fields": ("nickname", "profile_image", "phone_number", "birth", "experience", "portfolio", "ref_link")},
        ),
        (
            _("Relationships"),
            {"fields": ("position", "language", "stack", "coop_tool", "interest_field", "interest_trend", "career")},
        ),
        (_("Permissions"), {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
        (_("OAuth info"), {"fields": ("oauth_provider", "oauth_id")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2", "nickname", "is_staff", "is_active"),
            },
        ),
    )

    readonly_fields = ("date_joined", "last_login")


@admin.register(RefreshToken)
class RefreshTokenAdmin(admin.ModelAdmin):
    list_display = ("user", "token", "is_revoked", "created_at", "expires_at")
    search_fields = ("user__email",)
    list_filter = ("is_revoked",)


@admin.register(SocialAccount)
class SocialAccountAdmin(admin.ModelAdmin):
    list_display = ("user", "provider", "uid", "created_at")
    search_fields = ("user__email", "uid", "provider")
    list_filter = ("provider",)
