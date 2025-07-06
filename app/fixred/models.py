from django.db import models

from app.util.models import CreatedOnlyModel, TimestampModel

class Fixred(TimestampModel):
    user= models.ForeignKey("users.User",on_delete=models.CASCADE, related_name='fixreds')
    content = models.TextField()
    like_count = models.IntegerField(default=0)
    comment_count = models.IntegerField(default=0)
    read_permission = models.CharField(
        max_length=10,
        choices=[
            ('all', '모든 사람',),
            ('follow','내가 팔로우 하는 사람만'),
            ('mention', '멘션한 사람만')
        ],
        default='all'
    )
    
    class Meta:
        db_table = 'fixred'
        ordering = ['-created_at'] # 최신순

    def __str__(self): 
        return f"[{self.id}] {self.user.nickname}: {self.content[:20]}..."
    
class FixredImage(models.Model):
    post = models.ForeignKey(Fixred, on_delete=models.CASCADE)
    image = models.ImageField('fixred_image',upload_to='fixred_images/')

    def __str__(self):
        return f"{self.post.content[:10]} image"
    

class FixredComment(CreatedOnlyModel):
    fixred_id = models.ForeignKey(Fixred, on_delete=models.CASCADE)
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    comment = models.CharField(max_length=500)
    
class FixredReport(CreatedOnlyModel):
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    fixred_post = models.ForeignKey(Fixred, on_delete=models.CASCADE)
    reason = models.CharField(
        max_length=100, 
        choices=[
            ('abuse', '욕설/비하'),
            ('privacy','개인정보 노출'),
            ('inappropriate', '부적절한 내용'),
            ('illegal', '불법/범죄'),
            ('etc', '기타')
        ]
        )
    
class UserBlock(CreatedOnlyModel):
    blocker = models.Foreignkey("users.User", on_delete=models.CASCADE)
    blocked = models.ForeignKey("users.User", on_delete=models.CASCADE)