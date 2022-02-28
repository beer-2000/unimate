from unimate import my_settings
# 이메일 인증
import six
from django.contrib.auth.tokens import PasswordResetTokenGenerator

class TokenGenerator(PasswordResetTokenGenerator): 
	def _make_hash_value(self, user, timestamp): 
		return (six.text_type(user.pk) + six.text_type(timestamp)) + six.text_type(user.profile.school_auth_status)

account_activation_token = TokenGenerator()

# 휴대폰 인증
import sys
import os
import hashlib
import hmac
import base64
import requests
import time

def	make_signature():
	timestamp = int(time.time() * 1000)
	timestamp = str(timestamp)

	access_key = my_settings.HEADER['x-ncp-iam-access-key']				# access key id (from portal or Sub Account)
	secret_key = my_settings.HEADER['x-ncp-apigw-signature-v2']				# secret key (from portal or Sub Account)
	secret_key = bytes(secret_key, 'UTF-8')

	method = "GET"
	uri = "/photos/puppy.jpg?query1=&query2"

	message = method + " " + uri + "\n" + timestamp + "\n" + access_key
	message = bytes(message, 'UTF-8')
	signingKey = base64.b64encode(hmac.new(secret_key, message, digestmod=hashlib.sha256).digest())
	return signingKey