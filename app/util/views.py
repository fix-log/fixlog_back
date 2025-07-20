from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import generics, permissions, status
from rest_framework.response import Response

from app.util.models import Design, Language, Position, Stack
from app.util.serializers import DesignSerializer, LanguageSerializer, PositionSerializer, StackSerializer


# 포지션 전체 목록 조회 및 생성
@extend_schema(
    summary="포지션 목록 조회 및 생성",
    responses={
        200: OpenApiResponse(response=PositionSerializer, description="포지션 목록"),
        201: OpenApiResponse(response=PositionSerializer, description="포지션 생성 성공"),
        400: OpenApiResponse(description="잘못된 요청"),
        401: OpenApiResponse(description="인증 정보가 제공되지 않았습니다."),
        403: OpenApiResponse(description="권한이 없습니다."),
        500: OpenApiResponse(description="서버 내부 오류"),
    },
)
class PositionListView(generics.ListCreateAPIView):
    queryset = Position.objects.all()
    serializer_class = PositionSerializer
    permission_classes = [permissions.AllowAny]


# 포지션 단건 조회, 수정(PATCH), 삭제
@extend_schema(methods=["put"], exclude=True)
class PositionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Position.objects.all()
    serializer_class = PositionSerializer
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        methods=["get"],
        summary="포지션 상세 조회",
        responses={
            200: OpenApiResponse(response=PositionSerializer, description="포지션 상세"),
            401: OpenApiResponse(description="인증 정보가 제공되지 않았습니다."),
            403: OpenApiResponse(description="권한이 없습니다."),
            404: OpenApiResponse(description="해당 ID가 없습니다."),
            500: OpenApiResponse(description="서버 내부 오류"),
        },
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        methods=["patch"],
        summary="포지션 수정",
        request=PositionSerializer,
        responses={
            200: OpenApiResponse(response=PositionSerializer, description="포지션 수정 완료"),
            400: OpenApiResponse(description="요청 데이터 오류"),
            401: OpenApiResponse(description="인증 정보가 제공되지 않았습니다."),
            403: OpenApiResponse(description="권한이 없습니다."),
            404: OpenApiResponse(description="해당 ID가 없습니다."),
            500: OpenApiResponse(description="서버 내부 오류"),
        },
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return Response({"detail": "PUT 메서드는 지원하지 않습니다."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @extend_schema(
        methods=["delete"],
        summary="포지션 삭제",
        responses={
            200: OpenApiResponse(description="포지션 삭제 완료"),
            401: OpenApiResponse(description="인증 정보가 제공되지 않았습니다."),
            403: OpenApiResponse(description="권한이 없습니다."),
            404: OpenApiResponse(description="해당 ID가 없습니다."),
            500: OpenApiResponse(description="서버 내부 오류"),
        },
    )
    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        if not request.user.is_authenticated or not request.user.is_staff:
            return Response({"detail": "권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)
        self.perform_destroy(instance)
        return Response({"message": "포지션이 삭제되었습니다."}, status=status.HTTP_200_OK)


# 언어 전체 목록 조회 및 생성
@extend_schema(
    summary="언어 목록 조회 및 생성",
    responses={
        200: OpenApiResponse(response=LanguageSerializer, description="언어 목록"),
        201: OpenApiResponse(response=LanguageSerializer, description="언어 생성 성공"),
        400: OpenApiResponse(description="잘못된 요청"),
        401: OpenApiResponse(description="인증 정보가 제공되지 않았습니다."),
        403: OpenApiResponse(description="권한이 없습니다."),
        500: OpenApiResponse(description="서버 내부 오류"),
    },
)
class LanguageListView(generics.ListCreateAPIView):
    queryset = Language.objects.all()
    serializer_class = LanguageSerializer
    permission_classes = [permissions.AllowAny]


# 언어 단건 조회, 수정(PATCH), 삭제
@extend_schema(methods=["put"], exclude=True)
class LanguageDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Language.objects.all()
    serializer_class = LanguageSerializer
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        methods=["get"],
        summary="언어 상세 조회",
        responses={
            200: OpenApiResponse(response=LanguageSerializer, description="언어 상세"),
            401: OpenApiResponse(description="인증 정보가 제공되지 않았습니다."),
            403: OpenApiResponse(description="권한이 없습니다."),
            404: OpenApiResponse(description="해당 ID가 없습니다."),
            500: OpenApiResponse(description="서버 내부 오류"),
        },
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        methods=["patch"],
        summary="언어 수정",
        request=LanguageSerializer,
        responses={
            200: OpenApiResponse(response=LanguageSerializer, description="언어 수정 완료"),
            400: OpenApiResponse(description="요청 데이터 오류"),
            401: OpenApiResponse(description="인증 정보가 제공되지 않았습니다."),
            403: OpenApiResponse(description="권한이 없습니다."),
            404: OpenApiResponse(description="해당 ID가 없습니다."),
            500: OpenApiResponse(description="서버 내부 오류"),
        },
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return Response({"detail": "PUT 메서드는 지원하지 않습니다."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @extend_schema(
        methods=["delete"],
        summary="언어 삭제",
        responses={
            200: OpenApiResponse(description="언어 삭제 완료"),
            401: OpenApiResponse(description="인증 정보가 제공되지 않았습니다."),
            403: OpenApiResponse(description="권한이 없습니다."),
            404: OpenApiResponse(description="해당 ID가 없습니다."),
            500: OpenApiResponse(description="서버 내부 오류"),
        },
    )
    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        if not request.user.is_authenticated or not request.user.is_staff:
            return Response({"detail": "권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)
        self.perform_destroy(instance)
        return Response({"message": "언어가 삭제되었습니다."}, status=status.HTTP_200_OK)


# 기술스택 전체 목록 조회 및 생성
@extend_schema(
    summary="기술스택 목록 조회 및 생성",
    responses={
        200: OpenApiResponse(response=StackSerializer, description="기술스택 목록"),
        201: OpenApiResponse(response=StackSerializer, description="기술스택 생성 성공"),
        400: OpenApiResponse(description="잘못된 요청"),
        401: OpenApiResponse(description="인증 정보가 제공되지 않았습니다."),
        403: OpenApiResponse(description="권한이 없습니다."),
        500: OpenApiResponse(description="서버 내부 오류"),
    },
)
class StackListView(generics.ListCreateAPIView):
    queryset = Stack.objects.all()
    serializer_class = StackSerializer
    permission_classes = [permissions.AllowAny]


# 기술스택 단건 조회, 수정(PATCH), 삭제
@extend_schema(methods=["put"], exclude=True)
class StackDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Stack.objects.all()
    serializer_class = StackSerializer
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        methods=["get"],
        summary="기술스택 상세 조회",
        responses={
            200: OpenApiResponse(response=StackSerializer, description="기술스택 상세"),
            401: OpenApiResponse(description="인증 정보가 제공되지 않았습니다."),
            403: OpenApiResponse(description="권한이 없습니다."),
            404: OpenApiResponse(description="해당 ID가 없습니다."),
            500: OpenApiResponse(description="서버 내부 오류"),
        },
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        methods=["patch"],
        summary="기술스택 수정",
        request=StackSerializer,
        responses={
            200: OpenApiResponse(response=StackSerializer, description="기술스택 수정 완료"),
            400: OpenApiResponse(description="요청 데이터 오류"),
            401: OpenApiResponse(description="인증 정보가 제공되지 않았습니다."),
            403: OpenApiResponse(description="권한이 없습니다."),
            404: OpenApiResponse(description="해당 ID가 없습니다."),
            500: OpenApiResponse(description="서버 내부 오류"),
        },
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return Response({"detail": "PUT 메서드는 지원하지 않습니다."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @extend_schema(
        methods=["delete"],
        summary="기술스택 삭제",
        responses={
            200: OpenApiResponse(description="기술스택 삭제 완료"),
            401: OpenApiResponse(description="인증 정보가 제공되지 않았습니다."),
            403: OpenApiResponse(description="권한이 없습니다."),
            404: OpenApiResponse(description="해당 ID가 없습니다."),
            500: OpenApiResponse(description="서버 내부 오류"),
        },
    )
    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        if not request.user.is_authenticated or not request.user.is_staff:
            return Response({"detail": "권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)
        self.perform_destroy(instance)
        return Response({"message": "기술스택이 삭제되었습니다."}, status=status.HTTP_200_OK)


# 디자인 전체 목록 조회 및 생성
@extend_schema(
    summary="디자인 목록 조회 및 생성",
    responses={
        200: OpenApiResponse(response=DesignSerializer, description="디자인 목록"),
        201: OpenApiResponse(response=DesignSerializer, description="디자인 생성 성공"),
        400: OpenApiResponse(description="잘못된 요청"),
        401: OpenApiResponse(description="인증 정보가 제공되지 않았습니다."),
        403: OpenApiResponse(description="권한이 없습니다."),
        500: OpenApiResponse(description="서버 내부 오류"),
    },
)
class DesignListView(generics.ListCreateAPIView):
    queryset = Design.objects.all()
    serializer_class = DesignSerializer
    permission_classes = [permissions.AllowAny]


# 디자인 단건 조회, 수정(PATCH), 삭제
@extend_schema(methods=["put"], exclude=True)
class DesignDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Design.objects.all()
    serializer_class = DesignSerializer
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        methods=["get"],
        summary="디자인 상세 조회",
        responses={
            200: OpenApiResponse(response=DesignSerializer, description="디자인 상세"),
            401: OpenApiResponse(description="인증 정보가 제공되지 않았습니다."),
            403: OpenApiResponse(description="권한이 없습니다."),
            404: OpenApiResponse(description="해당 ID가 없습니다."),
            500: OpenApiResponse(description="서버 내부 오류"),
        },
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        methods=["patch"],
        summary="디자인 수정",
        request=DesignSerializer,
        responses={
            200: OpenApiResponse(response=DesignSerializer, description="디자인 수정 완료"),
            400: OpenApiResponse(description="요청 데이터 오류"),
            401: OpenApiResponse(description="인증 정보가 제공되지 않았습니다."),
            403: OpenApiResponse(description="권한이 없습니다."),
            404: OpenApiResponse(description="해당 ID가 없습니다."),
            500: OpenApiResponse(description="서버 내부 오류"),
        },
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return Response({"detail": "PUT 메서드는 지원하지 않습니다."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @extend_schema(
        methods=["delete"],
        summary="디자인 삭제",
        responses={
            200: OpenApiResponse(description="디자인 삭제 완료"),
            401: OpenApiResponse(description="인증 정보가 제공되지 않았습니다."),
            403: OpenApiResponse(description="권한이 없습니다."),
            404: OpenApiResponse(description="해당 ID가 없습니다."),
            500: OpenApiResponse(description="서버 내부 오류"),
        },
    )
    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        if not request.user.is_authenticated or not request.user.is_staff:
            return Response({"detail": "권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)
        self.perform_destroy(instance)
        return Response({"message": "디자인이 삭제되었습니다."}, status=status.HTTP_200_OK)
