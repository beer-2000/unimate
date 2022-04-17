from django.urls import path
from accounts.views import *
from knox import views as knox_views

urlpatterns = [
    path("hello/", HelloUser),
    path("register/", RegistrationAPI.as_view()),
    path("login/", LoginAPI.as_view()),
    path("logout/", knox_views.LogoutView.as_view(), name='knox_logout'),
    path("user/", UserAPI.as_view()),
    #id찾기
    path("findid/", FindIDAPI.as_view(), name='findid'),
    # PW 변경
    path("changepw/", ChangePasswordAPI.as_view(), name='changepw'),
    path("resetpw/", ResetPasswordAPI.as_view(), name='resetpw'),
    # 프로필
    path("profile_register/", ProfileRegisterAPI.as_view()),
    path("profile/<int:user_id>/", ProfileDetailAPI.as_view()),
    path("withdraw/", WithdrawAPI.as_view(), name='withdraw'),
    # 학교
    path('university/', UniversityView.as_view()),
    path('college/<int:university_id>/', CollegeView.as_view()),
    path('major/<int:university_id>/<int:college_id>/', MajorView.as_view()),
    path('major_univ/<int:university_id>/', MajorOfUnivView.as_view()),
    path('major_detail/', MajorDetailView.as_view()),
]