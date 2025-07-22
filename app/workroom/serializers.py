from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import serializers

from app.workroom.models import (
    CalendarEvent,
    Issue,
    PermissionLevel,
    Role,
    Workroom,
    WorkroomDesign,
    WorkroomLanguage,
    WorkroomMember,
    WorkroomPosition,
    WorkroomReview,
    WorkroomStack,
)

# User 모델 가져와 변수에 할당
User = get_user_model()  # Django 프로젝트의 사용자 모델을 User 변수에 할당


class WorkroomPositionSerializer(serializers.ModelSerializer):  # 워크룸-포지션 중간테이블 직렬화
    position_name = serializers.CharField(source="position.name", read_only=True)

    class Meta:
        model = WorkroomPosition  # 직렬화할 모델 지정
        fields = ["id", "workroom", "position", "position_name", "count", "current_count"]  # 포함할 필드 목록 지정


class WorkroomLanguageSerializer(serializers.ModelSerializer):  # 워크룸-언어 중간테이블 직렬화
    language_name = serializers.CharField(source="language.name", read_only=True)

    class Meta:
        model = WorkroomLanguage  # 직렬화할 모델 지정
        fields = ["id", "workroom", "language", "language_name"]  # 포함할 필드 목록 지정


class WorkroomStackSerializer(serializers.ModelSerializer):  # 워크룸-스택 중간테이블 직렬화
    stack_name = serializers.CharField(source="stack.name", read_only=True)

    class Meta:
        model = WorkroomStack  # 직렬화할 모델 지정
        fields = ["id", "workroom", "stack", "stack_name"]  # 포함할 필드 목록 지정


class WorkroomDesignSerializer(serializers.ModelSerializer):  # 워크룸-디자인 중간테이블 직렬화
    design_name = serializers.CharField(source="design.name", read_only=True)

    class Meta:
        model = WorkroomDesign  # 직렬화할 모델 지정
        fields = ["id", "workroom", "design", "design_name"]  # 포함할 필드 목록 지정


class WorkroomMemberRespondSerializer(serializers.ModelSerializer):
    # 상태 필드만 허용
    status = serializers.ChoiceField(
        choices=[("accepted", "승인"), ("rejected", "거절")], help_text="accepted 또는 rejected"
    )

    class Meta:
        model = WorkroomMember
        fields = ["status"]


# 포지션 PK와 최대 인원을 함께 받기 위한 시리얼라이저
class PositionCountInputSerializer(serializers.Serializer):
    position_id = serializers.IntegerField()  # 포지션의 고유 식별자 (Primary Key)
    count = serializers.IntegerField(min_value=1)  # 해당 포지션의 최대 인원 수 (최소 1명 이상)


