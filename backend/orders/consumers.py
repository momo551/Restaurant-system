import json
from channels.generic.websocket import AsyncWebsocketConsumer


class KDSConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Security: reject unauthenticated WebSocket connections
        user = self.scope.get("user")
        if not user or user.is_anonymous:
            await self.close(code=4003)
            return

        self.group_name = "kitchen_display"

        # Join kitchen group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        # Check if the 'token' subprotocol was used
        subprotocol = None
        if 'token' in self.scope.get('subprotocols', []):
            subprotocol = 'token'

        await self.accept(subprotocol=subprotocol)


    async def disconnect(self, close_code):
        # Leave kitchen group (only if group_name was set — i.e., auth passed)
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )

    # Receive message from room group
    async def order_update(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps(event["data"]))
