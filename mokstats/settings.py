import os

from .config import config

""" PART: Settings that are unique for each environment
********************************************************
"""

DEBUG = config.debug
ALLOWED_HOSTS = config.allowed_hosts
DATABASES = {"default": config.database}
SECRET_KEY = config.secret_key


""" PART: General settings
********************************************************
"""

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

STATIC_ROOT = "static"
STATIC_URL = "/static/"
ROOT_URLCONF = "mokstats.urls"

USE_TZ = True
TIME_ZONE = "Etc/UTC"
LANGUAGE_CODE = "en-us"
USE_I18N = False  # Translations are not used

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATICFILES_DIRS = (os.path.join(BASE_DIR, "mokstats/static"),)

STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
)

INSTALLED_APPS = (
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "mokstats",
)

MIDDLEWARE = (
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # Site wide Cache (https://docs.djangoproject.com/en/1.11/topics/cache/#the-per-site-cache)
    "django.middleware.cache.UpdateCacheMiddleware",
    "django.middleware.cache.FetchFromCacheMiddleware",
)

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.debug",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.template.context_processors.request",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# CACHE_SECONDS = 60*60*24*365 # 1 year
# CACHES = {
#     'default': {
#         'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
#         'LOCATION': 'site_cache',
#         'TIMEOUT': CACHE_SECONDS,
#     }
# }
# CACHE_MIDDLEWARE_SECONDS = CACHE_SECONDS
