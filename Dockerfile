FROM python:3.10-slim

# Встановлення робочого каталогу
WORKDIR /app

# Встановлення залежностей системи
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Копіювання файлу залежностей
COPY requirements.txt /app/

# Встановлення залежностей Python
RUN pip install --no-cache-dir -r requirements.txt

# Копіювання коду проєкту
COPY . /app/

# Створення директорій для медіа та статичних файлів
RUN mkdir -p /app/media /app/static

# Копіювання початкових медіа-файлів
COPY initial_media/* /app/media/

# Змінюємо дозволи для директорій
RUN chmod -R 755 /app/media /app/static

# Створення непривілейованого користувача
RUN adduser --disabled-password --gecos '' appuser
RUN chown -R appuser:appuser /app
USER appuser

# Змінюємо default.conf для Nginx
COPY nginx/default.conf /app/nginx/default.conf

# Виконання команди за замовчуванням
CMD ["gunicorn", "carsharing.wsgi:application", "--bind", "0.0.0.0:8000"]