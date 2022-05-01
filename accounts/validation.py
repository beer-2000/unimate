import re
from django.core.exceptions import ValidationError


def validate_username(value):
    username_regex = re.compile("^(?=.*[A-Za-z])(?=.*\d){4,14}$", re.I)
    if not username_regex.match(value):
        raise ValidationError('INVALID_USERNAME')


def validate_password(value):
    password_regex = re.compile("^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d$@$!%*#?&]{8,20}$")
    if not password_regex.match(value):
        raise ValidationError('INVALID_PASSWORD')
