from django.contrib import admin
from app.workroom.models import (
    Workroom,            # 워크룸 메인 모델
    WorkroomPosition,    # 워크룸-포지션 중간테이블 모델
    WorkroomLanguage,    # 워크룸-언어 중간테이블 모델
    WorkroomStack,       # 워크룸-스택 중간테이블 모델
    WorkroomDesign,      # 워크룸-디자인 중간테이블 모델
    WorkroomMember,      # 워크룸 멤버 모델
    CalendarEvent,       # 일정 모델
    Issue,               # 이슈 모델
    WorkroomReview,      # 워크룸 리뷰 모델
)

@admin.register(Workroom)
class WorkroomAdmin(admin.ModelAdmin):
    # 관리자 리스트 페이지에 표시할 필드 설정
    list_display = (
        'id',               # 워크룸 고유 ID
        'name',             # 워크룸 이름
        'introduction',     # 한 줄 소개
        'start_date',       # 프로젝트 시작일
        'end_date',         # 프로젝트 종료일
        'created_by',       # 생성자 (User FK)
        'created_at',       # 생성 시각
    )
    # 사이드바 필터로 제공할 필드 설정
    list_filter = (
        'start_date',       # 시작일별 필터
        'end_date',         # 종료일별 필터
    )
    # 상단 검색창으로 검색할 필드 설정
    search_fields = (
        'name',             # 이름 검색
        'introduction',     # 소개 검색
        'created_by__email',# 생성자 이메일 검색
    )
    # 읽기 전용으로 표시할 필드 설정
    readonly_fields = (
        'created_at',       # 생성 시간은 변경 불가
    )
    # 기본 정렬 순서 설정 (생성 시간 내림차순)
    ordering = ('-created_at',)


@admin.register(WorkroomPosition)
class WorkroomPositionAdmin(admin.ModelAdmin):
    # 워크룸-포지션 중간테이블 리스트 페이지 필드 설정
    list_display = (
        'workroom',         # 연결된 워크룸
        'position',         # 포지션 마스터
        'count',            # 최대 인원 수
        'current_count',    # 현재 참여 인원 수
    )
    # 사이드바 필터로 제공할 필드 설정
    list_filter = (
        'position',         # 포지션별 필터
    )
    # 상단 검색창으로 검색할 필드 설정
    search_fields = (
        'workroom__name',   # 워크룸 이름 검색
    )


@admin.register(WorkroomLanguage)
class WorkroomLanguageAdmin(admin.ModelAdmin):
    # 워크룸-언어 중간테이블 리스트 페이지 필드 설정
    list_display = (
        'workroom',         # 연결된 워크룸
        'language',         # 언어 마스터
    )
    list_filter = (
        'language',         # 언어별 필터
    )
    search_fields = (
        'workroom__name',   # 워크룸 이름 검색
    )


@admin.register(WorkroomStack)
class WorkroomStackAdmin(admin.ModelAdmin):
    # 워크룸-스택 중간테이블 리스트 페이지 필드 설정
    list_display = (
        'workroom',         # 연결된 워크룸
        'stack',            # 스택 마스터
    )
    list_filter = (
        'stack',            # 스택별 필터
    )
    search_fields = (
        'workroom__name',   # 워크룸 이름 검색
    )


@admin.register(WorkroomDesign)
class WorkroomDesignAdmin(admin.ModelAdmin):
    # 워크룸-디자인 중간테이블 리스트 페이지 필드 설정
    list_display = (
        'workroom',         # 연결된 워크룸
        'design',           # 디자인 마스터
    )
    list_filter = (
        'design',           # 디자인별 필터
    )
    search_fields = (
        'workroom__name',   # 워크룸 이름 검색
    )


@admin.register(WorkroomMember)
class WorkroomMemberAdmin(admin.ModelAdmin):
    # 워크룸 멤버 리스트 페이지 필드 설정
    list_display = (
        'id',               # 멤버 고유 ID
        'user',             # 사용자 (ForeignKey)
        'workroom',         # 소속 워크룸
        'role',             # 역할 (OWNER/MANAGER/MEMBER)
        'permission',       # 권한 레벨
        'status',           # 참여 상태 (pending/accepted/rejected)
        'position_name',    # 사용자가 맡는 포지션명
        'created_at',       # 가입 시각
    )
    list_filter = (
        'role',             # 역할별 필터
        'permission',       # 권한별 필터
        'status',           # 상태별 필터
    )
    search_fields = (
        'user__email',      # 사용자 이메일 검색
        'workroom__name',   # 워크룸 이름 검색
    )


@admin.register(CalendarEvent)
class CalendarEventAdmin(admin.ModelAdmin):
    # 일정 리스트 페이지 필드 설정
    list_display = (
        'id',               # 일정 고유 ID
        'title',            # 일정 제목
        'workroom',         # 소속 워크룸
        'created_by',       # 일정 생성자
        'start',            # 시작 시각
        'end',              # 종료 시각
        'all_day',          # 종일 여부
        'alert',            # 알림 여부
    )
    list_filter = (
        'all_day',          # 종일 여부 필터
        'alert',            # 알림 여부 필터
        'start',            # 시작일 필터
        'end',              # 종료일 필터
    )
    search_fields = (
        'title',            # 일정 제목 검색
        'workroom__name',   # 워크룸 이름 검색
        'created_by__email',# 생성자 이메일 검색
    )


@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    # 이슈 리스트 페이지 필드 설정
    list_display = (
        'id',               # 이슈 고유 ID
        'title',            # 이슈 제목
        'workroom',         # 소속 워크룸
        'user',             # 작성자
        'status',           # 이슈 상태
        'created_at',       # 생성 시각
    )
    list_filter = (
        'status',           # 상태별 필터
    )
    search_fields = (
        'title',            # 제목 검색
        'user__email',      # 작성자 이메일 검색
        'workroom__name',   # 워크룸 이름 검색
    )


@admin.register(WorkroomReview)
class WorkroomReviewAdmin(admin.ModelAdmin):
    # 리뷰 리스트 페이지 필드 설정
    list_display = (
        'id',               # 리뷰 고유 ID
        'workroom',         # 대상 워크룸
        'reviewer',         # 리뷰 작성자
        'reviewee',         # 리뷰 대상자
        'rating',           # 평점
        'created_at',       # 작성 시각
    )
    search_fields = (
        'workroom__name',   # 워크룸 이름 검색
        'reviewer__email',  # 작성자 이메일 검색
        'reviewee__email',  # 대상자 이메일 검색
    )