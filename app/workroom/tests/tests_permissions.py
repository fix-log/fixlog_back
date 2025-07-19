from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIRequestFactory

from app.workroom.models import PermissionLevel, Role, Workroom, WorkroomMember
from app.workroom.permissions import WorkroomPermission

User = get_user_model()


class WorkroomPermissionTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Users 생성
        cls.owner = User.objects.create_user(email="owner@a.com", password="pw")
        cls.manager = User.objects.create_user(email="manager@a.com", password="pw")
        cls.member = User.objects.create_user(email="member@a.com", password="pw")
        cls.other = User.objects.create_user(email="other@a.com", password="pw")
        # Workroom 생성
        cls.wr = Workroom.objects.create(
            name="WR",
            introduction="intro",
            start_date=timezone.now().date(),
            end_date=timezone.now().date(),
            description="desc",
            created_by=cls.owner,
        )
        # Membership 생성
        WorkroomMember.objects.create(
            workroom=cls.wr, user=cls.owner, role=Role.OWNER, permission=PermissionLevel.ADMIN, status="accepted"
        )
        WorkroomMember.objects.create(
            workroom=cls.wr,
            user=cls.manager,
            role=Role.MANAGER,
            permission=PermissionLevel.MODIFY_EVENT,
            status="accepted",
        )
        WorkroomMember.objects.create(
            workroom=cls.wr, user=cls.member, role=Role.MEMBER, permission=PermissionLevel.VIEW, status="accepted"
        )
        cls.factory = APIRequestFactory()
        cls.permission = WorkroomPermission()

    def test_has_permission_auth(self):
        # 인증된 사용자만 허용
        request = self.factory.get("/")
        request.user = self.other
        self.assertTrue(self.permission.has_permission(request, None))
        # 익명 사용자 차단
        request.user = None
        self.assertFalse(self.permission.has_permission(request, None))

    def test_owner_has_object_permission_all_methods(self):
        # owner는 모든 메서드에 True
        for method in ["get", "post", "patch", "delete"]:
            request = getattr(self.factory, method)("/fake-path/")
            request.user = self.owner
            self.assertTrue(self.permission.has_object_permission(request, None, self.wr))

    def test_manager_safe_methods(self):
        # manager는 읽기 허용
        for method in ["get", "head", "options"]:
            request = getattr(self.factory, method)("/fake-path/")
            request.user = self.manager
            self.assertTrue(self.permission.has_object_permission(request, None, self.wr))
        # manager는 delete WorkroomMember 차단
        fake_member = WorkroomMember.objects.get(user=self.member, workroom=self.wr)
        delete_req = self.factory.delete("/fake-path/")
        delete_req.user = self.manager
        self.assertFalse(self.permission.has_object_permission(delete_req, None, fake_member))

    def test_manager_modify_others(self):
        # manager can PATCH other objects
        request = self.factory.patch("/fake-path/", {"name": "new"})
        request.user = self.manager
        self.assertTrue(self.permission.has_object_permission(request, None, self.wr))

    def test_member_permissions(self):
        # member can GET only
        request = self.factory.get("/fake-path/")
        request.user = self.member
        self.assertTrue(self.permission.has_object_permission(request, None, self.wr))
        # member POST requires permission level ADD_EVENT or higher
        post_req = self.factory.post("/fake-path/", {})
        post_req.user = self.member
        self.assertFalse(self.permission.has_object_permission(post_req, None, self.wr))
        # member PATCH only own created objects
        # 예: created_by = member
        # create fake issue object with created_by = member
        from app.workroom.models import Issue

        issue = Issue.objects.create(
            workroom=self.wr, user=self.member, title="T", status="pending", content="C", due_date=self.wr.start_date
        )
        patch_req = self.factory.patch("/fake-path/", {"title": "X"})
        patch_req.user = self.member
        self.assertFalse(self.permission.has_object_permission(patch_req, None, issue))
        # 다른 사람의 객체는 차단
        patch_req.user = self.member
        other_issue = Issue.objects.create(
            workroom=self.wr, user=self.manager, title="T2", status="pending", content="C2", due_date=self.wr.start_date
        )
        self.assertFalse(self.permission.has_object_permission(patch_req, None, other_issue))

    def test_non_member_forbidden(self):
        # workspace non-member는 False
        request = self.factory.get("/fake-path/")
        request.user = self.other
        self.assertFalse(self.permission.has_object_permission(request, None, self.wr))
