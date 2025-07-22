from rest_framework import permissions

from app.workroom.models import PermissionLevel, Role, Workroom, WorkroomMember


class WorkroomPermission(permissions.BasePermission):
    # 역할(Role) 및 권한(PermissionLevel)에 따라 일정, 이슈, 멤버 접근을 통합 제어하는 권한 클래스

    def has_permission(self, request, view):
        # 인증된 사용자만 허용
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        user = request.user

        # 워크룸 객체 추출
        if isinstance(obj, Workroom):
            workroom = obj
        else:
            workroom = getattr(obj, "workroom", None)

        if not workroom:
            return False

        # 멤버십 조회
        membership = WorkroomMember.objects.filter(workroom=workroom, user=user, status="accepted").first()

        # 멤버십이 없으면 접근 불가
        if not membership:
            return False

        # 권한 레벨 저장
        permission_level = membership.permission

        # 총 관리자(owner)는 모든 작업 가능
        if membership.role == Role.OWNER:
            return True

        # 부관리자(manager) 권한 처리
        if membership.role == Role.MANAGER:
            if request.method in permissions.SAFE_METHODS:
                return True  # 읽기 허용
            if request.method in ["POST", "PUT", "PATCH", "DELETE"]:
                # 멤버 삭제는 허용하지 않음 (특정 모델에서만 삭제 허용)
                # WorkroomMember 삭제는 차단
                if isinstance(obj, WorkroomMember):
                    return False
                # 관리자 관련 객체는 수정 불가
                target_membership = getattr(obj, "membership", None)
                if isinstance(target_membership, WorkroomMember) and target_membership.role == Role.OWNER:
                    return False
                return True

        # 일반 멤버(member) 권한 처리
        if membership.role == Role.MEMBER:
            if request.method in permissions.SAFE_METHODS:
                return True  # 읽기 허용

            # 생성 요청 처리
            if request.method == "POST":
                return permission_level in [
                    PermissionLevel.ADD_EVENT,
                    PermissionLevel.MODIFY_EVENT,
                    PermissionLevel.ADMIN,
                ]

            # 수정/삭제 요청 처리
            if request.method in ["PUT", "PATCH", "DELETE"]:
                owner_user = getattr(obj, "created_by", None) or getattr(obj, "user", None)
                return owner_user == user and permission_level in [PermissionLevel.MODIFY_EVENT, PermissionLevel.ADMIN]

        return False
