import json
from django.http import JsonResponse, HttpResponse

from django.shortcuts import render, get_object_or_404, redirect
from rest_framework import viewsets, permissions, generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from knox.models import AuthToken
from users.serializers import *
from users.models import *
from users.functions import *

from .email import message
from .token import account_activation_token
from django.core.exceptions import ValidationError 
from django.core.validators import validate_email
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.core.mail import EmailMessage
from django.utils.encoding import force_bytes, force_str




# Create your views here.
@api_view(['GET'])
def HelloUser(request):
    return Response("hello world!")



class RegistrationAPI(generics.GenericAPIView):
    serializer_class = CreateUserSerializer

    def get(self, request, *args, **kwargs):
        user = request.user

        if user == None or user.is_anonymous:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        serializer = serializers.CreateUserSerializer(user)
        
        return Response(serializer.data)
    
    def post(self, request, *args, **kwargs):
        if len(request.data["username"]) < 4 or len(request.data["password"]) < 4:
            body = {"message": "short field"}
            return Response(body, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {
                "user": UserSerializer(
                    user, context=self.get_serializer_context()
                ).data,
                "token": AuthToken.objects.create(user)[1],
            }
        )


class LoginAPI(generics.GenericAPIView):
    serializer_class = LoginUserSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        return Response(
            {
                "user": UserSerializer(
                    user, context=self.get_serializer_context()
                ).data,
                "token": AuthToken.objects.create(user)[1],
            }
        )


class UserAPI(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class ProfileDetailAPI(generics.RetrieveUpdateDestroyAPIView):
    lookup_field = "user_id"
    queryset = Profile.objects.all()
    serializer_class = ProfileDetailSerializer


class EmailAuthView(APIView):
    lookup_field = "user_id"
    serializer_class = EmailSerializer

    def post(self, request, *args, **kwargs):
        data = request.data
        try:
            email = data["school_email"]
            profile = Profile.objects.get(school_email = email)
            profile_id = profile.user_id
            user = User.objects.get(pk=profile_id)

            current_site = get_current_site(request)
            domain = current_site.domain
            uid = urlsafe_base64_encode(force_bytes(profile_id))
            token = account_activation_token.make_token(user)
            message_data = message(domain, uid, token)

            mail_title = "학교 이메일 인증을 완료해주세요."
            mail_to = email
            email = EmailMessage(mail_title, message_data, to=[mail_to])
            email.send()

            return JsonResponse({"message" : "SUCCESS"}, status=200)
        except ValidationError:
            return JsonResponse({"error" : "VALIDATION_ERROR"}, status=400)
        except KeyError:
            return JsonResponse({"error" : "KEY_ERROR"}, status=400)
        except TypeError:
            return JsonResponse({"error" : "TYPE_ERROR"}, status=400)


class Activate(APIView):
    def get(self, request, uidb64, token):
        try: 
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
            
            if account_activation_token.check_token(user, token):
                user.profile.school_auth_status = 'Y'
                user.save() 
                # return redirect(EMAIL['REDIRECT_PAGE'])
                return Response('이메일 인증이 완료되었습니다.', status=status.HTTP_200_OK)
            return JsonResponse({"message" : "AUTH FAIL"}, status=400) 
        except ValidationError: 
            return JsonResponse({"message" : "TYPE_ERROR"}, status=400) 
        except KeyError: 
            return JsonResponse({"message" : "INVALID_KEY"}, status=400)



# 대학교 정보
class UniversityView(APIView):
    def get(self, request, *args, **kwargs):
        university = University.objects.all()
        serializer = UniversitySerializer(university, many=True)
        return Response(serializer.data)

# 단과대 정보
class CollegeView(APIView):
    def get(self, request, *args, **kwargs):
        university = University.objects.get(pk=kwargs['university_id'])
        college = College.objects.filter(university=university)
        serializer = CollegeSerializer(college, many=True)
        return Response(serializer.data)


# class AllCollegeView(APIView):
#     def get(self, request, *args, **kwargs):
#         user = request.user

#         if user == None or user.is_anonymous:
#             return Response(status=status.HTTP_404_NOT_FOUND)

#         college = College.objects.all()
#         serializer = serializers.CollegeSerializer(college, many=True)
#         return Response(serializer.data)

# 학과정보  
class MajorView(APIView):
    def get(self, request, *args, **kwargs):
        university = University.objects.get(pk=kwargs['university_id'])
        college = College.objects.get(pk=kwargs['college_id'])
        major = Major.objects.filter(university=university,college=college)
        serializer = MajorSerializer(major, many=True)
        return Response(serializer.data)


# class AllMajorView(APIView):
#     def get(self, request, *args, **kwargs):
#         user = request.user

#         if user == None or user.is_anonymous:
#             return Response(status=status.HTTP_404_NOT_FOUND)

#         major = Major.objects.all()
#         serializer = serializers.MajorSerializer(major, many=True)
#         return Response(serializer.data)


class RoomCreateAPI(APIView):
    serializer_class = RoomSerializer
    
    def post(self, request):
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


#방 목록 - 최신순 정렬(기본)
class RoomListAPI(generics.ListAPIView):
    queryset = Room.objects.all().order_by('-created_at')
    serializer_class = RoomSerializer


#방 정보
class RoomDetailAPI(APIView):
    def get(self, request, pk, format=None):
        room = Room.objects.get(pk=pk)
        serializer = RoomSerializer(room)
        return Response(serializer.data)


#'editing' 추천 기능(방과 프로필 비교) 작성 중
class RoomRecommendAPI(APIView):

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
    def get(self, request, format=None):
        queryset = User.objects.filter(pk=request.user.id).prefetch_related('room_set')[0].room_set.values()
        print(queryset)
        serializer = RoomWithoutownerSerializer(queryset, many=True)
        print(serializer)
        #return Response(status=status.HTTP_200_OK)
        return Response(serializer.data)


# 방 입장
class RoomEntranceAPI(APIView):
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
        body = {"message": "Exit complete"}
        return Response(body, status=status.HTTP_200_OK)


#방 목록 - 필터
class RoomFilterAPI(APIView):
    serializer_class = FilterSerializer

    def post(self, request):
        filter_serializer = FilterSerializer(data=request.data)
        if filter_serializer.is_valid():
            room = Room.objects.all()
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


class MeetCreateAPI(APIView):
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
    def get(self, request, pk, format=None):
        meet = Meet.objects.get(pk=pk)
        serializer = MeetSerializer(meet)
        return Response(serializer.data)


#약속 참여
class MeetEntranceAPI(APIView):
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