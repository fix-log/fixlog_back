from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import serializers, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import ListCreateAPIView, RetrieveAPIView, RetrieveUpdateDestroyAPIView, UpdateAPIView
from rest_framework.response import Response
from drf_spectacular.types import OpenApiTypes
from app.workroom.models import CalendarEvent, Issue, Workroom, WorkroomMember, WorkroomReview
from app.workroom.permissions import WorkroomPermission
from app.workroom.serializers import (
    CalendarEventSerializer,
    IssueSerializer,
    WorkroomDetailSerializer,
    WorkroomMemberInviteSerializer,
    WorkroomMemberRespondSerializer,
    WorkroomMemberSerializer,
    WorkroomReviewSerializer,
    WorkroomSerializer,
)


# 워크룸 API ------------------------------------
@extend_schema(
    summary="워크룸 전체 상세 정보 조회",
    description="워크룸 기본 정보와 함께 관련된 멤버, 이슈, 일정을 통합 조회합니다.",
    responses={
        200: WorkroomDetailSerializer,
        401: OpenApiResponse(description="인증되지 않음: 로그인 필요"),
        403: OpenApiResponse(description="권한 없음: 접근 권한이 없습니다"),
        404: OpenApiResponse(description="찾을 수 없음: 해당 워크룸이 존재하지 않습니다"),
        500: OpenApiResponse(description="서버 내부 오류"),
    },
)
class WorkroomDetailAllAPIView(RetrieveAPIView):  # 워크룸의 전체 정보 조회용 제너릭 뷰
    queryset = Workroom.objects.all()  # 워크룸 쿼리셋
    serializer_class = WorkroomDetailSerializer  # 전체 정보 직렬화 클래스
    permission_classes = [WorkroomPermission]  # 인증된 사용자만 접근 허용

    # 기본적으로 RetrieveAPIView는 GET 요청을 처리하며,
    # pk → URL에서 'workroom_id'로 지정된 인자를 사용하도록 설정
    lookup_url_kwarg = "workroom_id"


@extend_schema(
    summary="워크룸 목록 조회 및 생성",
    description="로그인한 사용자는 워크룸 전체 목록을 조회하거나 새 워크룸을 생성합니다.",
    responses={
        200: WorkroomSerializer(many=True),
        201: WorkroomSerializer,
        400: OpenApiResponse(description="잘못된 요청: 필드 유효성 검사 실패"),
        401: OpenApiResponse(description="인증되지 않음: 로그인 필요"),
        403: OpenApiResponse(description="권한 없음: 접근 권한이 없습니다"),
        500: OpenApiResponse(description="서버 내부 오류"),
    },
)
class WorkroomListCreateAPIView(ListCreateAPIView):
    queryset = Workroom.objects.all()  # 워크룸 전체 쿼리셋
    serializer_class = WorkroomSerializer  # 직렬화 클래스 지정
    permission_classes = [WorkroomPermission]  # 인증된 사용자만 접근 허용

    def perform_create(self, serializer):
        try:
            # 생성 시 생성자 필드에 현재 사용자 할당
            serializer.save(created_by=self.request.user)
        except ValidationError as e:
            # 유효성 검사 오류는 DRF 예외로 변환
            raise serializers.ValidationError(e.detail)
        except IntegrityError:
            # DB 제약 오류 응답
            raise serializers.ValidationError("워크룸 생성 중 오류가 발생했습니다.")


