from rest_framework import serializers

from .models import Fixred, FixredComment, FixredImage


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
    class Meta:
        model = Fixred
        fields = ["content", "content_type","images", "read_permission" ]
        read_only_fields = ["user", "created_at", "like_count", "comment_count"]

    def create(self, validated_data):
        images = validated_data.pop("images", [])
        fixred = Fixred.objects.create(**validated_data)

        for image in images:
            FixredImage.objects.create(post=fixred, image=image)

        return fixred