import os
import subprocess

import environ

app_dir = environ.Path(__file__) - 2
assert os.path.exists(app_dir('manage.py'))

env_file = app_dir('.env')
parent_dir = app_dir.path('..')
default_var_root = parent_dir('var')
default_log_root = parent_dir('log')

env = environ.Env(
    DEBUG=(bool, True),
    TIER=(str, 'dev'),  # one of: prod, qa, stage, test, dev
    SECRET_KEY=(str, ''),
    VAR_ROOT=(str, default_var_root),
    LOG_ROOT=(str, default_log_root),
    ALLOWED_HOSTS=(list, []),
    DATABASE_URL=(str, 'postgis:///datahubhel'),
    CACHE_URL=(str, 'locmemcache://'),
    EMAIL_URL=(str, 'consolemail://'),
    SENTRY_DSN=(str, ''),
    TUNNISTAMO_ISSUER_URL=(str, ''),  # Default depends on TIER, see below
)
if os.path.exists(env_file):  # pragma: no cover
    env.read_env(env_file)

DEBUG = env.bool('DEBUG')
TIER = env.str('TIER')
SECRET_KEY = env.str('SECRET_KEY') or ('xxx' if DEBUG else '')
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS')

TUNNISTAMO_ISSUER_URL = env.str('TUNNISTAMO_ISSUER_URL', default=(
    'http://localhost:8000/openid' if TIER == 'dev' else
    'https://api.hel.fi/sso/openid'))

DATABASES = {'default': env.db()}
CACHES = {'default': env.cache()}
vars().update(env.email_url())  # EMAIL_BACKEND, EMAIL_HOST, etc.

RAVEN_CONFIG = {
    'dsn': env.str('SENTRY_DSN'),
    'release': subprocess.Popen(
        'git describe --always --dirty', cwd=parent_dir(), shell=True,
        stdout=subprocess.PIPE).communicate()[0].decode('utf-8').strip() if (
            os.path.exists(parent_dir('.git'))) else None,
}

var_root = env.path('VAR_ROOT')
MEDIA_ROOT = var_root('media')
STATIC_ROOT = var_root('static')
MEDIA_URL = '/media/'
STATIC_URL = '/static/'

log_root = env.path('LOG_ROOT')

ROOT_URLCONF = 'datahubhel.urls'
WSGI_APPLICATION = 'datahubhel.wsgi.application'

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Europe/Helsinki'
USE_I18N = True
USE_L10N = True
USE_TZ = True


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',
    'raven.contrib.django.raven_compat',
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'django_extensions',
    'datahubhel',
    'datahubhel.gatekeeper',
    'datahubhel.mqttauth',
    'datahubhel.service',
    'datahubhel.dhh_auth',
    'ta120_adapter',
    'datahubhel.core',
    'datahubhel.sta',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

AUTH_USER_MODEL = 'dhh_auth.User'

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

AUTH_PASSWORD_VALIDATORS = [] if DEBUG else [
    {'NAME': 'django.contrib.auth.password_validation.' + name} for name in [
        'UserAttributeSimilarityValidator',
        'MinimumLengthValidator',
        'CommonPasswordValidator',
        'NumericPasswordValidator',
    ]
]

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ] + ([
        'rest_framework.renderers.BrowsableAPIRenderer',
    ] if DEBUG else []),
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'helusers.oidc.ApiTokenAuthentication',
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
        'datahubhel.dhh_auth.authentication.UserTokenAuthentication',
        'datahubhel.service.authentication.ServiceTokenAuthentication',
    ] + ([
        'rest_framework.authentication.SessionAuthentication',
    ] if DEBUG else []),
}

OIDC_API_TOKEN_AUTH = {
    'AUDIENCE': 'https://api.forumvirium.fi/auth/datahubhel',
    'API_AUTHORIZATION_FIELD': 'https://api.hel.fi/auth',
    'ISSUER': TUNNISTAMO_ISSUER_URL,
    'USER_RESOLVER': 'dhh_auth.tunnistamo.resolve_user',
}

CORS_ORIGIN_ALLOW_ALL = True

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': log_root('datahubhel_backend.log'),
            'formatter': 'verbose',
        },
    },
    'loggers': {
        '': {
            'level': 'WARNING',
            'handlers': ['console'],
        },
        'gatekeeper': {
            'level': 'INFO',
            'handlers': ['file', 'console'],
            'propagate': False,
        },
        'mqttauth': {
            'level': 'INFO',
            'handlers': ['file', 'console'],
            'propagate': False,
        },
    },
}

STA_VERSION = 'v1.0'
GATEKEEPER_STS_BASE_URL = 'http://localhost:8080/FROST-Server'
