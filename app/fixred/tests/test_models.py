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
            self.assertEqual(post.user.nickname, "testuser")
            self.assertEqual(post.content, "픽레드 테스트")