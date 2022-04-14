from django.db import models
from accounts.models import User
from rooms.models import Room

# Create your models here.

class Meet(models.Model):
    owner = models.ManyToManyField(User, through='MeetUser')
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    title = models.CharField(max_length=255, blank=True)
    purpose = models.CharField(max_length=255, blank=True)
    spot = models.CharField(max_length=255, blank=True)
    description = models.CharField(max_length=255, blank=True)
    meettime = models.DateTimeField(null=True, blank=True)


class MeetUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE) #user_id : User를 FK로 참조
    meet = models.ForeignKey(Meet, on_delete=models.CASCADE) #meet_id : Meet을 FK로 참조
    created_at = models.DateTimeField(auto_now_add=True) #방 입장 시간

    class Meta: #메타 클래스를 이용하여 테이블명 지정
        db_table = 'meet_users'
        #중복 입장을 방지
        unique_together = (
            ('user', 'meet'),
        )
