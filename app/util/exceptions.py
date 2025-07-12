from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError
from django.db import IntegrityError

def custom_exception_handler(exc, context):
    # 기본 DRF 예외 처리기를 호출하여 기본 응답 생성
    response = exception_handler(exc, context)

    # 추가 예외처리 로직 구현
    if response is not None:
        customized_response = {
            'errors': response.data,
            'status_code': response.status_code
        }
        return Response(customized_response, status=response.status_code)

    # Django ValidationError 처리
    if isinstance(exc, ValidationError):
        return Response({
            'errors': exc.message_dict if hasattr(exc, 'message_dict') else exc.messages,
            'status_code': status.HTTP_400_BAD_REQUEST
        }, status=status.HTTP_400_BAD_REQUEST)

    # IntegrityError (DB 중복, 외래키 오류 등) 처리
    if isinstance(exc, IntegrityError):
        return Response({
            'errors': '데이터베이스 오류: 중복된 값이 존재하거나 참조 무결성 문제가 있습니다.',
            'status_code': status.HTTP_400_BAD_REQUEST
        }, status=status.HTTP_400_BAD_REQUEST)

    # 처리되지 않은 예외는 500 서버 오류로 처리
    return Response({
        'errors': '서버 내부 오류가 발생했습니다.',
        'status_code': status.HTTP_500_INTERNAL_SERVER_ERROR
    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)