import os
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
    "carsharing.ratelimit_middleware.GlobalRateLimitMiddleware",  # Додано обмеження швидкості
    "django.contrib.sessions.middleware.SessionMiddleware",  # Управління сесіями
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
        "DIRS": [BASE_DIR / "templates"],  # Додаткові директорії для шаблонів (порожній список за замовчуванням)
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

# База даних
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",  # Використання PostgreSQL як бази даних
        "NAME": config("DB_NAME"),  # Назва бази даних
        "USER": config("DB_USER"),  # Ім'я користувача бази даних
        "PASSWORD": config("DB_PASSWORD"),  # Пароль користувача бази даних
        "HOST": config("DB_HOST"),  # Хост бази даних
        "PORT": config("DB_PORT"),  # Порт бази даних
    }
}

# Валідація паролів
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
        ),  # Перевірка схожості пароля з атрибутами користувача такими як персональні дані
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
LANGUAGE_CODE = "uk"  # Мова за замовчуванням
TIME_ZONE = "Europe/Kyiv"  # Часовий пояс за замовчуванням
USE_I18N = True  # Увімкнення інтернаціоналізації (для підтримки різних мов)
USE_TZ = True  # Увімкнення підтримки часових зон (для підтримки різних часових поясів)

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

# Налаштування Celery
CELERY_BROKER_URL = f"redis://{config('REDIS_HOST')}:{config('REDIS_PORT')}/{config('REDIS_DB')}"  # URL брокера завдань
CELERY_RESULT_BACKEND = CELERY_BROKER_URL  # Бекенд для збереження результатів завдань
CELERY_ACCEPT_CONTENT = ["json"]  # Прийнятний формат даних
CELERY_TASK_SERIALIZER = "json"  # Серіалізація завдань у формат JSON
CELERY_RESULT_SERIALIZER = "json"  # Серіалізація результатів у формат JSON
CELERY_TIMEZONE = "Europe/Kyiv"  # Часовий пояс для завдань

# Email налаштування
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend" # Використання консолі для відправки електронних листів
EMAIL_HOST = "localhost" # Хост для SMTP-сервера
EMAIL_PORT = 1025 # Порт для SMTP-сервера
EMAIL_USE_TLS = False # Використання TLS для безпеки
EMAIL_HOST_USER = "" # Ім'я користувача для SMTP-сервера
EMAIL_HOST_PASSWORD = "" # Пароль для SMTP-сервера
BASE_URL = "http://localhost" # Базовий URL для електронних листів

# Налаштування кешу для обмеження частоти запитів
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache", # Використання Redis як кешу
        "LOCATION": f"redis://{config('REDIS_HOST')}:{config('REDIS_PORT')}/{config('REDIS_DB')}", # URL Redis
    }
}

# Налаштування для django-ratelimit
RATELIMIT_USE_CACHE = "default" ## Використання кешу для зберігання даних про обмеження запитів
RATELIMIT_ENABLE = True # Увімкнення обмеження запитів
RATELIMIT_FAIL_OPEN = False  # Встановлення поведінки при збої у перевірці ліміту: якщо False — запит буде відхилено

# Налаштування LiqPay
LIQPAY_PUBLIC_KEY = config("LIQPAY_PUBLIC_KEY") # Публічний ключ LiqPay
LIQPAY_PRIVATE_KEY = config("LIQPAY_PRIVATE_KEY") # Приватний ключ LiqPay

# Налаштування платежів
MIN_PAYMENT_AMOUNT = "10.00"  # Мінімальна сума депозиту
MAX_PAYMENT_AMOUNT = "10000.00"  # Максимальна сума депозиту

