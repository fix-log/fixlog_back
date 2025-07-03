from rest_framework import serializers

from app.util.models import Design, Language, Position, Stack


# 포지션 모델 직렬화기
class PositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Position  # 직렬화 대상 모델
        fields = ["id", "name"]  # 포함할 필드 지정


# 언어 모델 직렬화기
class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language  # 직렬화 대상 모델
        fields = ["id", "name"]


# 스택 모델 직렬화기
class StackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stack  # 직렬화 대상 모델
        fields = ["id", "name"]


# 디자인 모델 직렬화기
class DesignSerializer(serializers.ModelSerializer):
    class Meta:
        model = Design  # 직렬화 대상 모델
        fields = ["id", "name"]
