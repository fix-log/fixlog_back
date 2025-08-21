# app/fixletter/consumers_debug.py
from channels.generic.websocket import AsyncJsonWebsocketConsumer
class EchoConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        await self.accept()
        await self.send_json({"hello": "ok"})
    async def receive_json(self, content):
        await self.send_json({"echo": content})