from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils import timezone


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('이메일은 필수입니다')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser):
    # 기본 필드
    email = models.CharField(max_length=50, unique=True, verbose_name='유저 email')
    password = models.CharField(max_length=100, verbose_name='유저 비밀번호')
    nickname = models.CharField(max_length=16, verbose_name='유저 닉네임')

    # 프로필 정보
    profile_image = models.CharField(max_length=100, blank=True, verbose_name='유저 이미지')
    phone_number = models.CharField(max_length=15, blank=True, verbose_name='유저 전화번호')
    birth = models.CharField(max_length=10, blank=True, verbose_name='유저 생년월일')

    # 직업/경력 정보
    position = models.TextField(blank=True, verbose_name='포지션')
    experience = models.TextField(blank=True, verbose_name='경력')
    language = models.TextField(blank=True, verbose_name='개발 언어')
    tech = models.TextField(blank=True, verbose_name='기술 스택')
    coop_tool = models.TextField(blank=True, verbose_name='협업/디자인 툴')

    # 관심사/포트폴리오
    interest_field = models.TextField(blank=True, verbose_name='관심 개발 분야')
    interest_trend = models.TextField(blank=True, verbose_name='관심 기술 & 트렌드')
    career = models.TextField(blank=True, verbose_name='커리어 & 성장')
    portfolio = models.TextField(blank=True, verbose_name='포트폴리오')
    ref_link = models.TextField(blank=True, verbose_name='참고링크')

    # 타임스탬프
    created_at = models.DateTimeField(default=timezone.now, verbose_name='유저 생성일')
    updated_at = models.DateTimeField(default=timezone.now, verbose_name='유저 업데이트일')

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nickname']

    class Meta:
        db_table = 'user'
        verbose_name = '사용자'
        verbose_name_plural = '사용자들'

    def save(self, *args, **kwargs):
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nickname} ({self.email})"

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser

