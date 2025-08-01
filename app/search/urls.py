from django.urls import path

from app.search.views import SearchHistoryDeleteOneView, SearchHistoryDeleteView, SearchHistoryView, SearchView

urlpatterns = [
    path("", SearchView.as_view(), name="search-history"),
    path("history/", SearchHistoryView.as_view(), name="search-history-list"),
    path("history/<int:pk>/", SearchHistoryDeleteOneView.as_view(), name="search-history-delete-one"),
    path("history/delete/", SearchHistoryDeleteView.as_view(), name="search-history-delete"),
]
