# -*- coding: utf-8 -*-
from django.test import TestCase
from django.urls import reverse


class HomeViewTest(TestCase):
    """Тест домашньої сторінки"""

    def test_home_view_status_code(self):
        """Тест, що домашня сторінка доступна (статус 200)"""
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)

    def test_home_view_uses_correct_template(self):
        """Тест, що домашня сторінка використовує правильний шаблон"""
        response = self.client.get(reverse("home"))
        self.assertTemplateUsed(response, "home.html")
