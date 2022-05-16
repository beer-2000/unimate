import re
from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.response import Response


def validate_username(value):
    username_regex = re.compile("^[A-Za-z\d]{4,14}$")
    if not username_regex.match(value):
        # raise ValidationError('INVALID_USERNAME')
        # return Response({"message": "INVALID_USERNAME"}, status=status.HTTP_400_BAD_REQUEST)
        return False


def validate_password(value1, value2):
    password_regex = re.compile("^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d$@$!%*#?&]{8,20}$")
    if not password_regex.match(value1):
        # raise ValidationError('INVALID_PASSWORD')
        return 'INVALID_PASSWORD'
        # return Response({"message": "INVALID_PASSWORD"}, status=status.HTTP_400_BAD_REQUEST)
    if value1 != value2:
        # raise ValidationError('INCORRECT_PASSWORD')
        # return Response({"message": "INCORRECT_PASSWORD"}, status=status.HTTP_400_BAD_REQUEST)
        return 'INCORRECT_PASSWORD'
