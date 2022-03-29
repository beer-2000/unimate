from channels.generic.websocket import AsyncWebsocketConsumer
import json

#추가
from channels.db import database_sync_to_async
from users.models import User
from chat.models import *


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']
        sender = self.scope['user'].username
        receiver = self.scope['path'].split('_')[0]

        # Send message to WebSocket
        await self.post_message(sender=sender, receiver=receiver, message=message)
        await self.send(text_data=json.dumps({
            'message': message
        }))
        print()

    @database_sync_to_async
    def post_message(self, sender ,receiver, message):
        sender = User.objects.filter(username = sender)[0]
        receiver = User.objects.filter(username = sender)[0]
        print(f"sender: {sender}")
        print(f"receiver: {receiver}")
        MessageModel.objects.create(user = sender , recipient = receiver , body = message)
