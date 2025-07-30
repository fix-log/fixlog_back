from app.notifications.models import Notification

# 알림 생성 함수 
def send_notification(user, sender, type_, event, target_id):
    Notification.objects.create(
        user=user,
        sender=sender,
        notification_type=type_,
        event=event,
        target_id=target_id
    )