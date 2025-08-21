from django.urls import path

from app.fixletter.views import FixletterListView, MessageListView, FixletterCreateView
from .views import ws_test


urlpatterns = [
    path("", FixletterListView.as_view()),
    path("<int:fixletter_id>/",MessageListView.as_view()),
    path("open/",FixletterCreateView.as_view(),name="fixletter_open"),
    path("test/", ws_test, name="fixletter_ws_test"),
    path("test/<int:fixletter_id>/", ws_test, name="fixletter_ws_test_with_id"),
]
