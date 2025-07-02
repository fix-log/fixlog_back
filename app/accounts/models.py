from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from app.util.models import Position, Language, Stack

class CoopTool(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class InterestField(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class InterestTrend(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Career(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('이메일은 필수입니다.')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=50, unique=True)
    password = models.CharField(max_length=100)
    nickname = models.CharField(max_length=16)
    profile_image = models.CharField(max_length=100, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    birth = models.CharField(max_length=10, blank=True, null=True)

    position = models.ManyToManyField(Position, blank=True)
    experience = models.CharField(max_length=255, blank=True, null=True)
    language = models.ManyToManyField(Language, blank=True)
    tech = models.ManyToManyField(Stack, blank=True)
    coop_tool = models.ManyToManyField(CoopTool, blank=True)
    interest_field = models.ManyToManyField(InterestField, blank=True)
    interest_trend = models.ManyToManyField(InterestTrend, blank=True)
    career = models.ManyToManyField(Career, blank=True)

    portfolio = models.TextField(blank=True, null=True)
    ref_link = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    oauth_provider = models.CharField(max_length=50, blank=True, null=True)
    oauth_id = models.CharField(max_length=100, blank=True, null=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    def get_full_name(self):
        return self.nickname or self.email

    def get_short_name(self):
        return self.nickname or self.email.split('@')[0]


class RefreshToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='refresh_tokens')
    token = models.TextField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_revoked = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.email} - {self.token[:50]}..."

    def is_expired(self):
        return timezone.now() > self.expires_at


class SocialAccount(models.Model):
    PROVIDER_CHOICES = [
        ('github', 'GitHub'),
        ('kakao', 'Kakao'),
        ('naver', 'Naver'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='social_accounts')
    provider = models.CharField(max_length=50, choices=PROVIDER_CHOICES)
    uid = models.CharField(max_length=100)
    extra_data = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} - {self.provider}"
