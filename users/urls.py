from django.urls import path, include
from users.views import ProfileUpdateAPI, ProfileDetailAPI
from users.views import HelloUser, RegistrationAPI, LoginAPI, UserAPI

urlpatterns = [
    path("hello/", HelloUser),
    path("auth/resister/", RegistrationAPI.as_view()),
    path("auth/login/", LoginAPI.as_view()),
    path("auth/user/", UserAPI.as_view()),
    path("auth/profile/<int:user_pk>/update/", ProfileUpdateAPI.as_view()),
    path("auth/profile/<int:pk>/detail/", ProfileDetailAPI.as_view()),
]