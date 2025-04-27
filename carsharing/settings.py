import os
from datetime import timedelta
from pathlib import Path

from decouple import Csv, config


# Посилання на корневий шлях всередині проєкту
BASE_DIR = Path(__file__).resolve().parent.parent

# Секретний ключ для Django
SECRET_KEY = config("SECRET_KEY")

# Налаштування режиму відладки
DEBUG = config("DEBUG", cast=bool)

ALLOWED_HOSTS = config("ALLOWED_HOSTS", cast=Csv())

# Налаштування додатків
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Сторонні додатки
    "rest_framework",
    "corsheaders",
    "django_filters",

    # Додатки проєкту
    "users",
    "cars",
    "bookings",
    "payments",
    "core",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "carsharing.urls"

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

WSGI_APPLICATION = "carsharing.wsgi.application"

# База даних
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# # Для продакшн середовища рекомендується використовувати PostgreSQL
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': config('DB_NAME'),
#         'USER': config('DB_USER'),
#         'PASSWORD': config('DB_PASSWORD'),
#         'HOST': config('DB_HOST'),
#         'PORT': config('DB_PORT'),
#     }
# }

# Валідація паролів
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

# Налаштування локалізації
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Шлях де зберігаються статичні файли
STATIC_URL = "static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static")

# Шлях де зберігаються медійні файли
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# DEFAULT_AUTO_FIELD визначає тип поля для автоматично створюваних первинних ключів у моделях Django.
# "django.db.models.BigAutoField" означає, що за замовчуванням для первинних ключів буде використовуватися
# 64-бітове ціле число (BigInteger), яке автоматично збільшується.
# Це корисно для проєктів, де очікується велика кількість записів у базі даних.
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Посилання на модель користувача
AUTH_USER_MODEL = "users.User"

# URL для входу
LOGIN_REDIRECT_URL = "/accounts/profile/"

# URL для виходу
LOGOUT_REDIRECT_URL = "/accounts/login/"

# Налаштування REST Framework
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 10,
}

# Налаштування JWT
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": True,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": config("SIGNING_KEY"),
    "VERIFYING_KEY": None,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
}

# Налаштування CORS
CORS_ALLOW_ALL_ORIGINS = True  # Тільки для розробки!


CELERY_BROKER_URL = f"redis://{config('REDIS_HOST')}:{config('REDIS_PORT')}/{config('REDIS_DB')}"
CELERY_RESULT_BACKEND = CELERY_BROKER_URL
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "UTC"


# Налаштування LiqPay
LIQPAY_PUBLIC_KEY = config("LIQPAY_PUBLIC_KEY")
LIQPAY_PRIVATE_KEY = config("LIQPAY_PRIVATE_KEY")

# Налаштування платежів
MIN_PAYMENT_AMOUNT = "10.00"  # Мінімальна сума депозиту
MAX_PAYMENT_AMOUNT = "10000.00"  # Максимальна сума депозиту
