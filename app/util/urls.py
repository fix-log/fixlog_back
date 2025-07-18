from django.urls import path

from app.util import views

urlpatterns = [
    # Position 관련 URL
    path("positions/", views.PositionListView.as_view(), name="position-list"),
    path("positions/<int:pk>/", views.PositionDetailView.as_view(), name="position-detail"),
    # Language 관련 URL
    path("languages/", views.LanguageListView.as_view(), name="language-list"),
    path("languages/<int:pk>/", views.LanguageDetailView.as_view(), name="language-detail"),
    # Stack 관련 URL
    path("stacks/", views.StackListView.as_view(), name="stack-list"),
    path("stacks/<int:pk>/", views.StackDetailView.as_view(), name="stack-detail"),
    # Design 관련 URL
    path("designs/", views.DesignListView.as_view(), name="design-list"),
    path("designs/<int:pk>/", views.DesignDetailView.as_view(), name="design-detail"),
    # CoopTool 관련 URL
    path("coop-tools/", views.CoopToolListView.as_view(), name="cooptool-list"),
    path("coop-tools/<int:pk>/", views.CoopToolDetailView.as_view(), name="cooptool-detail"),
    # InterestField 관련 URL
    path("interest-fields/", views.InterestFieldListView.as_view(), name="interestfield-list"),
    path("interest-fields/<int:pk>/", views.InterestFieldDetailView.as_view(), name="interestfield-detail"),
    # InterestTrend 관련 URL
    path("interest-trends/", views.InterestTrendListView.as_view(), name="interesttrend-list"),
    path("interest-trends/<int:pk>/", views.InterestTrendDetailView.as_view(), name="interesttrend-detail"),
    # Career 관련 URL
    path("careers/", views.CareerListView.as_view(), name="career-list"),
    path("careers/<int:pk>/", views.CareerDetailView.as_view(), name="career-detail"),
]
