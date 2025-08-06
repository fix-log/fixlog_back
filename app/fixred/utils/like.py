from django.shortcuts import get_object_or_404

from app.fixred.models import Fixred, FixredLike
from app.notifications.utils import send_notification


# Fixred 좋아요 토글 함수
def toggle_fixred_like(user, fixred_id):

    fixred = get_object_or_404(Fixred, id=fixred_id)

    like, created = FixredLike.objects.get_or_create(user=user, fixred=fixred)

    if not created:
        like.delete()
        fixred.refresh_from_db(fields=["like_count"])
        return {"fixred": fixred, "liked": False}

    if fixred.user != user:
        send_notification(user=fixred.user, sender=user, type_="fixred", event="like", target_id=fixred.id)
    fixred.refresh_from_db(fields=["like_count"])
    return {"fixred": fixred, "liked": True}
