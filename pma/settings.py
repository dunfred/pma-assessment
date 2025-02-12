"""
Django settings for pma project.

Generated by 'django-admin startproject' using Django 5.1.5.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

from datetime import timedelta
import os
from pathlib import Path
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# try to load local dev env vars, if not found, load dotenv for prod
try:
    '''load local dev env file'''
    load_dotenv(os.path.join(BASE_DIR, '.env.dev'), override=True)
except:
    '''try to load Docker Staging env file'''
    load_dotenv(os.path.join(BASE_DIR, '.env'), override=True)
else:
    '''load production env file'''
    load_dotenv(override=True)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG =  bool(int(os.getenv('DEBUG', 0)))

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')

# Application definition

INSTALLED_APPS = [
    'dal',
    'dal_select2',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Custom
    'apps.user',
    'apps.project',

    #Third Party
    'storages',
    'corsheaders',
    'rest_framework',
    'rest_framework.authtoken',
    'tz_detect',
    'rest_framework_simplejwt.token_blacklist',
    'django_cleanup.apps.CleanupConfig',
    'django_admin_listfilter_dropdown',
    'drf_spectacular',
    'drf_spectacular_sidecar',  # required for Django collectstatic discovery
    'django_filters',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'apps.user.middleware.TokenBlacklistMiddleware',
]

ROOT_URLCONF = 'pma.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
                BASE_DIR / 'templates'
            ],
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

WSGI_APPLICATION = 'pma.wsgi.application'

AUTH_USER_MODEL = 'user.User'

# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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

REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_RENDERER_CLASSES': ('api.utils.renderers.CustomResponseRenderer',),
    'EXCEPTION_HANDLER': 'api.utils.validation.custom_exception_handler',
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
      'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
        'rest_framework.parsers.JSONParser',
     ],
     'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
     ],

     # Test
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',

    'TEST_REQUEST_RENDERER_CLASSES': [
        'rest_framework.renderers.MultiPartRenderer',
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.TemplateHTMLRenderer'
    ]
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'ISSUER': None,'AUTH_HEADER_TYPES': ('Bearer', 'JWT'),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    'JTI_CLAIM': 'jti',
}

SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Bearer': {'type': 'apiKey', 'name': 'Authorization', 'in': 'header'},
        'Basic': {'type': 'basic'},
    }
}

SPECTACULAR_SETTINGS = {
    'SWAGGER_UI_DIST': 'SIDECAR',  # shorthand to use the sidecar instead
    'SWAGGER_UI_FAVICON_HREF': 'SIDECAR',
    'REDOC_DIST': 'SIDECAR',
    'TITLE': 'PMA API Documentation',
    'DESCRIPTION': "Project Management Application (PMA) backend API based on the OpenAPI 3.0 specification.",
    'VERSION': '1.0.11',
    'SERVE_PUBLIC': False,
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
    # Disable warning logs
    'DISABLE_ERRORS_AND_WARNINGS': True,
    'SERVE_PERMISSIONS': ['rest_framework.permissions.AllowAny'],
    'LICENSE': {
        'name': 'Apache 2.0',
        'url': 'http://www.apache.org/licenses/LICENSE-2.0.html',
    },
    'SERVERS': [
        {
            'url': 'http://127.0.0.1:8000',
            'description': 'Local Server',
        }
    ],
    'TAGS': [],
    'EXTERNAL_DOCS': {
        'description': 'Find out more about Swagger',
        'url': 'http://swagger.io',
    },
}

# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

AWS_ACCESS_KEY_ID       = os.getenv("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_ACCESS_KEY   = os.getenv("AWS_SECRET_ACCESS_KEY", "")
AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME", "")
AWS_S3_REGION_NAME      = os.getenv("AWS_STORAGE_REGION", "")

USE_S3 = all([
    AWS_ACCESS_KEY_ID != "",
    AWS_SECRET_ACCESS_KEY != "",
    AWS_S3_REGION_NAME != "",
    AWS_STORAGE_BUCKET_NAME != ""
])

if USE_S3:
    AWS_S3_FILE_OVERWRITE    = False
    AWS_QUERYSTRING_AUTH     = False
    AWS_S3_CUSTOM_DOMAIN     = '%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME
    AWS_S3_OBJECT_PARAMETERS = {"CacheControl": "max-age=86400"}
    AWS_DEFAULT_ACL          = os.getenv("AWS_DEFAULT_ACL", "public-read")

    # STORAGES configuration
    STORAGES = {
        "default": {
            "BACKEND": "pma.mediastorages.MediaStorage",
            "OPTIONS": {
                "access_key": AWS_ACCESS_KEY_ID,
                "secret_key": AWS_SECRET_ACCESS_KEY,
                "bucket_name": AWS_STORAGE_BUCKET_NAME,
                "region_name": AWS_S3_REGION_NAME,
                "default_acl": "public-read",
                "querystring_auth": False,
                "object_parameters": AWS_S3_OBJECT_PARAMETERS,
            },
        },
        "staticfiles": {
            "BACKEND": "pma.mediastorages.StaticStorage",
            "OPTIONS": {
                "access_key": AWS_ACCESS_KEY_ID,
                "secret_key": AWS_SECRET_ACCESS_KEY,
                "bucket_name": AWS_STORAGE_BUCKET_NAME,
                "region_name": AWS_S3_REGION_NAME,
                "default_acl": "public-read",
                "querystring_auth": False,  # Static files usually don't need signed URLs
                "object_parameters": AWS_S3_OBJECT_PARAMETERS,
                "location": "static",
            },
        },
        "media": {
            "BACKEND": "pma.mediastorages.MediaStorage",
            "OPTIONS": {
                "access_key": AWS_ACCESS_KEY_ID,
                "secret_key": AWS_SECRET_ACCESS_KEY,
                "bucket_name": AWS_STORAGE_BUCKET_NAME,
                "region_name": AWS_S3_REGION_NAME,
                "default_acl": None, # Important to avoid ACL issues
                "querystring_auth": False, # Set to True if you want signed URLs for media
                "location": "media",
            },
        },
        "private": {
            "BACKEND": "pma.mediastorages.PrivateMediaStorage",
            "OPTIONS": {
                "access_key": AWS_ACCESS_KEY_ID,
                "secret_key": AWS_SECRET_ACCESS_KEY,
                "bucket_name": AWS_STORAGE_BUCKET_NAME,
                "region_name": AWS_S3_REGION_NAME,
                "default_acl": 'private',
                "querystring_auth": True,  # If you want signed URLs for media
                "object_parameters": AWS_S3_OBJECT_PARAMETERS,
            },
        },
    }

    # URLs for serving static and media files
    STATIC_URL = f"https://{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/static/"
    MEDIA_URL = f"https://{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/media/"

else:
    # Use Django default static files config if no S3 creds were provided.
    DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
    STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
    
    STATIC_URL = 'static/'
    STATIC_ROOT = BASE_DIR / "staticfiles"

    MEDIA_URL = '/media/'
    MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
