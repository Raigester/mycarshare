#!/usr/bin/env python
"""Утиліта командного рядка Django для адміністративних завдань."""
import os
import sys


def main():
    """Запуск адміністративних завдань."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carsharing.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Не вдалося імпортувати Django. Ви впевнені, що він встановлений і "
            "доступний у вашій змінній середовища PYTHONPATH? Можливо, ви "
            "забули активувати віртуальне середовище?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
