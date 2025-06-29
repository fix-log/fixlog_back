from django.db import models
from django.conf import settings


class Project(models.Model):
    STATUS_CHOICES = [
        ('recruiting', '모집중'),
        ('completed', '모집완료'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    deadline = models.DateTimeField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_estimated_period = models.CharField(max_length=50)
    description = models.TextField()
    count = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='recruiting')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
