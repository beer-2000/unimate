from django.urls import path, include
from users.views import ProfileUpdateAPI, ProfileDetailAPI
from users.views import HelloUser, RegistrationAPI, LoginAPI, UserAPI

urlpatterns = [
    path("hello/", HelloUser),
    path("register/", RegistrationAPI.as_view()),
    path("login/", LoginAPI.as_view()),
    path("user/", UserAPI.as_view()),
    #user_pk : User 테이블의 pk인 'id' 참조
    #user_id : User 테이블에서 Profile 테이블로 참조해온 fk의 이름이 'user_id'임
    #path("profile/<int:user_pk>/update/", ProfileUpdateAPI.as_view()),
    path("profile/<int:user_id>/update/", ProfileUpdateAPI.as_view()),
    path("profile/<int:user_id>/detail/", ProfileDetailAPI.as_view()),
]