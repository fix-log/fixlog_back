from django.urls import path
from app.accounts.views import (
    signup_view,
    verify_code,
    LoginView,
    update_profile_view,
    delete_account_view,
    logout_view,
    get_profile_view,
    get_user_profile_view,
)
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = []

urlpatterns += [
    path("signup/", signup_view),
    path("verify-code/", verify_code),
    path("login/", LoginView.as_view()),
    path("profile/", get_profile_view),
    path("user/<int:user_id>/", get_user_profile_view),
    path("profile/update/", update_profile_view),
    path("delete-account/", delete_account_view),
    path("logout/", logout_view),
    path("token/refresh/", TokenRefreshView.as_view()),
]
