from datetime import datetime, timezone

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from app.crew.models import Project, UserBookmark
from app.util.models import Language, Position, Stack

User = get_user_model()


class BookmarkAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="test@example.com", password="testpass123", nickname="테스트유저")

        self.other_user = User.objects.create_user(
            email="other@example.com", password="testpass123", nickname="다른유저"
        )

        self.project = Project.objects.create(
            user=self.other_user,
            title="테스트 프로젝트",
            deadline=datetime(2024, 12, 31, tzinfo=timezone.utc),
            start_date=datetime(2024, 1, 1, tzinfo=timezone.utc),
            end_date=datetime(2024, 6, 30, tzinfo=timezone.utc),
            is_estimated_period="6개월",
            description="테스트용 프로젝트입니다.",
            status="recruiting",
        )

        # JWT 토큰 생성
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)

    def authenticate(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")

    def test_bookmark_add_success(self):
        """북마크 추가 성공 테스트"""
        self.authenticate()
        url = reverse("bookmark-manage", kwargs={"project_id": self.project.id})

        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "북마크 등록")
        self.assertTrue(UserBookmark.objects.filter(user=self.user, project=self.project).exists())

    def test_bookmark_add_duplicate(self):
        """중복 북마크 추가 실패 테스트"""
        self.authenticate()
        # 먼저 북마크 생성
        UserBookmark.objects.create(user=self.user, project=self.project)

        url = reverse("bookmark-manage", kwargs={"project_id": self.project.id})
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["message"], "북마크 등록 실패")

    def test_bookmark_delete_success(self):
        """북마크 삭제 성공 테스트"""
        self.authenticate()
        # 먼저 북마크 생성
        UserBookmark.objects.create(user=self.user, project=self.project)

        url = reverse("bookmark-manage", kwargs={"project_id": self.project.id})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "북마크 등록 취소")
        self.assertFalse(UserBookmark.objects.filter(user=self.user, project=self.project).exists())

    def test_bookmark_delete_not_found(self):
        """존재하지 않는 북마크 삭제 실패 테스트"""
        self.authenticate()

        url = reverse("bookmark-manage", kwargs={"project_id": self.project.id})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["message"], "북마크 등록 취소 실패")

    def test_bookmark_unauthorized(self):
        """인증되지 않은 사용자 접근 테스트"""
        url = reverse("bookmark-manage", kwargs={"project_id": self.project.id})

        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_bookmark_nonexistent_project(self):
        """존재하지 않는 프로젝트 북마크 테스트"""
        self.authenticate()
        url = reverse("bookmark-manage", kwargs={"project_id": 99999})

        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
