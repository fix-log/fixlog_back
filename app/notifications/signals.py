from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import NotificationSetting


# 유저 생성시 알림 온오프 모델 자동 생성
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_notification_setting(sender, instance, created, **kwargs):
    if created:
        NotificationSetting.objects.create(user=instance)