@extend_schema(
    summary="워크룸 상세 조회/수정/삭제",
    description="워크룸 상세 조회는 누구나 가능하며, 수정/삭제는 소유자만 가능합니다.",
    responses={
        200: WorkroomSerializer,
        204: OpenApiResponse(description="삭제 성공"),
        400: OpenApiResponse(description="잘못된 요청: 필드 유효성 검사 실패"),
        401: OpenApiResponse(description="인증되지 않음: 로그인 필요"),
        403: OpenApiResponse(description="권한 없음: 소유자만 수정/삭제 가능"),
        404: OpenApiResponse(description="찾을 수 없음: 해당 워크룸이 존재하지 않습니다"),
        500: OpenApiResponse(description="서버 내부 오류"),
    },
)
class WorkroomRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    http_method_names = ["get", "patch", "delete"]
    queryset = Workroom.objects.all()  # 워크룸 개별 쿼리셋
    serializer_class = WorkroomSerializer  # 직렬화 클래스 지정
    permission_classes = [WorkroomPermission]  # 인증된 사용자만 접근 허용

    def destroy(self, request, *args, **kwargs):
        """DELETE 요청 시 '삭제가 완료되었습니다.' 메시지를 JSON으로 반환"""
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"detail": "삭제가 완료되었습니다."}, status=status.HTTP_200_OK)


# 워크룸 멤버 API ------------------------------------
@extend_schema(
    summary="멤버 목록 조회 (GET) 및 이메일 초대 (POST)",
    description="워크룸의 멤버 목록을 조회하거나, 이메일을 통해 사용자를 초대합니다. "
    "조회는 모든 워크룸 멤버가 가능하며, 초대는 관리자/부관리자만 가능합니다.",
    request={"application/json": WorkroomMemberInviteSerializer},
    responses={
        200: OpenApiTypes.OBJECT,
        201: WorkroomMemberSerializer,
        400: OpenApiResponse(description="잘못된 요청: 이메일 형식 오류, 존재하지 않는 사용자, 중복 초대, 필수값 누락"),
        401: OpenApiResponse(description="인증되지 않음: 로그인 후 이용해주세요."),
        403: OpenApiResponse(description="권한 없음: 관리자 또는 부관리자만 초대가 가능합니다."),
        404: OpenApiResponse(description="찾을 수 없음: 존재하지 않는 워크룸입니다."),
        500: OpenApiResponse(description="서버 내부 오류: 관리자에게 문의하세요."),
    },
)
class WorkroomMemberListCreateAPIView(ListCreateAPIView):
    permission_classes = [WorkroomPermission]  # 인증된 사용자만 접근 허용
    filter_backends = [DjangoFilterBackend]  # 필터링 기능
    filterset_fields = ["status", "role"]  # 필터링 가능한 필드

    def get_queryset(self):
        workroom_id = self.kwargs.get("workroom_id")
        return WorkroomMember.objects.filter(workroom_id=workroom_id)

    def get_serializer_class(self):
        if self.request.method == "POST":
            return WorkroomMemberInviteSerializer  # 초대 생성 시에는 이메일 전용 시리얼라이저 사용
        return WorkroomMemberSerializer  # 조회 시에는 일반 시리얼라이저 사용
# todo 이메일로 검색 후 초대하는방식 -> 이메일로 메일을 전송하는 로직이 아님 nofitication 이후에 구현해야함
    def create(self, request, *args, **kwargs):
        # 이메일 초대용 커스텀 로직
        invite_ser = WorkroomMemberInviteSerializer(data=request.data)
        invite_ser.is_valid(raise_exception=True)
        user = invite_ser.validated_data["email"]  # User 인스턴스로 반환
        workroom = get_object_or_404(Workroom, pk=self.kwargs.get("workroom_id"))
        try:
            member = WorkroomMember.objects.create(
                user=user,
                workroom=workroom,
                role=invite_ser.validated_data["role"],
                permission=invite_ser.validated_data["permission"],
                position_name=invite_ser.validated_data.get("position_name", ""),
                status="pending",  # 초대받은 상태로 저장
            )
        except IntegrityError:
            return Response({"detail": "이미 초대된 사용자입니다."}, status=status.HTTP_400_BAD_REQUEST)
        out = WorkroomMemberSerializer(member)
        return Response(out.data, status=status.HTTP_201_CREATED)


