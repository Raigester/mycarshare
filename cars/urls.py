from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views


# Роутер для сумісності з існуючим API
router = DefaultRouter()

urlpatterns = [
    # API для сумісності з JS (для роботи карт тощо)
    path("api/", include(router.urls)),
    path("api/cars/<int:pk>/", views.get_car_api, name="car-api-detail"),

    # Представлення для брендів автомобілів
    path("brands/", views.CarBrandListView.as_view(), name="car-brand-list"),
    path("brands/<int:pk>/", views.CarBrandDetailView.as_view(), name="car-brand-detail"),
    path("brands/create/", views.CarBrandCreateView.as_view(), name="car-brand-create"),
    path("brands/<int:pk>/update/", views.CarBrandUpdateView.as_view(), name="car-brand-update"),
    path("brands/<int:pk>/delete/", views.CarBrandDeleteView.as_view(), name="car-brand-delete"),

    # Представлення для моделей автомобілів
    path("models/", views.CarModelListView.as_view(), name="car-model-list"),
    path("models/<int:pk>/", views.CarModelDetailView.as_view(), name="car-model-detail"),
    path("models/create/", views.CarModelCreateView.as_view(), name="car-model-create"),
    path("models/<int:pk>/update/", views.CarModelUpdateView.as_view(), name="car-model-update"),
    path("models/<int:pk>/delete/", views.CarModelDeleteView.as_view(), name="car-model-delete"),

    # Представлення для автомобілів
    path("", views.CarListView.as_view(), name="car-list"),
    path("available/", views.AvailableCarsView.as_view(), name="available-cars"),
    path("map/", views.cars_map_view, name="cars-map"),
    path("<int:pk>/", views.CarDetailView.as_view(), name="car-detail"),
    path("create/", views.CarCreateView.as_view(), name="car-create"),
    path("<int:pk>/update/", views.CarUpdateView.as_view(), name="car-update"),
    path("<int:pk>/delete/", views.CarDeleteView.as_view(), name="car-delete"),
    path("<int:pk>/location/", views.update_car_location, name="update-car-location"),
    path("<int:pk>/status/", views.change_car_status, name="change-car-status"),

    # Представлення для фотографій автомобілів
    path("photos/", views.CarPhotoListView.as_view(), name="car-photo-list"),
    path("photos/create/", views.CarPhotoCreateView.as_view(), name="car-photo-create"),
    path("photos/<int:pk>/delete/", views.CarPhotoDeleteView.as_view(), name="car-photo-delete"),

    # Представлення для відгуків на автомобілі
    path("<int:pk>/review/add/", views.add_car_review, name="add-car-review"),
    path("review/<int:pk>/edit/", views.edit_car_review, name="edit-car-review"),
    path("review/<int:pk>/delete/", views.delete_car_review, name="delete-car-review"),
]
