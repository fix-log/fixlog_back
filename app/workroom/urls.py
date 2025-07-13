from django.urls import path
from app.workroom.views import (
    CalendarEventListCreateAPIView,
    CalendarEventRetrieveUpdateDestroyAPIView,
    IssueListCreateAPIView,
    IssueRetrieveUpdateDestroyAPIView,
    WorkroomDetailAllAPIView,
    WorkroomListCreateAPIView,
    WorkroomMemberListCreateAPIView,
    WorkroomMemberRespondAPIView,
    WorkroomMemberRetrieveUpdateDestroyAPIView,
    WorkroomRetrieveUpdateDestroyAPIView,
    WorkroomReviewListCreateAPIView,
)

urlpatterns = [
    # 워크룸 CRUD 엔드포인트
    path("workrooms/", WorkroomListCreateAPIView.as_view(), name="workroom-list"),
    path("workrooms/<int:pk>/", WorkroomRetrieveUpdateDestroyAPIView.as_view(), name="workroom-detail"),
    # 멤버 관리 엔드포인트 (워크룸 내)
    path(
        "workrooms/<int:workroom_id>/members/", WorkroomMemberListCreateAPIView.as_view(), name="member-list"
    ),  # 멤버 목록 조회 및 이메일 초대
    path(
        "workrooms/<int:workroom_id>/members/<int:pk>/",
        WorkroomMemberRetrieveUpdateDestroyAPIView.as_view(),
        name="member-detail",
    ),  # 개별 멤버 조회/수정/삭제
    path(
        "workrooms/<int:workroom_id>/members/<int:pk>/respond/",
        WorkroomMemberRespondAPIView.as_view(),
        name="member-respond",
    ),  # 초대 수락/거절 처리
    # 리뷰 엔드포인트 (워크룸 내)
    path(
        "workrooms/<int:workroom_id>/reviews/", WorkroomReviewListCreateAPIView.as_view(), name="review-list"
    ),  # 리뷰 목록 조회 및 작성
    # 이슈 엔드포인트 (워크룸 내)
    path(
        "workrooms/<int:workroom_id>/issues/", IssueListCreateAPIView.as_view(), name="issue-list"
    ),  # 이슈 목록 조회 및 생성
    path(
        "workrooms/<int:workroom_id>/issues/<int:pk>/", IssueRetrieveUpdateDestroyAPIView.as_view(), name="issue-detail"
    ),  # 이슈 상세 조회/수정/삭제
    # 일정 엔드포인트 (워크룸 내)
    path(
        "workrooms/<int:workroom_id>/events/", CalendarEventListCreateAPIView.as_view(), name="event-list"
    ),  # 일정 목록 조회 및 생성
    path(
        "workrooms/<int:workroom_id>/events/<int:pk>/",
        CalendarEventRetrieveUpdateDestroyAPIView.as_view(),
        name="event-detail",
    ),  # 일정 상세 조회/수정/삭제
    path(
        "workrooms/<int:workroom_id>/all/", WorkroomDetailAllAPIView.as_view(), name="workroom-detail-all"
    ),  # 워크룸 내용, 일정, 이슈, 멤버 전체조회
]
