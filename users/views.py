import json
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import permissions, generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from knox.models import AuthToken
from users.serializers import *
from users.models import *
from users.functions import *

from .email import message
from .utils import account_activation_token
from django.core.exceptions import ValidationError
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.core.mail import EmailMessage
from django.utils.encoding import force_bytes, force_str
from django.db.models import Q



# Create your views here.
@api_view(['GET'])
def HelloUser(request):
    return Response("hello world!")



class RegistrationAPI(generics.GenericAPIView):
    serializer_class = CreateUserSerializer

    # def get(self, request, *args, **kwargs):
    #     user = request.user

    #     if user == None or user.is_anonymous:
    #         return Response(status=status.HTTP_404_NOT_FOUND)
        
    #     serializer = serializers.CreateUserSerializer(user)
        
    #     return Response(serializer.data)
    
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

#기존 로그인
class LoginAPI(generics.GenericAPIView):
    serializer_class = LoginUserSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        AuthToken.objects.filter(user=user).delete()
        return Response(
            {
                "user": UserSerializer(
                    user, context=self.get_serializer_context()
                ).data,
                "token": AuthToken.objects.create(user)[1],
            }
        )


# # 수정중
# class LoginAPI(generics.GenericAPIView):
#     serializer_class = LoginUserSerializer

#     def post(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         user = serializer.validated_data
#         AuthToken.objects.filter(user=user).delete()
#         url = 'http://127.0.0.1:8000/login/'
#         # headers = {"token": AuthToken.objects.create(user)[1],}
#         # print(headers)
#         res = requests.post(url)
#         res.headers["HTTP_token"] = AuthToken.objects.create(user)[1]
#         # print("request")
#         # print(request)
#         # print(type(request))
#         # print(dir(request))
#         # print(request.data)
#         print(res)
#         print(type(res))
#         print(dir(res))
#         print(res.url)
#         print(res.headers)
#         print(res.status_code)
#         return HttpResponse(res)


class UserAPI(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated,]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class ProfileDetailAPI(generics.RetrieveUpdateDestroyAPIView):
    #permission_classes = (permissions.IsAuthenticated,)
    lookup_field = "user_id"
    queryset = Profile.objects.all()
    serializer_class = ProfileDetailSerializer


