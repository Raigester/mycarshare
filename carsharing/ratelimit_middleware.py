from django.http import HttpResponse
from django_ratelimit import ALL
from django_ratelimit.core import is_ratelimited


class GlobalRateLimitMiddleware:
    """
    Middleware для обмеження швидкості запитів для всього сайту.
    Обмежує кількість запитів до 100 на хвилину на IP-адресу.
    """

    def __init__(self, get_response):
        self.get_response = get_response  # Зберігаємо посилання на функцію обробки запиту (chain of middleware)

    def __call__(self, request):
        # Перевірка, чи перевищено ліміт 100 запитів на хвилину для поточної IP-адреси
        limited = is_ratelimited(
            request=request,  # Поточний HTTP-запит
            group="global",  # Група ліміту (назва для ідентифікації)
            key="ip",  # Ключ обмеження — IP-адреса користувача
            rate="100/m",  # Обмеження — 100 запитів на хвилину
            method=ALL,  # Застосувати обмеження для всіх методів (GET, POST і т.д.)
            increment=True  # Якщо ліміт не перевищено, збільшуємо кількість запитів
        )

        # Якщо ліміт перевищено, повертаємо відповідь з кодом 429 (Too Many Requests)
        if limited:
            return HttpResponse("Перевищено ліміт запитів. Спробуйте знову через деякий час.", status=429)

        response = self.get_response(request)  # Якщо ліміт не перевищено, передаємо запит далі по ланцюжку обробки
        return response  # Повертаємо відповідь користувачу
