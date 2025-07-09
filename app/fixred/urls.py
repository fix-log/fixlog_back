from django.urls import path

from .views import FixredListView

urlpatterns = [
    path("", FixredListView.as_view(), name="fixred-list")
    # path("/<itn:pk>/", FixredDetailView.as_view(), name="fixred-detail"),
]
