from base64 import urlsafe_b64decode
import profile
from urllib import request
from rest_framework import serializers
from django.contrib.auth import authenticate
# from django.contrib.auth.models import User

from users.models import *

# 대학교
class UniversitySerializer(serializers.ModelSerializer):
    
    class Meta:
        model = University
        fields = ['id', 'university']


class CollegeSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = College
        fields = ['id', 'college', 'university']


class MajorSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Major
        fields = ['id', 'major', 'college', 'university']

        
# 회원가입
class CreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "password", "university", "college", "major")
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            None, validated_data["username"], validated_data["university"],
            validated_data["college"], validated_data["major"], validated_data["password"],
        )
        return user


# 접속 유지중인지 확인
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User

    def to_representation(self, instance):
        represent = dict()
        represent['id'] = instance.id
        represent['username'] = instance.username
        represent['university'] = instance.university.university
        represent['college'] = instance.college.college
        represent['major'] = instance.major.major
        return represent


# 로그인
class LoginUserSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            return user
        raise serializers.ValidationError(
            "Unable to log in with provided credentials.")


# class ProfileSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Profile
#         fields = ("nickname", "introducing",)


class ProfileDetailSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Profile
        fields = '__all__'
    
    def validate_email(self, value):
        if Profile.objects.filter(school_email=value).exists():
            raise serializers.ValidationError("email is already validated")
        return value

# 문자 전송
class SMSSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = SMSAuthRequest
        fields = ("id", "phone_number", "user",)

# 문자 인증
class SMSActivateSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = SMSAuthRequest
        fields = ("id", "auth_number", "user",)

# 문자 detail
class SMSDetailSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = SMSAuthRequest
        fields = "__all__"

# 이메일 인증
class EmailSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = Profile
        fields = ("id", "school_email", "user",)

#ID 찾기
class FindIDSerializer(serializers.Serializer):
    email = serializers.EmailField()


#ID 찾기 - ID 보여주기
class UsernameSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("username",)


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = '__all__'


# RoomSerializer - "owner"
class RoomWithoutownerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ("id", "created_at", "room_type", "title", "grade_limit", "heads_limit", "gender_limit",
                "meet_purpose", "room_description", "meet_status", "room_open", "common", "mbti", "interest", "college")


class FilterSerializer(serializers.Serializer):
    room_type = serializers.IntegerField(allow_null=True)
    grade = serializers.IntegerField(allow_null=True)
    gender = serializers.CharField(allow_null=True)
    common = serializers.CharField(allow_null=True)


class SearchSerializer(serializers.Serializer):
    keyword = serializers.CharField()


class MeetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meet
        fields = '__all__'


# MeetSerializer - "owner"
class MeetWithoutownerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meet
        fields = ("id", "created_at", "room_type", "title", "grade_limit", "heads_limit", "gender_limit",
                "meet_purpose", "room_description", "meet_status", "room_open", "common", "mbti", "interest", "college")