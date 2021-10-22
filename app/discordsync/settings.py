import os
import sentry_sdk
from distutils.util import strtobool
from celery.schedules import crontab
from sentry_sdk.integrations.django import DjangoIntegration

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT_URLCONF = 'discordsync.urls'
WSGI_APPLICATION = 'discordsync.wsgi.application'
AUTH_USER_MODEL = 'oauth.CustomUser'

LOGIN_REDIRECT_URL = '/'
LOGIN_URL = '/oauth/'
STATIC_URL = '/static/'
MEDIA_URL = '/media/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
TEMPLATES_DIRS = [os.path.join(BASE_DIR, 'templates')]

SESSION_COOKIE_AGE = int(os.getenv('SESSION_COOKIE_AGE', 3600 * 24 * 14))
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '*').split(' ')
DEBUG = strtobool(os.getenv('DEBUG', 'False'))
SECRET_KEY = os.environ['SECRET_KEY']
STATIC_ROOT = os.environ['STATIC_ROOT']
MEDIA_ROOT = os.environ['MEDIA_ROOT']

LANGUAGE_CODE = os.getenv('LANGUAGE_CODE', 'en-us')
DATETIME_FORMAT = os.getenv('DATETIME_FORMAT', 'N j, Y, f A')
TIME_ZONE = os.getenv('TZ', 'America/Los_Angeles')
USE_TZ = strtobool(os.getenv('USE_TZ', 'True'))

USE_I18N = True
USE_L10N = True

USE_X_FORWARDED_HOST = strtobool(os.getenv('USE_X_FORWARDED_HOST', 'False'))
SECURE_REFERRER_POLICY = os.getenv('SECURE_REFERRER_POLICY', 'no-referrer')
# SESSION_ENGINE = 'django.contrib.sessions.backends.cache'

OAUTH_CLIENT_ID = os.environ['OAUTH_CLIENT_ID']
OAUTH_CLIENT_SECRET = os.environ['OAUTH_CLIENT_SECRET']
OAUTH_REDIRECT_URI = os.environ['OAUTH_REDIRECT_URI']
OAUTH_GRANT_TYPE = os.environ['OAUTH_GRANT_TYPE']
OAUTH_SCOPE = os.environ['OAUTH_SCOPE']

DISCORD_API_URL = os.environ['DISCORD_API_URL'].rstrip('/')
DISCORD_BOT_REDIRECT = os.environ['DISCORD_BOT_REDIRECT']
DISCORD_BOT_TOKEN = os.environ['DISCORD_BOT_TOKEN']
DISCORD_URL = os.environ['DISCORD_URL']

CELERY_RESULT_BACKEND = os.environ['CELERY_RESULT_BACKEND']
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = os.getenv('TZ', 'America/Los_Angeles')

CELERY_BEAT_SCHEDULE = {
    'daily_cleanup': {
        'task': 'home.tasks.clear_sessions',
        'schedule': crontab(minute=0, hour=0),
    },
}

CACHES = {
    'default': {
        'BACKEND': os.getenv('CACHE_BACKEND',
                             'django.core.cache.backends.locmem.LocMemCache'),
        'LOCATION': os.getenv('CACHE_LOCATION', 'localhost:11211'),
        'OPTIONS': {
            'server_max_value_length': 1024 * 1024 * 4,
        }
    }
}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ['DATABASE_NAME'],
        'USER': os.environ['DATABASE_USER'],
        'PASSWORD': os.environ['DATABASE_PASS'],
        'HOST': os.environ['DATABASE_HOST'],
        'PORT': os.environ['DATABASE_PORT'],
        'OPTIONS': {
            'isolation_level': 'repeatable read',
            'init_command': "SET sql_mode='STRICT_ALL_TABLES'",
        },
    }
}

if 'SENTRY_URL' in os.environ:
    sentry_sdk.init(
        dsn=os.environ['SENTRY_URL'],
        integrations=[DjangoIntegration()],
        traces_sample_rate=float(os.getenv('SENTRY_SAMPLE_RATE', 1.0)),
        send_default_pii=True,
        debug=strtobool(os.getenv('SENTRY_DEBUG', os.getenv('DEBUG', 'False'))),
    )

if DEBUG:
    DEBUG_TOOLBAR_PANELS = [
        'debug_toolbar.panels.versions.VersionsPanel',
        'debug_toolbar.panels.timer.TimerPanel',
        'debug_toolbar.panels.settings.SettingsPanel',
        'debug_toolbar.panels.headers.HeadersPanel',
        'debug_toolbar.panels.request.RequestPanel',
        'debug_toolbar.panels.sql.SQLPanel',
        'debug_toolbar.panels.staticfiles.StaticFilesPanel',
        'debug_toolbar.panels.templates.TemplatesPanel',
        'debug_toolbar.panels.cache.CachePanel',
        'debug_toolbar.panels.signals.SignalsPanel',
        'debug_toolbar.panels.logging.LoggingPanel',
        'debug_toolbar.panels.redirects.RedirectsPanel',
    ]

    def show_toolbar(request):
        return True if request.user.is_superuser else False

    DEBUG_TOOLBAR_CONFIG = {'SHOW_TOOLBAR_CALLBACK': show_toolbar}


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': ('%(asctime)s - '
                       '%(levelname)s - '
                       '%(filename)s '
                       '%(module)s.%(funcName)s:%(lineno)d - '
                       '%(message)s'),
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': True,
        },
        'app': {
            'handlers': ['console'],
            'level': os.getenv('APP_LOG_LEVEL', 'DEBUG'),
            'propagate': True,
        },
    },
}

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_celery_beat',
    'django_extensions',
    'debug_toolbar',
    'home',
    'oauth',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': TEMPLATES_DIRS,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.media',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.static',
            ],
        },
    },
]
