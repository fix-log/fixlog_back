from django.db import models

# 포지션 정보 모델 (예: 백엔드, 프론트엔드 등)
class Position(models.Model):
    name = models.CharField(max_length=100)  # 포지션 이름 (예: 백엔드, 프론트엔드 등)

    def __str__(self):
        return self.name

# 사용 언어 정보 모델 (예: Python, JavaScript 등)
class Language(models.Model):
    name = models.CharField(max_length=100)  # 사용 언어 이름 (예: Python, JavaScript 등)

    def __str__(self):
        return self.name

# 기술 스택 정보 모델 (예: Django, React 등)
class Stack(models.Model):
    name = models.CharField(max_length=100)  # 기술 스택 이름 (예: Django, React 등)

    def __str__(self):
        return self.name

# 디자인 도구/분야 정보 모델 (예: Figma, UI/UX 등)
class Design(models.Model):
    name = models.CharField(max_length=100)  # 디자인 도구 또는 분야 이름 (예: Figma, UI/UX 등)

    def __str__(self):
        return self.name
    

# 공통 모델- - 작성일자, 수정일자
# 이 모델들은 다른 모델에서 상속받아 사용할 수 있도록 추상 클래스로 정의합니다.
class TimestampModel(models.Model):
    created_at = models.DateTimeField('작성일자', auto_now_add=True)
    updated_at = models.DateTimeField('수정일자', auto_now=True)

    class Meta:
        abstract = True # 이 모델은 데이터베이스에 테이블을 생성하지 않음

# 작성일자만 있는 모델
class CreatedOnlyModel(models.Model):
    created_at = models.DateTimeField('작성일자',auto_now_add=True)

    class Meta:
        abstract = True # 이 모델은 데이터베이스에 테이블을 생성하지 않음