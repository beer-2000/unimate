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
    university_name = models.CharField(max_length=200)
    college_name = models.CharField(max_length=200)
    major_name = models.CharField(max_length=200)
    school_email = models.EmailField(max_length=254)
    birth_of_date = models.DateField(null=True)
    gender = models.CharField(max_length=1)
    age = models.IntegerField(null=True)
    entrance_year = models.IntegerField(null=True)
    grade = models.IntegerField(null=True)
    nickname = models.CharField(max_length=200)
    introducing = models.CharField(max_length=255, blank=True)
    school_auth_status = models.BooleanField(default=False)
    registration_date = models.DateField(auto_now_add=True)
    mbti_first = models.CharField(max_length=1, blank=True)
    mbti_second = models.CharField(max_length=1, blank=True)
    mbti_third = models.CharField(max_length=1, blank=True)
    mbti_fourth = models.CharField(max_length=1, blank=True)
    #interest_list = 
    withdrawn_status = models.CharField(max_length=1, default="N")





@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    print(f"sender: {sender}, instance: {instance}, created: {created}")
    if created:
        Profile.objects.create(user=instance, user_id=instance.id)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()