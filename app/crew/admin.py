from django.contrib import admin
from .models import Project, ProjectPosition, ProjectLanguage, ProjectSkillTool, UserBookmark


class ProjectPositionInline(admin.TabularInline):
    model = ProjectPosition
    extra = 1


class ProjectLanguageInline(admin.TabularInline):
    model = ProjectLanguage
    extra = 1


class ProjectSkillToolInline(admin.TabularInline):
    model = ProjectSkillTool
    extra = 1


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ["title", "user", "status", "deadline", "count", "created_at"]
    list_filter = ["status", "created_at"]
    search_fields = ["title", "description", "user__nickname"]
    inlines = [ProjectPositionInline, ProjectLanguageInline, ProjectSkillToolInline]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(ProjectPosition)
class ProjectPositionAdmin(admin.ModelAdmin):
    list_display = ["project", "position", "count"]
    list_filter = ["position"]


@admin.register(ProjectLanguage)
class ProjectLanguageAdmin(admin.ModelAdmin):
    list_display = ["project", "language"]
    list_filter = ["language"]


@admin.register(ProjectSkillTool)
class ProjectSkillToolAdmin(admin.ModelAdmin):
    list_display = ["project", "skill_tool"]
    list_filter = ["skill_tool"]


@admin.register(UserBookmark)
class UserBookmarkAdmin(admin.ModelAdmin):
    list_display = ["user", "project", "created_at"]
    list_filter = ["created_at", "project__status"]
    search_fields = ["user__nickname", "project__title"]
    readonly_fields = ["created_at"]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("user", "project")
