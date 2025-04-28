import os
import tempfile

import pytest


# Створюємо тимчасову директорію для медіа-файлів під час тестування
@pytest.fixture(scope="session")
def temp_media_root():
    """Створює тимчасову директорію для медіа-файлів на час виконання тестів."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir

    # Очищення тимчасової директорії після завершення сесії тестування
    for root, dirs, files in os.walk(temp_dir, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))
    if os.path.exists(temp_dir):
        os.rmdir(temp_dir)

@pytest.fixture(autouse=True)
def media_storage(settings, temp_media_root):
    """Замінює MEDIA_ROOT на тимчасову директорію для всіх тестів."""
    settings.MEDIA_ROOT = temp_media_root

@pytest.fixture
def user_data():
    """Повертає дані для створення тестового користувача."""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword123",
        "first_name": "Test",
        "last_name": "User",
        "phone_number": "+380991234567",
    }

@pytest.fixture
def create_user(db, django_user_model):
    """Фікстура для створення користувача."""
    def make_user(**kwargs):
        return django_user_model.objects.create_user(**kwargs)
    return make_user

@pytest.fixture
def authenticated_client(client, create_user, user_data):
    """Фікстура для авторизованого клієнта."""
    user = create_user(**user_data)
    client.force_login(user)
    return client, user
