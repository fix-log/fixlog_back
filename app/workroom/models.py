from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from app.util.models import CreatedOnlyModel, Design, Language, Position, Stack

# 커스텀 유저 할당
User = get_user_model()


# 역할 정의 (총 관리자, 부관리자, 일반 멤버)
class Role(models.TextChoices):
    OWNER = "owner", "총 관리자"
    MANAGER = "manager", "부관리자"
    MEMBER = "member", "일반 멤버"


# 권한 레벨 정의 (보기만, 일정 추가, 일정 수정·삭제, 관리자)
class PermissionLevel(models.TextChoices):
    VIEW = "view", "보기만 가능"
    ADD_EVENT = "add_event", "일정 추가만 가능"
    MODIFY_EVENT = "modify_event", "일정 추가·삭제 가능"
    ADMIN = "admin", "모든 권한"


# 워크룸 메인 모델 (작성/수정 일자 포함)
class Workroom(CreatedOnlyModel):
    name = models.CharField(max_length=255)  # 워크룸 이름
    introduction = models.CharField(max_length=512)  # 워크룸 한 줄 소개
    # 프로젝트 시작일 (기존 레코드 기본값으로 현재 날짜 사용, null/blank 허용)
    start_date = models.DateField(
        default=timezone.now,  # 마이그레이션 시 기본값으로 현재 날짜 사용
        null=True,  # 기존 데이터에 null 허용
        blank=True,  # 폼 검증 시 빈 값 허용
    )
    # 프로젝트 종료일 (기존 레코드 기본값으로 현재 날짜 사용, null/blank 허용)
    end_date = models.DateField(
        default=timezone.now,  # 마이그레이션 시 기본값으로 현재 날짜 사용
        null=True,  # 기존 데이터에 null 허용
        blank=True,  # 폼 검증 시 빈 값 허용
    )
    description = models.TextField()  # 워크룸 상세 설명
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="created_workrooms"
    )  # 워크룸 생성자 (User 모델과 연결)

    # Position, Language, Stack, Design 마스터 모델과 M2M 관계 (중간테이블 사용)
    positions = models.ManyToManyField(
        Position, through="WorkroomPosition", related_name="workrooms"
    )  # 워크룸-포지션 관계
    languages = models.ManyToManyField(
        Language, through="WorkroomLanguage", related_name="workrooms"
    )  # 워크룸-언어 관계
    stacks = models.ManyToManyField(Stack, through="WorkroomStack", related_name="workrooms")  # 워크룸-스택 관계
    designs = models.ManyToManyField(Design, through="WorkroomDesign", related_name="workrooms")  # 워크룸-디자인 관계

    def clean(self):
        # 시작일이 종료일 이후이면 ValidationError 발생
        if self.start_date > self.end_date:
            raise ValidationError({"start_date": "시작일은 종료일 이전이어야 합니다."})

    def __str__(self):
        # 관리 화면 등에서 객체를 문자열로 표현할 때 사용
        return self.name

    class Meta:
        verbose_name = "워크룸"
        verbose_name_plural = "워크룸"


# 워크룸-포지션 중간테이블 모델
class WorkroomPosition(models.Model):
    workroom = models.ForeignKey(Workroom, on_delete=models.CASCADE, related_name="workroom_positions")  # 연결된 워크룸
    position = models.ForeignKey(Position, on_delete=models.PROTECT)  # Position 마스터 테이블
    count = models.PositiveIntegerField(default=1)  # 포지션별 최대 인원
    current_count = models.PositiveIntegerField(default=0)  # 현재 참여 인원 수

    class Meta:
        unique_together = ("workroom", "position")  # 워크룸-포지션 중복 방지
        verbose_name = "워크룸-포지션"
        verbose_name_plural = "워크룸-포지션"

    def clean(self):
        # current_count가 count를 초과하면 오류 발생
        if self.current_count > self.count:
            raise ValidationError("현재 인원은 최대 인원을 초과할 수 없습니다.")


# 워크룸-언어 중간테이블 모델
class WorkroomLanguage(models.Model):
    workroom = models.ForeignKey(Workroom, on_delete=models.CASCADE, related_name="workroom_languages")  # 연결된 워크룸
    language = models.ForeignKey(Language, on_delete=models.PROTECT)  # Language 마스터 테이블

    class Meta:
        unique_together = ("workroom", "language")  # 중복 방지
        verbose_name = "워크룸-언어"
        verbose_name_plural = "워크룸-언어"


# 워크룸-스택 중간테이블 모델
class WorkroomStack(models.Model):
    workroom = models.ForeignKey(Workroom, on_delete=models.CASCADE, related_name="workroom_stacks")  # 연결된 워크룸
    stack = models.ForeignKey(Stack, on_delete=models.PROTECT)  # Stack 마스터 테이블

    class Meta:
        unique_together = ("workroom", "stack")  # 중복 방지
        verbose_name = "워크룸-스택"
        verbose_name_plural = "워크룸-스택"