@extend_schema(
    summary="초대 응답 처리 (PATCH)",
    description="초대받은 사용자가 초대를 수락(accepted)하거나 거절(rejected)할 수 있습니다.",
    request=WorkroomMemberRespondSerializer,
    responses={
        200: WorkroomMemberSerializer,
        400: OpenApiResponse(description="잘못된 요청: decision 필드가 누락되었거나 허용된 값이 아닙니다."),
        401: OpenApiResponse(description="인증되지 않음: 로그인 후 이용해주세요."),
        403: OpenApiResponse(description="권한 없음: 초대한 사용자만 응답할 수 있습니다."),
        404: OpenApiResponse(description="찾을 수 없음: 해당 멤버 또는 워크룸이 존재하지 않습니다."),
        500: OpenApiResponse(description="서버 내부 오류: 관리자에게 문의하세요."),
    },
)
class WorkroomMemberRespondAPIView(UpdateAPIView):
    http_method_names = ["get", "patch", "delete"]
    serializer_class = WorkroomMemberRespondSerializer  # status 필드만 업데이트
    permission_classes = [WorkroomPermission]  # 인증된 사용자만 접근 허용
    lookup_url_kwarg = "pk"  # URL kwarg 이름

    def get_queryset(self):
        workroom_id = self.kwargs.get("workroom_id")
        return WorkroomMember.objects.filter(workroom_id=workroom_id)

    def perform_update(self, serializer):
        member = self.get_object()
        # 본인만 응답 가능
        if member.user != self.request.user:
            raise PermissionDenied("권한이 없습니다.")
        serializer.save()

    def patch(self, request, pk=None, *args, **kwargs):
        workroom_id = self.kwargs.get("workroom_id")
        member = get_object_or_404(WorkroomMember, pk=pk, workroom_id=workroom_id)
        if member.user != request.user:
            return Response({"detail": "권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)
        decision = request.data.get("decision")
        if decision not in ["accepted", "rejected"]:
            return Response(
                {"detail": "decision 필드는 accepted 또는 rejected 이어야 합니다."}, status=status.HTTP_400_BAD_REQUEST
            )
        member.status = decision
        member.save()
        return Response(WorkroomMemberSerializer(member).data)


@extend_schema(
    summary="워크룸 멤버 상세 조회 / 수정 / 삭제",
    description="워크룸 멤버의 정보를 조회, 수정 또는 삭제할 수 있습니다. "
    "수정 및 삭제는 관리자, 부관리자 또는 본인만 가능합니다.",
    responses={
        200: WorkroomMemberSerializer,
        204: OpenApiResponse(description="삭제 성공: 멤버가 삭제되었습니다."),
        400: OpenApiResponse(description="잘못된 요청: 필드 유효성 검사 실패 또는 요청 본문 오류"),
        401: OpenApiResponse(description="인증되지 않음: 로그인 후 이용해주세요."),
        403: OpenApiResponse(description="권한 없음: 관리자/부관리자 또는 본인만 접근 가능합니다."),
        404: OpenApiResponse(description="찾을 수 없음: 해당 멤버가 존재하지 않습니다."),
        500: OpenApiResponse(description="서버 내부 오류: 관리자에게 문의하세요."),
    },
)
class WorkroomMemberRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    http_method_names = ["get", "patch", "delete"]
    serializer_class = WorkroomMemberSerializer
    permission_classes = [WorkroomPermission]  # 인증된 사용자만 접근 허용

    def get_queryset(self):
        workroom_id = self.kwargs.get("workroom_id")
        return WorkroomMember.objects.filter(workroom_id=workroom_id)

    def destroy(self, request, *args, **kwargs):
        """DELETE 요청 시 '삭제가 완료되었습니다.' 메시지를 JSON으로 반환"""
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"detail": "삭제가 완료되었습니다."}, status=status.HTTP_200_OK)


