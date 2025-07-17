import re
from rest_framework import serializers
from app.accounts.models import User, CoopTool, InterestField, InterestTrend, Career
from app.util.models import Position, Language, Stack

class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    birth = serializers.CharField()
    phone_number = serializers.CharField()

    # ManyToMany 필드용 PK 입력 받기
    position = serializers.PrimaryKeyRelatedField(queryset=Position.objects.all(), many=True)
    language = serializers.PrimaryKeyRelatedField(queryset=Language.objects.all(), many=True)
    tech = serializers.PrimaryKeyRelatedField(queryset=Stack.objects.all(), many=True)
    coop_tool = serializers.PrimaryKeyRelatedField(queryset=CoopTool.objects.all(), many=True)
    interest_field = serializers.PrimaryKeyRelatedField(queryset=InterestField.objects.all(), many=True)
    interest_trend = serializers.PrimaryKeyRelatedField(queryset=InterestTrend.objects.all(), many=True)
    career = serializers.PrimaryKeyRelatedField(queryset=Career.objects.all(), many=True)

    class Meta:
        model = User
        fields = [
            "email", "password", "nickname", "phone_number", "birth",
            "portfolio", "ref_link",
            "position", "language", "tech", "coop_tool",
            "interest_field", "interest_trend", "career"
        ]
        extra_kwargs = {
            "portfolio": {"required": False},
            "ref_link": {"required": False},
        }

    # 기존 validation 메서드들은 그대로 유지!

    def create(self, validated_data):
        m2m_fields = [
            "position", "language", "tech", "coop_tool",
            "interest_field", "interest_trend", "career"
        ]
        m2m_data = {field: validated_data.pop(field, []) for field in m2m_fields}

        user = User.objects.create_user(**validated_data)
        for field, items in m2m_data.items():
            getattr(user, field).set(items)
        return user

    def validate_nickname(self, value):
        # 한글 최대 8자, 영어 최대 16자, _, - 허용
        if not re.match(r"^[가-힣a-zA-Z0-9_-]{1,16}$", value):
            raise serializers.ValidationError("닉네임은 한글 8자, 영어 16자, 특수문자(_, -)만 허용됩니다.")
        return value

    def validate_password(self, value):
        if not (8 <= len(value) < 16):
            raise serializers.ValidationError("비밀번호는 8자 이상 16자 미만이어야 합니다.")
        if not re.search(r"[A-Z]", value):
            raise serializers.ValidationError("비밀번호는 영문 대문자를 최소 1자 포함해야 합니다.")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>_\-]", value):
            raise serializers.ValidationError("비밀번호에 특수문자가 포함되어야 합니다.")
        return value

    def validate_birth(self, value):
        # YYYYMMDD 형식
        if not re.match(r"^\d{8}$", value):
            raise serializers.ValidationError("생년월일은 YYYYMMDD 형식으로 입력해주세요.")
        return value

    def validate_phone_number(self, value):
        # 01012345678 형식
        if not re.match(r"^010\d{8}$", value):
            raise serializers.ValidationError("전화번호는 010으로 시작하고 '-' 없이 숫자만 입력해주세요.")
        return value

    def validate_portfolio(self, value):
        if value and not value.lower().endswith(".pdf"):
            raise serializers.ValidationError("포트폴리오는 PDF 파일이어야 합니다.")
        return value
