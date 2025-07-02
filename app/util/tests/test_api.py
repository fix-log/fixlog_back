from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from app.util.models import Position, Language, Stack, Design


class UtilViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

    # Position API 테스트
    def test_create_position(self):  # 포지션 생성 테스트
        response = self.client.post(reverse("position-list"), {"name": "백엔드"})  # 포지션 생성 요청
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)# 생성 성공 코드 확인
        self.assertEqual(response.data["name"], "백엔드")  # 반환된 name 확인

    def test_list_position(self):  # 포지션 목록 조회 테스트
        Position.objects.create(name="프론트엔드")  # 테스트용 포지션 데이터 생성
        response = self.client.get(reverse("position-list"))  # 목록 요청
        self.assertEqual(response.status_code, status.HTTP_200_OK)  # 응답 코드 확인
        self.assertEqual(response.data[0]["name"], "프론트엔드")  # 응답 데이터 확인

    def test_retrieve_update_delete_position(self):  # 포지션 단건 조회/수정/삭제 테스트
        position = Position.objects.create(name="디자이너")  # 테스트 데이터 생성
        url = reverse("position-detail", args=[position.id])  # 해당 포지션 단건 URL 생성

        response = self.client.get(url)  # 단건 조회 요청
        self.assertEqual(response.status_code, status.HTTP_200_OK)  # 응답 코드 확인

        response = self.client.patch(url, {"name": "기획자"})  # 이름 수정 요청
        self.assertEqual(response.status_code, status.HTTP_200_OK)  # 수정 성공 확인
        self.assertEqual(response.data["name"], "기획자")  # 수정된 name 확인

        response = self.client.delete(url)  # 삭제 요청
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)  # 인증 안 된 유저 삭제 금지 확인

    # Language API 테스트
    def test_create_language(self):  # 언어 생성 테스트
        response = self.client.post(reverse("language-list"), {"name": "Python"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)  # 생성 성공 코드 확인
        self.assertEqual(response.data["name"], "Python")   # 응답 데이터 확인

    def test_list_language(self):  # 언어 목록 조회 테스트
        Language.objects.create(name="JavaScript")
        response = self.client.get(reverse("language-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)  # 응답 코드 확인
        self.assertEqual(response.data[0]["name"], "JavaScript")  # 응답 데이터 확인

    def test_retrieve_update_delete_language(self):  # 언어 단건 테스트
        language = Language.objects.create(name="Java")
        url = reverse("language-detail", args=[language.id])

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)  # 응답 코드 확인

        response = self.client.patch(url, {"name": "Go"})  # 이름 수정 요청
        self.assertEqual(response.status_code, status.HTTP_200_OK)  # 수정 성공 확인
        self.assertEqual(response.data["name"], "Go")  # 수정된 name 확인

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)  # 인증 안 된 유저 삭제 금지 확인

    # Stack API 테스트
    def test_create_stack(self):  # 기술스택 생성 테스트
        response = self.client.post(reverse("stack-list"), {"name": "Django"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)  # 생성 성공 코드 확인
        self.assertEqual(response.data["name"], "Django")  # 응답 데이터 확인

    def test_list_stack(self):  # 기술스택 목록 조회 테스트
        Stack.objects.create(name="React")
        response = self.client.get(reverse("stack-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)  # 응답 코드 확인
        self.assertEqual(response.data[0]["name"], "React")  # 응답 데이터 확인

    def test_retrieve_update_delete_stack(self):  # 기술스택 단건 테스트
        stack = Stack.objects.create(name="Flask")
        url = reverse("stack-detail", args=[stack.id])

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)  # 응답 코드 확인

        response = self.client.patch(url, {"name": "FastAPI"})  # 이름 수정 요청
        self.assertEqual(response.status_code, status.HTTP_200_OK)  # 수정 성공 확인
        self.assertEqual(response.data["name"], "FastAPI")  # 수정된 name 확인

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)  # 인증 안 된 유저 삭제 금지 확인

    # 디자인 API 테스트
    def test_create_design(self):  # 디자인 생성 테스트
        response = self.client.post(reverse("design-list"), {"name": "Figma"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)  # 생성 성공 코드 확인
        self.assertEqual(response.data["name"], "Figma")  # 응답 데이터 확인

    def test_list_design(self):  # 디자인 목록 조회 테스트
        Design.objects.create(name="AdobeXD")
        response = self.client.get(reverse("design-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)  # 응답 코드 확인
        self.assertEqual(response.data[0]["name"], "AdobeXD")  # 응답 데이터 확인

    def test_retrieve_update_delete_design(self):  # 디자인 단건 테스트
        design = Design.objects.create(name="Photoshop")
        url = reverse("design-detail", args=[design.id])

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)  # 응답 코드 확인

        response = self.client.patch(url, {"name": "Illustrator"})  # 이름 수정 요청
        self.assertEqual(response.status_code, status.HTTP_200_OK)  # 수정 성공 확인
        self.assertEqual(response.data["name"], "Illustrator")  # 수정된 name 확인

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)  # 인증 안 된 유저 삭제 금지 확인
