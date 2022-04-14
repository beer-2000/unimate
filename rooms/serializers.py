from rest_framework import serializers
from rooms.models import *

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