# 워크룸 리뷰 API ------------------------------------
@extend_schema(
    summary="리뷰 목록 조회 및 작성",
    description="워크룸 종료 후 리뷰를 조회하거나 작성합니다.",
    responses={
        200: WorkroomReviewSerializer(many=True),
        201: WorkroomReviewSerializer,
        400: OpenApiResponse(description="잘못된 요청: 리뷰 작성 조건 불충분"),
        401: OpenApiResponse(description="인증되지 않음: 로그인 필요"),
        403: OpenApiResponse(description="권한 없음: 관리자/부관리자만 가능"),
        404: OpenApiResponse(description="찾을 수 없음: 해당 워크룸이 존재하지 않습니다"),
        500: OpenApiResponse(description="서버 내부 오류"),
    },
)
class WorkroomReviewListCreateAPIView(ListCreateAPIView):
    serializer_class = WorkroomReviewSerializer  # 리뷰 직렬화 클래스
    permission_classes = [WorkroomPermission]  # 인증된 사용자만 접근 허용

    def get_queryset(self):
        workroom_id = self.kwargs.get("workroom_id")
        return WorkroomReview.objects.filter(workroom_id=workroom_id)

    def perform_create(self, serializer):
        workroom = get_object_or_404(Workroom, pk=self.kwargs.get("workroom_id"))
        # 워크룸 종료일 검증
        if workroom.end_date > timezone.now().date():
            return Response(
                {"detail": "워크룸 종료 이후에만 리뷰 작성이 가능합니다."}, status=status.HTTP_400_BAD_REQUEST
            )
        serializer.save(workroom=workroom, reviewer=self.request.user)


# 이슈 API ------------------------------------
@extend_schema(
    summary="이슈 목록 조회 및 생성",
    description="모든 인증된 사용자가 이슈를 조회하거나 작성할 수 있습니다.",
    responses={
        200: IssueSerializer(many=True),
        201: IssueSerializer,
        400: OpenApiResponse(description="잘못된 요청: 필드 유효성 검사 실패"),
        401: OpenApiResponse(description="인증되지 않음: 로그인 필요"),
        403: OpenApiResponse(description="권한 없음: 접근 권한이 없습니다"),
        404: OpenApiResponse(description="찾을 수 없음: 해당 워크룸이 존재하지 않습니다"),
        500: OpenApiResponse(description="서버 내부 오류"),
    },
)
class IssueListCreateAPIView(ListCreateAPIView):
    serializer_class = IssueSerializer  # 이슈 직렬화 클래스
    permission_classes = [WorkroomPermission]  # 인증된 사용자만 접근 허용
    filter_backends = [DjangoFilterBackend]  # 필터링 기능
    filterset_fields = ["user", "status"]  # 필터링 가능한 필드

    def get_queryset(self):
        workroom_id = self.kwargs.get("workroom_id")
        return Issue.objects.filter(workroom_id=workroom_id)

    def perform_create(self, serializer):
        workroom = get_object_or_404(Workroom, pk=self.kwargs.get("workroom_id"))
        serializer.save(workroom=workroom, user=self.request.user)


@extend_schema(
    summary="이슈 상세 조회/수정/삭제",
    description="작성자 본인 및 관리자/부관리자는 이슈 수정/삭제가 가능합니다.",
    responses={
        200: IssueSerializer,
        204: OpenApiResponse(description="삭제 성공"),
        400: OpenApiResponse(description="잘못된 요청: 필드 유효성 검사 실패"),
        401: OpenApiResponse(description="인증되지 않음: 로그인 필요"),
        403: OpenApiResponse(description="권한 없음: 작성자 또는 관리자만 가능"),
        404: OpenApiResponse(description="찾을 수 없음: 해당 이슈가 존재하지 않습니다"),
        500: OpenApiResponse(description="서버 내부 오류"),
    },
)
class IssueRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    http_method_names = ["get", "patch", "delete"]
    serializer_class = IssueSerializer  # 이슈 직렬화 클래스
    permission_classes = [WorkroomPermission]  # 인증된 사용자만 접근 허용

    def get_queryset(self):
        workroom_id = self.kwargs.get("workroom_id")
        return Issue.objects.filter(workroom_id=workroom_id)

    def destroy(self, request, *args, **kwargs):
        """DELETE 요청 시 '삭제가 완료되었습니다.' 메시지를 JSON으로 반환"""
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"detail": "삭제가 완료되었습니다."}, status=status.HTTP_200_OK)


