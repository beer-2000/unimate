from rooms.serializers import *
from rooms.functions import *
from rest_framework import permissions, generics
from rest_framework.views import APIView, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q

from accounts.models import Profile

# Create your views here.


class RoomCreateAPI(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = RoomSerializer
    
    def post(self, request):
        profile = Profile.objects.get(id=request.id)
        if profile.auth_status == 'Profile complete':
            body = {"message": "School authentication is necessary"}
            return Response(body, status=status.HTTP_400_BAD_REQUEST)
        elif profile.auth_status == 'Phone complete':
            body = {"message": "Should enter profile"}
            return Response(body, status=status.HTTP_400_BAD_REQUEST)                   
        elif profile.auth_status == 'Registered':
            body = {"message": "Should authenticate phone"}
            return Response(body, status=status.HTTP_400_BAD_REQUEST)            
        room_serializer = RoomSerializer(data=request.data)
        if room_serializer.is_valid():
            room_serializer.save()
            #입장시키기
            print(room_serializer.data['id'])
            print(request.user.id)
            person = User.objects.get(pk=request.user.id)
            room = Room.objects.get(pk=room_serializer.data['id'])
            room.owner.add(person)
            #university 불러와서 저장
            room.university = str(request.user.university)
            room.save()
            # print(request.user.university)
            # print(room.owner, room.university)
            return Response(room_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(room_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# #방 생성 전 - 학교 인증 여부 확인
# class SchoolAuthAPI(APIView):
#     permission_classes = (permissions.IsAuthenticated,)

#     def post(self, request):
#         profile = Profile.objects.get(pk=request.user.pk)
#         if profile.school_auth_status == 'N':
#             body = {"message": "School authentication is necessary"}
#             return Response(body, status=status.HTTP_400_BAD_REQUEST)
#         else:
#             body = {"message": "School authentication is complete"}
#             return Response(body, status=status.HTTP_200_OK)


#방 목록 - 최신순 정렬(기본)
class RoomListAPI(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Room.objects.all().order_by('-created_at')
    serializer_class = RoomSerializer


#방 정보
class RoomDetailAPI(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request, pk, format=None):
        room = Room.objects.get(pk=pk)
        serializer = RoomSerializer(room)
        return Response(serializer.data)


#'editing' 추천 기능(방과 프로필 비교) 작성 중
class RoomRecommendAPI(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request, format=None):
        profile = Profile.objects.get(user_id=request.user.id)
        allroom = Room.objects.all().order_by('-created_at')
        recommend_list = []
        recommend_count = 0
        for i in range(len(allroom)):
            room = allroom[i]
            if compare_total(room, profile):
                recommend_list.append(room)
                recommend_count += 1
            if recommend_count == 5:
                break
        serializer = RoomWithoutownerSerializer(recommend_list, many=True)
        return Response(serializer.data)

        room = allroom[0]
        
        #print(compare_mbti(room.mbti, profile.mbti))
        #print(room, profile, compare_interest(room.interest, profile.interest_list))
        return Response(status=status.HTTP_200_OK)





# 대화 중인 채팅방 (owner가 안 불러와져서, RoomWithoutownerSerializer 작성)
class ParticipationListAPI(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request, format=None):
        queryset = User.objects.filter(pk=request.user.id).prefetch_related('room_set')[0].room_set.values()
        #print(queryset)
        serializer = RoomWithoutownerSerializer(queryset, many=True)
        #print(serializer)
        #return Response(status=status.HTTP_200_OK)
        return Response(serializer.data)


# 방 입장
class RoomEntranceAPI(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get_object(self, pk):
        return get_object_or_404(Room, pk=pk)

    def get(self, request, pk, format=None):
        print(request.user.id)
        room = self.get_object(pk)
        serializer = RoomSerializer(room)
        return Response(serializer.data)
    # 입장하기 (토큰 주인 대상)
    def post(self, request, pk):
        room = self.get_object(pk)
        person = User.objects.get(pk=request.user.id)
        profile = person.profile
        if profile.auth_status == 'Profile complete':
            body = {"message": "School authentication is necessary"}
            return Response(body, status=status.HTTP_400_BAD_REQUEST)
        elif profile.auth_status == 'Phone complete':
            body = {"message": "Should enter profile"}
            return Response(body, status=status.HTTP_400_BAD_REQUEST)                   
        elif profile.auth_status == 'Registered':
            body = {"message": "Should authenticate phone"}
            return Response(body, status=status.HTTP_400_BAD_REQUEST)           
        #입장 가능 여부 확인
        enter, message = compare_total(room, profile)
        if not enter:
            return Response(message, status=status.HTTP_400_BAD_REQUEST)
        elif person in room.owner.all():
            body = {"message": "Already entered"}
            return Response(body, status=status.HTTP_400_BAD_REQUEST)
        else:
            room.owner.add(person)
            body = {"message": "Entrance complete"}
            return Response(body, status=status.HTTP_200_OK)


# 방 퇴장
class RoomExitAPI(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get_object(self, pk):
        return get_object_or_404(Room, pk=pk)

    def get(self, request, pk, format=None):
        print(request.user.id)
        room = self.get_object(pk)
        serializer = RoomSerializer(room)
        return Response(serializer.data)
    # 퇴장하기 (토큰 주인 대상)
    def post(self, request, pk):
        room = self.get_object(pk)
        roomuser = RoomUser.objects.filter(room_id=room.id, user_id=request.user.id)
        roomuser.delete()
        if len(room.owner.all()) == 0:
            room.delete()
        body = {"message": "Exit complete"}
        return Response(body, status=status.HTTP_200_OK)


#방 목록 - 필터
class RoomFilterAPI(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = FilterSerializer

    def post(self, request):
        filter_serializer = FilterSerializer(data=request.data)
        if filter_serializer.is_valid():
            room = Room.objects.all().order_by('-created_at')
            print(filter_serializer.data)
            #방 성격
            if filter_serializer.data['room_type'] == None:
                room1 = room
            else:
                room1 = room.filter(room_type=filter_serializer.data['room_type'])
            print(room1)
            #학년 제한
            if filter_serializer.data['grade'] == None:
                room2 = room1
            else:
                room2 = room1.filter(grade_limit=filter_serializer.data['grade'])
            print(room2)
            #성별 제한
            if filter_serializer.data['gender'] == None:
                room3 = room2
            else:
                room3 = room2.filter(gender_limit=filter_serializer.data['gender'])
            print(room3)
            #공통점
            if filter_serializer.data['common'] == None:
                room4 = room3
            #공통점 - mbti
            elif filter_serializer.data['common'] == 'mbti':
                profile = Profile.objects.get(user_id=request.user.id)
                room4 = []
                for i in range(len(room3)):
                    target = room3[i]
                    compare = RoomEnterPosible(target, profile)
                    if target.mbti == '':
                        pass
                    elif compare.compare_mbti():
                        room4.append(target)
            #공통점 - interest
            elif filter_serializer.data['common'] == 'interest':
                profile = Profile.objects.get(user_id=request.user.id)
                room4 = []
                for i in range(len(room3)):
                    target = room3[i]
                    compare = RoomEnterPosible(target, profile)
                    if target.interest == None:
                        pass
                    elif compare.compare_interest():
                        room4.append(target)
            #공통점 - college
            elif filter_serializer.data['common'] == 'college':
                profile = Profile.objects.get(user_id=request.user.id)
                room4 = []
                for i in range(len(room3)):
                    target = room3[i]
                    compare = RoomEnterPosible(target, profile)
                    if target.college == '':
                        pass
                    elif compare.compare_college():
                        room4.append(target)
            print(room4)
            output_serializer = RoomWithoutownerSerializer(room4, many=True)
            return Response(output_serializer.data)


#방 검색
class RoomSearchAPI(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = SearchSerializer

    def post(self, request, format=None):
        search_serializer = SearchSerializer(data=request.data)
        if search_serializer.is_valid():
            keyword = search_serializer.data['keyword']
            room = Room.objects.filter(
                Q(title__icontains=keyword) |
                Q(room_description__icontains=keyword)
            ).order_by('-created_at')
            serializer = RoomWithoutownerSerializer(room, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(search_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
