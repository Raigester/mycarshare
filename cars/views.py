from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Avg
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from .forms import (
    CarBrandForm,
    CarFilterForm,
    CarForm,
    CarLocationForm,
    CarModelForm,
    CarPhotoForm,
    CarReviewForm,
    CarStatusForm,
)
from .models import Car, CarBrand, CarModel, CarPhoto, CarReview


# Функція перевірки адміністратора
def is_staff(user):
    """
    Перевіряє, чи є користувач адміністратором.

    Args:
        user: Об'єкт користувача, для якого виконується перевірка.

    Returns:
        bool: True, якщо користувач є адміністратором, False - в іншому випадку.
    """
    return user.is_staff

# Представлення для брендів автомобілів
class CarBrandListView(ListView):
    """Представлення для списку брендів автомобілів"""
    model = CarBrand
    template_name = "brand_list.html"
    context_object_name = "brands"
    paginate_by = 10

class CarBrandDetailView(DetailView):
    """Представлення для деталей бренду автомобіля"""
    model = CarBrand
    template_name = "brand_detail.html"
    context_object_name = "brand"

    def get_context_data(self, **kwargs):
        """
        Додає моделі автомобілів бренду до контексту.

        Args:
            **kwargs: Додаткові іменовані аргументи.

        Returns:
            dict: Контекст з доданими моделями автомобілів.
        """
        context = super().get_context_data(**kwargs)
        context["models"] = self.object.models.all()
        return context

class CarBrandCreateView(UserPassesTestMixin, CreateView):
    """Представлення для створення бренду автомобіля"""
    model = CarBrand
    form_class = CarBrandForm
    template_name = "brand_form.html"
    success_url = reverse_lazy("car-brand-list")

    def test_func(self):
        """
        Перевіряє, чи має користувач право на створення бренду.

        Args:
            self: Екземпляр класу.

        Returns:
            bool: True, якщо користувач є адміністратором, False - в іншому випадку.
        """
        return self.request.user.is_staff

    def form_valid(self, form):
        """
        Обробляє валідну форму при створенні бренду.

        Args:
            self: Екземпляр класу.
            form: Валідована форма для створення бренду.

        Returns:
            HttpResponse: Відповідь після успішного створення бренду.
        """
        messages.success(self.request, f"Бренд автомобіля '{form.instance.name}' успішно створено.")
        return super().form_valid(form)

