from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from app.notifications.models import Notification
from rest_framework import Response, status
from app.notifications.serializers import NotificationSerializer
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse


# 알림 목록 조회
@extend_schema(
    summary="알림 목록 조회",
    description="로그인한 사용자의 알림 목록을 최신순으로 조회합니다.\n옵션으로 알림 타입(`fixred`, `workroom`, `crew`) 필터링이 가능합니다.",
    parameters=[
        OpenApiParameter(name="type", description="알림 타입 필터링", required=False, type=str),
    ],
    responses=NotificationSerializer
)
class NotificationListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationSerializer

    def get_queryset(self):
        user = self.request.user
        qs= Notification.objects.filter(user=user).order_by('-created_at')
        noti_type = self.request.query_params.get('type')
        if noti_type:
            qs = qs.filter(notification_type=noti_type)
        return qs
    
# 단일 알림 읽음 처리
@extend_schema(
    summary="단일 알림 읽음 처리",
    description="알림 ID를 받아 해당 알림을 읽음 처리합니다.",
    responses={
        200: OpenApiResponse(description="알림 읽음 처리 완료"),
        403: OpenApiResponse(description="권한 없음"),
    },
)
class NotificationReadView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Notification.objects.all()
    lookup_field = 'pk'

    def patch(self, request, *args, **kwargs):
        notification = self.get_object()
        if notification.user != request.user:
            return Response(
                {"error": "권한이 없습니다."},
                status=status.HTTP_403_FORBIDDEN
            )
        if not notification.is_read:
            notification.is_read = True
            notification.save()
        return Response(
            {"message": "알림 읽음 처리 완료"}, status=status.HTTP_200_OK
        )
    
# 알림 전체 읽음 처리
@extend_schema(
    summary="모든 알림 읽음 처리",
    description="사용자의 읽지 않은 모든 알림을 읽음 처리합니다.",
    responses={
        200: OpenApiResponse(description="읽음 처리된 알림 수 리턴"),
    },
)
class NotificationReadAllView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        updated = Notification.objects.filter(
            user=request.user, is_read=False
        ).update(is_read=True)
        
        return Response(
            {"message": f"{updated}개의 알림을 읽음 처리했습니다."},
            status=status.HTTP_200_OK
        )