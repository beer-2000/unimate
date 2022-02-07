from django.urls import path, include
from users.views import HelloUser, RegistrationAPI, LoginAPI, UserAPI

urlpatterns = [
    path("hello/", HelloUser),
    path("auth/resister/", RegistrationAPI.as_view()),
    path("auth/login/", LoginAPI.as_view()),
    path("auth/user/", UserAPI.as_view()),
]