import re
from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.response import Response


def validate_username(value):
    username_regex = re.compile("^(?=.*[A-Za-z])(?=.*\d){4,14}$", re.I)
    if not username_regex.match(value):
        raise ValidationError('INVALID_USERNAME')


def validate_password(value1, value2):
    password_regex = re.compile("^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d$@$!%*#?&]{8,20}$")
    if not password_regex.match(value1):
        raise ValidationError('INVALID_PASSWORD')
    if value1 != value2:
        raise ValidationError('INCORRECT_PASSWORD')