class WithdrawAPI(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = WithdrawSerializer

    def post(self, request, *args, **kwargs):
        profile = Profile.objects.get(pk=request.user.id)
        profile.withdrawn_status = 'withdrawal'
        profile.save()
        Withdraw.objects.create(
            user_id=request.user.id, withdraw_reason=request.data['withdraw_reason']
            )
        body = {"message": "Withdraw complete"}
        return Response(body, status=status.HTTP_200_OK)



# 이메일 인증
class EmailAuthView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = EmailSerializer

    def post(self, request, *args, **kwargs):
        data = request.data
        try:
            email = data["school_email"]
            if Profile.objects.filter(school_email=request.data['school_email']).exists():
                return JsonResponse({"error" : "Existing school_email"}, status=400)
            user = request.user
            user_id = user.id
            SchoolEmail.objects.filter(user_id=user).update(school_email=email)

            current_site = get_current_site(request)
            domain = current_site.domain
            uid = urlsafe_base64_encode(force_bytes(user_id))
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

# 이메일 인증 확인
class EmailActivate(APIView):
    def get(self, request, uidb64, token):
        try: 
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
            email = SchoolEmail.objects.get(user_id=user).school_email
            
            if account_activation_token.check_token(user, token):
                user.profile.school_auth_status = 'Y'
                user.profile.school_email=email
                user.save() 
                # return redirect(EMAIL['REDIRECT_PAGE'])
                return JsonResponse({"message" : "EMAIL AUTH SUCCESS"}, status=status.HTTP_200_OK)
            return JsonResponse({"message" : "AUTH FAIL"}, status=400) 
        except ValidationError: 
            return JsonResponse({"message" : "TYPE_ERROR"}, status=400) 
        except KeyError: 
            return JsonResponse({"message" : "INVALID_KEY"}, status=400)


#SMS 보내기 for 회원가입
class SMSVerificationView(APIView):
    permission_classes = (permissions.IsAuthenticated,)    
    serializer_class = SMSSerializer

    def send_verification(self, phone, code):
        SMS_URL = 'https://sens.apigw.ntruss.com/sms/v2/services/' + my_settings.SMS['uri'] + '/messages'
        timestamp = str(int(time.time() * 1000))
        secret_key = bytes(my_settings.SMS['secret_key'], 'utf-8')

        method = 'POST'
        uri = '/sms/v2/services/' + my_settings.SMS['uri'] + '/messages'
        message = method + ' ' + uri + '\n' + timestamp + '\n' + my_settings.SMS['access_key']

        message = bytes(message, 'utf-8')

        # 알고리즘으로 암호화 후, base64로 인코딩
        signingKey = base64.b64encode(
            hmac.new(secret_key, message, digestmod=hashlib.sha256).digest())

        headers = {
            'Content-Type': 'application/json; charset=utf-8',
            'x-ncp-apigw-timestamp': timestamp,
            'x-ncp-iam-access-key': my_settings.SMS['access_key'],
            'x-ncp-apigw-signature-v2': signingKey,
        }

        body = {
            'type': 'SMS',
            'contentType': 'COMM',
            'countryCode': '82',
            'from': my_settings.SMS['from'],
            'content': f'안녕하세요. unimate 입니다. 인증번호 [{code}]를 입력해주세요.',
            'messages': [
                {
                    'to': phone
                }
            ]
        }

# body를 json으로 변환
        encoded_data = json.dumps(body)
		
# post 메서드로 데이터를 보냄
        res = requests.post(SMS_URL, headers=headers, data=encoded_data)
        return HttpResponse(res.status_code)

    def post(self, request, *args, **kwargs):
        try:
            data = request.data
            user = request.user
            phone = data['phone_number']
            code = randint(100000, 999999)
            
            # phone_number 중복 검사
            if Profile.objects.filter(phone_number=phone).exists():
                return JsonResponse({'message': 'REGISTERED_NUMBER'}, status=401)
						
			#update(조건, defaults = 생성할 데이터 값)
            SMSAuthRequest.objects.filter(user_id=user).update(
                phone_number=phone,
                auth_number=code
            )

	        # phone, code 를 인자로 send_verification 메서드를 호출
            self.send_verification(
                phone=phone,
                code=code
            )
            return JsonResponse({'message': 'SUCCESS'}, status=201)


        except KeyError as e:
            return JsonResponse({'message': f'KEY_ERROR: =>  {e}'}, status=400)

        except ValueError as e:
            return JsonResponse({'message': f'VALUE_ERROR: =>  {e}'}, status=400)


#SMS 보내기 for PW찾기
class SMSVerificationForPasswordView(APIView):
    lookup_field = "user_id"
    serializer_class = SMSSerializer

    def send_verification(self, phone, code):
        SMS_URL = 'https://sens.apigw.ntruss.com/sms/v2/services/' + my_settings.SMS['uri'] + '/messages'
        timestamp = str(int(time.time() * 1000))
        secret_key = bytes(my_settings.SMS['secret_key'], 'utf-8')

        method = 'POST'
        uri = '/sms/v2/services/' + my_settings.SMS['uri'] + '/messages'
        message = method + ' ' + uri + '\n' + timestamp + '\n' + my_settings.SMS['access_key']

        message = bytes(message, 'utf-8')

        # 알고리즘으로 암호화 후, base64로 인코딩
        signingKey = base64.b64encode(
            hmac.new(secret_key, message, digestmod=hashlib.sha256).digest())

        headers = {
            'Content-Type': 'application/json; charset=utf-8',
            'x-ncp-apigw-timestamp': timestamp,
            'x-ncp-iam-access-key': my_settings.SMS['access_key'],
            'x-ncp-apigw-signature-v2': signingKey,
        }
        ####
        print("headers")
        print(headers)

        body = {
            'type': 'SMS',
            'contentType': 'COMM',
            'countryCode': '82',
            'from': my_settings.SMS['from'],
            'content': f'안녕하세요. unimate 입니다. 인증번호 [{code}]를 입력해주세요.',
            'messages': [
                {
                    'to': phone
                }
            ]
        }

    # body를 json으로 변환
        encoded_data = json.dumps(body)
		
    # post 메서드로 데이터를 보냄
        res = requests.post(SMS_URL, headers=headers, data=encoded_data)
        ####
        print("res")
        print(res)
        print(f'type: {type(res)}')
        # print('all in res')
        #num = 0
        # for i in res:
        #     print(num)
        #     print(i)
        #     num = num + 1
        print(f'headers: {res.headers}')
        print(f'content: {res.content}')
        print(f'status_code: {res.status_code}')

        return HttpResponse(res.status_code)

    def post(self, request, *args, **kwargs):
        try:
            data = request.data
            profile = Profile.objects.get(phone_number=data['phone_number'])
            user = User.objects.get(pk=profile.pk)
            phone = data['phone_number']
            code = randint(100000, 999999)

			#update(조건, defaults = 생성할 데이터 값)
            SMSAuthRequest.objects.filter(user_id=user).update(
                phone_number=phone,
                auth_number=code
            )
						
	        # phone, code 를 인자로 send_verification 메서드를 호출
            self.send_verification(
                phone=phone,
                code=code
            )
            return JsonResponse({'message': 'SUCCESS'}, status=201)


        except KeyError as e:
            return JsonResponse({'message': f'KEY_ERROR: =>  {e}'}, status=400)

        except ValueError as e:
            return JsonResponse({'message': f'VALUE_ERROR: =>  {e}'}, status=400)
        #등록되지 않은 번호 입력 시
        except Profile.DoesNotExist as e:
            return JsonResponse({'message': f'VALUE_ERROR: =>  {e}'}, status=400)


# 문자인증 확인과정(사용) for 회원가입
class SMSVerificationConfirmView(APIView):
    permission_classes = (permissions.IsAuthenticated,)    
    serializer_class = SMSActivateSerializer

    def post(self, request, *args, **kwargs):
        try:
            user = request.user
            profile = Profile.objects.get(pk=user.pk)
            phone_info = SMSAuthRequest.objects.get(user_id=profile.pk)
            phone = phone_info.phone_number
            verification_number = request.data['auth_number']

            if int(verification_number) == phone_info.auth_number:
                Profile.objects.filter(user_id=user).update(phone_number=phone)
                return JsonResponse({'message': 'SUCCESS'}, status=200)
            else:
                return JsonResponse({'message': 'INVALID_NUMBER'}, status=401)

        except KeyError as e:
            return JsonResponse({'message': f'KEY_ERROR: =>  {e}'}, status=400)

        except ValueError as e:
            return JsonResponse({'message': f'VALUE_ERROR: =>  {e}'}, status=400)


# 문자인증 확인과정(사용) for PW찾기
class SMSVerificationConfirmForPasswordView(APIView):
    serializer_class = SMSDetailSerializer

    def post(self, request, *args, **kwargs):
        try:
            data = request.data
            profile = Profile.objects.get(phone_number=data['phone_number'])
            user = User.objects.get(pk=profile.pk)
            phone_info = SMSAuthRequest.objects.get(user_id=profile.pk)
            phone = phone_info.phone_number
            verification_number = data['auth_number']

            if int(verification_number) == phone_info.auth_number:
                        # knox의 AuthToken에 user의 토큰 모두 삭제
                AuthToken.objects.filter(user=user).delete()
                # create and return new token
                return Response(
                    {
                        "user": UserSerializer(
                            user, context=user
                        ).data,
                        "token": AuthToken.objects.create(user)[1],
                    }
                )
            else:   
                return JsonResponse({'message': 'INVALID_NUMBER'}, status=401)

        except KeyError as e:
            return JsonResponse({'message': f'KEY_ERROR: =>  {e}'}, status=400)

        except ValueError as e:
            return JsonResponse({'message': f'VALUE_ERROR: =>  {e}'}, status=400)


# 문자인증 확인과정(이전)
# class SMSVerificationConfirmView(APIView):
#     lookup_field = "user_id"
#     serializer_class = SMSActivateSerializer
#     def get(self, request, *args, **kwargs):
        
#         user = User.objects.get(pk=kwargs['user_id'])
#         phone_info = SMSAuthRequest.objects.get(user_id=user)
#         serializer =  SMSDetailSerializer(phone_info)
#         print(f"kwargs: {kwargs}")
#         return Response(serializer.data)

#     def post(self, request, *args, **kwargs):
#         try:
#             user = User.objects.get(pk=kwargs['user_id'])
#             phone_info = SMSAuthRequest.objects.get(user_id=user)
#             phone = phone_info.phone_number
#             data = request.data
#             verification_number = data['auth_number']

#             if int(verification_number) == phone_info.auth_number:
#                 if not Profile.objects.filter(phone_number=phone).exists():
#                     Profile.objects.filter(user_id=user).update(phone_number=phone)
#                     return JsonResponse({'message': 'SUCCESS'}, status=200)

#                 else:
#                     return JsonResponse({'message': 'REGISTERED_NUMBER'}, status=401)
#             return JsonResponse({'message': 'INVALID_NUMBER'}, status=401)

#         except KeyError as e:
#             return JsonResponse({'message': f'KEY_ERROR: =>  {e}'}, status=400)

#         except ValueError as e:
#             return JsonResponse({'message': f'VALUE_ERROR: =>  {e}'}, status=400)




#ID 찾기
class FindIDAPI(APIView):
    serializer_class = FindIDSerializer
    def post(self, request, format=None):
        email_serializer = FindIDSerializer(data=request.data)
        if email_serializer.is_valid:
            print(request.data['email'])
            if User.objects.filter(email=request.data['email']).exists():
                user = User.objects.get(email=request.data['email'])
                serializer = UsernameSerializer(user)
                return Response(serializer.data)
            else:
                body = {"message": "Unregistered email"}
                return Response(body, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


#PW 변경
class ChangePasswordAPI(generics.UpdateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = ChangePasswordSerializer

    def update(self, request, *args, **kwargs):
        # request를 serialize해서 self(put method)를 실행함
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # put method를 실행하고 유효성 검사 후 저장함
        user = serializer.save()
        # knox의 AuthToken에 user의 토큰 모두 삭제
        AuthToken.objects.filter(user=user).delete()
        # create and return new token
        return Response(
            {
                "user": UserSerializer(
                    user, context=self.get_serializer_context()
                ).data,
                "token": AuthToken.objects.create(user)[1],
            }
        )


#PW 리셋
class ResetPasswordAPI(generics.UpdateAPIView):
    permission_classes = (permissions.IsAuthenticated,)    
    serializer_class = ResetPasswordSerializer

    def update(self, request, *args, **kwargs):
        # data를 serialize해서 self(put method)를 실행함
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # put method를 실행하고 유효성 검사 후 저장함
        user = serializer.save()
        # knox의 AuthToken에 user의 토큰 모두 삭제
        AuthToken.objects.filter(user=user).delete()
        # create and return new token
        return Response({"user": UserSerializer(user, context=self.get_serializer_context()).data})


# #PW 리셋(user_id버전)
# class ResetPasswordAPI(generics.UpdateAPIView):
#     serializer_class = ResetPasswordSerializer

#     def update(self, request, *args, **kwargs):
#         # request.data에 user_id를 추가
#         data = request.data
#         data['user_id'] = kwargs['user_id']
#         # data를 serialize해서 self(put method)를 실행함
#         serializer = self.get_serializer(data=data)
#         serializer.is_valid(raise_exception=True)
#         # put method를 실행하고 유효성 검사 후 저장함
#         user = serializer.save()
#         # knox의 AuthToken에 user의 토큰 모두 삭제
#         AuthToken.objects.filter(user=user).delete()
#         # create and return new token
#         return Response({"user": UserSerializer(user, context=self.get_serializer_context()).data})


# 대학교 정보
class UniversityView(APIView):
    def get(self, request, *args, **kwargs):
        university = University.objects.all().order_by('university')
        serializer = UniversitySerializer(university, many=True)
        return Response(serializer.data)

# 단과대 정보
class CollegeView(APIView):
    def get(self, request, *args, **kwargs):
        university = University.objects.get(pk=kwargs['university_id'])
        college = College.objects.filter(university=university)
        serializer = CollegeSerializer(college, many=True)
        return Response(serializer.data)

# 학과정보  
class MajorView(APIView):
    def get(self, request, *args, **kwargs):
        university = University.objects.get(pk=kwargs['university_id'])
        college = College.objects.get(pk=kwargs['college_id'])
        major = Major.objects.filter(university=university,college=college)
        serializer = MajorSerializer(major, many=True)
        return Response(serializer.data)

# 대학교에 소속된 학과 정보 
class MajorOfUnivView(APIView):
    def get(self, request, *args, **kwargs):
        university = University.objects.get(pk=kwargs['university_id'])
        print(type(university))
        # university에 속한 college 불러오기
        colleges = College.objects.filter(university=university)
        # colleges에 속한 major 불러와서 정렬하기
        major = Major.objects.filter(college__in=colleges).order_by('major')
        serializer = MajorSerializer(major, many=True)
        return Response(serializer.data)

# 학과 정보를 id->이름 으로 치환하기
class MajorDetailView(APIView):
    serializer_class = MajorDetailSerializer
    
    def post(self, request):
        major_data = request.data
        major_data['college'] = College.objects.get(id=major_data['college']).college
        major_data['university'] = University.objects.get(id=major_data['university']).university
        serializer = MajorDetailSerializer(data=major_data)
        if serializer.is_valid():
            return Response(serializer.data)


class RoomCreateAPI(APIView):
    permission_classes = (permissions.IsAuthenticated,)
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


#방 생성 전 - 학교 인증 여부 확인
class SchoolAuthAPI(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        profile = Profile.objects.get(pk=request.user.pk)
        if profile.school_auth_status == 'N':
            body = {"message": "School authentication is necessary"}
            return Response(body, status=status.HTTP_400_BAD_REQUEST)
        else:
            body = {"message": "School authentication is complete"}
            return Response(body, status=status.HTTP_200_OK)


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
        if profile.school_auth_status == 'N':
            body = {"message": "School authentication is necessary"}
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