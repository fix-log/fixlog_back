from django.urls import path

from app.search.views import SearchHistoryDeleteView, SearchHistoryView, SearchView

urlpatterns = [
    path("", SearchView.as_view(), name="search-history"),
    path("history/", SearchHistoryView.as_view(), name="search-history-list"),
    path("history/delete/", SearchHistoryDeleteView.as_view(), name="search-history-delete"),
]
