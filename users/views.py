from django.shortcuts import render
from rest_framework import viewsets, permissions, generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from knox.models import AuthToken
from users.serializers import *
from users.models import *

# Create your views here.
@api_view(['GET'])
def HelloUser(request):
    return Response("hello world!")


# class RegistrationAPI(generics.GenericAPIView):
#     serializer_class = CreateUserSerializer

#     def post(self, request, *args, **kwargs):
#         if len(request.data["username"]) < 4 or len(request.data["password"]) < 4:
#             body = {"message": "short field"}
#             return Response(body, status=status.HTTP_400_BAD_REQUEST)
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         user = serializer.save()
#         return Response(
#             {
#                 "user": UserSerializer(
#                     user, context=self.get_serializer_context()
#                 ).data,
#                 "token": AuthToken.objects.create(user)[1],
#             }
#         )

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
        
        univ = University.objects.get(pk=request.data['university'])
        col = College.objects.get(pk=request.data['college'])
        maj = College.objects.get(pk=request.data['major'])
        
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
    def get_queryset(self):
        # col = College.objects.filter(university=)
        return super().get_queryset()


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


class UniversityView(APIView):
    def get(self, request, *args, **kwargs):
        university = University.objects.all()
        serializer = UniversitySerializer(university, many=True)
        return Response(serializer.data)


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

                  
class MajorView(APIView):
    def get(self, request, *args, **kwargs):
        college = College.objects.get(pk=kwargs['college_id'])
        major = Major.objects.filter(college=college)
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

