from django.urls import path
from users.views import *
from knox import views as knox_views

urlpatterns = [
    path("hello/", HelloUser),
    path("register/", RegistrationAPI.as_view()),
    path("login/", LoginAPI.as_view()),
    path("logout/", knox_views.LogoutView.as_view(), name='knox_logout'),
    path("user/", UserAPI.as_view()),
    # email 인증
    path("email/<int:user_id>/", EmailAuthView.as_view(), name='email'),
    path("activate/<str:uidb64>/<str:token>", EmailActivate.as_view(), name='activate'),
    path("findid/", FindIDAPI.as_view(), name='findid'),
    #PW 변경
    path("changepw/", ChangePasswordAPI.as_view(), name='changepw'),
    path("resetpw/", ResetPasswordAPI.as_view(), name='resetpw'),
    # sms 인증 for 회원가입
    path("sms/", SMSVerificationView.as_view(), name='sms'),
    path("smsactivate/", SMSVerificationConfirmView.as_view(), name='smsactivate'),
    # sms 인증 for PW찾기
    path("sms_pw/", SMSVerificationForPasswordView.as_view(), name='sms_pw'),
    path("smsactivate_pw/", SMSVerificationConfirmForPasswordView.as_view(), name='smsactivate_pw'),
    #path("smsactivate/<int:user_id>/", SMSVerificationConfirmView.as_view(), name='sms'),
    #user_pk : User 테이블의 pk인 'id' 참조
    #user_id : User 테이블에서 Profile 테이블로 참조해온 fk의 이름이 'user_id'임
    #path("profile/<int:user_pk>/update/", ProfileUpdateAPI.as_view()),
    path("profile/<int:user_id>/", ProfileDetailAPI.as_view()),
    path("withdraw/", WithdrawAPI.as_view(), name='withdraw'),
    # 학교
    path('university/', UniversityView.as_view()),
    path('college/<int:university_id>/', CollegeView.as_view()),
    path('major/<int:university_id>/<int:college_id>/', MajorView.as_view()),
    #방 관련
    path('room_create/', RoomCreateAPI.as_view(), name='room_create'),
    path('room_list/', RoomListAPI.as_view(), name='room_list'),
    path('room_filter/', RoomFilterAPI.as_view(), name='room_filter'),
    path('room_search/', RoomSearchAPI.as_view(), name='room_search'),
    path('room_detail/<int:pk>', RoomDetailAPI.as_view(), name='room_detail'),
    path('room_recommend/', RoomRecommendAPI.as_view(), name='room_recommend'),
    path('room_entrance/<int:pk>/', RoomEntranceAPI.as_view(), name='room_entrance'),
    path('room_exit/<int:pk>/', RoomExitAPI.as_view(), name='room_exit'),
    path('participation/', ParticipationListAPI.as_view(), name='participation'),
    #약속 관련
    path('meet_create/', MeetCreateAPI.as_view(), name='meet_create'),
    path('meet_detail/<int:pk>/', MeetDetailAPI.as_view(), name='meet_detail'),
    path('meet_entrance/<int:pk>/', MeetEntranceAPI.as_view(), name='meet_entrance'),
    path('meet_exit/<int:pk>/', MeetExitAPI.as_view(), name='meet_exit'),
    path('meet_list/<int:id>/', MeetListAPI.as_view(), name='meet_list'),
]