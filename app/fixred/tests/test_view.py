import json
import tempfile

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

import shutil
from django.test import override_settings
import tempfile

TEST_MEDIA_ROOT = tempfile.mkdtemp()

from app.fixred.models import Fixred, FixredComment, FixredImage

User = get_user_model()


@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class FixredFeedViewTest(APITestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEST_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        # 유저 생성
        self.user1 = User.objects.create_user(email="u1@test.com", password="pw", nickname="u1")
        self.user2 = User.objects.create_user(email="u2@test.com", password="pw", nickname="u2")
        self.user3 = User.objects.create_user(email="u3@test.com", password="pw", nickname="u3")

        # 각각 글 생성
        self.post2 = Fixred.objects.create(user=self.user2, content="post by u2")
        self.post3 = Fixred.objects.create(user=self.user3, content="post by u3")

        # 이미지 하나씩 달아두고
        tmp = SimpleUploadedFile("img.png", b"data")
        FixredImage.objects.create(post=self.post2, image=tmp)
        FixredImage.objects.create(post=self.post3, image=tmp)

        # 로그인
        self.client = APIClient()
        self.client.force_authenticate(self.user1)

    def test_unauthenticated(self):
        client = APIClient()
        resp = client.get(reverse("fixred-list"))
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_all(self):
        resp = self.client.get(reverse("fixred-list"), {"filter": "all"})
        print("test_list_all response:", json.dumps(resp.json(), indent=2, ensure_ascii=False))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        ids = {item["id"] for item in resp.json()}
        # 두 글이 모두 반환돼야 함
        self.assertSetEqual(ids, {self.post2.id, self.post3.id})


@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class FixredDetailViewTest(APITestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEST_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.user = User.objects.create_user(email="u@test.com", password="pw", nickname="u")
        self.other = User.objects.create_user(email="o@test.com", password="pw", nickname="o")

        # 글, 댓글 생성
        self.post = Fixred.objects.create(user=self.user, content="detail test")
        c1 = FixredComment.objects.create(fixred=self.post, user=self.other, comment="hello")
        c2 = FixredComment.objects.create(fixred=self.post, user=self.user, comment="world")

        # 이미지
        tmp = SimpleUploadedFile("detail.png", b"data")
        FixredImage.objects.create(post=self.post, image=tmp)

        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_unauthenticated_detail(self):
        client = APIClient()
        resp = client.get(reverse("fixred-detail", args=[self.post.id]))
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_detail_success(self):
        resp = self.client.get(reverse("fixred-detail", args=[self.post.id]))
        data = resp.json()
        print("test_detail_success response:", json.dumps(data, indent=2, ensure_ascii=False))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # 기본 필드 검증
        self.assertEqual(data["id"], self.post.id)
        self.assertEqual(data["content"], "detail test")

        # 이미지 포함
        self.assertTrue("images" in data and len(data["images"]) == 1)

        # 댓글이 created_at 내림차순으로
        comments = data["comments"]
        self.assertEqual(len(comments), 2)
        # 첫 댓글은 c2 (user) 이어야 함 (최신순)
        self.assertEqual(comments[0]["comment"], "world")
        self.assertEqual(comments[1]["comment"], "hello")
