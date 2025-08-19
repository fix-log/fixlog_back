from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q, F, UniqueConstraint, CheckConstraint
from django.utils import timezone

from app.accounts.models import User
from app.accounts.models import User
from app.util.models import CreatedOnlyModel


# 픽레터 모델
class Fixletter(CreatedOnlyModel):
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_letters")
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_letters")
    last_message = models.ForeignKey("Message", on_delete=models.SET_NULL, null=True, related_name="last_fixletters")
    last_sent_at = models.DateTimeField(default=timezone.now, db_index=True)
    
    @classmethod
    def get_pair(cls, u1_id: int, u2_id: int):
        if u1_id == u2_id:
            raise ValidationError("본인과 픽레터 불가")
        a, b = sorted([u1_id, u2_id])
        obj, _ = cls.objects.get_or_create(
            from_user_id=a,
            to_user_id=b,
            defaults={"last_sent_at": timezone.now()},
        )
        return obj

    def participants(self):
        return (self.from_user, self.to_user)

    def other_user(self, user: User) -> User:
        return self.to_user if user.id == self.from_user_id else self.from_user
   
    class Meta:
        db_table = "fixletter"
        ordering = ["-last_sent_at"]
        constraints = [
            # FK 실제 컬럼인 *_id 로 비교하는 게 가장 명확함
            CheckConstraint(
                check=Q(from_user_id__lt=F("to_user_id")),
                name="fixletter_from_lt_to",
            ),
            UniqueConstraint(
                fields=["from_user", "to_user"],
                name="fixletter_unique_pair",
            ),
        ]
    def __str__(self):
        last_msg = self.last_message.content[:10] if self.last_message else "No message"
        return f"{self.last_sent_at}|[{self.from_user.nickname}] -> [{self.to_user.nickname}]: {last_msg}..."


# 픽레터 메시지 모델
class Message(models.Model):
    fixletter = models.ForeignKey(Fixletter, on_delete=models.CASCADE, related_name="messages")
    send_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="messages_sent")
    content = models.TextField(max_length=500)
    sent_at = models.DateTimeField(auto_now_add=True, db_index=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=['fixletter', 'sent_at']),
            models.Index(fields=['fixletter', 'is_read', 'sent_at']),
        ]

    def __str__(self):
        return f"[{self.sent_at}] {self.send_user.nickname}: {self.content[:10]}..."


# 픽레터 차단 모델
class FixletterBlock(models.Model):
    blocker = models.ForeignKey(User, on_delete=models.CASCADE, related_name="letter_blocks_made")
    blocked = models.ForeignKey(User, on_delete=models.CASCADE, related_name="letter_blocks_received")
    is_active = models.BooleanField(default=True)  # 차단 활성화 여부

    blocked_at = models.DateTimeField(auto_now_add=True)
    unblocked_at = models.DateTimeField(null=True, blank=True)
    # 차단 해제 시각은 null 허용, 차단 중인 경우는 None

    def save(self, *args, **kwargs):
        # 자기 자신을 차단하는 경우 예외 처리
        if self.blocker == self.blocked:
            raise ValidationError("자기 자신을 차단할 수 없습니다.")

        # 차단 해제시 unblocked_at 자동 설정
        if not self.is_active and self.unblocked_at is None:
            self.unblocked_at = timezone.now()
        super().save(*args, **kwargs)

    class Meta:
        db_table = "fixletter_block"
        constraints = [
            UniqueConstraint(fields=["blocker", "blocked"], name="uniq_fixletter_block_pair"),
        ]


    def __str__(self):
        status = "활성" if self.is_active else f"해제({self.unblocked_at})"
        return f"{self.blocker.nickname} → {self.blocked.nickname} | {status}"
