import json
import shutil
import tempfile
from types import SimpleNamespace

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings

from app.fixred.models import Fixred, FixredComment, FixredImage
from app.fixred.serializers import (
    FixredCommentSerializer,
    FixredDetailSerializer,
    FixredImageSerializer,
    FixredListSerializer,
)

# 테스트 전용 임시 MEDIA_ROOT
TEST_MEDIA_ROOT = tempfile.mkdtemp()


User = get_user_model()


class FixredImageSerializerTest(TestCase):
    def test_image_url_field(self):
        # 모델 인스턴스를 생성하지 않고, 인스턴스만 만들어서 image 속성을 덮어씁니다
        img = FixredImage()
        img.image = SimpleNamespace(url="/media/path/to/img.png")
        data = FixredImageSerializer(img).data
        print(f"{self.__class__.__name__}.{self._testMethodName}: 성공")
        self.assertEqual(data["image_url"], "/media/path/to/img.png")


@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class FixredListSerializerTest(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        # 테스트 후 임시 MEDIA_ROOT 삭제
        shutil.rmtree(TEST_MEDIA_ROOT, ignore_errors=True)

    def test_list_serializer_fields(self):
        user = User.objects.create_user(email="testuser@test.com", password="pw", nickname="nick")
        fixred = Fixred.objects.create(user=user, content="hello world", like_count=5, comment_count=2)
        dummy = SimpleUploadedFile("test.png", b"file-bytes")
        img = FixredImage.objects.create(post=fixred, image=dummy)
        fixred.fixredimage_set.add(img)
        fixred.fixredimage_set.set([img])

        data = FixredListSerializer(fixred).data
        print(f"{self.__class__.__name__}.{self._testMethodName}: 성공")
        self.assertEqual(data["id"], fixred.id)
        self.assertEqual(data["user"]["id"], user.id)
        self.assertEqual(data["user"]["nickname"], user.nickname)
        image_url = data["images"][0]["image_url"]
        self.assertTrue(image_url.endswith(".png"), f"Expected image_url to end with '.png', got {image_url}")
        self.assertEqual(data["like_count"], 5)
        self.assertEqual(data["comment_count"], 2)


class FixredCommentSerializerTest(TestCase):
    def test_comment_serializer(self):
        user = User.objects.create_user(email="testuse2r@test.com", password="pw", nickname="nick2")
        fixred = Fixred.objects.create(user=user, content="hi")
        comment = FixredComment.objects.create(fixred=fixred, user=user, comment="great")
        data = FixredCommentSerializer(comment).data
        print(f"{self.__class__.__name__}.{self._testMethodName}: 성공")
        self.assertEqual(data["id"], comment.id)
        self.assertEqual(data["user"]["id"], user.id)
        self.assertEqual(data["comment"], "great")


class FixredDetailSerializerTest(TestCase):
    def test_detail_serializer_includes_comments(self):
        user = User.objects.create_user(email="testuser3@test.com", password="pw", nickname="nick3")
        fixred = Fixred.objects.create(user=user, content="hey")
        # 댓글 두 개 생성
        c1 = FixredComment.objects.create(fixred=fixred, user=user, comment="first")
        c2 = FixredComment.objects.create(fixred=fixred, user=user, comment="second")
        data = FixredDetailSerializer(fixred).data
        print(f"{self.__class__.__name__}.{self._testMethodName}: 성공")
        # 댓글 필드 포함 여부 및 개수 확인
        self.assertIn("comments", data)
        self.assertEqual(len(data["comments"]), 2)
        comments = {c["comment"] for c in data["comments"]}
        self.assertSetEqual(comments, {"first", "second"})
