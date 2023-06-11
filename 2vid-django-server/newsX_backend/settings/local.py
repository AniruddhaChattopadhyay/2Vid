from .base import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'newsx_local',
        'USER': 'newsxUser',
        'PASSWORD': 'upcoming_unicorn',
        'HOST': '127.0.0.1',
        'OPTIONS': {
            'charset': 'utf8mb4'
        }
    }
}



ENV_NAME = "LOCAL"
ALLOWED_HOSTS = ['*']
DEBUG = True
