from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    university_name = models.CharField(max_length=200)
    college_name = models.CharField(max_length=200)
    major_name = models.CharField(max_length=200)
    school_email = models.EmailField(max_length=254)
    birth_of_date = models.DateField()
    gender = models.CharField(max_length=1)
    age = models.IntegerField()
    entrance_year = models.IntegerField()
    grade = models.IntegerField()
    nickname = models.CharField(max_length=200)
    introducing = models.CharField(max_length=255)
    school_auth_status = models.BooleanField(default=False)
    registration_date = models.DateField(auto_now_add=True)
    mbti_first = models.CharField(max_length=1)
    mbti_second = models.CharField(max_length=1)
    mbti_third = models.CharField(max_length=1)
    mbti_fourth = models.CharField(max_length=1)
    #interest_list = 





@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance, user_pk=instance.id)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()