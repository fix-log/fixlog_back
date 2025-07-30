from datetime import datetime, timezone

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from app.crew.models import Application, Project, UserBookmark
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


class ApplicationAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="applicant@example.com", password="testpass123", nickname="지원자")

        self.project_owner = User.objects.create_user(
            email="owner@example.com", password="testpass123", nickname="프로젝트소유자"
        )

        self.project = Project.objects.create(
            user=self.project_owner,
            title="지원 테스트 프로젝트",
            deadline=datetime(2024, 12, 31, tzinfo=timezone.utc),
            start_date=datetime(2024, 1, 1, tzinfo=timezone.utc),
            end_date=datetime(2024, 6, 30, tzinfo=timezone.utc),
            is_estimated_period="6개월",
            description="지원자 테스트용 프로젝트입니다.",
            status="recruiting",
        )

        # JWT 토큰 생성
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)

        refresh_owner = RefreshToken.for_user(self.project_owner)
        self.owner_access_token = str(refresh_owner.access_token)

    def authenticate_user(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")

    def authenticate_owner(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.owner_access_token}")

    def test_project_apply_success(self):
        """프로젝트 지원 성공 테스트"""
        self.authenticate_user()
        url = reverse("project-apply", kwargs={"project_id": self.project.id})

        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["message"], "지원 성공")
        self.assertTrue(Application.objects.filter(user=self.user, project=self.project).exists())

    def test_project_apply_own_project(self):
        """자신의 프로젝트 지원 실패 테스트"""
        self.authenticate_owner()
        url = reverse("project-apply", kwargs={"project_id": self.project.id})

        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["message"], "지원 실패")
        self.assertFalse(Application.objects.filter(user=self.project_owner, project=self.project).exists())

    def test_project_apply_duplicate(self):
        """중복 지원 실패 테스트"""
        self.authenticate_user()
        # 먼저 지원 생성
        Application.objects.create(user=self.user, project=self.project)

        url = reverse("project-apply", kwargs={"project_id": self.project.id})
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["message"], "지원 실패")

    def test_project_apply_cancel_success(self):
        """프로젝트 지원 취소 성공 테스트"""
        self.authenticate_user()
        # 먼저 지원 생성
        Application.objects.create(user=self.user, project=self.project)

        url = reverse("project-apply", kwargs={"project_id": self.project.id})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "지원 취소")
        self.assertFalse(Application.objects.filter(user=self.user, project=self.project).exists())

    def test_project_apply_cancel_not_applied(self):
        """지원하지 않은 프로젝트 취소 실패 테스트"""
        self.authenticate_user()

        url = reverse("project-apply", kwargs={"project_id": self.project.id})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["message"], "지원 취소 성공")

    def test_project_applicants_list_owner(self):
        """프로젝트 소유자의 지원자 목록 조회 테스트"""
        self.authenticate_owner()
        # 지원자 생성
        Application.objects.create(user=self.user, project=self.project)

        url = reverse("project-applicants", kwargs={"project_id": self.project.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["user_id"], self.user.id)

    def test_project_applicants_list_not_owner(self):
        """프로젝트 소유자가 아닌 사용자의 지원자 목록 조회 실패 테스트"""
        self.authenticate_user()

        url = reverse("project-applicants", kwargs={"project_id": self.project.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_project_applicants_empty_list(self):
        """지원자가 없는 프로젝트의 지원자 목록 조회 테스트"""
        self.authenticate_owner()

        url = reverse("project-applicants", kwargs={"project_id": self.project.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_application_unauthorized(self):
        """인증되지 않은 사용자 접근 테스트"""
        url = reverse("project-apply", kwargs={"project_id": self.project.id})

        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        url = reverse("project-applicants", kwargs={"project_id": self.project.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_application_nonexistent_project(self):
        """존재하지 않는 프로젝트 지원 테스트"""
        self.authenticate_user()
        url = reverse("project-apply", kwargs={"project_id": 99999})

        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
