# 읽기, 댓글 등 권한 체크 유틸

PUBLIC = "public"
FOLLOWER = "follower"
MENTION = "mention"


def can_view_fixred(user, fixred):
    if fixred.user_id == user.id:
        return True
    if fixred.read_permission == PUBLIC:
        return True
    if fixred.read_permission == FOLLOWER:
        return fixred.user.followers.filter(follower=user).exists()
    if fixred.read_permission == MENTION:
        return fixred.mentioned_users.filter(id=user.id).exists()
    return False