class CarBrandUpdateView(UserPassesTestMixin, UpdateView):
    """Представлення для оновлення бренду автомобіля"""
    model = CarBrand
    form_class = CarBrandForm
    template_name = "brand_form.html"

    def test_func(self):
        """
        Перевіряє, чи має користувач право на оновлення бренду.

        Args:
            self: Екземпляр класу.

        Returns:
            bool: True, якщо користувач є адміністратором, False - в іншому випадку.
        """
        return self.request.user.is_staff

    def get_success_url(self):
        """
        Визначає URL-адресу перенаправлення після успішного оновлення бренду.

        Args:
            self: Екземпляр класу.

        Returns:
            str: URL-адреса для перенаправлення.
        """
        return reverse("car-brand-detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        """
        Обробляє валідну форму при оновленні бренду.

        Args:
            self: Екземпляр класу.
            form: Валідована форма для оновлення бренду.

        Returns:
            HttpResponse: Відповідь після успішного оновлення бренду.
        """
        messages.success(self.request, f"Бренд автомобіля '{form.instance.name}' успішно оновлено.")
        return super().form_valid(form)

class CarBrandDeleteView(UserPassesTestMixin, DeleteView):
    """Представлення для видалення бренду автомобіля"""
    model = CarBrand
    template_name = "brand_confirm_delete.html"
    success_url = reverse_lazy("car-brand-list")

    def test_func(self):
        """
        Перевіряє, чи має користувач право на видалення бренду.

        Args:
            self: Екземпляр класу.

        Returns:
            bool: True, якщо користувач є адміністратором, False - в іншому випадку.
        """
        return self.request.user.is_staff

    def delete(self, request, *args, **kwargs):
        """
        Обробляє видалення бренду автомобіля.

        Args:
            self: Екземпляр класу.
            request: Об'єкт запиту.
            *args: Додаткові позиційні аргументи.
            **kwargs: Додаткові іменовані аргументи.

        Returns:
            HttpResponse: Відповідь після успішного видалення бренду.
        """
        brand = self.get_object()
        messages.success(request, f"Бренд автомобіля '{brand.name}' успішно видалено.")
        return super().delete(request, *args, **kwargs)

# Представлення для моделей автомобілів
class CarModelListView(ListView):
    """Представлення для списку моделей автомобілів"""
    model = CarModel
    template_name = "model_list.html"
    context_object_name = "models"
    paginate_by = 10

    def get_queryset(self):
        """
        Отримує список моделей автомобілів з можливою фільтрацією за брендом.

        Args:
            self: Екземпляр класу.

        Returns:
            QuerySet: Відфільтрований QuerySet моделей автомобілів.
        """
        queryset = super().get_queryset()

        # Фільтрація по бренду, якщо вказано
        brand_id = self.request.GET.get("brand")
        if brand_id:
            queryset = queryset.filter(brand_id=brand_id)

        return queryset

    def get_context_data(self, **kwargs):
        """
        Додає до контексту список всіх брендів та обраний бренд для фільтрації.

        Args:
            self: Екземпляр класу.
            **kwargs: Додаткові іменовані аргументи.

        Returns:
            dict: Контекст з доданими брендами та обраним брендом.
        """
        context = super().get_context_data(**kwargs)
        context["brands"] = CarBrand.objects.all()
        context["selected_brand"] = self.request.GET.get("brand")
        return context

class CarModelDetailView(DetailView):
    """View for car model details"""
    model = CarModel
    template_name = "model_detail.html"
    context_object_name = "model"

    def get_context_data(self, **kwargs):
        """
        Додає до контексту список автомобілів для обраної моделі.

        Args:
            self: Екземпляр класу.
            **kwargs: Додаткові іменовані аргументи.

        Returns:
            dict: Контекст з доданим списком автомобілів.
        """
        context = super().get_context_data(**kwargs)
        context["cars"] = self.object.cars.all()
        return context

class CarModelCreateView(UserPassesTestMixin, CreateView):
    """View for creating a car model"""
    model = CarModel
    form_class = CarModelForm
    template_name = "model_form.html"
    success_url = reverse_lazy("car-model-list")

    def test_func(self):
        """
        Перевіряє, чи має користувач право на створення моделі автомобіля.

        Args:
            self: Екземпляр класу.

        Returns:
            bool: True, якщо користувач є адміністратором, False - в іншому випадку.
        """
        return self.request.user.is_staff

    def form_valid(self, form):
        """
        Обробляє валідну форму при створенні моделі автомобіля.

        Args:
            self: Екземпляр класу.
            form: Валідована форма для створення моделі.

        Returns:
            HttpResponse: Відповідь після успішного створення моделі.
        """
        messages.success(self.request, f"Модель автомобіля '{form.instance.name}' успішно створена.")
        return super().form_valid(form)

class CarModelUpdateView(UserPassesTestMixin, UpdateView):
    """View for updating a car model"""
    model = CarModel
    form_class = CarModelForm
    template_name = "model_form.html"

    def test_func(self):
        """
        Перевіряє, чи має користувач право на оновлення моделі автомобіля.

        Args:
            self: Екземпляр класу.

        Returns:
            bool: True, якщо користувач є адміністратором, False - в іншому випадку.
        """
        return self.request.user.is_staff

    def get_success_url(self):
        """
        Визначає URL-адресу перенаправлення після успішного оновлення моделі.

        Args:
            self: Екземпляр класу.

        Returns:
            str: URL-адреса для перенаправлення.
        """
        return reverse("car-model-detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        """
        Обробляє валідну форму при оновленні моделі автомобіля.

        Args:
            self: Екземпляр класу.
            form: Валідована форма для оновлення моделі.

        Returns:
            HttpResponse: Відповідь після успішного оновлення моделі.
        """
        messages.success(self.request, f"Модель автомобіля '{form.instance.name}' успішно оновлена.")
        return super().form_valid(form)

class CarModelDeleteView(UserPassesTestMixin, DeleteView):
    """Представлення для видалення моделі автомобіля"""
    model = CarModel
    template_name = "model_confirm_delete.html"
    success_url = reverse_lazy("car-model-list")

    def test_func(self):
        """
        Перевіряє, чи має користувач право на видалення моделі автомобіля.

        Args:
            self: Екземпляр класу.

        Returns:
            bool: True, якщо користувач є адміністратором, False - в іншому випадку.
        """
        return self.request.user.is_staff

    def delete(self, request, *args, **kwargs):
        """
        Обробляє видалення моделі автомобіля.

        Args:
            self: Екземпляр класу.
            request: Об'єкт запиту.
            *args: Додаткові позиційні аргументи.
            **kwargs: Додаткові іменовані аргументи.

        Returns:
            HttpResponse: Відповідь після успішного видалення моделі.
        """
        model = self.get_object()
        messages.success(request, f"Модель автомобіля '{model.name}' успішно видалена.")
        return super().delete(request, *args, **kwargs)

# Представлення для автомобілів
class CarListView(ListView):
    """Представлення для списку автомобілів"""
    model = Car
    template_name = "car_list.html"
    context_object_name = "cars"
    paginate_by = 10

    def get_queryset(self):
        """
        Отримує список автомобілів з можливими фільтрами.

        Args:
            self: Екземпляр класу.

        Returns:
            QuerySet: Відфільтрований QuerySet автомобілів.
        """
        queryset = super().get_queryset()

        # Застосування фільтрів з форми
        form = CarFilterForm(self.request.GET)

        if form.is_valid():
            # Фільтр за брендом
            if form.cleaned_data.get("brand"):
                queryset = queryset.filter(model__brand=form.cleaned_data["brand"])

            # Фільтр за моделлю
            if form.cleaned_data.get("model"):
                queryset = queryset.filter(model=form.cleaned_data["model"])

            # Фільтр за типом палива
            if form.cleaned_data.get("fuel_type"):
                queryset = queryset.filter(fuel_type=form.cleaned_data["fuel_type"])

            # Фільтр за типом трансмісії
            if form.cleaned_data.get("transmission"):
                queryset = queryset.filter(transmission=form.cleaned_data["transmission"])

            # Фільтр за статусом
            if form.cleaned_data.get("status"):
                queryset = queryset.filter(status=form.cleaned_data["status"])

            # Фільтр за роком випуску
            if form.cleaned_data.get("min_year"):
                queryset = queryset.filter(year__gte=form.cleaned_data["min_year"])

            if form.cleaned_data.get("max_year"):
                queryset = queryset.filter(year__lte=form.cleaned_data["max_year"])

            # Фільтр за кількістю місць
            if form.cleaned_data.get("min_seats"):
                queryset = queryset.filter(seats__gte=form.cleaned_data["min_seats"])

            # Фільтри за додатковими опціями
            if form.cleaned_data.get("has_air_conditioning"):
                queryset = queryset.filter(has_air_conditioning=True)

            if form.cleaned_data.get("has_gps"):
                queryset = queryset.filter(has_gps=True)

            if form.cleaned_data.get("has_child_seat"):
                queryset = queryset.filter(has_child_seat=True)

        return queryset

    def get_context_data(self, **kwargs):
        """
        Додає до контексту форму фільтрації та статистику автомобілів.

        Args:
            self: Екземпляр класу.
            **kwargs: Додаткові іменовані аргументи.

        Returns:
            dict: Контекст з доданою формою фільтрації та статистикою.
        """
        context = super().get_context_data(**kwargs)
        context["filter_form"] = CarFilterForm(self.request.GET)

        # Статистика автомобілів
        context["total_cars"] = Car.objects.count()
        context["available_cars"] = Car.objects.filter(status="available").count()
        context["busy_cars"] = Car.objects.filter(status="busy").count()

        return context

class CarDetailView(DetailView):
    """Представлення для деталей автомобіля"""
    model = Car
    template_name = "car_detail.html"
    context_object_name = "car"

    def get_context_data(self, **kwargs):
        """
        Додає до контексту фотографії, відгуки та форму для відгуку.

        Args:
            self: Екземпляр класу.
            **kwargs: Додаткові іменовані аргументи.

        Returns:
            dict: Контекст з доданими фотографіями, відгуками та формою для відгуку.
        """
        context = super().get_context_data(**kwargs)

        # Добавляем фотографії автомобіля
        context["photos"] = self.object.photos.all()

        # Добавляем відгуки об автомобілі
        context["reviews"] = self.object.reviews.all().order_by("-created_at")

        # Форма для відгука
        if self.request.user.is_authenticated:
            # Перевіряємо, чи залишав користувач вже відгук
            user_review = CarReview.objects.filter(car=self.object, user=self.request.user).first()

            if user_review:
                context["user_review"] = user_review
            else:
                # Якщо відгук ще не залишено, додаємо форму
                context["review_form"] = CarReviewForm(initial={"car": self.object}, user=self.request.user)

        return context

class CarCreateView(UserPassesTestMixin, CreateView):
    """Представлення для створення автомобіля"""
    model = Car
    form_class = CarForm
    template_name = "car_form.html"
    success_url = reverse_lazy("car-list")

    def test_func(self):
        """
        Перевіряє, чи має користувач право на створення автомобіля.

        Args:
            self: Екземпляр класу.

        Returns:
            bool: True, якщо користувач є адміністратором, False - в іншому випадку.
        """
        return self.request.user.is_staff

    def form_valid(self, form):
        """
        Обробляє валідну форму при створенні автомобіля.

        Args:
            self: Екземпляр класу.
            form: Валідована форма для створення автомобіля.

        Returns:
            HttpResponse: Відповідь після успішного створення автомобіля.
        """
        messages.success(self.request, f"Автомобіль '{form.instance.model}' успішно додано.")
        return super().form_valid(form)

class CarUpdateView(UserPassesTestMixin, UpdateView):
    """Представлення для оновлення автомобіля"""
    model = Car
    form_class = CarForm
    template_name = "car_form.html"

    def test_func(self):
        """
        Перевіряє, чи має користувач право на оновлення автомобіля.

        Args:
            self: Екземпляр класу.

        Returns:
            bool: True, якщо користувач є адміністратором, False - в іншому випадку.
        """
        return self.request.user.is_staff

    def get_success_url(self):
        """
        Визначає URL-адресу перенаправлення після успішного оновлення автомобіля.

        Args:
            self: Екземпляр класу.

        Returns:
            str: URL-адреса для перенаправлення.
        """
        return reverse("car-detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        """
        Обробляє валідну форму при оновленні автомобіля.

        Args:
            self: Екземпляр класу.
            form: Валідована форма для оновлення автомобіля.

        Returns:
            HttpResponse: Відповідь після успішного оновлення автомобіля.
        """
        messages.success(self.request, f"Автомобіль '{form.instance.model}' успішно оновлено.")
        return super().form_valid(form)

class CarDeleteView(UserPassesTestMixin, DeleteView):
    """Представлення для видалення автомобіля"""
    model = Car
    template_name = "car_confirm_delete.html"
    success_url = reverse_lazy("car-list")

    def test_func(self):
        """
        Перевіряє, чи має користувач право на видалення автомобіля.

        Args:
            self: Екземпляр класу.

        Returns:
            bool: True, якщо користувач є адміністратором, False - в іншому випадку.
        """
        return self.request.user.is_staff

    def delete(self, request, *args, **kwargs):
        """
        Обробляє видалення автомобіля.

        Args:
            self: Екземпляр класу.
            request: Об'єкт запиту.
            *args: Додаткові позиційні аргументи.
            **kwargs: Додаткові іменовані аргументи.

        Returns:
            HttpResponse: Відповідь після успішного видалення автомобіля.
        """
        car = self.get_object()
        messages.success(request, f"Автомобіль '{car.model}' успішно видалено.")
        return super().delete(request, *args, **kwargs)

@login_required
@user_passes_test(is_staff)
def update_car_location(request, pk):
    """
    Представлення для оновлення місцезнаходження автомобіля.

    Args:
        request: Об'єкт запиту Django.
        pk: Первинний ключ автомобіля.

    Returns:
        HttpResponse: Відображення форми оновлення місцезнаходження або перенаправлення на сторінку деталей автомобіля.
    """
    car = get_object_or_404(Car, pk=pk)

    if request.method == "POST":
        form = CarLocationForm(request.POST)
        if form.is_valid():
            car.current_latitude = form.cleaned_data["latitude"]
            car.current_longitude = form.cleaned_data["longitude"]
            car.save()

            messages.success(request, f"Местоположение автомобіля '{car.model}' успішно оновлено.")
            return redirect("car-detail", pk=car.pk)
    else:
        form = CarLocationForm(initial={
            "latitude": car.current_latitude,
            "longitude": car.current_longitude
        })

    return render(request, "car_location_form.html", {
        "form": form,
        "car": car
    })

@login_required
@user_passes_test(is_staff)
def change_car_status(request, pk):
    """
    Представлення для зміни статусу автомобіля.

    Args:
        request: Об'єкт запиту Django.
        pk: Первинний ключ автомобіля.

    Returns:
        HttpResponse: Відображення форми зміни статусу або перенаправлення на сторінку деталей автомобіля.
    """
    car = get_object_or_404(Car, pk=pk)

    if request.method == "POST":
        form = CarStatusForm(request.POST)
        if form.is_valid():
            car.status = form.cleaned_data["status"]
            car.save()

            messages.success(request, f"Статус автомобіля '{car.model}' змінено на '{car.get_status_display()}'.")
            return redirect("car-detail", pk=car.pk)
    else:
        form = CarStatusForm(initial={"status": car.status})

    return render(request, "car_status_form.html", {
        "form": form,
        "car": car
    })

# Представлення для фотографій автомобілів
class CarPhotoListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """Представлення для списку фотографій автомобілів"""
    model = CarPhoto
    template_name = "photo_list.html"
    context_object_name = "photos"
    paginate_by = 20

    def test_func(self):
        """
        Перевіряє, чи має користувач право на перегляд списку фотографій.

        Args:
            self: Екземпляр класу.

        Returns:
            bool: True, якщо користувач є адміністратором, False - в іншому випадку.
        """
        return self.request.user.is_staff

    def get_queryset(self):
        """
        Отримує список фотографій з можливою фільтрацією за автомобілем.

        Args:
            self: Екземпляр класу.

        Returns:
            QuerySet: Відфільтрований QuerySet фотографій автомобілів.
        """
        queryset = super().get_queryset()

        # Фільтрація за автомобілем, якщо вказано
        car_id = self.request.GET.get("car")
        if car_id:
            queryset = queryset.filter(car_id=car_id)

        return queryset

    def get_context_data(self, **kwargs):
        """
        Додає до контексту список всіх автомобілів та обраний автомобіль для фільтрації.

        Args:
            self: Екземпляр класу.
            **kwargs: Додаткові іменовані аргументи.

        Returns:
            dict: Контекст з доданими автомобілями та обраним автомобілем.
        """
        context = super().get_context_data(**kwargs)
        context["cars"] = Car.objects.all()
        context["selected_car"] = self.request.GET.get("car")
        return context

class CarPhotoCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """Представлення для створення фотографії автомобіля"""
    model = CarPhoto
    form_class = CarPhotoForm
    template_name = "photo_form.html"
    success_url = reverse_lazy("car-photo-list")

    def test_func(self):
        """
        Перевіряє, чи має користувач право на створення фотографії автомобіля.

        Args:
            self: Екземпляр класу.

        Returns:
            bool: True, якщо користувач є адміністратором, False - в іншому випадку.
        """
        return self.request.user.is_staff

    def form_valid(self, form):
        """
        Обробляє валідну форму при створенні фотографії автомобіля.

        Args:
            self: Екземпляр класу.
            form: Валідована форма для створення фотографії.

        Returns:
            HttpResponse: Відповідь після успішного створення фотографії.
        """
        messages.success(self.request, f"Фото для автомобіля '{form.instance.car}' успішно додано.")
        return super().form_valid(form)

class CarPhotoDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Представлення для видалення фотографії автомобіля"""
    model = CarPhoto
    template_name = "photo_confirm_delete.html"

    def test_func(self):
        """
        Перевіряє, чи має користувач право на видалення фотографії автомобіля.

        Args:
            self: Екземпляр класу.

        Returns:
            bool: True, якщо користувач є адміністратором, False - в іншому випадку.
        """
        return self.request.user.is_staff

    def get_success_url(self):
        """
        Визначає URL-адресу перенаправлення після успішного видалення фотографії.

        Args:
            self: Екземпляр класу.

        Returns:
            str: URL-адреса для перенаправлення.
        """
        return reverse("car-detail", kwargs={"pk": self.object.car.pk})

    def delete(self, request, *args, **kwargs):
        """
        Обробляє видалення фотографії автомобіля.

        Args:
            self: Екземпляр класу.
            request: Об'єкт запиту.
            *args: Додаткові позиційні аргументи.
            **kwargs: Додаткові іменовані аргументи.

        Returns:
            HttpResponse: Відповідь після успішного видалення фотографії.
        """
        photo = self.get_object()
        messages.success(request, f"Фото для автомобіля '{photo.car}' успішно видалено.")
        return super().delete(request, *args, **kwargs)

# Представлення для відгуків на автомобілі
@login_required
def add_car_review(request, pk):
    """
    Представлення для додавання відгуку на автомобіль.

    Args:
        request: Об'єкт запиту Django.
        pk: Первинний ключ автомобіля.

    Returns:
        HttpResponse: Відображення форми додавання відгуку або перенаправлення на сторінку деталей автомобіля.
    """
    car = get_object_or_404(Car, pk=pk)

    # Перевірка, чи залишав користувач вже відгук
    if CarReview.objects.filter(car=car, user=request.user).exists():
        messages.error(request, "Ви вже залишили відгук на цей автомобіль.")
        return redirect("car-detail", pk=car.pk)

    if request.method == "POST":
        form = CarReviewForm(request.POST, user=request.user)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.car = car
            review.save()

            # Перераховуємо середній рейтинг автомобіля
            car.rating = CarReview.objects.filter(car=car).aggregate(Avg("rating"))["rating__avg"] or 0
            car.save()

            messages.success(request, "Ваш відгук успішно додано.")
            return redirect("car-detail", pk=car.pk)
    else:
        form = CarReviewForm(initial={"car": car}, user=request.user)

    return render(request, "review_form.html", {
        "form": form,
        "car": car
    })

@login_required
def edit_car_review(request, pk):
    """
    Представлення для редагування відгуку на автомобіль.

    Args:
        request: Об'єкт запиту Django.
        pk: Первинний ключ відгуку.

    Returns:
        HttpResponse: Відображення форми редагування відгуку або перенаправлення на сторінку деталей автомобіля.
    """
    review = get_object_or_404(CarReview, pk=pk)

    # Перевірка, що відгук належить поточному користувачу
    if review.user != request.user and not request.user.is_staff:
        messages.error(request, "Ви не можете редагувати цей відгук.")
        return redirect("car-detail", pk=review.car.pk)

    if request.method == "POST":
        form = CarReviewForm(request.POST, instance=review, user=request.user)
        if form.is_valid():
            form.save()

            # Перераховуємо середній рейтинг автомобіля
            car = review.car
            car.rating = CarReview.objects.filter(car=car).aggregate(Avg("rating"))["rating__avg"] or 0
            car.save()

            messages.success(request, "Ваш відгук успішно оновлено.")
            return redirect("car-detail", pk=review.car.pk)
    else:
        form = CarReviewForm(instance=review, user=request.user)

    return render(request, "review_form.html", {
        "form": form,
        "car": review.car,
        "review": review
    })

@login_required
def delete_car_review(request, pk):
    """
    Представлення для видалення відгуку на автомобіль.

    Args:
        request: Об'єкт запиту Django.
        pk: Первинний ключ відгуку.

    Returns:
        HttpResponse: Відображення сторінки підтвердження видалення або перенаправлення на сторінку деталей автомобіля.
    """
    review = get_object_or_404(CarReview, pk=pk)

    # Перевірка, що відгук належить поточному користувачу або адміну
    if review.user != request.user and not request.user.is_staff:
        messages.error(request, "Ви не можете видалити цей відгук.")
        return redirect("car-detail", pk=review.car.pk)

    car = review.car

    if request.method == "POST":
        review.delete()

        # Перераховуємо середній рейтинг автомобіля
        car.rating = CarReview.objects.filter(car=car).aggregate(Avg("rating"))["rating__avg"] or 0
        car.save()

        messages.success(request, "Відгук успішно видалено.")
        return redirect("car-detail", pk=car.pk)

    return render(request, "review_confirm_delete.html", {
        "review": review,
        "car": car
    })

# API-представлення для отримання автомобіля по ID (для сумісності з JavaScript)
def get_car_api(request, pk):
    """
    API для отримання деталей автомобіля за ID.

    Args:
        request: Об'єкт запиту Django.
        pk: Первинний ключ автомобіля.

    Returns:
        JsonResponse: JSON-відповідь з даними автомобіля.
    """
    car = get_object_or_404(Car, pk=pk)

    # Створюємо словник з даними автомобіля
    car_data = {
        "id": car.id,
        "model": car.model.id,
        "brand_name": car.model.brand.name,
        "model_name": car.model.name,
        "year": car.year,
        "license_plate": car.license_plate,
        "color": car.color,
        "mileage": car.mileage,
        "fuel_type": car.fuel_type,
        "transmission": car.transmission,
        "price_per_minute": str(car.price_per_minute),
        "engine_capacity": str(car.engine_capacity) if car.engine_capacity else None,
        "power": car.power,
        "seats": car.seats,
        "has_air_conditioning": car.has_air_conditioning,
        "has_gps": car.has_gps,
        "has_child_seat": car.has_child_seat,
        "has_bluetooth": car.has_bluetooth,
        "has_usb": car.has_usb,
        "status": car.status,
        "current_latitude": car.current_latitude,
        "current_longitude": car.current_longitude,
        "main_photo": request.build_absolute_uri(car.main_photo.url) if car.main_photo else None,
        "rating": float(car.rating)
    }

    return JsonResponse(car_data)

# Представлення для відображення доступних автомобілів
class AvailableCarsView(ListView):
    """Представлення для списку доступних автомобілів"""
    model = Car
    template_name = "available_cars.html"
    context_object_name = "cars"
    paginate_by = 12

    def get_queryset(self):
        """
        Отримує список доступних автомобілів з можливими фільтрами.

        Args:
            self: Екземпляр класу.

        Returns:
            QuerySet: Відфільтрований QuerySet доступних автомобілів.
        """
        queryset = Car.objects.all()
        self.filter_form = CarFilterForm(self.request.GET)
        if self.filter_form.is_valid():
            if self.filter_form.cleaned_data.get("brand"):
                queryset = queryset.filter(model__brand=self.filter_form.cleaned_data["brand"])
            if self.filter_form.cleaned_data.get("model"):
                queryset = queryset.filter(model=self.filter_form.cleaned_data["model"])
            if self.filter_form.cleaned_data.get("fuel_type"):
                queryset = queryset.filter(fuel_type=self.filter_form.cleaned_data["fuel_type"])
            if self.filter_form.cleaned_data.get("transmission"):
                queryset = queryset.filter(transmission=self.filter_form.cleaned_data["transmission"])
            if self.filter_form.cleaned_data.get("min_year"):
                queryset = queryset.filter(year__gte=self.filter_form.cleaned_data["min_year"])
            if self.filter_form.cleaned_data.get("max_year"):
                queryset = queryset.filter(year__lte=self.filter_form.cleaned_data["max_year"])
            if self.filter_form.cleaned_data.get("min_seats"):
                queryset = queryset.filter(seats__gte=self.filter_form.cleaned_data["min_seats"])
            if self.filter_form.cleaned_data.get("has_air_conditioning"):
                queryset = queryset.filter(has_air_conditioning=True)
            if self.filter_form.cleaned_data.get("has_gps"):
                queryset = queryset.filter(has_gps=True)
            if self.filter_form.cleaned_data.get("has_child_seat"):
                queryset = queryset.filter(has_child_seat=True)

        return queryset.filter(status="available")

    def get_context_data(self, **kwargs):
        """
        Додає до контексту форму фільтрації.

        Args:
            self: Екземпляр класу.
            **kwargs: Додаткові іменовані аргументи.

        Returns:
            dict: Контекст з доданою формою фільтрації.
        """
        context = super().get_context_data(**kwargs)
        context["filter_form"] = self.filter_form
        return context

# Представлення для відображення карти з автомобілями
def cars_map_view(request):
    """
    Представлення для відображення автомобілів на карті.

    Args:
        request: Об'єкт запиту Django.

    Returns:
        HttpResponse: Відображення сторінки з картою автомобілів.
    """
    # Отримуємо всі автомобілі
    cars = Car.objects.all()

    # Фільтрація по статусу, якщо вказано
    status = request.GET.get("status")
    if status:
        cars = cars.filter(status=status)

    # Фільтрація по марці, якщо вказано
    brand_id = request.GET.get("brand")
    if brand_id:
        cars = cars.filter(model__brand_id=brand_id)

    return render(request, "cars_map.html", {
        "cars": cars,
        "brands": CarBrand.objects.all(),
        "selected_status": status,
        "selected_brand": brand_id
    })
