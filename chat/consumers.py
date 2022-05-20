import json
from channels.generic.websocket import AsyncWebsocketConsumer

from channels.db import database_sync_to_async
from accounts.models import User
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
        self.user_id = self.scope['user'].id
        print(f"receiver : {self.user_id}")

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'user_id': self.user_id,
            }
        )

    async def chat_message(self, event):
        message = event['message']
        print(f"0.event: {event}")
        sender = self.scope['user'].username
        print(f"1.sender: {sender}")
        receiver = self.scope['path'].split('_')[0]
        print(f"2.receiver: {receiver}")
        receiver = self.scope['path'].split('_')[0].split('/')[3]
        print(f"3.receiver: {receiver}")

        # Send message to WebSocket
        await self.post_message(sender=sender, receiver=receiver, message=message)
        await self.send(text_data=json.dumps({
            'message': message
        }))

    @database_sync_to_async
    def post_message(self, sender ,receiver, message):
        print(sender)
        print(receiver)
        sender = User.objects.filter(username = sender)[0]
        receiver = Room.objects.filter(title = receiver)[0]
        print(f"sender: {sender}")
        print(f"receiver: {receiver}")
        MessageModel.objects.create(user = sender, room = receiver, body = message)
