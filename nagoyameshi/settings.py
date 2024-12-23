"""
Django settings for nagoyameshi project.

Generated by 'django-admin startproject' using Django 4.2.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

import os
import environ
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
if os.path.exists("./.is_debug"):
    DEBUG = True
else:
    DEBUG = True
    # Herokuチェックのため退避
    # DEBUG = False

ALLOWED_HOSTS = ["127.0.0.1", ".herokuapp.com"]

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    # my apps
    "restaurant",
    "accounts",
    'bootstrapform',
    # allauth
    "django.contrib.sites",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    # S3
    "storages",
]

if DEBUG:
    INSTALLED_APPS += ['debug_toolbar']

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    # "whitenoise.middleware.WhiteNoiseMiddleware",
]

if DEBUG:
    MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
    INTERNAL_IPS = ['127.0.0.1']

    DEBUG_TOOLBAR_CONFIG = {
        "SHOW_TOOLBAR_CALLBACK" : lambda request: True,
    }

ROOT_URLCONF = "nagoyameshi.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "nagoyameshi.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "ja"
TIME_ZONE = "Asia/Tokyo"
USE_I18N = True
USE_TZ = True

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# allauth
AUTH_USER_MODEL = 'accounts.CustomUser'
SITE_ID = 1
AUTHENTICATION_BACKENDS = (
    'allauth.account.auth_backends.AuthenticationBackend', # 一般ユーザー用(メールアドレス認証)
    'django.contrib.auth.backends.ModelBackend', # 管理サイト用(ユーザー名認証)
    )
 
# メールアドレス認証に変更する設定
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_USERNAME_REQUIRED = False
# サインアップにメールアドレス確認を行わない設定
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_EMAIL_REQUIRED = True
# ChatGPT指示20241130
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = False
# ChatGPT指示20241127
LOGIN_URL = 'login'
# ログイン/ログアウト後の遷移先を設定
LOGIN_REDIRECT_URL = 'top_page'
ACCOUNT_LOGOUT_REDIRECT_URL = 'top_page'
# ログアウトリンクのクリック一発でログアウトする設定
ACCOUNT_LOGOUT_ON_GET = True
# allauth アダプタ
ACCOUNT_ADAPTER = 'accounts.adapter.AccountAdapter'
# ログインフォームのカスタム用設定
ACCOUNT_FORMS = {
    'login': 'accounts.forms.MyLoginForm',
    'signup': 'accounts.forms.MySignupForm',
    }

# Initialize environment variables
env = environ.Env()
# environ.Env.read_env()  # Reads from the .env file in the same directory as manage.py
environ.Env.read_env(BASE_DIR / ".env")  # Explicitly point to the .env file

# メール設定
EMAIL_BACKEND = env("EMAIL_BACKEND", default="django.core.mail.backends.smtp.EmailBackend")
EMAIL_HOST = env("EMAIL_HOST", default="smtp.example.com")
EMAIL_PORT = env.int("EMAIL_PORT", default=587)  # Type-casting for integer
EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", default=True)  # Type-casting for boolean
EMAIL_HOST_USER = env("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD")

# Stripe設定
STRIPE_SECRET_KEY = env("STRIPE_SECRET_KEY")
STRIPE_PUBLISHABLE_KEY = env("STRIPE_PUBLISHABLE_KEY")

# YOUR_DOMAINが開発環境と本番環境で変わるように記述
# Detect the environment
ENVIRONMENT = os.getenv('DJANGO_ENV', 'development')

if ENVIRONMENT == 'production':
    YOUR_DOMAIN = "https://your-production-domain.com"
else:
    YOUR_DOMAIN = "http://127.0.0.1:8000"

# S3設定
AWS_ACCESS_KEY_ID = env("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = env("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = env("AWS_STORAGE_BUCKET_NAME")
AWS_S3_REGION_NAME = env("AWS_S3_REGION_NAME", default="us-east-1")  # リージョンのデフォルト設定
AWS_S3_CUSTOM_DOMAIN = f"{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_S3_REGION_NAME}.amazonaws.com"

# メディアファイルの設定

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/
# STATIC_URL = "static/" # S3使用前

STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATIC_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/static/"
STATICFILES_STORAGE = "storages.backends.s3boto3.S3StaticStorage"

# 開発環境でもS3を使うために静的ファイルの設定をコメントアウト
STATICFILES_DIRS = (os.path.join(BASE_DIR, "static"),) # S3使用前

# メディアファイルの設定
# MEDIA_URL = "media/"  # S3使用前
MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/media/"
MEDIA_ROOT = "media/"
DEFAULT_FILE_STORAGE = "nagoyameshi.storage_backends.MediaStorage"
# DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"

# 開発環境でもS3を使うためにメディアファイルの保存設定をコメントアウト
# MEDIA_ROOT = os.path.join(BASE_DIR, "media")  # S3使用前