from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from meets.serializers import *
from rest_framework.views import APIView
from rest_framework.response import Response

# Create your views here.


class MeetCreateAPI(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = MeetSerializer
    
    def post(self, request):
        meet_serializer = MeetSerializer(data=request.data)
        if meet_serializer.is_valid():
            meet_serializer.save()
            #입장시키기
            print(meet_serializer.data['id'])
            print(request.user.id)
            person = User.objects.get(pk=request.user.id)
            meet = Meet.objects.get(pk=meet_serializer.data['id'])
            meet.owner.add(person)
            meet.save()
            serializer = MeetSerializer(meet)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(meet_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MeetDetailAPI(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request, pk, format=None):
        meet = Meet.objects.get(pk=pk)
        serializer = MeetSerializer(meet)
        return Response(serializer.data)


#약속 참여
class MeetEntranceAPI(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get_object(self, pk):
        return get_object_or_404(Meet, pk=pk)

    def get(self, request, pk, format=None):
        print(request.user.id)
        meet = self.get_object(pk)
        serializer = MeetSerializer(meet)
        return Response(serializer.data)
    # 입장하기 (토큰 주인 대상)
    def post(self, request, pk):
        meet = self.get_object(pk)
        person = User.objects.get(pk=request.user.id)
        profile = person.profile
        meet.owner.add(person)
        body = {"message": "Entrance complete"}
        return Response(body, status=status.HTTP_200_OK)


# 약속 퇴장
class MeetExitAPI(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get_object(self, pk):
        return get_object_or_404(Meet, pk=pk)

    def get(self, request, pk, format=None):
        print(request.user.id)
        meet = self.get_object(pk)
        serializer = MeetSerializer(meet)
        return Response(serializer.data)
    # 퇴장하기 (토큰 주인 대상)
    def post(self, request, pk):
        meet = self.get_object(pk)
        meetuser = MeetUser.objects.filter(meet_id=meet.id, user_id=request.user.id)
        meetuser.delete()
        body = {"message": "Exit complete"}
        return Response(body, status=status.HTTP_200_OK)


#약속 내역 - room_id == id 인 방에 종속된 약속 list
class MeetListAPI(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, requets, id, format=None):
        meet = Meet.objects.filter(room_id=id)
        meet = Meet.objects.filter(room_id=id).order_by('-created_at')
        serializer = MeetSerializer(meet, many=True)
        return Response(serializer.data) 