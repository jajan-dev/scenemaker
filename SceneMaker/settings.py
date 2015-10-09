"""
Django settings for SceneMaker project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'cs_@fveuuo1k#*8y+y301j@1+n^z!2a6@^7+2s_)d#q4t_9#1@'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'API',
    'storages',
    'south',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 'django.contrib.admin',
    # 'django.contrib.admindocs',
)

ROOT_URLCONF = 'SceneMaker.urls'

WSGI_APPLICATION = 'SceneMaker.wsgi.application'

# Honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# View Templates
TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, 'templates'),
)

if os.environ.has_key('ATHENA_SYS'):
    PRODUCTION = True
    USE_AWS = True
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
    AWS_ACCESS_KEY_ID = 'AKIAIEV4LDWLMWWHLDMA'
    AWS_SECRET_ACCESS_KEY = '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'
    AWS_STORAGE_BUCKET_NAME = 'jajan-scenemaker-assets'
    AWS_QUERYSTRING_AUTH = False
    AWS_S3_FILE_OVERWRITE = True
    DATABASES = {
        'default' : {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'jajan+scenemaker',
            'USER': 'jajan',
            'PASSWORD': 'jajandevpw',
            'HOST': 'sql.mit.edu'
        }
    }
    SCENEMAKER_URL = "/scenemaker/"
else:
    PRODUCTION = False
    # Database
    # https://docs.djangoproject.com/en/1.6/ref/settings/#databases
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': 'mydatabase',
        }
    }

    # Media
    USE_AWS = False
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
    MEDIA_URL = '/media/'
    SCENEMAKER_URL = '/'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_ROOT = 'staticfiles'
STATIC_URL = '/static/'

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)