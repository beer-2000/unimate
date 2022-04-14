from rest_framework import serializers
from meets.models import *

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