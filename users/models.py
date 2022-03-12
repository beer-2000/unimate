from random import randint
import time
import hmac
import base64
import hashlib
import requests
import json
import datetime


from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from model_utils.models import TimeStampedModel
from django.db.models.signals import post_save
from django.dispatch import receiver
from unimate import my_settings

# Create your models here.
# 대학교 정보
class University(models.Model):
    university = models.CharField(max_length=32, blank=True)

    class Meta:
        db_table = 'university'
    
    def __str__(self):   
        return self.university

# 단과대 정보
class College(models.Model):
    college = models.CharField(max_length=32)
    university = models.ForeignKey(University, on_delete=models.CASCADE, db_column="university")
    

    class Meta:
        db_table = 'college'
    
    def __str__(self):   
        return self.college

# # 학과 정보
class Major(models.Model):
    university = models.ForeignKey(University, on_delete=models.CASCADE, related_name="universities", db_column="university")
    college = models.ForeignKey(College, on_delete=models.CASCADE, related_name="colleges", db_column="college")
    major = models.CharField(max_length=32)

    class Meta:
        db_table = 'major'
    
    def __str__(self):   
        return self.major

### null=True 와 blank=True 의 차이점
# null은 null로 저장, blank는 입력 폼에서 빈 칸으로 입력하고 DB에는 '' 으로 저장됨.
# 따라서, CharField의 경우 null=True 만으로는 빈칸 입력이 불가능하여 blank=True로 처리함.
# IntegerField의 경우 null=True로 처리했고, Profile 생성 시  None 이 저장됨.

# user 커스터마이징
class UserManager(BaseUserManager):
    def create_user(self, email, username, university, college, major, password=None):
        if not username:
            raise ValueError('User must have an username')
        
        user = self.model(
            username = self.model.normalize_username(username),
            email = self.normalize_email(email),
            university = university,
            college = college,
            major = major,
        )

        user.set_password(password)
        user.save(using=self._db)
       
        return user
    
    def create_superuser(self, username, email, password):
            user = self.create_user(
                username = self.model.normalize_username(username),
                email = self.normalize_email(email),
                university = University.objects.get(university='univ1'),
                college = College.objects.get(college='col1'),
                major = Major.objects.get(major='major1'),
                password=password,
            )
            user.is_superuser = True
            user.is_staff = True
            user.save(using=self._db)
            return user

class User(AbstractUser):
    username = models.CharField(max_length=30, unique=True)
    email = models.EmailField(max_length=254, blank=True)
    university = models.ForeignKey(University, on_delete=models.CASCADE)
    college = models.ForeignKey(College, on_delete=models.CASCADE)
    major = models.ForeignKey(Major, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)

    objects = UserManager()
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.username


# Profile : User와 one-to-one 관계로, 프로필 정보들을 저장
class Profile(models.Model):

    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
    )
    SCHOOL_AUTH_CHOICES = (
        ('Y', 'School authentication complete'),
        ('N', 'School authentication necessary'),
    )
    WITHDRAWN_CHOICES = (
        ('general', 'General Member'),
        ('withdrawal', 'Withdrawal member'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=80, blank=True, null=True)
    school_email = models.EmailField(max_length=254, blank=True)
    birth_of_date = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=80, choices=GENDER_CHOICES) #choice 필요
    entrance_year = models.IntegerField(blank=True, null=True)
    grade = models.IntegerField(null=True)
    nickname = models.CharField(max_length=200)
    introducing = models.CharField(max_length=255, blank=True)
    school_auth_status = models.CharField(max_length=80, choices=SCHOOL_AUTH_CHOICES, default = 'N') #choice 필요
    registration_date = models.DateField(auto_now_add=True)
    mbti = models.CharField(max_length=255, blank=True)
    interest_list = models.CharField(max_length=255, blank=True)
    withdrawn_status = models.CharField(max_length=80, choices=WITHDRAWN_CHOICES, default = 'general') #choice 필요

    class Meta: #메타 클래스를 이용하여 테이블명 지정
        db_table = 'profile'


