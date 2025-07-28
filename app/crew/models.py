from django.conf import settings
from django.db import models

from app.util.models import Language, Position, Stack


class Project(models.Model):
    STATUS_CHOICES = [
        ("recruiting", "모집중"),
        ("completed", "모집완료"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="projects")
    title = models.CharField(max_length=100)
    deadline = models.DateTimeField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_estimated_period = models.CharField(max_length=50)
    description = models.TextField()
    count = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="recruiting")

    # ManyToMany 관계 추가
    positions = models.ManyToManyField(Position, through="ProjectPosition", blank=True)
    languages = models.ManyToManyField(Language, through="ProjectLanguage", blank=True)
    skill_tools = models.ManyToManyField(Stack, through="ProjectSkillTool", blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


# 중간 테이블들
class ProjectPosition(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    position = models.ForeignKey(Position, on_delete=models.CASCADE)
    count = models.IntegerField(default=1)  # 해당 포지션 필요 인원수

    class Meta:
        unique_together = ("project", "position")
        db_table = "project_position"


class ProjectLanguage(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    language = models.ForeignKey(Language, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("project", "language")
        db_table = "project_language"


class ProjectSkillTool(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    skill_tool = models.ForeignKey(Stack, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("project", "skill_tool")
        db_table = "project_skill_tool"


<<<<<<< HEAD
class Application(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="applications")
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="applications")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "project")
        db_table = "application"

    def __str__(self):
        return f"{self.user.username} - {self.project.title}"
=======
# 북마크 모델
class UserBookmark(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bookmarks")
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="bookmarks")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "project")
        db_table = "user_bookmark"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.nickname} → {self.project.title}"
>>>>>>> develop
