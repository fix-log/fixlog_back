import json
import traceback

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.db import transaction
from django.db.models import Q

from .models import Fixletter, FixletterBlock, Message


class FixletterConsumer(AsyncJsonWebsocketConsumer):
    async def encode_json(cls, content):
        # 한글 그대로(UTF-8) 내려보내기
        return json.dumps(content, ensure_ascii=False)

    async def connect(self):
        try:
            print("WS connect:", self.scope.get("path"), self.scope.get("user"))
            self.fixletter_id = int(self.scope["url_route"]["kwargs"]["fixletter_id"])
            self.group_name = f"fixletter_{self.fixletter_id}"
            user = self.scope["user"]

            # 1) 인증 체크
            if not (user and user.is_authenticated):
                await self.close(code=4401)  # Unauthorized
                return

            # 2) 참여자 권한 체크
            if not await self._is_participant(user.id, self.fixletter_id):
                await self.close(code=4403)  # Forbidden
                return

            # 3) 차단 체크(둘 중 누가 누구를 막아도 입장 불가)
            if await self._is_blocked(self.fixletter_id):
                await self.close(code=4403)  # Forbidden
                return

            # 4) 그룹 조인 + 연결 승인
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()

            # 방입장 동시에 읽음처리하기
            changed = await self._mark_all_read(user.id, self.fixletter_id)
            if changed:
                await self.channel_layer.group_send(
                    self.group_name,
                    {
                        "type": "message_read_broadcast",
                        "payload": {"fixletter_id": self.fixletter_id, "reader_id": user.id},
                    },
                )
        except Exception:
            traceback.print_exc()
            await self.close(code=1011)

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive_json(self, content, **kwargs):
        typ = content.get("type")
        uid = self.scope["user"].id

        if typ == "message.send":
            text = (content.get("text") or "").strip()
            if not text:
                await self.send_json({"type": "error", "error": "empty"})
                return

            # 보낼 때도 차단 재확인
            if await self._is_blocked(self.fixletter_id):
                await self.send_json({"type": "error", "error": "blocked"})
                return

            payload = await self._create_message(uid, self.fixletter_id, text)

            # 방 전체에 브로드캐스트
            await self.channel_layer.group_send(
                self.group_name,
                {"type": "message_broadcast", "payload": payload},
            )
        # 모두 읽음 처리
        elif typ == "message.read_all":
            changed = await self._mark_all_read(uid, self.fixletter_id)
            if changed:
                await self.channel_layer.group_send(
                    self.group_name,
                    {
                        "type": "message_read_broadcast",
                        "payload": {"fixletter_id": self.fixletter_id, "reader_id": uid},
                    },
                )

        else:
            await self.send_json({"type": "error", "error": "unknown_type"})

    # === 그룹 이벤트 핸들러 ===
    async def message_broadcast(self, event):
        await self.send_json(event["payload"])

    async def message_read_broadcast(self, event):
        await self.send_json({"type": "message.read", **event["payload"]})

    # === DB helpers ===
    @database_sync_to_async
    # 유저가 해당 픽레터의 참여자인지 체크
    def _is_participant(self, user_id, fid):
        return Fixletter.objects.filter(id=fid).filter(Q(from_user_id=user_id) | Q(to_user_id=user_id)).exists()

    @database_sync_to_async
    # 양방향 차단 여부 확인
    def _is_blocked(self, fid):
        f = Fixletter.objects.select_related("from_user", "to_user").get(id=fid)
        a, b = f.from_user_id, f.to_user_id
        return FixletterBlock.objects.filter(
            Q(blocker_id=a, blocked_id=b, is_active=True) | Q(blocker_id=b, blocked_id=a, is_active=True)
        ).exists()

    @database_sync_to_async
    def _create_message(self, sender_id, fid, text):
        with transaction.atomic():
            msg = Message.objects.create(
                fixletter_id=fid,
                send_user_id=sender_id,
                content=text,
                is_read=False,
            )
            # 최신 메시지/시간 갱신
            Fixletter.objects.filter(id=fid).update(last_message=msg, last_sent_at=msg.sent_at)
        return {
            "type": "message",
            "id": msg.id,
            "fixletter_id": fid,
            "sender_id": sender_id,
            "content": msg.content,
            "sent_at": msg.sent_at.isoformat(),
            "is_read": msg.is_read,
        }

    @database_sync_to_async
    # 받은 메세지 중 미읽음메세지만 일괄읽음 처리
    def _mark_all_read(self, reader_id, fid):
        qs = Message.objects.filter(fixletter_id=fid, is_read=False).exclude(send_user_id=reader_id)
        return qs.update(is_read=True)
