from tkinter import CASCADE
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.


### null=True 와 blank=True 의 차이점
# null은 null로 저장, blank는 입력 폼에서 빈 칸으로 입력하고 DB에는 '' 으로 저장됨.
# 따라서, CharField의 경우 null=True 만으로는 빈칸 입력이 불가능하여 blank=True로 처리함.
# IntegerField의 경우 null=True로 처리했고, Profile 생성 시  None 이 저장됨.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    university_name = models.CharField(max_length=32)
    college_name = models.CharField(max_length=32)
    major_name = models.CharField(max_length=32)
    school_email = models.EmailField(max_length=254)
    birth_of_date = models.DateField(null=True)
    gender = models.IntegerField(null=True)
    age = models.IntegerField(null=True)
    entrance_year = models.IntegerField(null=True)
    grade = models.IntegerField(null=True)
    nickname = models.CharField(max_length=200)
    introducing = models.CharField(max_length=255, blank=True)
    school_auth_status = models.BooleanField(default=False)
    registration_date = models.DateField(auto_now_add=True)
    mbti = models.CharField(max_length=4, blank=True)
    interest_list = models.TextField(blank=True)
    withdrawn_status = models.CharField(max_length=1, default="N")

    class Meta: #메타 클래스를 이용하여 테이블명 지정
        db_table = 'profile'


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    print(f"sender: {sender}, instance: {instance}, created: {created}")
    if created:
        Profile.objects.create(user=instance, user_id=instance.id)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


# class Room(models.Model):
#     # user = models.ForeignKey(User, on_delete = models.CASCADE, related_name = 'user')
#     room_type = models.IntegerField(max_length=1)
#     title = models.CharField(max_length=64) #32자 이내
#     grade_limit = models.IntegerField(max_length=1, null=True)
#     heads_limit = models.IntegerField(max_length=1, null=True)
#     gender_limit = models.IntegerField(max_length=1, null=True)
#     meet_purpose = models.CharField(max_length=255, blank=True)
#     room_description = models.CharField(max_length=255, blank=True)
#     meet_status = models.CharField(max_length=1, blank=True)
#     room_open = models.CharField(max_length=1, default="Y")
#     common = models.TextField(blank=True)
#     mbti = models.CharField(max_length=4, blank=True)
#     interest = models.TextField(blank=True)
    
#     users = models.ManyToManyField(User, related_name='users')

#     class Meta:
#         db_table = 'room'

# class UserRoom(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     room = models.ForeignKey(Room, on_delete=models.CASCADE)

#     class Meta:
#         db_table = 'user_room'


# class Meet(models.Model):
#     room_id = models.ForeignKey("Room", on_delete=CASCADE)

#     class Meta:
#         db_table = 'meet'