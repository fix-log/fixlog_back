from django.core.exceptions import ValidationError
from django.db import models

from app.accounts.models import User
from app.util.models import CreatedOnlyModel, TimestampModel


# 픽레드 모델
class Fixred(TimestampModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="fixreds")
    content = models.TextField()
    like_count = models.IntegerField(default=0)
    comment_count = models.IntegerField(default=0)
    read_permission = models.CharField(
        max_length=10,
        choices=[
            ("all", "모든 사람"),
            ("follow", "내가 팔로우 하는 사람만"),
            ("mention", "멘션한 사람만"),
        ],
        default="all",
    )

    class Meta:
        db_table = "fixred"
        ordering = ["-created_at"]  # 최신순 정렬

    def __str__(self):
        return f"[{self.id}] {self.user.nickname}: {self.content[:20]}..."


# 픽레드 이미지 모델
class FixredImage(models.Model):
    post = models.ForeignKey(Fixred, on_delete=models.CASCADE)
    image = models.ImageField("fixred_image", upload_to="fixred_images/")

    def __str__(self):
        return f"{self.post.content[:10]} image"


# 픽레드 댓글 모델
class FixredComment(CreatedOnlyModel):
    fixred = models.ForeignKey(Fixred, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.CharField(max_length=500)

    def __str__(self):
        return f"[{self.id}] {self.user.nickname}: {self.comment[:10]}..."


# 픽레드 신고 모델
class FixredReport(CreatedOnlyModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    fixred_post = models.ForeignKey(Fixred, on_delete=models.CASCADE)
    reason = models.CharField(
        max_length=100,
        choices=[
            ("abuse", "욕설/비하"),
            ("privacy", "개인정보 노출"),
            ("inappropriate", "부적절한 내용"),
            ("illegal", "불법/범죄"),
            ("etc", "기타"),
        ],
    )

    def __str__(self):
        return (
            f"[{self.id}] {self.user.nickname}님의 신고\n"
            f"- 게시물 ID: [{self.fixred_post.id}]\n"
            f"- 내용: {self.fixred_post.content[:10]}...\n"
            f"- 사유: {self.reason}"
        )


# 픽레드 차단 모델
class FixredBlock(CreatedOnlyModel):
    blocker = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="fixred_blocks_made",
        verbose_name="차단자",
    )
    blocked = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="fixred_blocks_received",
        verbose_name="차단 대상",
    )

    class Meta:
        db_table = "fixred_block"
        unique_together = ("blocker", "blocked")  # 차단 중복 방지
        verbose_name = "픽레드 차단"
        verbose_name_plural = "픽레드 차단 목록"

    def clean(self):
        # 자기 자신 차단 방지
        if self.blocker == self.blocked:
            raise ValidationError("자기 자신을 차단할 수 없습니다.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.blocker.nickname} → {self.blocked.nickname} | 차단"
