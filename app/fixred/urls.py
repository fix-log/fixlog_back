from django.urls import path

from .views import FixredCreateView, FixredDeleteView, FixredDetailView, FixredListView, FixredUpdateView

urlpatterns = [
    path("", FixredListView.as_view(), name="fixred-list"),
    path("<int:pk>/", FixredDetailView.as_view(), name="fixred-detail"),
    path("create/", FixredCreateView.as_view(), name="fixred-create"),
    path("<int:pk>/update/", FixredUpdateView.as_view(), name="fixred-update"),
    path("<int:pk>/delete/", FixredDeleteView.as_view(), name="fixred-delete"),
]
