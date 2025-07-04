from django.urls import path, include
from .views import FixredListView

urlpatterns = [
    path("fixred/", FixredListView.as_view(), name="fixred-list"),
]