from random import randint
import time
import hmac
import base64
import hashlib
import requests
import json
import datetime
from unimate import my_settings

from django.http import JsonResponse, HttpResponse
from rest_framework import permissions
from rest_framework.views import APIView
from knox.models import AuthToken
from rest_framework import status
from rest_framework.response import Response
from auths.serializers import *

from .email import message
from .utils import account_activation_token
from django.core.exceptions import ValidationError
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.core.mail import EmailMessage
from django.utils.encoding import force_bytes, force_str



# Create your views here.

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
                user.profile.auth_status = 'School complete'
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
                Profile.objects.filter(user_id=user).update(auth_status='Phone complete')
                auth_status = Profile.objects.filter(user_id=user)[0].auth_status
                return JsonResponse({'auth_status': auth_status}, status=200)
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


