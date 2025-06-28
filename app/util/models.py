from django.db import models

# 포지션 정보 모델 (예: 백엔드, 프론트엔드 등)
class Position(models.Model):
    name = models.CharField(max_length=100)  # 포지션 이름 (예: 백엔드, 프론트엔드 등)


# 사용 언어 정보 모델 (예: Python, JavaScript 등)
class Language(models.Model):
    name = models.CharField(max_length=100)  # 사용 언어 이름 (예: Python, JavaScript 등)


# 기술 스택 정보 모델 (예: Django, React 등)
class Stack(models.Model):
    name = models.CharField(max_length=100)  # 기술 스택 이름 (예: Django, React 등)


# 디자인 도구/분야 정보 모델 (예: Figma, UI/UX 등)
class Design(models.Model):
    name = models.CharField(max_length=100)  # 디자인 도구 또는 분야 이름 (예: Figma, UI/UX 등)