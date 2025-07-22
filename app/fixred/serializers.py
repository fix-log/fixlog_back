from rest_framework import serializers

from .models import Fixred, FixredComment, FixredImage

from app.accounts.models import User 

# 사용자 정보 직렬화
class SimpleUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "nickname", "email", "profile_image"]  # 필요한 필드만

class FixredImageSerializer(serializers.ModelSerializer):
    image_url = serializers.ImageField(source="image", read_only=True)

    class Meta:
        model = FixredImage
        fields = ["image_url"]


class FixredListSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    images = FixredImageSerializer(source="fixredimage_set", many=True, read_only=True)

    class Meta:
        model = Fixred
        fields = [
            "id",
            "user",
            "content",
            "images",
            "like_count",
            "comment_count",
            "read_permission",
            "created_at",
        ]
        read_only_fields = ["id", "read_permission", "created_at", "like_count", "comment_count"]

    def get_user(self, obj):
        return {"id": obj.user.id, "nickname": obj.user.nickname, "profile_image": obj.user.profile_image or None}


class FixredCommentSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        model = FixredComment
        fields = ["id", "user", "comment", "created_at"]
        read_only_fields = ["id", "created_at"]

    def get_user(self, obj):
        return {"id": obj.user.id, "nickname": obj.user.nickname, "profile_image": obj.user.profile_image or None}


class FixredDetailSerializer(FixredListSerializer):
    comments = FixredCommentSerializer(many=True, read_only=True)

    class Meta(FixredListSerializer.Meta):
        fields = FixredListSerializer.Meta.fields + ["comments"]


class FixredCreateSerializer(serializers.ModelSerializer):
    user = SimpleUserSerializer(read_only=True)
    images = serializers.ListField(
        child=serializers.ImageField(), write_only=True, required=False
    )
    class Meta:
        model = Fixred
        fields = ["id","user","content", "images", "read_permission","created_at"]
        read_only_fields = ["user", "created_at", "like_count", "comment_count"]

    def create(self, validated_data):
        images = validated_data.pop("images", [])
        fixred = Fixred.objects.create(**validated_data)

        for image in images:
            FixredImage.objects.create(post=fixred, image=image)

        return fixred

class FixredUpdateSerializer(FixredCreateSerializer):
    delete_image_ids = serializers.ListField(
        child=serializers.IntegerField(), required=False, write_only=True
    )

    class Meta(FixredCreateSerializer.Meta):
        fields = FixredCreateSerializer.Meta.fields + ["id", "delete_image_ids","created_at","updated_at"]
        read_only_fields = FixredCreateSerializer.Meta.read_only_fields + ["id","images","created_at","updated_at"]

    def update(self, instance, validated_data):
        # content(내용), read_permission(권한)만 수정
        instance.content = validated_data.get("content", instance.content)
        instance.read_permission = validated_data.get("read_permission", instance.read_permission)
        instance.save()

        # 삭제 요청된 이미지 ID만 삭제
        delete_image_ids = validated_data.get("delete_image_ids", [])
        if delete_image_ids:
            FixredImage.objects.filter(id__in=delete_image_ids, post=instance).delete()

        return instance


class FixredDeleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fixred
        fields = ["id"]
        read_only_fields = ["id"]

    def validate(self, attrs):
        return attrs