# 일정 API ------------------------------------
@extend_schema(
    summary="일정 목록 조회 및 생성",
    description="승인된 멤버는 일정을 조회 및 생성할 수 있으며, 권한에 따라 수정/삭제가 가능합니다. 또한, 'created_by`는 일정을 생성한 사용자의 nickname을 나타냅니다.",
    request=CalendarEventSerializer,
    responses={
        200: CalendarEventSerializer(many=True),
        202: OpenApiResponse(description="이벤트가 생성되었습니다."),
        400: OpenApiResponse(description="잘못된 요청: 필드 유효성 검사 실패"),
        401: OpenApiResponse(description="인증되지 않음: 로그인 필요"),
        403: OpenApiResponse(description="권한 없음: 승인된 멤버이지만, 일정 생성 권한이 없음"),
        404: OpenApiResponse(description="찾을 수 없음: 해당 워크룸이 존재하지 않습니다"),
        500: OpenApiResponse(description="서버 내부 오류"),
    },
)
class CalendarEventListCreateAPIView(ListCreateAPIView):
    serializer_class = CalendarEventSerializer  # 일정 직렬화 클래스
    permission_classes = [WorkroomPermission]  # 인증된 사용자만 접근 허용
    filter_backends = [DjangoFilterBackend]  # 필터링 기능
    filterset_fields = ["alert"]  # 필터링 가능한 필드

    def get_queryset(self):
        workroom_id = self.kwargs.get("workroom_id")
        return CalendarEvent.objects.filter(workroom_id=workroom_id)

    def create(self, request, *args, **kwargs):
        # URL에서 워크룸 ID 기반으로 워크룸 객체 조회
        workroom = get_object_or_404(Workroom, pk=self.kwargs.get("workroom_id"))

        # 요청 데이터 직렬화
        serializer = self.get_serializer(data=request.data)  # request.data를 기반으로 직렬화 객체 생성
        serializer.is_valid(raise_exception=True)  # 유효성 검증 수행

        # 유효한 데이터로 일정 저장 (workroom, created_by 추가)
        serializer.save(workroom=workroom, created_by=request.user)

        # 저장된 데이터 반환
        return Response({"detail": "이벤트가 생성되었습니다.", "data": serializer.data}, status=status.HTTP_201_CREATED)


@extend_schema(
    summary="일정 상세 조회/수정/삭제",
    description="권한에 따라 일정 수정/삭제가 가능합니다.",
    responses={
        200: CalendarEventSerializer,
        204: OpenApiResponse(description="삭제 성공"),
        400: OpenApiResponse(description="잘못된 요청: 필드 유효성 검사 실패"),
        401: OpenApiResponse(description="인증되지 않음: 로그인 필요"),
        403: OpenApiResponse(description="권한 없음: 권한 레벨 부족"),
        404: OpenApiResponse(description="찾을 수 없음: 해당 일정이 존재하지 않습니다"),
        500: OpenApiResponse(description="서버 내부 오류"),
    },
)
class CalendarEventRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    http_method_names = ["get", "patch", "delete"]
    serializer_class = CalendarEventSerializer  # 일정 직렬화 클래스
    permission_classes = [WorkroomPermission]  # 인증된 사용자만 접근 허용

    def get_queryset(self):
        workroom_id = self.kwargs.get("workroom_id")
        return CalendarEvent.objects.filter(workroom_id=workroom_id)

    def destroy(self, request, *args, **kwargs):
        """DELETE 요청 시 '삭제가 완료되었습니다.' 메시지를 JSON으로 반환"""
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"detail": "삭제가 완료되었습니다."}, status=status.HTTP_200_OK)
