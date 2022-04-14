from django.db import models
from accounts.models import User

# Create your models here.

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
# room1.owner.add(person1) --> room1과 person1이 연결됨
# person1.room_set.add(room1) --> person1과 room1이 연결됨 (owner는 Room에서 정의했기 때문에, person1은 room_set을 사용해야 함)

