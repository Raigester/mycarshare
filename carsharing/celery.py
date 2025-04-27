import os

from celery import Celery


# Set the environment variable for Django settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carsharing.settings")

app = Celery("carsharing")

# Use Django settings for Celery configuration
app.config_from_object("django.conf:settings", namespace="CELERY")

# Automatically discover and register tasks from tasks.py files
app.autodiscover_tasks()

# Configure periodic tasks
app.conf.beat_schedule = {
    "process-minute-billing": {
        "task": "bookings.tasks.process_minute_billing",
        "schedule": 60.0,  # Every minute
    },
}
