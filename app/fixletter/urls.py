from django.urls import path

from app.fixletter.views import FixletterListView, MessageListView


urlpatterns = [
    path("", FixletterListView.as_view()),
    path("<int:fixletter_id>/messages/",MessageListView.as_view())
]