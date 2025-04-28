from django.http import HttpResponse
from django_ratelimit import ALL
from django_ratelimit.core import is_ratelimited


class GlobalRateLimitMiddleware:
    """
    Middleware для обмеження швидкості запитів для всього сайту.
    Обмежує кількість запитів до 10 на хвилину на IP-адресу.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Обмеження 10 запитів на хвилину для всіх шляхів
        limited = is_ratelimited(
            request=request,
            group="global",
            key="ip",
            rate="10/m",
            method=ALL,
            increment=True
        )

        if limited:
            return HttpResponse("Перевищено ліміт запитів. Спробуйте знову через деякий час.", status=429)

        response = self.get_response(request)
        return response
