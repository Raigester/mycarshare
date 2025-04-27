import os
from datetime import timedelta
from pathlib import Path

from decouple import Csv, config


# Посилання на корневий шлях всередині проєкту
BASE_DIR = Path(__file__).resolve().parent.parent

# Секретний ключ для Django
SECRET_KEY = config("SECRET_KEY")

# Налаштування режиму відладки (True для розробки, False для продакшн середовища)
DEBUG = config("DEBUG", cast=bool)

# Список дозволених хостів для доступу до сервера
ALLOWED_HOSTS = config("ALLOWED_HOSTS", cast=Csv())

# Налаштування додатків
INSTALLED_APPS = [
    # Вбудовані додатки Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Сторонні додатки
    "rest_framework",  # Django REST Framework для створення API
    "corsheaders",  # Додаток для налаштування CORS
    "django_filters",  # Додаток для фільтрації даних у запитах

    # Додатки проєкту
    "users",  # Додаток для управління користувачами
    "cars",  # Додаток для управління автомобілями
    "bookings",  # Додаток для управління бронюваннями
    "payments",  # Додаток для управління платежами
    "core",  # Основний додаток проєкту
]

# Налаштування проміжного програмного забезпечення (middleware)
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",  # Забезпечення безпеки
    "django.contrib.sessions.middleware.SessionMiddleware",  # Управління сесіями
    "corsheaders.middleware.CorsMiddleware",  # Дозволяє налаштувати CORS
    "django.middleware.common.CommonMiddleware",  # Загальні налаштування
    "django.middleware.csrf.CsrfViewMiddleware",  # Захист від CSRF атак
    "django.contrib.auth.middleware.AuthenticationMiddleware",  # Аутентифікація користувачів
    "django.contrib.messages.middleware.MessageMiddleware",  # Управління повідомленнями
    "django.middleware.clickjacking.XFrameOptionsMiddleware",  # Захист від Clickjacking атак
]

# Головний файл конфігурації URL-адрес проєкту
ROOT_URLCONF = "carsharing.urls"

# Налаштування шаблонів для рендерингу HTML-сторінок
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",  # Використання шаблонів Django
        "DIRS": [],  # Додаткові директорії для шаблонів (порожній список за замовчуванням)
        "APP_DIRS": True,  # Увімкнення автоматичного пошуку шаблонів у додатках
        "OPTIONS": {
            "context_processors": [  # Контекстні процесори для шаблонів
                "django.template.context_processors.debug",  # Додаткові дані для налагодження
                "django.template.context_processors.request",  # Доступ до об'єкта запиту
                "django.contrib.auth.context_processors.auth",  # Інформація про аутентифікацію
                "django.contrib.messages.context_processors.messages",  # Повідомлення для користувача
            ],
        },
    },
]

# Налаштування WSGI-додатка для запуску проєкту
WSGI_APPLICATION = "carsharing.wsgi.application"

# Налаштування бази даних
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",  # Використання SQLite як бази даних за замовчуванням
        "NAME": BASE_DIR / "db.sqlite3",  # Шлях до файлу бази даних
    }
}

# # Для продакшн середовища рекомендується використовувати PostgreSQL
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',  # Використання PostgreSQL як бази даних
#         'NAME': config('DB_NAME'),  # Назва бази даних
#         'USER': config('DB_USER'),  # Ім'я користувача бази даних
#         'PASSWORD': config('DB_PASSWORD'),  # Пароль користувача бази даних
#         'HOST': config('DB_HOST'),  # Хост бази даних
#         'PORT': config('DB_PORT'),  # Порт бази даних
#     }
# }

# Валідація паролів
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation.MinimumLengthValidator"
        ),  # Перевірка мінімальної довжини пароля
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation.CommonPasswordValidator"
        ),  # Перевірка на використання поширених паролів
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation.NumericPasswordValidator"
        ),  # Перевірка на використання лише числових паролів
    },
]

# Налаштування локалізації
LANGUAGE_CODE = "en-us"  # Мова за замовчуванням
TIME_ZONE = "UTC"  # Часовий пояс за замовчуванням
USE_I18N = True  # Увімкнення інтернаціоналізації
USE_TZ = True  # Увімкнення підтримки часових зон

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
        "rest_framework_simplejwt.authentication.JWTAuthentication",  # Аутентифікація через JWT
    ),
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",  # Доступ лише для аутентифікованих користувачів
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",  # Пагінація для API
    "PAGE_SIZE": 10,  # Кількість елементів на сторінку
}

# Налаштування JWT
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=5),  # Термін дії токена доступу
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),  # Термін дії токена оновлення
    "ROTATE_REFRESH_TOKENS": False,  # Чи оновлювати токен оновлення після використання
    "BLACKLIST_AFTER_ROTATION": True,  # Додавати старі токени до чорного списку після ротації
    "ALGORITHM": "HS256",  # Алгоритм підпису токенів
    "SIGNING_KEY": config("SIGNING_KEY"),  # Ключ для підпису токенів
    "VERIFYING_KEY": None,  # Ключ для перевірки токенів
    "AUTH_HEADER_TYPES": ("Bearer",),  # Тип заголовка для передачі токена
    "USER_ID_FIELD": "id",  # Поле для ідентифікації користувача
    "USER_ID_CLAIM": "user_id",  # Поле в токені для збереження ID користувача
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),  # Клас токена доступу
    "TOKEN_TYPE_CLAIM": "token_type",  # Тип токена
}

# Налаштування CORS
CORS_ALLOW_ALL_ORIGINS = True  # Дозволити всі джерела (тільки для розробки!)

# Налаштування Celery
CELERY_BROKER_URL = f"redis://{config('REDIS_HOST')}:{config('REDIS_PORT')}/{config('REDIS_DB')}"  # URL брокера завдань
CELERY_RESULT_BACKEND = CELERY_BROKER_URL  # Бекенд для збереження результатів завдань
CELERY_ACCEPT_CONTENT = ["json"]  # Прийнятний формат даних
CELERY_TASK_SERIALIZER = "json"  # Серіалізація завдань у формат JSON
CELERY_RESULT_SERIALIZER = "json"  # Серіалізація результатів у формат JSON
CELERY_TIMEZONE = "UTC"  # Часовий пояс для завдань

# Налаштування LiqPay
LIQPAY_PUBLIC_KEY = config("LIQPAY_PUBLIC_KEY")
LIQPAY_PRIVATE_KEY = config("LIQPAY_PRIVATE_KEY")

# Налаштування платежів
MIN_PAYMENT_AMOUNT = "10.00"  # Мінімальна сума депозиту
MAX_PAYMENT_AMOUNT = "10000.00"  # Максимальна сума депозиту