# 워크룸-디자인 중간테이블 모델
class WorkroomDesign(models.Model):
    workroom = models.ForeignKey(Workroom, on_delete=models.CASCADE, related_name="workroom_designs")  # 연결된 워크룸
    design = models.ForeignKey(Design, on_delete=models.PROTECT)  # Design 마스터 테이블

    class Meta:
        unique_together = ("workroom", "design")  # 중복 방지
        verbose_name = "워크룸-디자인"
        verbose_name_plural = "워크룸-디자인"


# 워크룸 멤버 모델
class WorkroomMember(CreatedOnlyModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="workroom_members")  # 멤버 사용자
    workroom = models.ForeignKey(Workroom, on_delete=models.CASCADE, related_name="members")  # 소속 워크룸
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.MEMBER)  # 역할 (OWNER/MANAGER/MEMBER)
    permission = models.CharField(
        max_length=20, choices=PermissionLevel.choices, default=PermissionLevel.VIEW
    )  # 권한 레벨
    status = models.CharField(
        max_length=10, choices=[("pending", "대기"), ("accepted", "승인"), ("rejected", "거절")], default="pending"
    )  # 참여 상태
    position_name = models.CharField(max_length=50, blank=True, null=True)  # 사용자가 맡는 포지션 이름

    class Meta:
        unique_together = ("user", "workroom")  # 중복 가입 방지
        verbose_name = "워크룸-멤버"
        verbose_name_plural = "워크룸-멤버"

    def clean(self):
        # 부관리자는 최대 3명까지 허용
        if self.role == Role.MANAGER:
            count = WorkroomMember.objects.filter(workroom=self.workroom, role=Role.MANAGER).exclude(pk=self.pk).count()
            if count >= 3:
                raise ValidationError("부관리자는 최대 3명까지 지정할 수 있습니다.")
        # 총 관리자는 한 명만 허용
        if self.role == Role.OWNER:
            exists = WorkroomMember.objects.filter(workroom=self.workroom, role=Role.OWNER).exclude(pk=self.pk).exists()
            if exists:
                raise ValidationError("총 관리자는 한 명만 존재해야 합니다.")


# 이슈 모델
class Issue(CreatedOnlyModel):
    STATUS_CHOICES = [("pending", "시작전"), ("in_progress", "진행중"), ("completed", "완료")]
    workroom = models.ForeignKey(Workroom, on_delete=models.CASCADE, related_name="issues")  # 소속 워크룸
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="issues")  # 작성자
    title = models.CharField(max_length=255)  # 이슈 제목
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="pending"
    )  # 이슈 상태 -> 기본 상태 = 시작전
    content = models.TextField()  # 업무 세부 내용
    due_date = models.DateField()  # 마감일

    def __str__(self):
        return f"{self.title} - {self.get_status_display()}"

    class Meta:
        verbose_name = "워크룸 이슈"
        verbose_name_plural = "워크룸 이슈"


# 일정 모델
class CalendarEvent(CreatedOnlyModel):
    workroom = models.ForeignKey(Workroom, on_delete=models.CASCADE, related_name="events")  # 소속 워크룸
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="calendar_events")
    title = models.CharField(max_length=255)  # 일정 제목
    start = models.DateTimeField()  # 시작 시각
    end = models.DateTimeField()  # 종료 시각
    all_day = models.BooleanField(default=False)  # 종일 여부
    recurrence = models.JSONField(default=dict, blank=True, null=True)  # 반복 설정 (frequency, interval 등)
    color = models.CharField(max_length=7, default="#F74627")  # 색상 코드 (#F74627)-> 기본 색상
    alert = models.BooleanField(default=False)  # 알림 추가 여부
    location = models.CharField(max_length=255, blank=True)  # 위치 정보
    url = models.URLField(blank=True, null=True)  # 관련 URL
    memo = models.TextField(blank=True, null=True)  # 메모

    def __str__(self):
        return f"{self.title} ({self.start.date()}~{self.end.date()})"

    class Meta:
        verbose_name = "워크룸 일정"
        verbose_name_plural = "워크룸 일정"


# 워크룸 리뷰
# todo positive negative 리뷰 내용 PR 되면 수정예정
class WorkroomReview(CreatedOnlyModel):
    workroom = models.ForeignKey(Workroom, on_delete=models.CASCADE, related_name="reviews")  # 리뷰 대상 워크룸
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="given_reviews")  # 리뷰 작성자
    reviewee = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_reviews")  # 리뷰 대상자
    rating = models.PositiveSmallIntegerField()  # 평점 (1~5 등)
    comment = models.TextField()  # 자유 코멘트

    class Meta:
        unique_together = ("workroom", "reviewer", "reviewee")
        verbose_name = "워크룸 리뷰"
        verbose_name_plural = "워크룸 리뷰"

    def __str__(self):
        return f"{self.reviewer} → {self.reviewee} : {self.rating}"
