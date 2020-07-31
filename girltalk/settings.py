"""
Django settings for girltalk project.

Generated by 'django-admin startproject' using Django 3.0.3.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os
import environ
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
from django.core.mail.backends.smtp import EmailBackend




BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env=environ.Env()
environ.Env.read_env()


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('APP_SECRET_KEY')


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1','localhost','ac6e9e4ee35a.ngrok.io']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'accounts.apps.AccountsConfig',
    'subscription.apps.SubscriptionConfig',
    'system_admin.apps.SystemAdminConfig',
    'paypal.standard.ipn',
    'djstripe',

]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    #'accounts.middleware.OneSessionPerUserMiddleware',
]

ROOT_URLCONF = 'girltalk.urls'

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

WSGI_APPLICATION = 'girltalk.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases
#PRODUCTION DATABASE CONNECTION

if DEBUG:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': env('DATABASE_NAME_LOCAL'),
            'USER': env('DATABASE_USER_LOCAL'),
            'PASSWORD': env('DATABASE_PASSWORD_LOCAL'),
            'HOST': env('DATABASE_HOST_LOCAL'),

        }
    }

else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': env('DATABASE_NAME_PRODUCTION'),
            'USER': env('DATABASE_USER_PRODUCTION'),
            'PASSWORD': env('DATABASE_PASSWORD_PRODUCTION'),
            'HOST': env('DATABASE_HOST_PRODUCTION'),

        }
    }
















#STRIPE LIVE KEYS
STRIPE_PUBLIC_KEY = env('STRIPE_PUBLIC_KEY')
STRIPE_LIVE_SECRET_KEY =env('STRIPE_LIVE_SECRET_KEY')
STRIPE_LIVE_MODE = True
DJSTRIPE_WEBHOOK_SECRET = "whsec_xxx"  # We don't use this, but it must be set

#STRIPE TEST DETAILS
STRIPE_PUBLIC_KEY = env('STRIPE_PUBLIC_KEY')
STRIPE_TEST_SECRET_KEY  =env('STRIPE_TEST_SECRET_KEY')
STRIPE_LIVE_MODE = False
DJSTRIPE_WEBHOOK_SECRET = "whsec_xxx"  # We don't use this, but it must be set

#PayPal Details
PAYPAL_RECEIVER_EMAIL = 'knovitecards@gmail.com'
PAYPAL_TEST = False

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True
#Configuring sending emails
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'girltallk7@gmail.com'
EMAIL_HOST_PASSWORD = 'qjabetllzeplyvqf'
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),]

STATIC_URL = '/static/'


