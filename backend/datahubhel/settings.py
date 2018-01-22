import os
import subprocess

import environ

checkout_dir = environ.Path(__file__) - 3
assert os.path.exists(checkout_dir('backend/manage.py'))

parent_dir = checkout_dir.path('..')
etc_dir = parent_dir('etc')
env_file = etc_dir('env') if os.path.isdir(etc_dir) else checkout_dir('.env')
root_dir = parent_dir if os.path.isdir(etc_dir) else checkout_dir
default_var_root = root_dir('var')

env = environ.Env(
    DEBUG=(bool, True),
    TIER=(str, 'dev'),  # one of: prod, qa, stage, test, dev
    SECRET_KEY=(str, ''),
    VAR_ROOT=(str, default_var_root),
    ALLOWED_HOSTS=(list, []),
    DATABASE_URL=(str,
                  'postgres://datahubhel:datahubhel@localhost/datahubhel'),
    CACHE_URL=(str, 'locmemcache://'),
    EMAIL_URL=(str, 'consolemail://'),
    SENTRY_DSN=(str, ''),
)
if os.path.exists(env_file):  # pragma: no cover
    env.read_env(env_file)

DEBUG = env.bool('DEBUG')
TIER = env.str('TIER')
SECRET_KEY = env.str('SECRET_KEY') or ('xxx' if DEBUG else '')
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS')

DATABASES = {'default': env.db()}
CACHES = {'default': env.cache()}
vars().update(env.email_url())  # EMAIL_BACKEND, EMAIL_HOST, etc.

RAVEN_CONFIG = {
    'dsn': env.str('SENTRY_DSN'),
    'release': subprocess.Popen(
        'git describe --always --dirty', cwd=checkout_dir(), shell=True,
        stdout=subprocess.PIPE).communicate()[0].decode('utf-8').strip(),
}

var_root = env.path('VAR_ROOT')
MEDIA_ROOT = var_root('media')
STATIC_ROOT = var_root('static')
MEDIA_URL = '/media/'
STATIC_URL = '/static/'

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
    'raven.contrib.django.raven_compat',
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'guardian',
    'datahubhel',
    'gatekeeper',
    'mqttauth',
]

MIDDLEWARE_CLASSES = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

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
    'gatekeeper.backends.TokenBackend',
    'django.contrib.auth.backends.ModelBackend',
    'guardian.backends.ObjectPermissionBackend',
]

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
    ] + ([
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ] if DEBUG else []),
}

CORS_ORIGIN_ALLOW_ALL = True

STA_VERSION = 'v1.0'
GATEKEEPER_STS_BASE_URL = 'http://localhost:8080/SensorThingsService'
