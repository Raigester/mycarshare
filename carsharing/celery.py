import os

from celery import Celery


# Встановлення змінної середовища для налаштувань Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carsharing.settings")

app = Celery("carsharing")

# Використання налаштувань Django для конфігурації Celery
app.config_from_object("django.conf:settings", namespace="CELERY")

# Автоматичне виявлення та реєстрація завдань із файлів tasks.py
app.autodiscover_tasks()

# Налаштування періодичних завдань
app.conf.beat_schedule = {
    "process-minute-billing": {
        "task": "bookings.tasks.process_minute_billing",
        "schedule": 60.0,  # Щохвилини
    },
}
