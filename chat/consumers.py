from email import message
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
import json
from rooms.models import Room as ChatRoom
from chat.models import Chat

#추가
# from channels.db import database_sync_to_async
# from accounts.models import User
# from chat.models import *


# class ChatConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         self.room_name = self.scope['url_route']['kwargs']['room_name']
#         self.room_group_name = 'chat_%s' % self.room_name

#         # Join room group
#         await self.channel_layer.group_add(
#             self.room_group_name,
#             self.channel_name
#         )
#         await self.accept()

#     async def disconnect(self, close_code):
#         # Leave room group
#         await self.channel_layer.group_discard(
#             self.room_group_name,
#             self.channel_name
#         )

#     # Receive message from WebSocket
#     async def receive(self, text_data):
#         text_data_json = json.loads(text_data)
#         message = text_data_json['message']

#         # Send message to room group
#         await self.channel_layer.group_send(
#             self.room_group_name,
#             {
#                 'type': 'chat_message',
#                 'message': message
#             }
#         )

#     # Receive message from room group
#     async def chat_message(self, event):
#         message = event['message']
#         sender = self.scope['user'].username
#         receiver = self.scope['path'].split('_')[0]

#         # Send message to WebSocket
#         await self.post_message(sender=sender, receiver=receiver, message=message)
#         await self.send(text_data=json.dumps({
#             'message': message
#         }))
#         print()

#     @database_sync_to_async
#     def post_message(self, sender ,receiver, message):
#         sender = User.objects.filter(username = sender)[0]
#         receiver = User.objects.filter(username = sender)[0]
#         print(f"sender: {sender}")
#         print(f"receiver: {receiver}")
#         MessageModel.objects.create(user = sender , recipient = receiver , body = message)

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        self.user_id = self.scope['user'].id

        # Find room object
        room = await database_sync_to_async(ChatRoom.objects.get)(name=self.room_name)

        # Create new chat object
        chat = Chat(
            content=message,
            user=self.scope['user'],
            room=room
        )

        await database_sync_to_async(chat.save)()

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'user_id' : self.user_id
            })

    async def chat_message(self, event):
        message = event['message']
        user_id = event['user_id']

        await self.send(text_data=json.dumps({
            'message': message,
            'user_id' : user_id
        }))
