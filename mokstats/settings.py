import os


""" PART: Settings that are unique for each environment
********************************************************
"""

DEBUG = True
ALLOWED_HOSTS = ["*"]
# DATABASES = {"default": config.database}
SECRET_KEY = "asd"


# Database settings
if os.getenv('SERVER_SOFTWARE', '').startswith('Google App Engine'):
    # Running on production App Engine, so connect to Google Cloud SQL using
    # the unix socket at /cloudsql/<your-cloudsql-connection string>
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'HOST': '??',
            'NAME': 'mokstats',
            'USER': '??',
            'PASSWORD': '??',
        }
    }
else:
    DATABASES = {
        'default': {
            "ENGINE": os.environ.get("DB_ENGINE", "django.db.backends.postgresql"),
            "HOST": os.environ.get("DB_HOST", "localhost"),
            "PORT": os.environ.get("DB_PORT", "5432"),
            "NAME": os.environ.get("DB_NAME", "mokstats"),
            "USER": os.environ.get("DB_USER", "mokstats"),
            "PASSWORD": os.environ.get("DB_PASSWORD", "mokstats"),
        }
    }
    # Running locally so connect to either a local MySQL instance or connect to
    # Cloud SQL via the proxy. To start the proxy via command line:
    #
    #     $ cloud_sql_proxy -instances=[INSTANCE_CONNECTION_NAME]=tcp:3306
    #
    # See https://cloud.google.com/sql/docs/mysql-connect-proxy
    # if DEV_USE_LOCAL_PROD_DB_PROXY:
    #     DATABASES = {
    #         'default': {
    #             'ENGINE': 'django.db.backends.mysql',
    #             'HOST': '127.0.0.1',
    #             'PORT': '3307',
    #             'NAME': 'mokstats',
    #             'USER': '??',
    #             'PASSWORD': '??',
    #         }
    #     }

""" PART: General settings
********************************************************
"""

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

STATIC_ROOT = 'static'
STATIC_URL = '/static/'
ROOT_URLCONF = 'mokstats.urls'

USE_TZ = True
TIME_ZONE = "Etc/UTC"
LANGUAGE_CODE = "en-us"
USE_I18N = False  # Translations are not used

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "mokstats/static"),
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'mokstats',
)

MIDDLEWARE = (
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # Site wide Cache (https://docs.djangoproject.com/en/1.11/topics/cache/#the-per-site-cache)
    'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',
)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                "django.template.context_processors.tz",
                'django.template.context_processors.request',
                'django.contrib.messages.context_processors.messages',
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
