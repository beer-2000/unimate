from django.db import models
from django.db.models import Q
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db.models.signals import post_save
from django.dispatch import receiver


# Create your models here.
#  대학교 정보
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

# 관심사 정보
class Interest(models.Model):
    interest = models.CharField(max_length=16, blank=True)

    class Meta:
        db_table = 'interest'
    
    def __str__(self):   
        return self.interest
### null=True 와 blank=True 의 차이점
# null은 null로 저장, blank는 입력 폼에서 빈 칸으로 입력하고 DB에는 '' 으로 저장됨.
# 따라서, CharField의 경우 null=True 만으로는 빈칸 입력이 불가능하여 blank=True로 처리함.
# IntegerField의 경우 null=True로 처리했고, Profile 생성 시  None 이 저장됨.

# user 커스터마이징
class UserManager(BaseUserManager):
    def create_user(self, username, email, university, college, major, use_agree, information_agree, password=None):
        if not username:
            raise ValueError('User must have an username')
        
        user = self.model(
            username = self.model.normalize_username(username),
            email = self.normalize_email(email),
            university = university,
            college = college,
            major = major,
            use_agree = use_agree,
            information_agree = information_agree,
        )

        user.set_password(password)
        user.save(using=self._db)
       
        return user

    
    def create_superuser(self, username, email, password):
            user = self.create_user(
                username = self.model.normalize_username(username),
                email = self.normalize_email(email),
                university = University.objects.get(university='홍익대학교'),
                college = College.objects.get(
                    Q(university=1) &
                    Q(college='공과대학')
                ),
                major = Major.objects.get(
                    Q(university=1)&
                    Q(college=1) &
                    Q(major='컴퓨터공학부')
                ),
                password=password,
                use_agree = True,
                information_agree = True,
            )
            user.is_superuser = True
            user.is_staff = True
            user.save(using=self._db)
            return user

class User(AbstractUser):
    username = models.CharField(max_length=30, unique=True)
    email = models.EmailField(max_length=254, unique=True)
    university = models.ForeignKey(University, on_delete=models.CASCADE)
    college = models.ForeignKey(College, on_delete=models.CASCADE)
    major = models.ForeignKey(Major, on_delete=models.CASCADE)
    use_agree = models.BooleanField(default=False)
    information_agree = models.BooleanField(default=False)
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
    AUTH_STATUS = (
        ('Registered', 'Registered - Should authenticate phone'),
        ('Phone complete', 'Phone complete -  Should enter profile'),        
        ('Profile complete', 'Profile complete - Should authenticate school'),
        ('School complete', 'School complete - School authentication complete'),
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
    name = models.CharField(max_length=200, blank=True)
    nickname = models.CharField(max_length=200, blank=True)
    introducing = models.CharField(max_length=255, blank=True)
    auth_status = models.CharField(max_length=80, choices=AUTH_STATUS, default = 'Registered') #choice 필요
    registration_date = models.DateField(auto_now_add=True)
    mbti = models.CharField(max_length=255, blank=True)
    # interest_list = models.CharField(max_length=255, blank=True, choices=INTEREST_CHOICES)
    interest_list = models.ForeignKey(Interest, on_delete=models.CASCADE, null=True, blank=True)
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
