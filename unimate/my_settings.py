DATABASES = {
    'default': {
        #'ENGINE': 'django.db.backends.mysql',
        'ENGINE': 'mysql.connector.django',
        'NAME': 'unimate',  # DB name
        'USER': 'root',  # DB account
        'PASSWORD': 'miami0306!',  # DB account's password
        'HOST': '127.0.0.1',  # DB address(IP)
        'PORT': '3306',  # DB port(normally 3306)
    }
}