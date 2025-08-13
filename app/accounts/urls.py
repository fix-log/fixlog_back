from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from app.accounts import views, views_follow

urlpatterns = [
    # --- 이메일 인증 (회원가입 / 비밀번호 재설정 공용) ---
    # signup / password_reset 으로 나눠서 사용 가능 purpose 부분에 둘 중 하나 넣으면 됩니다
    # signup 넣으면 가입용 인증번호, password_reset 넣으면 비번 재설정에 맞는 인증번호 가는데 password는 이름도 검증합니다!
    path("request/<str:purpose>/", views.request_verification_code_view, name="request_verification_code"),
    path("confirm/<str:purpose>/", views.confirm_verification_code_view, name="confirm_verification_code"),
    # --- 회원가입 & 로그인/로그아웃 ---
    path("register/", views.signup_view, name="signup"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("token/refresh/", views.refresh_token_view, name="token_refresh"),
    path("leave/", views.delete_account_view, name="leave"),  # 회원 탈퇴
    # --- 프로필 ---
    path("profile/", views.profile_view, name="my_profile"),  # 내 프로필 조회/수정
    path("profile/<int:user_id>/", views.get_user_profile_view, name="user_profile"),  # 다른 사용자 프로필
    # --- 아이디·비밀번호 찾기 ---
    path("find-email/", views.find_email_view, name="find_email"),
    path("password-reset/", views.reset_password_view, name="reset_password"),  # 새 비번 설정
    # --- 팔로우 ---
    path("<int:user_id>/follow/", views_follow.follow_toggle_view, name="follow_toggle"),
    path("<int:user_id>/followers/", views_follow.followers_list_view, name="followers_list"),
    path("<int:user_id>/following/", views_follow.following_list_view, name="following_list"),
]
