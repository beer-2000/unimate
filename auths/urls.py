from django.urls import path
from auths.views import *

urlpatterns = [
    # email 인증
    path("email/", EmailAuthView.as_view(), name='email'),
    path("activate/<str:uidb64>/<str:token>", EmailActivate.as_view(), name='activate'),
    # sms 인증 for 회원가입
    path("sms/", SMSVerificationView.as_view(), name='sms'),
    path("smsactivate/", SMSVerificationConfirmView.as_view(), name='smsactivate'),
    # sms 인증 for PW찾기
    path("sms_pw/", SMSVerificationForPasswordView.as_view(), name='sms_pw'),
    path("smsactivate_pw/", SMSVerificationConfirmForPasswordView.as_view(), name='smsactivate_pw'),
]