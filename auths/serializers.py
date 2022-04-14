from rest_framework import serializers

from auths.models import *
from accounts.models import Profile
from accounts.serializers import UserSerializer


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
