from django.db import models
from app.util.models import CreatedOnlyModel
from app.accounts.models import User
from django.core.exceptions import ValidationError

# 픽레터 모델
class Fixletter(CreatedOnlyModel):
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_letters')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_letters')
    last_message = models.ForeignKey("Message", on_delete=models.CASCADE)
    last_sent_at = models.DateTimeField()

    class Meta:
        db_table = 'fixletter'
        ordering = ['-last_sent_at']  # 최신순으로 정렬
    
    def __str__(self):
        last_msg = self.last_message.content[:10] if self.last_message else 'No message'
        return f"{self.last_sent_at}|[{self.from_user.nickname}] -> [{self.to_user.nickname}]: {last_msg}..."
    
# 픽레터 메시지 모델
class Message(models.Model):
    fixletter = models.ForeignKey(Fixletter, on_delete=models.CASCADE, related_name='messages')
    send_user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(max_length=500)
    sent_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        db_table = 'message'
        ordering = ['-sent_at'] # 최신순으로 정렬

    def __str__(self):
        return f"[{self.sent_at}] {self.send_user.nickname}: {self.content[:10]}..."

# 픽레터 차단 모델
class FixletterBlock(models.Model):
    blocker = models.ForeignKey(User, on_delete=models.CASCADE, related_name='letter_blocks_made')
    blocked = models.ForeignKey(User, on_delete=models.CASCADE, related_name='letter_blocks_received')
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
            from django.utils import timezone
            self.unblocked_at = timezone.now()
        super().save(*args, **kwargs)
    
    class Meta:
        db_table = 'fixletter_block'
        unique_together = ('blocker', 'blocked') # 차단 중복 방지

    def __str__(self):
        status = "활성" if self.is_active else f"해제({self.unblocked_at})"
        return f"{self.blocker.nickname} → {self.blocked.nickname} | {status}"