class WorkroomSerializer(serializers.ModelSerializer):
    # 클라이언트로부터 입력받는 필드들로, 워크룸 생성/수정 시 사용됨
    positions = PositionCountInputSerializer(
        many=True, write_only=True, required=False
    )  # 포지션 및 최대 인원 정보 입력
    language_ids = serializers.ListField(child=serializers.IntegerField(), write_only=True, required=False)  # 언어 ID
    stack_ids = serializers.ListField(child=serializers.IntegerField(), write_only=True, required=False)  # 스택 ID
    design_ids = serializers.ListField(child=serializers.IntegerField(), write_only=True, required=False)  # 디자인 ID

    # 데이터 조회 시 클라이언트에 반환되는 필드들로, 관련 중간 테이블 정보 포함
    positions_ro = WorkroomPositionSerializer(source="workroom_positions", many=True, read_only=True)  # 포지션 정보
    languages_ro = WorkroomLanguageSerializer(source="workroom_languages", many=True, read_only=True)  # 언어 정보
    stacks_ro = WorkroomStackSerializer(source="workroom_stacks", many=True, read_only=True)  # 스택 정보
    designs_ro = WorkroomDesignSerializer(source="workroom_designs", many=True, read_only=True)  # 디자인 정보

    class Meta:
        model = Workroom
        fields = [
            "id",
            "name",
            "introduction",
            "start_date",
            "end_date",
            "description",
            "created_by",
            "positions",
            "language_ids",
            "stack_ids",
            "design_ids",
            "positions_ro",
            "languages_ro",
            "stacks_ro",
            "designs_ro",
        ]
        read_only_fields = ["created_by", "positions_ro", "languages_ro", "stacks_ro", "designs_ro"]

    # 내부 유틸: 다대다(through 모델) bulk 생성
    def _bulk_create(self, workroom, items, through_model, fk_field):
        through_model.objects.filter(workroom=workroom).delete()
        bulk = []
        for itm in items:
            if isinstance(itm, dict):  # 포지션: {"position_id": X, "count": Y}
                bulk.append(
                    through_model(
                        workroom=workroom, position_id=itm["position_id"], count=itm["count"], current_count=0
                    )
                )
            else:  # language_ids, stack_ids, design_ids
                bulk.append(through_model(workroom=workroom, **{fk_field: itm}))
        through_model.objects.bulk_create(bulk)

    # create 워크룸 + 중간테이블 + OWNER 멤버 생성
    def create(self, validated_data):
        # 워크룸 생성 시, 입력받은 포지션, 언어, 스택, 디자인 데이터를 분리 추출
        pos_data = validated_data.pop("positions", [])
        lang_ids = validated_data.pop("language_ids", [])
        stack_ids = validated_data.pop("stack_ids", [])
        design_ids = validated_data.pop("design_ids", [])

        # 워크룸 기본 정보로 워크룸 인스턴스 생성
        workroom = Workroom.objects.create(**validated_data)

        # 중간 테이블에 데이터 일괄 생성
        self._bulk_create(workroom, pos_data, WorkroomPosition, "position_id")
        self._bulk_create(workroom, lang_ids, WorkroomLanguage, "language_id")
        self._bulk_create(workroom, stack_ids, WorkroomStack, "stack_id")
        self._bulk_create(workroom, design_ids, WorkroomDesign, "design_id")

        # 워크룸 생성자 본인을 OWNER로 워크룸 멤버에 등록
        WorkroomMember.objects.create(
            workroom=workroom,
            user=workroom.created_by,
            role=Role.OWNER,
            permission=PermissionLevel.ADMIN,
            status="accepted",
        )

        return workroom

    # update 변경된 중간테이블 정보 반영 (None이면 그대로 유지)
    def update(self, instance, validated_data):
        # 워크룸 수정 시, 입력받은 포지션, 언어, 스택, 디자인 데이터를 분리 추출 (없으면 None)
        pos_data = validated_data.pop("positions", None)
        lang_ids = validated_data.pop("language_ids", None)
        stack_ids = validated_data.pop("stack_ids", None)
        design_ids = validated_data.pop("design_ids", None)

        # 워크룸 기본 필드 값들 업데이트
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # 포지션 정보가 있으면 중간 테이블 업데이트
        if pos_data is not None:
            self._bulk_create(instance, pos_data, WorkroomPosition, "position_id")
        # 언어 정보가 있으면 중간 테이블 업데이트
        if lang_ids is not None:
            self._bulk_create(instance, lang_ids, WorkroomLanguage, "language_id")
        # 스택 정보가 있으면 중간 테이블 업데이트
        if stack_ids is not None:
            self._bulk_create(instance, stack_ids, WorkroomStack, "stack_id")
        # 디자인 정보가 있으면 중간 테이블 업데이트
        if design_ids is not None:
            self._bulk_create(instance, design_ids, WorkroomDesign, "design_id")

        return instance


class WorkroomMemberInviteSerializer(serializers.Serializer):  # 워크룸 멤버 이메일 초대용 시리얼라이저
    email = serializers.EmailField()  # 초대할 사용자 이메일 입력 필드
    role = serializers.ChoiceField(choices=WorkroomMember._meta.get_field("role").choices)  # 부여할 역할 입력 필드
    permission = serializers.ChoiceField(
        choices=WorkroomMember._meta.get_field("permission").choices
    )  # 부여할 권한 입력 필드

    def validate_email(self, value):  # 이메일 유효성 검사 메서드
        try:
            return User.objects.get(email=value)  # 이메일로 User 객체 조회 후 반환
        except User.DoesNotExist:
            raise serializers.ValidationError("해당 이메일의 사용자가 존재하지 않습니다.")  # 사용자 없을 때 예외 발생


class WorkroomMemberSerializer(serializers.ModelSerializer):
    nickname = serializers.CharField(source="user.nickname", read_only=True)  # 사용자 닉네임 출력 필드 추가

    class Meta:
        model = WorkroomMember  # 직렬화할 모델 지정
        fields = ["id", "user", "nickname", "workroom", "role", "permission", "status"]  # nickname 필드 포함
        read_only_fields = ["status"]  # 상태 필드는 읽기 전용으로 설정


