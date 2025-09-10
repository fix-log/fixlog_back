from django.db.models import Q
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from drf_spectacular.utils import OpenApiExample, OpenApiParameter, OpenApiTypes, extend_schema, extend_schema_view
from rest_framework import generics, permissions, status
from rest_framework.response import Response

from .models import Fixletter, Message
from .serializers import (
    FixletterCreateResponseSerializer,
    FixletterCreateSerializer,
    FixletterSerializer,
    MessageSerializer,
)


def chat_test(request):
    return render(request, "test_chat.html")


def ws_test(request, fixletter_id=None):
    """테스트 페이지: /fixletter/test/<fixletter_id>/"""
    return render(request, "ws_test.html", {"fixletter_id": fixletter_id or ""})


@extend_schema_view(
    post=extend_schema(
        tags=["Fixletter"],
        operation_id="fixletter_create_or_get",
        summary="픽레터 방 생성/가져오기",
        description=(
            "`peer_id`를 전달하면 기존 방이 있으면 그 ID를, 없으면 새로 만들고 ID를 반환합니다. "
            "방의 `last_sent_at`이 비어 있으면 현재 시각으로 초기화됩니다."
        ),
        request=FixletterCreateSerializer,
        responses={
            200: FixletterCreateResponseSerializer,
            400: OpenApiTypes.OBJECT,
            401: OpenApiTypes.NONE,
        },
        examples=[
            OpenApiExample(
                "생성됨",
                value={"fixletter_id": 101, "created": True},
                response_only=True,
            ),
            OpenApiExample(
                "기존방",
                value={"fixletter_id": 7, "created": False},
                response_only=True,
            ),
        ],
    )
)
class FixletterCreateView(generics.CreateAPIView):
    """상대 사용자(peer_user_id)와의 픽레터 방을 열거나 기존 방을 반환합니다."""

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = FixletterCreateSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        peer_user_id = serializer.validated_data["peer_id"]

        current_user_id = request.user.id
        fixletter_instance = Fixletter.get_pair(current_user_id, peer_user_id)

        # last_sent_at 비어 있으면 현재 시각으로 초기화
        if not fixletter_instance.last_sent_at:
            fixletter_instance.last_sent_at = timezone.now()
            fixletter_instance.save(update_fields=["last_sent_at"])

        response_payload = {
            "fixletter_id": fixletter_instance.id,
            "created": fixletter_instance.messages.count() == 0,
        }
        return Response(response_payload, status=status.HTTP_200_OK)


@extend_schema_view(
    get=extend_schema(
        tags=["Fixletter"],
        operation_id="fixletter_list",
        summary="내 픽레터 방 목록",
        description="로그인 사용자가 참여한 방 목록을 반환합니다.",
        parameters=[
            OpenApiParameter(
                name="page", description="페이지 번호", required=False, type=int, location=OpenApiParameter.QUERY
            ),
            OpenApiParameter(
                name="page_size", description="페이지 크기", required=False, type=int, location=OpenApiParameter.QUERY
            ),
        ],
        responses={200: FixletterSerializer(many=True)},
    )
)
class FixletterListView(generics.ListAPIView):
    serializer_class = FixletterSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        current_user = self.request.user
        return Fixletter.objects.filter(Q(from_user=current_user) | Q(to_user=current_user)).select_related(
            "last_message", "from_user", "to_user"
        )


@extend_schema_view(
    get=extend_schema(
        tags=["Message"],
        operation_id="message_list_by_fixletter",
        summary="특정 방의 메시지 목록(최신순)",
        description="요청 사용자가 방 참여자가 아니면 404를 반환합니다.",
        parameters=[
            OpenApiParameter(
                name="fixletter_id", description="픽레터 방 ID", required=True, type=int, location=OpenApiParameter.PATH
            ),
            OpenApiParameter(
                name="page", description="페이지 번호", required=False, type=int, location=OpenApiParameter.QUERY
            ),
            OpenApiParameter(
                name="page_size", description="페이지 크기", required=False, type=int, location=OpenApiParameter.QUERY
            ),
        ],
        responses={200: MessageSerializer(many=True), 404: OpenApiTypes.NONE},
        examples=[
            OpenApiExample(
                "예시",
                value=[
                    {
                        "id": 345,
                        "fixletter_id": 7,
                        "sender_id": 12,
                        "content": "내일 몇시에 탈까?",
                        "sent_at": "2025-09-09T19:12:53Z",
                        "is_read": False,
                    },
                    {
                        "id": 344,
                        "fixletter_id": 7,
                        "sender_id": 3,
                        "content": "퇴근하고 바로!",
                        "sent_at": "2025-09-09T18:59:10Z",
                        "is_read": True,
                    },
                ],
                response_only=True,
            )
        ],
    )
)
class MessageListView(generics.ListAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        current_user = self.request.user
        fixletter_id = self.kwargs["fixletter_id"]
        # 참여자 검증 (404 반환)
        get_object_or_404(Fixletter, Q(id=fixletter_id) & (Q(from_user=current_user) | Q(to_user=current_user)))
        return Message.objects.filter(fixletter_id=fixletter_id).order_by("-sent_at")
