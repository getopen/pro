"""
Django settings for pro project.

Generated by 'django-admin startproject' using Django 1.8.2.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '^q-t_@fb8v(p6+r!@ar0e*0j9o-*9l%sh)@8_g%v&%lf=_es(m'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'question',
    'people',
    'sites',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'people.views.MyMiddleware',
)

ROOT_URLCONF = 'pro.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR,'templates')],
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

WSGI_APPLICATION = 'pro.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

AUTH_USER_MODEL = 'people.Member'

# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

# LANGUAGE_CODE = 'en-us'

# TIME_ZONE = 'UTC'
LANGUAGE_CODE = 'zh_Hans'
TIME_ZONE='Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "static"),
)


# Gravtar Define
GRAVATAR_DEFAULT_IMAGE = ""
GRAVATAR_URL_PREFIX = "http://www.gravatar.com/"
GRAVATAR_DEFAULT_RATING = "g"
GRAVATAR_DEFAULT_SIZE = "48"

SITE_URL = "http://127.0.0.1:8000"

NUM_TOPICS_PER_PAGE = 20
NUM_COMMENT_PER_PAGE = 30

# Email setting
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
#EMAIL_HOST = "smtp.ym.163.com"
EMAIL_HOST = "smtp.163.com"
#EMAIL_PORT = 994
EMAIL_USE_TLS = True
#与SMTP服务器通信时，是否启动TLS链接(安全链接)。默认是false
EMAIL_HOST_USER = "18636030403@163.com"
EMAIL_HOST_PASSWORD = "woaini21G"
EMAIL_TOKEN_SALT = "helloworld"