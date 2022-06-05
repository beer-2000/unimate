from rest_framework import serializers
from accounts.models import *

from django.contrib.auth import authenticate, password_validation
from django.utils.translation import gettext_lazy as _



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


class MajorDetailSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    major = serializers.CharField()
    college = serializers.CharField()
    university = serializers.CharField()

        
# 회원가입
# class CreateUserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ("id", "username", "password", "email", "university", "college", "major", "agree")
#         extra_kwargs = {"password": {"write_only": True}}

#     def create(self, validated_data):
#         user = User.objects.create_user(
#             None, validated_data["username"], validated_data["email"], validated_data["university"],
#             validated_data["college"], validated_data["major"], validated_data["password"],
#         )
#         return user


# 회원가입(수정)
class CreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "password", "email", "university", "college", "major", "use_agree", "information_agree",)
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            validated_data["username"], validated_data["email"], validated_data["university"],
            validated_data["college"], validated_data["major"], validated_data["use_agree"],
            validated_data["information_agree"], validated_data["password"],
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
        represent['email'] = instance.email
        represent['university'] = instance.university.university
        represent['college'] = instance.college.college
        represent['major'] = instance.major.major
        represent['use_agree'] = instance.use_agree
        represent['information_agree'] = instance.information_agree
        return represent


# ID, nickname 중복 확인용
class IDSerializer(serializers.Serializer):
    username = serializers.CharField()


class NicknameSerializer(serializers.Serializer):
    nickname = serializers.CharField()

# 비밀번호 유효성 체크
class PWSerializer(serializers.Serializer):
    pw1 = serializers.CharField()
    pw2 = serializers.CharField()


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

class InterestSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Interest
        fields = ['id', 'interest']

# class ProfileRegisterSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Profile
#         fields = ("nickname", "mbti", "interest_list", "name", "birth_of_date", "introducing", "gender", "grade", "entrance_year",)


class ProfileRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ("nickname", "mbti", "interest_list", "name", "birth_of_date", "introducing", "gender", "grade", "entrance_year", "auth_status",)


# class ProfileModifySerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Profile
#         fields = ("nickname", "mbti", "interest_list", "name", "birth_of_data", "introducing", "gender",)


class WithdrawSerializer(serializers.ModelSerializer):
    class Meta:
        model = Withdraw
        fields = ("withdraw_reason",)


#ID 찾기
class FindIDSerializer(serializers.Serializer):
    email = serializers.EmailField()


#ID 찾기 - ID 보여주기
class UsernameSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("username",)


#PW 변경
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(max_length=128, write_only=True, required=True)
    new_password = serializers.CharField(max_length=128, write_only=True, required=True)
    new_password2 = serializers.CharField(max_length=128, write_only=True, required=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError(
                _('Wrong password')
            )
        return value

    def validate(self, data):
        if data['new_password'] != data['new_password2']:
            raise serializers.ValidationError({'new_password2': _("Passwords didn't match")})
        if data['new_password'] == data['old_password']:
            raise serializers.ValidationError({'new_password': _("Same password as the previous one")})
        password_validation.validate_password(data['new_password'], self.context['request'].user)
        return data
    

    def save(self, **kwargs):
        password = self.validated_data['new_password']
        user = self.context['request'].user
        user.set_password(password)
        user.save()
        return user


#PW 리셋
class ResetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(max_length=128, write_only=True, required=True)
    new_password2 = serializers.CharField(max_length=128, write_only=True, required=True)

    def validate(self, data):
        if data['new_password'] != data['new_password2']:
            raise serializers.ValidationError({'new_password2': _("Passwords didn't match")})
        password_validation.validate_password(data['new_password'], self.context['request'].user)
        return data

    def save(self, **kwargs):
        password = self.validated_data['new_password']
        print(f"request.data: {self.context['request'].data}")
        print(f"request.user: {self.context['request'].user}")
        user = self.context['request'].user
        user.set_password(password)
        user.save()
        return user


# #PW 리셋(user_id버전)
# class ResetPasswordSerializer(serializers.Serializer):
#     new_password = serializers.CharField(max_length=128, write_only=True, required=True)
#     new_password2 = serializers.CharField(max_length=128, write_only=True, required=True)
#     user_id = serializers.IntegerField(required=True)

#     def validate(self, data):
#         if data['new_password'] != data['new_password2']:
#             raise serializers.ValidationError({'new_password2': _("Passwords didn't match")})
#         user = User.objects.get(pk=data['user_id'])
#         password_validation.validate_password(data['new_password'], user)
#         return data

#     def save(self, **kwargs):
#         password = self.validated_data['new_password']
#         user = User.objects.get(pk=self.validated_data['user_id'])
#         user.set_password(password)
#         user.save()
#         return user

