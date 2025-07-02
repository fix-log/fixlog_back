from django.db import models
from django.conf import settings


class Crew(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='projects')
    title = models.CharField(max_length=100)
    deadline = models.DateTimeField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_estimated_period = models.CharField(max_length=50)
    description = models.TextField()
    count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
