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
<<<<<<< HEAD
    path("designs/", views.DesignListView.as_view(), name="design-list"),  # 목록 및 생성
    path("designs/<int:pk>/", views.DesignDetailView.as_view(), name="design-detail"),  # 조회, 수정(PATCH), 삭제
    # 북마크 관련 URL
    path("users/bookmarks", views.user_bookmarks, name="user-bookmarks"),  # 내 북마크 목록 조회
=======
    path("designs/", views.DesignListView.as_view(), name="design-list"),
    path("designs/<int:pk>/", views.DesignDetailView.as_view(), name="design-detail"),
    # CoopTool 관련 URL
    path("coop-tool/", views.CoopToolListView.as_view(), name="cooptool-list"),
    path("coop-tool/<int:pk>/", views.CoopToolDetailView.as_view(), name="cooptool-detail"),
    # InterestField 관련 URL
    path("interest-field/", views.InterestFieldListView.as_view(), name="interestfield-list"),
    path("interest-field/<int:pk>/", views.InterestFieldDetailView.as_view(), name="interestfield-detail"),
    # InterestTrend 관련 URL
    path("interest-trend/", views.InterestTrendListView.as_view(), name="interesttrend-list"),
    path("interest-trend/<int:pk>/", views.InterestTrendDetailView.as_view(), name="interesttrend-detail"),
    # Career 관련 URL
    path("career/", views.CareerListView.as_view(), name="career-list"),
    path("career/<int:pk>/", views.CareerDetailView.as_view(), name="career-detail"),
>>>>>>> develop
]
