from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from app.accounts.views import (
    LoginView,
    confirm_email_code_view,
    delete_account_view,
    get_user_profile_view,
    logout_view,
    profile_view,
    request_verification_code_view,
    signup_view,
)
from app.accounts import views_follow

urlpatterns = [
    path("request/", request_verification_code_view),
    path("confirm/", confirm_email_code_view),
    path("register/", signup_view),
    path("login/", LoginView.as_view()),
    path("profile/", profile_view),
    path("<int:user_id>/", get_user_profile_view),
    path("logout/", logout_view),
    path("token/refresh/", TokenRefreshView.as_view()),
    path("leave/", delete_account_view),

    # 팔로우 관련 URL
    path("<int:user_id>/follow/", views_follow.follow_toggle_view),
    path("<int:user_id>/followers/", views_follow.followers_list_view),
    path("<int:user_id>/following/", views_follow.following_list_view),
]
