from django.urls import path

from .views import FixredListView

urlpatterns = [
    path("list/", FixredListView.as_view(), name="fixred-list"),
]
