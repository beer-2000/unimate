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

        # Send message to room group (chat_message에 event로 들어감)
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
        sender_id = event['user_id']
        receiver_id = self.scope['user'].id 
        sender = self.scope['user'].username
        # url 확인
        # room_title = self.scope['path'].split('_')[0]
        room_title = self.scope['path'].split('_')[0].split('/')[3]

        # 보낸 사람(event 기준)과 현재 사용자(토큰 -> 미들웨어 -> scope 기준)가 같다면 메세지 저장
        if sender_id == receiver_id :
            await self.post_message(sender_id=sender_id, room_title=room_title, message=message)
        await self.send(text_data=json.dumps({
            'message': message,
            'sender': sender_id,
            'receiver': receiver_id
        }))


    @database_sync_to_async
    def post_message(self, sender_id ,room_title, message):
        sender = User.objects.filter(id = sender_id)[0]
        room = Room.objects.filter(title = room_title)[0]
        MessageModel.objects.create(user = sender, room = room, body = message)
