from rest_framework import status
from rest_framework.response import Response


def ok(message=None, data=None, code=status.HTTP_200_OK, **extra):
    body = {}
    if message:
        body["message"] = message
    if data:
        body.update(data)
    return Response(body, status=code)


def fail(message="오류가 발생했습니다.", code=status.HTTP_400_BAD_REQUEST):

    return Response({"message": message}, status=code)
