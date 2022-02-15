from django.urls import path
from users.views import *

urlpatterns = [
    path("hello/", HelloUser),
    path("register/", RegistrationAPI.as_view()),
    path("login/", LoginAPI.as_view()),
    path("user/", UserAPI.as_view()),
    #user_pk : User 테이블의 pk인 'id' 참조
    #user_id : User 테이블에서 Profile 테이블로 참조해온 fk의 이름이 'user_id'임
    #path("profile/<int:user_pk>/update/", ProfileUpdateAPI.as_view()),
    path("profile/<int:user_id>/", ProfileDetailAPI.as_view()),
    path('university/', UniversityView.as_view()),
    path('college/<int:university_id>/', CollegeView.as_view()),
    path('major/<int:college_id>/', MajorView.as_view()),
    #방 관련
    path('room_create/', RoomCreateAPI.as_view(), name='room_create'),
    path('room_list/', RoomListAPI.as_view(), name='room_list'),
    path('room_entrance/<int:pk>/', RoomEntranceAPI.as_view(), name='room_entrance'),
]