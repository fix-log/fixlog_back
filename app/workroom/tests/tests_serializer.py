from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model

from app.workroom.models import (
    Workroom, Position, WorkroomPosition, Issue
)
from app.workroom.serializers import (
    PositionCountInputSerializer,
    WorkroomMemberRespondSerializer,
    IssueSerializer,
    CalendarEventSerializer,
    WorkroomPositionSerializer,
)

User = get_user_model()

class PositionCountInputSerializerTest(TestCase):
    def test_valid_data(self):  # count가 2 이상이면 유효
        data = {"position_id": 1, "count": 2}
        serializer = PositionCountInputSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_invalid_count(self):  # count가 1 미만이면 오류
        data = {"position_id": 1, "count": 0}
        serializer = PositionCountInputSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('count', serializer.errors)

class WorkroomMemberRespondSerializerTest(TestCase):
    def test_valid_status_accepted(self):  # accepted는 허용
        data = {"status": "accepted"}
        serializer = WorkroomMemberRespondSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_invalid_status(self):  # 등록되지 않은 status는 오류
        data = {"status": "unknown"}
        serializer = WorkroomMemberRespondSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('status', serializer.errors)

class IssueSerializerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="a@a.com", password="pw")
        self.workroom = Workroom.objects.create(
            name="WR", introduction="intro",
            start_date=timezone.now().date(),
            end_date=(timezone.now() + timezone.timedelta(days=1)).date(),
            description="desc", created_by=self.user
        )

    def test_due_date_before_start(self):  # due_date가 시작일 이전이면 invalid
        data = {"due_date": self.workroom.start_date - timezone.timedelta(days=1)}
        serializer = IssueSerializer(data=data, context={"workroom": self.workroom})
        self.assertFalse(serializer.is_valid())
        # non_field_errors 또는 __all__ 검사
        self.assertTrue(serializer.errors)

    def test_partial_update_allows_missing_due_date(self):  # due_date 없이 partial update 가능
        issue = Issue.objects.create(
            workroom=self.workroom, user=self.user,
            title="T", status="pending",
            content="C", due_date=self.workroom.start_date
        )
        serializer = IssueSerializer(
            issue,
            data={"title": "New"},
            partial=True,
            context={"workroom": self.workroom}
        )
        self.assertTrue(serializer.is_valid())
        updated = serializer.save()
        self.assertEqual(updated.title, "New")

class CalendarEventSerializerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="b@b.com", password="pw")
        self.workroom = Workroom.objects.create(
            name="WR2", introduction="intro",
            start_date=timezone.now().date(),
            end_date=(timezone.now() + timezone.timedelta(days=2)).date(),
            description="desc", created_by=self.user
        )

    def test_start_after_end_invalid(self):  # start >= end 시 invalid
        now = timezone.now()
        data = {
            "title": "Evt",
            "start": now,
            "end": now,
            "all_day": False,
            "recurrence": {},
            "color": "#fff",
            "alert": False,
            "location": "",
            "url": "",
            "memo": ""
        }
        serializer = CalendarEventSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        errors = serializer.errors.get('non_field_errors', [])
        self.assertTrue(any("시작 시각은 종료 시각 이전이어야 합니다." in e for e in errors))

    def test_default_recurrence(self):  # recurrence 기본값 빈 dict
        valid = {
            "title": "Evt",
            "start": timezone.now(),
            "end": timezone.now() + timezone.timedelta(hours=1),
            "all_day": False,
            "color": "#fff",
            "alert": False,
            "location": "",
            "url": "",
            "memo": ""
        }
        serializer = CalendarEventSerializer(data=valid)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        obj = serializer.save(workroom=self.workroom, created_by=self.user)
        self.assertEqual(obj.recurrence, {})

class WorkroomPositionSerializerTest(TestCase):
    def setUp(self):
        self.position = Position.objects.create(name="Dev")
        self.user = User.objects.create_user(email="c@c.com", password="pw")
        self.workroom = Workroom.objects.create(
            name="WR3", introduction="intro",
            start_date=timezone.now().date(),
            end_date=(timezone.now() + timezone.timedelta(days=3)).date(),
            description="desc", created_by=self.user
        )
        self.wp = WorkroomPosition.objects.create(
            workroom=self.workroom, position=self.position,
            count=5, current_count=1
        )

    def test_representation_contains_position_name(self):  # position_name 필드 확인
        serializer = WorkroomPositionSerializer(self.wp)
        data = serializer.data
        self.assertEqual(data['position_name'], "Dev")
