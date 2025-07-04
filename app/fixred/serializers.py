from rest_framework import serializers

from .models import Fixred, FixredImage


class FixredImageSerializer(serializers.ModelSerializer):
    image_url = serializers.ImageField(source="image", read_only=True)

    class Meta:
        model = FixredImage
        fields = ["image_url"]


class FixredSerializer(serializers.ModelSerializer):
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
