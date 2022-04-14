from django.db import models
from model_utils.models import TimeStampedModel
from accounts.models import User

from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.

# 문자 인증
class SMSAuthRequest(TimeStampedModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(verbose_name='휴대폰 번호', max_length=50)
    auth_number = models.IntegerField(verbose_name='인증 번호', null=True)

    class Meta:
        db_table = 'sms'

@receiver(post_save, sender=User)
def create_user_sms(sender, instance, created, **kwargs):
    print(f"sender: {sender}, instance: {instance}, created: {created}")
    if created:
        SMSAuthRequest.objects.create(user=instance, user_id=instance.id)

@receiver(post_save, sender=User)
def save_user_sms(sender, instance, **kwargs):
    instance.smsauthrequest.save()

# 학교 이메일 인증
class SchoolEmail(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    school_email = models.EmailField(max_length=254, blank=True)

    class Meta:
        db_table = 'schoolemail'

@receiver(post_save, sender=User)
def create_user_eamil(sender, instance, created, **kwargs):
    print(f"sender: {sender}, instance: {instance}, created: {created}")
    if created:
        SchoolEmail.objects.create(user=instance, user_id=instance.id)

@receiver(post_save, sender=User)
def save_user_email(sender, instance, **kwargs):
    instance.schoolemail.save()

