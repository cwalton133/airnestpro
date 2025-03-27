from pathlib import Path
import os
from django.contrib.messages import constants as messages
from dotenv import load_dotenv
from environs import Env

load_dotenv()  


env = Env()
env.read_env()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-t_mf(p8fu^wl#xsmg@nq)du!i4#ytrrpl=lebs1q3q*dl8vu+o"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_filters",
    "core",
    "taggit",
    "userauths",
    "django_ckeditor_5",
    "rest_framework",
    "rest_framework.authtoken",
    #"django_summernote",
    "tinymce",
    "corsheaders",
    'drf_yasg',
    # Default Django apps.
    "django_extensions", 
    "paypal.standard",
    "paystack",

]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',  
    ],
        'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
    ),
}

# Allow only specific frontend origins (Recommended for security)
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5500",  
    "http://localhost:5173",  
     "http://localhost:8000",  

]

# Enable CORS for specific HTTP methods (optional)
CORS_ALLOW_METHODS = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]

# Allow frontend to send Authorization headers (for JWT tokens)
CORS_ALLOW_HEADERS = ["Authorization", "Content-Type"]


CSRF_TRUSTED_ORIGINS = [
    "http://127.0.0.1:8000",
    "http://localhost:5173",  
]
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "https://airrnest.vercel.app"
]
CORS_ALLOW_CREDENTIALS = True

ROOT_URLCONF = "airbnbrental.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = "airbnbrental.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'airbnb.db',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Africa/Lagos"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/


STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MEDIA_URL = '/media/'

MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


AUTH_USER_MODEL = "userauths.User"

# CKEDITOR_UPLOAD_PATH = "uploads/"
# CKEDITOR_RESTRICT_BY_USER = True


SESSION_COOKIE_AGE = 86400  # 1 day
SESSION_EXPIRE_AT_BROWSER_CLOSE = False


# PayPal Configuration
PAYPAL_MODE = "sandbox"  
PAYPAL_CLIENT_ID = os.getenv("PAYPAL_CLIENT_ID", "admin@airbnbrealty.com")
PAYPAL_SECRET = os.getenv("PAYPAL_SECRET", "your-paypal-secret")
PAYPAL_ACCESS_TOKEN = os.getenv("PAYPAL_ACCESS_TOKEN", "your-paypal-access-token")

# Paystack Configuration
PAYSTACK_PUBLIC_KEY = os.getenv("PAYSTACK_PUBLIC_KEY", "your-paystack-public-key")
PAYSTACK_SECRET_KEY = os.getenv("PAYSTACK_SECRET_KEY", "your-paystack-secret-key")
PAYSTACK_BASE_URL = "https://api.paystack.co"

# Stripe Configuration
STRIPE_PUBLIC_KEY = os.getenv("STRIPE_PUBLIC_KEY", "your-stripe-public-key")
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "your-stripe-secret-key")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "your-stripe-webhook-secret")


# Debugging: Print API Keys (Remove in production)
if os.getenv("DEBUG", "True") == "True":
    print("🔍 PAYPAL_CLIENT_ID:", PAYPAL_CLIENT_ID)
    print("🔍 PAYSTACK_SECRET_KEY:", PAYSTACK_SECRET_KEY)
    print("🔍 STRIPE_SECRET_KEY:", STRIPE_SECRET_KEY)
    
    
    TINYMCE_DEFAULT_CONFIG = {
    'height': 500,
    'width': 800,
    'toolbar': 'undo redo | bold italic | link image | alignleft aligncenter alignright | bullist numlist outdent indent',
    'plugins': 'advlist autolink link image lists charmap print preview',
}



