from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import permissions, generics, status
from accounts.serializers import *
from accounts.models import *
from accounts.validation import *

from knox.models import AuthToken

# Create your views here.



# Create your views here.
@api_view(['GET'])
def HelloUser(request):
    return Response("hello world!")


class RegistrationAPI(generics.GenericAPIView):
    serializer_class = CreateUserSerializer
    
    def post(self, request, *args, **kwargs):

        # if len(request.data["username"]) < 4 or len(request.data["password"]) < 4:
        #     body = {"message": "short field"}
        #     return Response(body, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 이미 is_vaild 메서드에서 중복 검사를 함
        # if User.objects.filter(email=serializer["email"].value):
        #         return Response({"message": "Duplicated email"}, status=status.HTTP_400_BAD_REQUEST)
        user = serializer.save()
        return Response(
            {
                "user": UserSerializer(
                    user, context=self.get_serializer_context()
                ).data,
                "token": AuthToken.objects.create(user)[1],
            }
        )

#ID 유효성 확인
class IDDuplicateApI(generics.GenericAPIView):
    serializer_class = IDSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if (len(serializer["username"].value) < 4) or (len(serializer["username"].value) > 14):
            body = {"message": "Username must be not less than 4 characters but not more than 14 characters"}
            return Response(body, status=status.HTTP_400_BAD_REQUEST)
        if (' ' in serializer["username"].value):
            body = {"message": "Username can not contain spaces"}
            return Response(body, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(username=serializer["username"].value):
            return Response({"message": "Duplicated ID"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message": "Available ID"}, status=status.HTTP_200_OK)

# 비밀번호 유효성 확인
class PWValidateApI(generics.GenericAPIView):
    serializer_class = PWSerializer
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        pw1 = request.data["pw1"]
        pw2 = request.data["pw2"]
        try:
            validate_password(pw1, pw2)
            return Response({"message": "VALID_PASSWORD"}, status=status.HTTP_200_OK)
        except ValidationError:
            body = {"message": "INVALID_PASSWORD"}
            return Response(body, status=status.HTTP_400_BAD_REQUEST)

#닉네임 중복 확인
class NicknameDuplicateApI(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = NicknameSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        print(serializer["nickname"].value[0])
        print(serializer["nickname"].value[-1])
        if (len(serializer["nickname"].value) < 2) or (len(serializer["nickname"].value) > 10):
            body = {"message": "Nickname must be not less than 2 characters but not more than 10 characters"}
            return Response(body, status=status.HTTP_400_BAD_REQUEST)
        # 공백으로 시작할 시, 자동으로 제거되어 등록됨
        # if (serializer["nickname"].value[0]) == ' ' or (serializer["nickname"].value[-1] == ' '):
        #     body = {"message": "Nickname can not start or end with a space"}
        #     return Response(body, status=status.HTTP_400_BAD_REQUEST)
        if Profile.objects.filter(nickname=serializer["nickname"].value):
            return Response({"message": "Duplicated nickname"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message": "Available nickname"}, status=status.HTTP_200_OK)


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


class ProfileRegisterAPI(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = ProfileRegisterSerializer

    def post(self, request, *args, **kwargs):
        profile = Profile.objects.get(id=request.user.id)
        data = request.data
        data["auth_status"] = "Profile complete"
        profile_serializer = ProfileRegisterSerializer(profile, data)
        if profile_serializer.is_valid():
            profile_serializer.save()
            return Response(profile_serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(profile_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
        # university에 속한 college 불러오기
        colleges = College.objects.filter(university=university)
        print(colleges)
        print(colleges[0])
        print(colleges[0].id)
        # colleges에 속한 major 불러와서 정렬하기
        major = Major.objects.filter(college__in=colleges).order_by('major')
        # major = Major.objects.filter(college__in=[1]).order_by('major')
        print(major)
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


# 내정보 들어갈 때 프로필 등록 여부 체크
class ProfileCheckView(APIView):
    permission_classes = (permissions.IsAuthenticated,)    
    
    def get(self, request):
        profile = Profile.objects.get(id=request.id)
        if profile.auth_status == "Registered":
            return Response({"message": "Should authenticate phone"}, status=status.HTTP_400_BAD_REQUEST)
        elif profile.auth_status == "Phone complete":
            return Response({"message": "Should enter profile"}, status=status.HTTP_400_BAD_REQUEST)            
        else:
            return Response({"message": "Profile status OK"}, status=status.HTTP_200_OK)
