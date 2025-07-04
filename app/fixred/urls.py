from django.urls import path, include
from .views import FixRedListView

urlpatterns = [
    path("fixred/", FixRedListView.as_view(), name="fixred-list"),
]