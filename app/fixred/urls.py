from django.urls import include, path

from .views import FixredListView

urlpatterns = [
    path("fixred/", FixredListView.as_view(), name="fixred-list"),
]
