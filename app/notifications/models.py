from django.db import models

from app.crew.models import Project
from app.fixred.models import Fixred
from app.util.models import CreatedOnlyModel
from app.workroom.models import Workroom


class Notification(CreatedOnlyModel):
    TYPE_CHOICES = [
        ("fixred", "픽레드"),
        # ("fixletter", "픽레터"),
        ("crew", "크루모집"),
        ("workroom", "워크룸"),
    ]
    EVENT_CHOICES = [
        ("apply", "지원"),
        ("comment", "댓글"),
        ("complete", "완료"),
        ("deadline", "마감임박"),
        ("feedback", "평가"),
        ("follow", "팔로우"),
        ("invite", "초대"),
        ("like", "좋아요"),
        ("mention", "언급"),
    ]
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name="notifications")
    sender = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True, blank=True)

    notification_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    event = models.CharField(max_length=50, choices=EVENT_CHOICES, null=True, blank=True)
    target_id = models.PositiveIntegerField(null=True, blank=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.nickname}: [{self.notification_type} 알림] {self.content[:20]}..."

    def get_target_object(self):
        if self.notification_type == "fixred":
            return Fixred.objects.filter(pk=self.target_id).first()
        elif self.notification_type == "workroom":
            return Workroom.objects.filter(pk=self.target_id).first()
        elif self.notification_type == "crew":
            return Project.objects.filter(pk=self.target_id).first()
        # elif notification.notification_type == 'fixletter':
        #     return None  # 픽레터는 현재 구현되지 않음
        else:
            return None
