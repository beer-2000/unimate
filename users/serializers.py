from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

from users.models import Profile


# 회원가입
class CreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "password")
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            validated_data["username"], None, validated_data["password"]
        )
        return user
    

# 접속 유지중인지 확인
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username")


# 로그인
class LoginUserSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Unable to log in with provided credentials.")


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ("nickname", "introducing",)
#        fields = ("id", "user_id", "university_name", "college_name", "major_name", "school_email", "birth_of_date", "gender",
#            "age", "entrance_year", "grade", "nickname", "introducing", "school_auth_status", "registration_date",
#            "mbti_first", "mbti_second", "mbti_third", "mbti_fourth", "withdrawn_status")


class ProfileDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ("id", "user_id", "university_name", "college_name", "major_name", "school_email", "birth_of_date", "gender",
            "age", "entrance_year", "grade", "nickname", "introducing", "school_auth_status", "registration_date",
            "mbti", "withdrawn_status")


