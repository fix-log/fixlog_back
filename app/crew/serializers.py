from rest_framework import serializers

from app.crew.models import Project, ProjectLanguage, ProjectPosition, ProjectSkillTool, ProjectDesign, ProjectCoopTool, Application
from app.util.models import Language, Position, Stack, Design, CoopTool


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


class ProjectDesignSerializer(serializers.ModelSerializer):
    design_name = serializers.CharField(source="design.name", read_only=True)

    class Meta:
        model = ProjectDesign
        fields = ["design", "design_name"]


class ProjectCoopToolSerializer(serializers.ModelSerializer):
    coop_tool_name = serializers.CharField(source="coop_tool.name", read_only=True)

    class Meta:
        model = ProjectCoopTool
        fields = ["coop_tool", "coop_tool_name"]


class ProjectSerializer(serializers.ModelSerializer):
    # 유저 닉네임 추가
    user_nickname = serializers.CharField(source="user.nickname", read_only=True)
    # 유저 프로필 이미지 추가
    user_profile_image = serializers.CharField(source="user.profile_image", read_only=True)

    # 중간 테이블 정보를 포함한 필드들
    project_positions = ProjectPositionSerializer(source="projectposition_set", many=True, read_only=True)
    project_languages = ProjectLanguageSerializer(source="projectlanguage_set", many=True, read_only=True)
    project_skill_tools = ProjectSkillToolSerializer(source="projectskilltool_set", many=True, read_only=True)
    project_designs = ProjectDesignSerializer(source="projectdesign_set", many=True, read_only=True)
    project_coop_tools = ProjectCoopToolSerializer(source="projectcooptool_set", many=True, read_only=True)

    # 단순 ID 리스트 (생성/수정 시 사용)
    position_ids = serializers.ListField(child=serializers.IntegerField(), write_only=True, required=False)
    language_ids = serializers.ListField(child=serializers.IntegerField(), write_only=True, required=False)
    skill_tool_ids = serializers.ListField(child=serializers.IntegerField(), write_only=True, required=False)
    design_ids = serializers.ListField(child=serializers.IntegerField(), write_only=True, required=False)
    coop_tool_ids = serializers.ListField(child=serializers.IntegerField(), write_only=True, required=False)

    class Meta:
        model = Project
        fields = [
            "id",
            "user",
            "user_nickname",
            "user_profile_image",
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
            "project_designs",
            "project_coop_tools",
            "position_ids",
            "language_ids",
            "skill_tool_ids",
            "design_ids",
            "coop_tool_ids",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def create(self, validated_data):
        # ManyToMany 관계 데이터 분리
        position_ids = validated_data.pop("position_ids", [])
        language_ids = validated_data.pop("language_ids", [])
        skill_tool_ids = validated_data.pop("skill_tool_ids", [])
        design_ids = validated_data.pop("design_ids", [])
        coop_tool_ids = validated_data.pop("coop_tool_ids", [])

        # 프로젝트 생성
        validated_data["user"] = self.context["request"].user
        project = Project.objects.create(**validated_data)

        # 중간 테이블 데이터 생성
        self._create_relations(project, position_ids, language_ids, skill_tool_ids, design_ids, coop_tool_ids)

        return project

    def update(self, instance, validated_data):
        # ManyToMany 관계 데이터 분리
        position_ids = validated_data.pop("position_ids", None)
        language_ids = validated_data.pop("language_ids", None)
        skill_tool_ids = validated_data.pop("skill_tool_ids", None)
        design_ids = validated_data.pop("design_ids", None)
        coop_tool_ids = validated_data.pop("coop_tool_ids", None)

        # 기본 필드 업데이트
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # 중간 테이블 데이터 업데이트
        if any([position_ids is not None, language_ids is not None, skill_tool_ids is not None, design_ids is not None, coop_tool_ids is not None]):
            self._update_relations(instance, position_ids, language_ids, skill_tool_ids, design_ids, coop_tool_ids)

        return instance

    def _create_relations(self, project, position_ids, language_ids, skill_tool_ids, design_ids, coop_tool_ids):
        # Position 관계 생성
        for position_id in position_ids:
            ProjectPosition.objects.create(project=project, position_id=position_id)

        # Language 관계 생성
        for language_id in language_ids:
            ProjectLanguage.objects.create(project=project, language_id=language_id)

        # SkillTool 관계 생성
        for skill_tool_id in skill_tool_ids:
            ProjectSkillTool.objects.create(project=project, skill_tool_id=skill_tool_id)

        # Design 관계 생성
        for design_id in design_ids:
            ProjectDesign.objects.create(project=project, design_id=design_id)

        # CoopTool 관계 생성
        for coop_tool_id in coop_tool_ids:
            ProjectCoopTool.objects.create(project=project, coop_tool_id=coop_tool_id)

    def _update_relations(self, project, position_ids, language_ids, skill_tool_ids, design_ids, coop_tool_ids):
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

        # Design 관계 업데이트
        if design_ids is not None:
            ProjectDesign.objects.filter(project=project).delete()
            for design_id in design_ids:
                ProjectDesign.objects.create(project=project, design_id=design_id)

        # CoopTool 관계 업데이트
        if coop_tool_ids is not None:
            ProjectCoopTool.objects.filter(project=project).delete()
            for coop_tool_id in coop_tool_ids:
                ProjectCoopTool.objects.create(project=project, coop_tool_id=coop_tool_id)


class ApplicationSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source="user.id", read_only=True)
    project_id = serializers.IntegerField(source="project.id", read_only=True)

    class Meta:
        model = Application
        fields = ["id", "user_id", "project_id"]
        read_only_fields = ["id", "user_id", "project_id"]
