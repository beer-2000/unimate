from unimate import my_settings
# 이메일 인증
import six
from django.contrib.auth.tokens import PasswordResetTokenGenerator

class TokenGenerator(PasswordResetTokenGenerator): 
	def _make_hash_value(self, user, timestamp): 
		return (six.text_type(user.pk) + six.text_type(timestamp)) + six.text_type(user.profile.school_auth_status)

account_activation_token = TokenGenerator()
