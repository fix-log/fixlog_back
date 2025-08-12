from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from app.fixred.models import FixredLike
from app.notifications.models import Notification
from app.notifications.utils import send_notification


@receiver(post_save, sender=FixredLike)
def handle_like_created(sender, instance, created, **kwargs):
    if created:
        # 자기 자신에게는 알림 안 보내도록 예외 처리
        if instance.fixred.user != instance.user:
            send_notification(
                user=instance.fixred.user,
                sender=instance.user,
                type_="fixred",
                event="like",
                target_id=instance.fixred.id,
            )
