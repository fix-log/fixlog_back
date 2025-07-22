from django.urls import path

from .views import FixredCreateView, FixredDetailView, FixredListView

urlpatterns = [
    path("", FixredListView.as_view(), name="fixred-list"),
    path("<int:pk>/", FixredDetailView.as_view(), name="fixred-detail"),
    path("create/", FixredCreateView.as_view(), name="fixred-create"),
]
