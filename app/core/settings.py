"""
Django settings for app project.

Generated by 'django-admin startproject' using Django 4.2.9.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""
import os
from pathlib import Path
from celery.schedules import crontab


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('DJANGO_SECRET')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = bool(int(os.environ.get('DEBUG')))

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS').split(' ')


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'corsheaders',

    'rest_framework',
    'djoser',
    'rest_framework.authtoken',

    'rest_framework_simplejwt',
    'django_filters',
    'django_celery_beat',
    'django_json_widget',

    'fantasy',
    'users',

    'drf_spectacular',

]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
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
]

WSGI_APPLICATION = 'core.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('POSTGRES_DB'),
        'USER': os.environ.get('POSTGRES_USER'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD'),
        'HOST': os.environ.get('POSTGRES_HOST'),
        'PORT': os.environ.get('POSTGRES_PORT'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = []


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Europe/Kiev'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]
STATIC_ROOT = os.path.join(BASE_DIR, 'static_root')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL = 'users.CustomUser'
AUTHENTICATION_BACKENDS = ['users.backends.EmailBackend']

DJOSER = {
    "USER_CREATE_PASSWORD_RETYPE": False,
    "LOGIN_FIELD": "email",
    "SERIALIZERS": {
        'user_create': 'api.serializers.UserCreateByEmailSerializer',
    }
}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': ['rest_framework.authentication.TokenAuthentication'],
    # 'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.AllowAny'],
    'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.IsAuthenticated'],
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 50,
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

CORS_ORIGIN_ALLOW_ALL = True

SPECTACULAR_SETTINGS = {
    'TITLE': 'CyberFantasy API',
    'DESCRIPTION': '-',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}

SILENCED_SYSTEM_CHECKS = ["auth.W004"]


# CELERY
CELERY_BROKER_URL = 'redis://redis:6379'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Europe/Kiev'
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"redis://redis:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}


DATA_UPLOAD_MAX_NUMBER_FIELDS = 10**5

FANTASY_FORMULA = {
    'kills': {
        'type': '+',
        'coef': {'core': 2, 'support': 3},
    },
    'deaths': {
        'type': '-',
        'coef': {'core': 2, 'support': 1.5},
    },
    'assists': {
        'type': '+',
        'coef': {'core': 1, 'support': 1},
    },
    'last_hits': {
        'type': '+',
        'coef': {'core': 0.01, 'support': 0.02},
    },
    'denies': {
        'type': '+',
        'coef': {'core': 0.02, 'support': 0.04},
    },
    'hero_damage': {
        'type': '+',
        'coef': {'core': 0.0002, 'support': 0.0002},
    },
    'tower_damage': {
        'type': '+',
        'coef': {'core': 0.0002, 'support': 0.0002},
    },
    'camps_stacked': {
        'type': '+',
        'coef': {'core': 0.15, 'support': 0.25},
    },
    'rune_pickups': {
        'type': '+',
        'coef': {'core': 0.1, 'support': 0.1},
    },
    'obs_placed': {
        'type': '+',
        'coef': {'core': 0.1, 'support': 0.1},
    },
    'sen_placed': {
        'type': '+',
        'coef': {'core': 0.15, 'support': 0.2},
    },
    'observer_kills': {
        'type': '+',
        'coef': {'core': 0.1, 'support': 0.1},
    },
    'sentry_kills': {
        'type': '+',
        'coef': {'core': 0.15, 'support': 0.2},
    },
    'courier_kills': {
        'type': '+',
        'coef': {'core': 1.5, 'support': 1.5},
    },
    'stuns': {
        'type': '+',
        'coef': {'core': 0.1, 'support': 0.1},
    },
    'hero_healing': {
        'type': '+',
        'coef': {'core': 0.001, 'support': 0.0015},
    },
    'buyback_count': {
        'type': '-',
        'coef': {'core': 1.5, 'support': 1.5},
    },
    'teamfight_participation': {
        'type': '+',
        'coef': {'core': 5, 'support': 5},
    },
}