from datetime import timedelta

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from app.workroom.models import PermissionLevel, Role, Workroom, WorkroomMember

# 사용자 모델 할당
User = get_user_model()


# Workroom 관련 API 전반을 테스트하는 클래스
class WorkroomViewTests(APITestCase):
    # 워크룸 CRUD, 멤버, 이슈, 일정, 리뷰 뷰 테스트

    @classmethod
    def setUpTestData(cls):
        # 공통 사용자, 클라이언트, 워크룸, 멤버 생성
        cls.user = User.objects.create_user(email="test@example.com", password="testpass", nickname="테스트유저")
        cls.client = APIClient()
        cls.client.force_authenticate(user=cls.user)
        cls.workroom = Workroom.objects.create(
            name="기본 워크룸",
            introduction="소개",
            start_date=timezone.now().date(),
            end_date=(timezone.now() + timedelta(days=7)).date(),
            description="설명",
            created_by=cls.user,
        )
        WorkroomMember.objects.create(
            workroom=cls.workroom, user=cls.user, role=Role.OWNER, permission=PermissionLevel.ADMIN, status="accepted"
        )

    def setUp(self):
        # 매 테스트마다 클라이언트에 인증 정보 설정
        self.client.force_authenticate(user=self.user)

    def test_workroom_list_and_create(self):
        # 워크룸 리스트 조회 및 생성
        url = reverse("workroom-list")
        # 조회
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # 생성
        payload = {
            "name": "NewRoom",
            "introduction": "intro2",
            "start_date": timezone.now().date().isoformat(),
            "end_date": (timezone.now().date() + timedelta(days=5)).isoformat(),
            "description": "desc2",
        }
        resp = self.client.post(url, payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        # ID가 반환되는지 간단 확인
        self.assertIn("id", resp.data)

    def test_workroom_retrieve_update_delete(self):
        # 워크룸 상세 조회, 수정, 삭제
        url = reverse("workroom-detail", kwargs={"pk": self.workroom.id})
        # 상세 조회
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # 수정
        resp = self.client.patch(url, {"name": "Updated"}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # 삭제
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)


class IssueTests(APITestCase):
    # 이슈 뷰 테스트

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(email="test@example.com", password="testpass", nickname="테스트유저")
        cls.client = APIClient()
        cls.client.force_authenticate(user=cls.user)
        cls.workroom = Workroom.objects.create(
            name="기본 워크룸",
            introduction="소개",
            start_date=timezone.now().date(),
            end_date=(timezone.now() + timedelta(days=7)).date(),
            description="설명",
            created_by=cls.user,
        )
        WorkroomMember.objects.create(
            workroom=cls.workroom, user=cls.user, role=Role.OWNER, permission=PermissionLevel.ADMIN, status="accepted"
        )

    def setUp(self):
        # 매 테스트마다 클라이언트에 인증 정보 설정
        self.client.force_authenticate(user=self.user)

    def _issue_url(self):
        return reverse("issue-list", kwargs={"workroom_id": self.workroom.id})

    def _issue_detail_url(self, pk):
        return reverse("issue-detail", kwargs={"workroom_id": self.workroom.id, "pk": pk})

    def test_issue_create_and_update(self):
        # 이슈 생성 및 수정
        payload = {
            "title": "테스트 이슈",
            "content": "내용",
            "status": "pending",
            "due_date": (timezone.now() + timedelta(days=1)).date().isoformat(),
            "user": self.user.id,  # 여기에 user 필드를 추가
        }
        resp = self.client.post(self._issue_url(), payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        pk = resp.data["id"]
        resp = self.client.patch(self._issue_detail_url(pk), {"title": "수정된 이슈"}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)


class EventTests(APITestCase):
    # 일정 뷰 테스트

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(email="test@example.com", password="testpass", nickname="테스트유저")
        cls.client = APIClient()
        cls.client.force_authenticate(user=cls.user)
        cls.workroom = Workroom.objects.create(
            name="기본 워크룸",
            introduction="소개",
            start_date=timezone.now().date(),
            end_date=(timezone.now() + timedelta(days=7)).date(),
            description="설명",
            created_by=cls.user,
        )
        WorkroomMember.objects.create(
            workroom=cls.workroom, user=cls.user, role=Role.OWNER, permission=PermissionLevel.ADMIN, status="accepted"
        )

    def setUp(self):
        # 매 테스트마다 클라이언트에 인증 정보 설정
        self.client.force_authenticate(user=self.user)

    def _event_url(self):
        return reverse("event-list", kwargs={"workroom_id": self.workroom.id})

    def _event_detail_url(self, pk):
        return reverse("event-detail", kwargs={"workroom_id": self.workroom.id, "pk": pk})

    def test_event_create_and_delete(self):
        # 일정 생성 및 삭제
        payload = {
            "title": "미팅",
            "start": timezone.now().isoformat(),
            "end": (timezone.now() + timedelta(hours=1)).isoformat(),
            "all_day": False,
            "recurrence": {},
            "color": "#000000",
            "alert": False,
            "location": "",
            "url": "",
            "memo": "",
        }
        resp = self.client.post(self._event_url(), payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        pk = resp.data["data"]["id"]
        resp = self.client.delete(self._event_detail_url(pk))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)


# class ReviewTests(APITestCase):
#     리뷰 뷰 테스트
#
#     @classmethod
#     def setUpTestData(cls):
#         cls.user = User.objects.create_user(
#             email="test@example.com", password="testpass", nickname="테스트유저"
#         )
#         cls.client = APIClient()
#         cls.client.force_authenticate(user=cls.user)
#         cls.workroom = Workroom.objects.create(
#             name="기본 워크룸",
#             introduction="소개",
#             start_date=timezone.now().date(),
#             end_date=(timezone.now() + timedelta(days=7)).date(),
#             description="설명",
#             created_by=cls.user,
#         )
#         WorkroomMember.objects.create(
#             workroom=cls.workroom, user=cls.user,
#             role=Role.OWNER, permission=PermissionLevel.ADMIN, status="accepted"
#         )
#
#     def setUp(self):
#         # 매 테스트마다 클라이언트에 인증 정보 설정
#         self.client.force_authenticate(user=self.user)
#
#     def _review_url(self):
#         return reverse("review-list", kwargs={"workroom_id": self.workroom.id})
#
#     def test_review_create_and_list(self):
#         리뷰 생성 및 목록 조회
#         # 리뷰는 워크룸 종료 후 생성 가능하므로 종료일을 과거로 설정
#         self.workroom.end_date = timezone.now().date() - timedelta(days=1)
#         self.workroom.save()
#         payload = {"reviewee": self.user.id, "rating": 5, "comment": "좋아요"}
#         resp = self.client.post(self._review_url(), payload, format="json")
#         self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
#         resp = self.client.get(self._review_url())
#         self.assertEqual(resp.status_code, status.HTTP_200_OK)
