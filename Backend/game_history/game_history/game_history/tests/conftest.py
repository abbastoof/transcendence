import os
import django
from django.conf import settings
import pytest
from datetime import timedelta


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'game_history.settings')

if not settings.configured:
    settings.configure(
        DEBUG=True,
        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.postgresql",
                "NAME": "game_history",
                "HOST": "postgresql",
                "USER": "root",
                "PASSWORD": "root",
                "PORT": "5432",
                "ATOMIC_REQUESTS": True,
            "TEST": {
                "NAME": "mytestdatabase",
                "ATOMIC_REQUESTS": True,
                },
            },
        },
        INSTALLED_APPS=[
            'django.contrib.admin',
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'django.contrib.messages',
            'django.contrib.staticfiles',
            'rest_framework',
            'corsheaders',
            'game_data',
        ],
        MIDDLEWARE=[
            'django.middleware.security.SecurityMiddleware',
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.middleware.common.CommonMiddleware',
            'django.middleware.csrf.CsrfViewMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware',
            'django.contrib.messages.middleware.MessageMiddleware',
            'django.middleware.clickjacking.XFrameOptionsMiddleware',
        ],
        ROOT_URLCONF='game_history.urls',
        TEMPLATES=[
            {
                'BACKEND': 'django.template.backends.django.DjangoTemplates',
                'DIRS': [],
                'APP_DIRS': True,
                'OPTIONS': {
                    'context_processors': [
                        'django.template.context_processors.debug',
                        'django.template.context_processors.request',
                        'django.contrib.auth.context_processors.auth',
                        'django.contrib.messages.context_processors.messages',
                    ],
                },
            },
        ],
        WSGI_APPLICATION='game_history.wsgi.application',
        SECRET_KEY='django-insecure-woftd2en2**zr(b%#*2vit2v%s@(k54gb^c(ots0abo7(wsmo%',
        ALLOWED_HOSTS=['localhost', '127.0.0.1', '[::1]', 'game-history', 'game-history:8002'],
        RABBITMQ_HOST='localhost',
        RABBITMQ_USER='user',
        RABBITMQ_PASS='pass',
        RABBITMQ_PORT='5672',
        REST_FRAMEWORK={
            'DEFAULT_AUTHENTICATION_CLASSES': (
                'rest_framework_simplejwt.authentication.JWTAuthentication',
            ),
        },
        SIMPLE_JWT={
            'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
            'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
            'ROTATE_REFRESH_TOKENS': False,
            'BLACKLIST_AFTER_ROTATION': True,
            'AUTH_HEADER_TYPES': ('Bearer',),
            'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
            'TOKEN_OBTAIN_SERIALIZER': 'user_auth.serializers.CustomTokenObtainPairSerializer',
        },
        LANGUAGE_CODE='en-us',
        TIME_ZONE='UTC',
        USE_I18N=True,
        USE_L10N=True,
        USE_TZ=True,
        STATIC_URL='/static/',
        DEFAULT_AUTO_FIELD='django.db.models.BigAutoField',
        CORS_ORIGIN_ALLOW_ALL=True,
    )

django.setup()

@pytest.fixture(scope='session', autouse=True)
def django_db_modify_db_settings():
    settings.DATABASES['default'] = settings.DATABASES['default']['TEST']

@pytest.fixture(scope='session')
def db_access(db):
    pass
