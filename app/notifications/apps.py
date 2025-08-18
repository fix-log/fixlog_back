from django.apps import AppConfig


class NotificationsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "app.notifications"

    def ready(self):
        import app.notifications.signals