class Withdraw(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    withdraw_reason = models.TextField(blank=True, null=True)


# User의 Post가 save되면 그것을 참조하는 Profile 객체를 만들어 저장하라는 명령
# * 이해 필요
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    print(f"sender: {sender}, instance: {instance}, created: {created}")
    if created:
        Profile.objects.create(user=instance, user_id=instance.id)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

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


### Room : 방 정보를 저장하는 테이블로, Profile과 many-to-many관계, 중간테이블로 RoomUser 생성
class Room(models.Model):

    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('N', 'Not specified'),
    )
    MEET_CHOICES = (
        ('Y', 'Meeting exist'),
        ('N', 'Meeting not exist'),
    )
    OPEN_CHOICES = (
        ('open', 'Open'),
        ('closed', 'Closed'),
    )
    
    owner = models.ManyToManyField(User, through='RoomUser') #방의 구성원을 저장, * 이해 필요(우측 형태로 저장되어있는데, 테이블 조회시 보여지지는 않고, 매개 역할을 하는 듯) --> <django.db.models.fields.related_descriptors.create_forward_many_to_many_manager.<locals>.ManyRelatedManager object at 0x7fad8950fbb0> 형태로 저장
    university = models.CharField(max_length=32, blank=True, default='') #방 만드는 user의 university 가져오기
    created_at = models.DateTimeField(auto_now_add=True) #방 생성 일시
    room_type = models.IntegerField() #방 성격 / 채팅방: 0, 약속방: 1 로 지정 / required
    title = models.CharField(max_length=64) #방 제목: 32자 이내
    grade_limit = models.IntegerField(null=True, blank=True) #학년 제한 / null(전체학년), 1~5(각 학년만)
    heads_limit = models.IntegerField() #최대 입장 인원수 제한 / 3~15 / required
    gender_limit = models.CharField(max_length=80, choices=GENDER_CHOICES, default='N') #성별 입장 제한 / null(상관없음), 0(여자만), 1(남자만)
    meet_purpose = models.CharField(max_length=255, blank=True) #약속 목적 / 약속이 정해진 방에만 기입, 나머지는 ''
    room_description = models.CharField(max_length=255, blank=True) #방 설명: 100자 이내 / 방을 자유자재로 소개, 설명
    meet_status = models.CharField(max_length=80, choices=MEET_CHOICES, default='N') #약속 상태 / Y(약속이 정해진 방), N(약속이 정해지지 않은 방)
    room_open = models.CharField(max_length=80, choices=OPEN_CHOICES, default='open') #방문 상태 / Y(열림, 입장 가능), N(닫힘, 입장 불가능)
    common = models.CharField(max_length=80, blank=True) #공통점: 방의 공통점은 0개 또는 1개로, 공통점이 있다면 그 종류를 지정 / ''(공통점 없음), mbti, interest, college
    mbti = models.CharField(max_length=255, blank=True) #common이 mbti인 경우만
    interest = models.IntegerField(null=True, blank=True) #common이 interest인 경우만, 방 만드는 사람의 관심사 중 1개 지정
    college = models.CharField(max_length=32, blank=True) #common이 interest인 경우만, 방 만드는 사람의 단과대 정보

    class Meta: #메타 클래스를 이용하여 테이블명 지정
        db_table = 'rooms'


class RoomUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE) #user_id : User를 FK로 참조
    room = models.ForeignKey(Room, on_delete=models.CASCADE) #room_id : Room을 FK로 참조
    created_at = models.DateTimeField(auto_now_add=True) #방 입장 시간

    class Meta: #메타 클래스를 이용하여 테이블명 지정
        db_table = 'room_users'
        #중복 입장을 방지
        unique_together = (
            ('user', 'room'),
        )

### many-to-many 저장하는 방법(python)
# room1 = Room.objects.get(pk=1) --> room1 객체에 Room의 행 1개를 저장
# person1 = User.objects.get(pk=1) --> person1 객체에 User의 행 1개를 저장
# room1.owner.add(person1) --> room1과 person1ㅇ이 연결됨
# person1.room_set.add(room1) --> person1과 room1이 연결됨 (owner는 Room에서 정의했기 때문에, person1은 room_set을 사용해야 함)


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
