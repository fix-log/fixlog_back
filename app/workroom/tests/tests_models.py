from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase
from django.utils import timezone

from app.workroom.models import (
    CalendarEvent,
    Issue,
    Workroom,
    WorkroomDesign,
    WorkroomLanguage,
    WorkroomMember,
    WorkroomPosition,
    WorkroomReview,
    WorkroomStack,
)

User = get_user_model()


class TestWorkroomModel(TestCase):
    def test_str_returns_name(self):
        # 테스트용 유저 생성
        user = User.objects.create_user(email="a@a.com", password="pw")
        # Workroom 객체 생성
        wr = Workroom.objects.create(
            name="테스트룸",
            introduction="소개",
            start_date=timezone.now().date(),
            end_date=timezone.now().date(),
            description="상세",
            created_by=user,
        )
        # __str__ 결과가 name 과 동일해야 함
        self.assertEqual(str(wr), "테스트룸")

    def test_clean_raises_if_start_after_end(self):
        # 테스트용 유저 생성
        user = User.objects.create_user(email="b@b.com", password="pw")
        # 종료일이 시작일 이전인 Workroom 인스턴스 준비
        wr = Workroom(
            name="룸",
            introduction="소개",
            start_date=timezone.now().date(),
            end_date=timezone.now().date() - timezone.timedelta(days=1),
            description="상세",
            created_by=user,
        )
        # clean() 호출 시 ValidationError 발생 확인
        with self.assertRaises(ValidationError):
            wr.clean()


class TestM2MModels(TestCase):
    @classmethod
    def setUpTestData(cls):
        # 테스트용 Workroom 생성 fixture
        cls.user = User.objects.create_user(email="c@c.com", password="pw")
        cls.base_wr = Workroom.objects.create(
            name="M2M룸",
            introduction="소개",
            start_date=timezone.now().date(),
            end_date=timezone.now().date(),
            description="상세",
            created_by=cls.user,
        )
        # 팩토리 대체용 간단한 객체 생성
        # Position, Language, Stack, Design 생성
        # Assuming position_factory(), language_factory(), etc. create and return model instances
        # Here we create minimal instances manually for testing

        # For Position
        from app.workroom.models import Design, Language, Position, Stack

        cls.pos = Position.objects.create(name="포지션1")
        cls.lang = Language.objects.create(name="언어1")
        cls.stk = Stack.objects.create(name="스택1")
        cls.des = Design.objects.create(name="디자인1")

    def test_position_unique_together(self):
        # 중복 없이 생성 가능
        WorkroomPosition.objects.create(workroom=self.base_wr, position=self.pos, count=2, current_count=1)
        # 동일 조합으로 두 번째 생성 시 IntegrityError 발생
        with self.assertRaises(IntegrityError):
            WorkroomPosition.objects.create(workroom=self.base_wr, position=self.pos, count=1, current_count=0)

    def test_language_unique_together(self):
        # 중복 없이 생성 가능
        WorkroomLanguage.objects.create(workroom=self.base_wr, language=self.lang)
        # 동일 조합으로 두 번째 생성 시 IntegrityError 발생
        with self.assertRaises(IntegrityError):
            WorkroomLanguage.objects.create(workroom=self.base_wr, language=self.lang)

    def test_stack_unique_together(self):
        # 중복 없이 생성 가능
        WorkroomStack.objects.create(workroom=self.base_wr, stack=self.stk)
        # 동일 조합으로 두 번째 생성 시 IntegrityError 발생
        with self.assertRaises(IntegrityError):
            WorkroomStack.objects.create(workroom=self.base_wr, stack=self.stk)

    def test_design_unique_together(self):
        # 중복 없이 생성 가능
        WorkroomDesign.objects.create(workroom=self.base_wr, design=self.des)
        # 동일 조합으로 두 번째 생성 시 IntegrityError 발생
        with self.assertRaises(IntegrityError):
            WorkroomDesign.objects.create(workroom=self.base_wr, design=self.des)

    def test_member_unique_together(self):
        # 두 명의 유저 생성
        u1 = User.objects.create_user(email="d1@d.com", password="pw")
        u2 = User.objects.create_user(email="d2@d.com", password="pw")
        # 첫 번째 멤버로 등록
        WorkroomMember.objects.create(user=u1, workroom=self.base_wr, role="member", permission="view")
        # 동일 조합으로 두 번째 생성 시 IntegrityError 발생
        with self.assertRaises(IntegrityError):
            WorkroomMember.objects.create(user=u1, workroom=self.base_wr, role="member", permission="view")


class TestIssueModel(TestCase):
    def test_str_and_status_display(self):
        # 유저 및 워크룸 생성
        user = User.objects.create_user(email="e@e.com", password="pw")
        wr = Workroom.objects.create(
            name="룸",
            introduction="소개",
            start_date=timezone.now().date(),
            end_date=timezone.now().date(),
            description="상세",
            created_by=user,
        )
        # 이슈 생성
        issue = Issue.objects.create(
            workroom=wr,
            user=user,
            title="이슈",
            status="in_progress",
            content="내용",
            due_date=timezone.now().date(),
        )
        # __str__ 결과와 choices 표시 확인
        self.assertEqual(str(issue), "이슈 - 진행중")


class TestCalendarEventModel(TestCase):
    def test_str_representation(self):
        # 유저 및 워크룸 생성
        user = User.objects.create_user(email="f@f.com", password="pw")
        wr = Workroom.objects.create(
            name="캘룸",
            introduction="소개",
            start_date=timezone.now().date(),
            end_date=timezone.now().date(),
            description="상세",
            created_by=user,
        )
        # 일정 생성
        ce = CalendarEvent.objects.create(
            workroom=wr,
            created_by=user,
            title="이벤트",
            start=timezone.now(),
            end=timezone.now() + timezone.timedelta(hours=1),
        )
        # __str__ 결과에 제목 포함 확인
        self.assertIn("이벤트", str(ce))


class TestWorkroomReviewModel(TestCase):
    def test_unique_review(self):
        # 유저 및 워크룸 생성
        reviewer = User.objects.create_user(email="g1@g.com", password="pw")
        reviewee = User.objects.create_user(email="g2@g.com", password="pw")
        wr = Workroom.objects.create(
            name="리뷰룸",
            introduction="소개",
            start_date=timezone.now().date(),
            end_date=timezone.now().date(),
            description="상세",
            created_by=reviewer,
        )
        # 첫 리뷰 생성
        WorkroomReview.objects.create(workroom=wr, reviewer=reviewer, reviewee=reviewee, rating=5, comment="굿")
        # 동일 조합으로 두 번째 생성 시 IntegrityError 발생
        with self.assertRaises(IntegrityError):
            WorkroomReview.objects.create(workroom=wr, reviewer=reviewer, reviewee=reviewee, rating=4, comment="또")