class WorkroomReviewSerializer(serializers.ModelSerializer):  # 워크룸 리뷰 모델 직렬화 클래스
    class Meta:
        model = WorkroomReview  # 직렬화할 모델 지정
        fields = ["id", "workroom", "reviewer", "reviewee", "rating", "comment", "created_at"]  # 포함할 필드 지정
        read_only_fields = ["workroom", "created_at"]  # 작성 시각은 읽기 전용으로 설정

    def validate(self, data):
        workroom = self.context.get("workroom")  # context에서 workroom 가져오기
        if not workroom:  # workroom 정보가 없는 경우
            raise serializers.ValidationError("워크룸 정보가 필요합니다.")  # 오류 반환
        if workroom.end_date > timezone.now().date():  # 워크룸 종료일이 아직 안 지난 경우
            raise serializers.ValidationError("워크룸 종료 이후에만 리뷰를 작성할 수 있습니다.")  # 유효성 오류 반환
        return data  # 유효성 검사 통과


class IssueSerializer(serializers.ModelSerializer):  # 이슈 모델 직렬화 클래스
    class Meta:
        model = Issue  # 직렬화할 모델 지정
        fields = ["id", "workroom", "user", "title", "status", "content", "due_date", "created_at"]  # 포함할 필드 지정
        read_only_fields = ["workroom", "created_at"]  # 작성/수정 시각은 읽기 전용으로 설정

    def validate(self, data):
        due = data.get("due_date")
        workroom = self.context.get("workroom")  # context에서 workroom 가져오기
        if due and workroom and due < workroom.start_date:  # 마감일이 워크룸 시작일보다 이른 경우
            raise serializers.ValidationError("마감일은 워크룸 시작일 이후여야 합니다.")  # 유효성 오류 반환
        return data  # 유효성 검사 통과


class CalendarEventSerializer(serializers.ModelSerializer):  # 일정 모델 직렬화 클래스
    created_by = serializers.SerializerMethodField(read_only=True)
    recurrence = serializers.JSONField(default=dict)  # recurrence 필드에 기본값으로 빈 딕셔너리 설정

    class Meta:
        model = CalendarEvent  # 직렬화할 모델 지정
        fields = [
            "id",
            "workroom",
            "title",
            "start",
            "end",
            "all_day",
            "recurrence",
            "color",
            "alert",
            "location",
            "url",
            "memo",
            "created_by",
            "created_at",
        ]
        read_only_fields = ["workroom", "created_by", "created_at"]  # 작성자와 작성일시는 읽기 전용

    def get_created_by(self, obj):
        if obj.created_by:
            return obj.created_by.nickname
        return None

    def validate(self, data):  # 일정 생성/수정 시 검증 메서드
        start = data.get("start")
        end = data.get("end")
        if start and end and start >= end:
            raise serializers.ValidationError("시작 시각은 종료 시각 이전이어야 합니다.")
        return data

    def create(self, validated_data):
        # CalendarEvent 객체를 DB에 저장
        return CalendarEvent.objects.create(**validated_data)


class WorkroomDetailSerializer(serializers.ModelSerializer):  # 전체 워크룸 정보를 통합 직렬화하는 클래스
    issues = serializers.SerializerMethodField()  # 이슈 목록
    events = serializers.SerializerMethodField()  # 일정 목록
    member = serializers.SerializerMethodField()  # 멤버 목록
    positions_ro = WorkroomPositionSerializer(
        source="workroom_positions", many=True, read_only=True
    )  # 포지션 정보 출력
    languages_ro = WorkroomLanguageSerializer(source="workroom_languages", many=True, read_only=True)  # 언어 정보 출력
    stacks_ro = WorkroomStackSerializer(source="workroom_stacks", many=True, read_only=True)  # 스택 정보 출력
    designs_ro = WorkroomDesignSerializer(source="workroom_designs", many=True, read_only=True)  # 디자인 정보 출력

    class Meta:
        model = Workroom  # 기준이 되는 모델은 Workroom
        fields = [
            "id",
            "name",
            "introduction",
            "start_date",
            "end_date",
            "description",
            "created_by",
            "positions_ro",
            "languages_ro",
            "stacks_ro",
            "designs_ro",
            "issues",
            "events",
            "member",  # 연관 정보 추가
        ]
        read_only_fields = fields  # 모든 필드는 읽기 전용

    # related_name으로 연결된 이슈/멤버/일정 쿼리셋 반환 후 시리얼라이즈
    def get_issues(self, obj):
        try:
            issues = obj.issues.all()
            return IssueSerializer(issues, many=True).data
        except Exception as e:
            print(f"[get_issues 오류] {e}")
            return []

    def get_member(self, obj):
        try:
            members = obj.members.filter(status="accepted")
            return WorkroomMemberSerializer(members, many=True).data
        except Exception as e:
            print(f"[get_member 오류] {e}")
            return []

    def get_events(self, obj):
        try:
            events = obj.events.all()
            return CalendarEventSerializer(events, many=True).data
        except Exception as e:
            print(f"[get_events 오류] {e}")
            return []
