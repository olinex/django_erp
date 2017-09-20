#!/usr/bin/env python3
#-*- coding:utf-8 -*-

"""
Django settings for django_erp project.

Generated by 'django-admin startproject' using Django 1.11.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os
from . import get_environ
from . import privates
from django.core.urlresolvers import reverse_lazy

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = get_environ('DEBUG')
FILE_SERVICE = get_environ('FILE_SERVICE')

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '[::1]'
]

ALLOWED_METHODS = ['GET', 'POST', 'HEAD', 'PUT', 'PATCH', 'OPTIONS', 'DELETE']


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = (
    "yf#D@epr$b@_fAA03vC(;;vdZEeCC~^@Q l<C1me!&ltpA+w}{/>8&ja%D'3L/eb%YAO24E~pKgrjA,eb+L[X4^.sz"
    if DEBUG
    else get_environ('SECRET_KEY')
)


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'channels',
    'rest_framework',

    'django_dva',
    'django_perm',
    'django_account',
    'django_product',
    'django_file',
    'django_stock',
    'django_purchase',
    'django_sale',
    'django_api',
]

if DEBUG:
    INSTALLED_APPS += [
        'django_extensions',
        'debug_toolbar',
    ]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

if DEBUG:
    MIDDLEWARE.insert(0,'debug_toolbar.middleware.DebugToolbarMiddleware')

ROOT_URLCONF = 'django_erp.urls'
REACT_ROOT = os.path.join(BASE_DIR, 'django_dva')

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(REACT_ROOT, 'templates')],
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

# authenticate against different sources.
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'django_account.authentication.EmailAuthBackend',
    'django_account.authentication.PhoneNumberBackend',
    'django_perm.backends.ObjectPermissionBackend',
)

WSGI_APPLICATION = 'django_erp.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    'django.contrib.auth.hashers.BCryptPasswordHasher',
]

# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'zh-hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# account login and logout config
# LOGIN_REDIRECT_URL = reverse_lazy('account:user_edit_url')
# LOGIN_URL=reverse_lazy('account:login')
# LOGOUT_URL=reverse_lazy('account:logout')


STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'collectstatics')

# user's media files

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# mail
DEFAULT_FROM_EMAIL = get_environ('DEFAULT_FROM_EMAIL')
EMAIL_HOST = get_environ('EMAIL_HOST')
EMAIL_PORT = get_environ('EMAIL_PORT')
EMAIL_HOST_USER = get_environ('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = get_environ('EMAIL_HOST_PASSWORD')
EMAIL_USE_LTS = True

# cache
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': get_environ('REDIS_CACHE_LOCATION'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'PASSWORD': get_environ('REDIS_CONF_PASSWORD'),
            'MAX_ENTRIES': 1000
        },
        'TIMEOUT': 3600,
        'KEY_PREFIX': 'DJANGO_ERP_DEFAULT_CACHE',
    }
}

# session
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'
SESSION_CACHE_ALIAS = 'default'
SESSION_EXPIRE_AT_BROWSER_CLOSE = False


#--------------------------------------------Third part package params-------------------------------------------------#

PERM_NOT_ALLOW_NOTICE = ''

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
        'common.rest.permissions.ViewAccess',
    ),
    'DEFAULT_THROTTLE_CLASS': (
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
    ),
    'DEFAULT_THROTTLE_RATES': {
        'anon': '10/min',
        'user': '60/min',
    },
    'PAGE_SIZE': 10,
}

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "asgi_redis.RedisChannelLayer",
        "CONFIG": {
            "hosts": [
                get_environ('CHANNEL_HOST')
            ],
        },
        "ROUTING": "django_erp.routing.channel_routing",
    },
}

# Redis
REDIS_CONF = {
    'host': get_environ('REDIS_CONF_HOST'),
    'port': get_environ('REDIS_CONF_PORT'),
    'db': get_environ('REDIS_CONF_DB'),
    'password': get_environ('REDIS_CONF_PASSWORD')
}

# Celery
CELERY_TASK_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ('json',)
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
CELERY_ENABLE_UTC = USE_TZ
CELERY_BROKER_URL = get_environ('CELERY_BROKER_URL')
CELERY_RESULT_BACKEND = get_environ('CELERY_RESULT_BACKEND')

# debug toolbar settings
INTERNAL_IPS = ['127.0.0.1']
DEBUG_TOOLBAR_CONFIG = {
    'JQUERY_URL': 'http://code.jquery.com/jquery-2.1.1.min.js'
}
