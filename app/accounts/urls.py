from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from app.accounts.views import (
    LoginView,
    delete_account_view,
    get_user_profile_view,
    logout_view,
    profile_view,
    signup_view,
    verify_code,
)

urlpatterns = []

urlpatterns += [
    path("register/", signup_view),
    path("verify-code/", verify_code),
    path("login/", LoginView.as_view()),
    path("profile/", profile_view),
    path("user/<int:user_id>/", get_user_profile_view),
    path("", delete_account_view),
    path("logout/", logout_view),
    path("token/refresh/", TokenRefreshView.as_view()),
]
