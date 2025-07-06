from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from app.accounts.models import User
from app.fixletter.models import Fixletter, FixletterBlock, Message


class FixletterModelTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(email="sender@test.com", password="pw", nickname="sender")
        self.user2 = User.objects.create_user(email="receiver@test.com", password="pw", nickname="receiver")

    def test_message_create_and_str(self):
        fixletter = Fixletter.objects.create(
            from_user=self.user1, to_user=self.user2, last_sent_at=timezone.now(), last_message=None
        )
        msg = Message.objects.create(
            fixletter=fixletter,
            send_user=self.user1,
            content="테스트 메시지입니다.",
        )
        self.assertEqual(msg.content, "테스트 메시지입니다.")
        self.assertTrue(str(msg).startswith(f"[{msg.sent_at}] {self.user1.nickname}"))
        # 생성된 메시지 문자열 출력
        print("Message str:", str(msg))

    def test_fixletter_create_and_str(self):
        fixletter = Fixletter.objects.create(
            from_user=self.user1, to_user=self.user2, last_sent_at=timezone.now(), last_message=None
        )
        msg = Message.objects.create(
            fixletter=fixletter,
            send_user=self.user1,
            content="마지막 메시지",
        )
        fixletter.last_message = msg
        fixletter.save()
        self.assertEqual(fixletter.last_message, msg)
        self.assertEqual(self.user1.sent_letters.count(), 1)
        self.assertEqual(self.user2.received_letters.count(), 1)
        self.assertIn(self.user1.nickname, str(fixletter))
        # 생성된 Fixletter 문자열 출력
        print("Fixletter str:", str(fixletter))

    def test_fixletterblock_create_and_str(self):
        block = FixletterBlock.objects.create(blocker=self.user1, blocked=self.user2)
        self.assertTrue(block.is_active)
        self.assertIn(self.user1.nickname, str(block))
        # 생성된 FixletterBlock 문자열 출력
        print("FixletterBlock str:", str(block))

    def test_fixletterblock_self_block(self):
        with self.assertRaises(ValidationError):
            FixletterBlock.objects.create(blocker=self.user1, blocked=self.user1)

    def test_fixletterblock_unblock(self):
        block = FixletterBlock.objects.create(blocker=self.user1, blocked=self.user2)
        block.is_active = False
        block.save()
        self.assertIsNotNone(block.unblocked_at)
        # 차단 해제 시간 출력
        print("Unblocked at:", block.unblocked_at)
