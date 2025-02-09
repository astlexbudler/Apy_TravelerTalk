from pathlib import Path
import os

##################################################
# 기본 정보 설정
##################################################
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-ysfp9p2+rl$28l!t*7mlg=y7@h6a!^j^xmv69t75o(e@=!p=o9'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

X_FRAME_OPTIONS = 'ALLOWALL'

XS_SHARING_ALLOWED_METHODS = ['POST', 'GET', 'OPTIONS', 'PUT', 'DELETE']

##################################################
# Application 설정
##################################################
# Application definition
INSTALLED_APPS = [
  'django.contrib.admin',
  'django.contrib.auth',
  'django.contrib.contenttypes',
  'django.contrib.sessions',
  'django.contrib.messages',
  'django.contrib.staticfiles',
  'django.contrib.sites',
  'django.contrib.sitemaps',
  'app_core',
  'app_api',
  'app_user',
  'app_partner',
  'app_supervisor',
  'app_post',
  'app_coupon',
  'app_message',
  'corsheaders',
  'django_hosts',
]

AUTHENTICATION_BACKENDS = [
  'django.contrib.auth.backends.ModelBackend',
]

MIDDLEWARE = [
  'django_hosts.middleware.HostsRequestMiddleware',
  'django.middleware.security.SecurityMiddleware',
  'django.contrib.sessions.middleware.SessionMiddleware',
  'django.middleware.common.CommonMiddleware',
  'django.middleware.csrf.CsrfViewMiddleware',
  'django.contrib.auth.middleware.AuthenticationMiddleware',
  'django.contrib.messages.middleware.MessageMiddleware',
  'django.middleware.clickjacking.XFrameOptionsMiddleware',
  'django_hosts.middleware.HostsResponseMiddleware',
  'corsheaders.middleware.CorsMiddleware',
]

# scheduler 설정
APSCHEDULER_DATETIME_FORMAT = "N J, Y, f:s a"
SCHEDULER_DEFAULT = True

# sitemap 설정
SITE_ID = 2
SITE_DOMAIN = 'kibang01.com'
CSRF_TRUSTED_ORIGINS=[
    'http://127.0.0.1:8000', 
    'http://kibang01.com', 'http://partner.kibang01.com', 'http://spv.kibang01.com',
    'http://kibang02.com', 'http://partner.kibang02.com', 'http://spv.kibang02.com',
]

#MAIN_URL = os.getenv('MAIN_URL', 'http://kibang01.com') # 메인 도메인
#PARTNER_URL = os.getenv('PARTNER_URL', 'http://partner.kibang01.com') # 파트너 도메인
#SUPERVISOR_URL = os.getenv('SUPERVISOR_URL', 'http://spv.kibang01.com') # 슈퍼바이저 도메인
MAIN_URL = os.getenv('MAIN_URL', 'http://127.0.0.1:8000')  # 테스트용
PARTNER_URL = os.getenv('PARTNER_URL', 'http://127.0.0.1:8000/partner') # 테스트용
SUPERVISOR_URL = os.getenv('SUPERVISOR_URL', 'http://127.0.0.1:8000/supervisor') # 테스트용

ROOT_URLCONF = 'apptoaster.urls'

# django-host 설정
ROOT_HOSTCONF = 'apptoaster.hosts'
DEFAULT_HOST = 'main'

# CORS 설정
CORS_ORIGIN_ALLOW_ALL = True
SECURE_CROSS_ORIGIN_OPENER_POLICY='same-origin-allow-popups'

##################################################
# template 설정
##################################################
TEMPLATES = [
  {
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [os.path.join(BASE_DIR, 'templates')],
    'APP_DIRS': True,
    'OPTIONS': {
      'context_processors': [
        'django.template.context_processors.debug',
        'django.template.context_processors.request',
        'django.contrib.auth.context_processors.auth',
        'django.contrib.messages.context_processors.messages',
        'apptoaster.context_processors.main_url',
      ],
    },
  },
]

WSGI_APPLICATION = 'apptoaster.wsgi.application'



##################################################
# 데이터베이스 설정
##################################################
# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

AUTH_USER_MODEL = 'app_core.ACCOUNT' # User model 설정
DATABASES = {
  'default': {
    'ENGINE': 'django.db.backends.sqlite3',
    'NAME': BASE_DIR / 'db.sqlite3',
  }
}



##################################################
# 비밀번호
##################################################
# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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



##################################################
# 서버 time zone 설정
##################################################
# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Seoul'

USE_I18N = True

USE_L10N = True

USE_TZ = False

##################################################
# static, media 디렉토리 설정
##################################################
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'

STATIC_ROOT = os.path.join('staticfiles')

STATICFILES_DIRS = [
  os.path.join(BASE_DIR, 'static'),
]

MEDIA_URL = '/media/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

##################################################
# model 기본 primary key 설정
##################################################
# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'