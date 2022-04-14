#MySQL, python 버전 호환 문제 해결
import pymysql
pymysql.install_as_MySQLdb()

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'unimate',  # DB name
        'USER': 'root',  # DB account
        'PASSWORD': 'miami0306!',  # DB account's password
        'HOST': '127.0.0.1',  # DB address(IP)
        'PORT': '3306',  # DB port(normally 3306)
    },
    'OPTIONS': {
        "init_command": "SET foreign_key_checks = 0;", }
}

EMAIL = {
    'EMAIL_BACKEND': 'django.core.mail.backends.smtp.EmailBackend',
    'EMAIL_HOST': 'smtp.gmail.com',
    'EMAIL_USE_TLS': True,
    'EMAIL_PORT': 587,
    'EMAIL_HOST_USER': 'unimate.official@gmail.com',
    'EMAIL_HOST_PASSWORD': 'unimate1!@',
    'REDIRECT_PAGE': 'http://127.0.0.1:8000/profile/<int:user_id>/'
}


SMS = {
    "from": "01021082205",
    'uri' : 'ncp:sms:kr:281058376077:unimate',
    "access_key" : 'dM96IMy476W5Ya2ePGli',
    "secret_key" : 'LSxSFRiFrf1NcvURkVlYY9PXvMrWyE79IK72kTZr'
}