from django.db import models
from django.db.models import Model, TextField, DateTimeField, ForeignKey, CASCADE
from accounts.models import User
from rooms.models import Room

# Create your models here.
class MessageModel(Model):
    """
    This class represents a chat message. It has a owner (user), timestamp and
    the message body.
    """
    user = ForeignKey(User, on_delete=CASCADE, verbose_name='user',
                      related_name='from_user', db_index=True)
    room = ForeignKey(Room, on_delete=CASCADE, verbose_name='room',
                           related_name='to_room', db_index=True)
    timestamp = DateTimeField('timestamp', auto_now_add=True, editable=False,
                              db_index=True)
    body = TextField('body')
