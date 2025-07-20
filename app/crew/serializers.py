from rest_framework import serializers

from app.crew.models import Project, ProjectLanguage, ProjectPosition, ProjectSkillTool, Application
from app.util.models import Language, Position, Stack


class ProjectPositionSerializer(serializers.ModelSerializer):
    position_name = serializers.CharField(source="position.name", read_only=True)

    class Meta:
        model = ProjectPosition
        fields = ["position", "position_name", "count"]


class ProjectLanguageSerializer(serializers.ModelSerializer):
    language_name = serializers.CharField(source="language.name", read_only=True)

    class Meta:
        model = ProjectLanguage
        fields = ["language", "language_name"]


class ProjectSkillToolSerializer(serializers.ModelSerializer):
    skill_tool_name = serializers.CharField(source="skill_tool.name", read_only=True)

    class Meta:
        model = ProjectSkillTool
        fields = ["skill_tool", "skill_tool_name"]


class ProjectSerializer(serializers.ModelSerializer):
    # 유저 닉네임 추가
    user_nickname = serializers.CharField(source="user.nickname", read_only=True)

    # 중간 테이블 정보를 포함한 필드들
    project_positions = ProjectPositionSerializer(source="projectposition_set", many=True, read_only=True)
    project_languages = ProjectLanguageSerializer(source="projectlanguage_set", many=True, read_only=True)
    project_skill_tools = ProjectSkillToolSerializer(source="projectskilltool_set", many=True, read_only=True)

    # 단순 ID 리스트 (생성/수정 시 사용)
    position_ids = serializers.ListField(child=serializers.IntegerField(), write_only=True, required=False)
    language_ids = serializers.ListField(child=serializers.IntegerField(), write_only=True, required=False)
    skill_tool_ids = serializers.ListField(child=serializers.IntegerField(), write_only=True, required=False)

    class Meta:
        model = Project
        fields = [
            "id",
            "user",
            "user_nickname",
            "title",
            "deadline",
            "start_date",
            "end_date",
            "is_estimated_period",
            "description",
            "count",
            "status",
            "project_positions",
            "project_languages",
            "project_skill_tools",
            "position_ids",
            "language_ids",
            "skill_tool_ids",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def create(self, validated_data):
        # ManyToMany 관계 데이터 분리
        position_ids = validated_data.pop("position_ids", [])
        language_ids = validated_data.pop("language_ids", [])
        skill_tool_ids = validated_data.pop("skill_tool_ids", [])

        # 프로젝트 생성
        validated_data["user"] = self.context["request"].user
        project = Project.objects.create(**validated_data)

        # 중간 테이블 데이터 생성
        self._create_relations(project, position_ids, language_ids, skill_tool_ids)

        return project

    def update(self, instance, validated_data):
        # ManyToMany 관계 데이터 분리
        position_ids = validated_data.pop("position_ids", None)
        language_ids = validated_data.pop("language_ids", None)
        skill_tool_ids = validated_data.pop("skill_tool_ids", None)

        # 기본 필드 업데이트
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # 중간 테이블 데이터 업데이트
        if position_ids is not None or language_ids is not None or skill_tool_ids is not None:
            self._update_relations(instance, position_ids, language_ids, skill_tool_ids)

        return instance

    def _create_relations(self, project, position_ids, language_ids, skill_tool_ids):
        # Position 관계 생성
        for position_id in position_ids:
            ProjectPosition.objects.create(project=project, position_id=position_id)

        # Language 관계 생성
        for language_id in language_ids:
            ProjectLanguage.objects.create(project=project, language_id=language_id)

        # SkillTool 관계 생성
        for skill_tool_id in skill_tool_ids:
            ProjectSkillTool.objects.create(project=project, skill_tool_id=skill_tool_id)

    def _update_relations(self, project, position_ids, language_ids, skill_tool_ids):
        # Position 관계 업데이트
        if position_ids is not None:
            ProjectPosition.objects.filter(project=project).delete()
            for position_id in position_ids:
                ProjectPosition.objects.create(project=project, position_id=position_id)

        # Language 관계 업데이트
        if language_ids is not None:
            ProjectLanguage.objects.filter(project=project).delete()
            for language_id in language_ids:
                ProjectLanguage.objects.create(project=project, language_id=language_id)

        # SkillTool 관계 업데이트
        if skill_tool_ids is not None:
            ProjectSkillTool.objects.filter(project=project).delete()
            for skill_tool_id in skill_tool_ids:
                ProjectSkillTool.objects.create(project=project, skill_tool_id=skill_tool_id)


class ApplicationSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source="user.id", read_only=True)
    project_id = serializers.IntegerField(source="project.id", read_only=True)

    class Meta:
        model = Application
        fields = ["id", "user_id", "project_id"]
        read_only_fields = ["id", "user_id", "project_id"]
