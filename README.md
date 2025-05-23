# CarSharing Platform

Проєкт CarSharing - це веб-платформа для сервісу каршерінгу, яка дозволяє користувачам орендувати автомобілі на короткі періоди часу з хвилинною тарифікацією.

## Особливості

- Реєстрація та автентифікація користувачів
- Верифікація водійських прав 
- Управління балансом користувача та платежами через LiqPay
- Каталог автомобілів з фільтрацією за різними параметрами
- Система бронювання з хвилинною тарифікацією
- Відображення автомобілів на карті
- Система відгуків про автомобілі

## Технічний стек

- **Backend**: Django 5.2
- **База даних**: PostgreSQL
- **Обробка фонових задач**: Celery + Redis
- **Сервер**: Nginx + Gunicorn
- **Контейнеризація**: Docker

## Розгортання проєкту

### Підготовка

1. Клонуйте репозиторій:
   ```
   git clone https://github.com/yourusername/carsharing.git
   cd carsharing
   ```

2. Створіть файл .env на основі .env.example:
   ```
   cp .env.example .env
   ```

3. Налаштуйте змінні середовища у файлі .env:
   - Згенеруйте надійний `SECRET_KEY`
   - Встановіть `DEBUG=False` для продакшена
   - Вкажіть доменне ім'я в `ALLOWED_HOSTS`
   - Налаштуйте підключення до бази даних
   - Додайте ключі API LiqPay для обробки платежів
   - Налаштуйте підключення до Redis

### Розгортання з Docker Compose

1. Переконайтеся, що Docker і Docker Compose встановлені у вашій системі.

2. Запустіть сервіси:
   ```
   docker-compose up -d
   ```

3. Створіть суперкористувача (адміністратора):
   ```
   docker-compose exec web python manage.py createsuperuser
   ```

4. Вам тепер має бути доступний:
   - Веб-сайт за адресою http://ваш_домен
   - Адмін-панель за адресою http://ваш_домен/admin/

### Ручне розгортання

1. Створіть і активуйте віртуальне середовище:
   ```
   python -m venv venv
   source venv/bin/activate  # для Linux/Mac
   venv\Scripts\activate     # для Windows
   ```

2. Встановіть залежності:
   ```
   pip install -r requirements.txt
   ```

3. Застосуйте міграції:
   ```
   python manage.py migrate
   ```

4. Зберіть статичні файли:
   ```
   python manage.py collectstatic
   ```

5. Запустіть Gunicorn:
   ```
   gunicorn carsharing.wsgi:application --bind 0.0.0.0:8000
   ```

6. Налаштуйте Nginx для проксіювання запитів до Gunicorn і запустіть сервіс.

7. Запустіть воркери Celery і Celery Beat:
   ```
   celery -A carsharing worker -l info
   celery -A carsharing beat -l info
   ```

## Структура проєкту

- **carsharing/**: Основний пакет Django проєкту
- **users/**: Додаток для управління користувачами та їхніми балансами
- **cars/**: Додаток для управління автомобілями, брендами, моделями та фотографіями
- **bookings/**: Додаток для управління бронюваннями та білінгом
- **payments/**: Додаток для обробки платежів (інтеграція з LiqPay)
- **core/**: Основний додаток з базовою функціональністю

## Система білінгу

Система використовує Celery для фонових задач обробки хвилинної тарифікації. Кожну хвилину виконується задача `process_minute_billing`, яка списує кошти з балансу користувача за активні бронювання автомобіля.

## Технічне обслуговування

### Резервне копіювання бази даних

```
docker-compose exec db pg_dump -U carsharing_user carsharing_db > backup_$(date +%Y%m%d).sql
```

### Моніторинг логів

```
docker-compose logs -f
```

### Оновлення проєкту

1. Отримайте останню версію коду:
   ```
   git pull origin main
   ```

2. Перезапустіть контейнери:
   ```
   docker-compose down
   docker-compose up -d
   ```

3. Застосуйте міграції:
   ```
   docker-compose exec web python manage.py migrate
   ```
