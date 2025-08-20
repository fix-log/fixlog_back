from django.urls import path

from .views import NotificationListView, NotificationReadAllView, NotificationReadView, NotificationSettingView

urlpatterns = [
    path("", NotificationListView.as_view(), name="notification-list"),
    path("<int:pk>/read/", NotificationReadView.as_view(), name="notification-read"),
    path("read-all/", NotificationReadAllView.as_view(), name="notification-read-all"),
    path("on-off/", NotificationSettingView.as_view(), name="notification-on/off"),
]
