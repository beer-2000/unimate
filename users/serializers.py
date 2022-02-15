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
    # university = serializers.ReadOnlyField(source="university.university")
    # universities = UniversitySerializer()
    # college = serializers.ReadOnlyField(source="college.college")
    # major = serializers.ReadOnlyField(source="major.major")
    class Meta:
        model = User
        fields = ("id", "username", "password", "university", "college", "major")
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            validated_data["username"], validated_data["password"],
            validated_data["university"], validated_data["college"], validated_data["major"]
            # **validated_data
        )
        return user


# 접속 유지중인지 확인
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username",)


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


# user, 학교 정보 연결 후 , "school_info", "university", "college", "major" 추가
class ProfileDetailSerializer(serializers.ModelSerializer):
    university = serializers.ReadOnlyField(source="user.university_id", read_only=True)
    college = serializers.ReadOnlyField(source="user.college_id", read_only=True)
    major = serializers.ReadOnlyField(source="user.major_id", read_only=True)
    class Meta:
        model = Profile
        fields = ("id", "user_id", "university", "college", "major", "school_email", "birth_of_date", "gender",
                  "entrance_year", "grade", "nickname", "introducing", "school_auth_status", "registration_date",
                  "mbti", "withdrawn_status")


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = '__all__'
