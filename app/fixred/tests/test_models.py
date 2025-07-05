from django.test import TestCase

from app.accounts.models import User
from app.fixred.models import Fixred


class TestFixredModel(TestCase):
    def setUp(self):
        # 테스트용 유저 생성
        self.user = User.objects.create_user(
            email="testuser@test.com",
            password="testpassword",
            nickname="testuser",
        )

    def test_fixred_create(self):
        post = Fixred.objects.create(
            user=self.user,
            content="픽레드 테스트",
        )
        # 로그 출력
        print(f"생성된 Fixred: id={post.id}, user={post.user.nickname}, content={post.content}")
        self.assertEqual(post.user.nickname, "testuser")
        self.assertEqual(post.content, "픽레드 테스트")
