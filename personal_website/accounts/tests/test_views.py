from http import HTTPStatus

from django.contrib.auth.models import User
from django.core import mail
from django.test import TestCase
from django.urls import resolve, reverse
from django.utils.crypto import get_random_string

from accounts.views import signup


class UserPersmissionsTest(TestCase):
    """
    Проверка полномочий пользователя.
    """

    url = "/main/"

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username="user", password="UserPassword")
        cls.staff = User.objects.create_user(username="staff", is_staff=True, password="StaffUserPassword")
        cls.superuser = User.objects.create_superuser(username="superuser", password="SuperUserSecretPassword")

    def test_header_elements(self):
        """
        Проверка информации и ссылок, отображаемых в меню навигации в зависимости от статуса пользователя.
        """
        # Проверить отображение блоков меню навигации для неавторизованного пользователя.
        response = self.client.get(self.url)
        self.assertNotContains(response, "Администрирование")
        self.assertNotContains(response, "Вы вошли как")
        self.assertNotContains(response, "Выйти")
        self.assertContains(response, "Войти")
        self.assertContains(response, "Регистрация")

        # Проверить отображение блоков меню навигации для обычного пользователя, который авторизовался.
        self.assertTrue(self.client.login(username="user", password="UserPassword"))
        response = self.client.get(self.url)
        self.assertContains(response, f"Вы вошли как {self.user.username}")
        self.assertContains(response, "Выйти")
        self.assertNotContains(response, "Войти")
        self.assertNotContains(response, "Регистрация")
        self.assertNotContains(response, "Администрирование")

        # Проверить отображение блоков меню навигации для пользователя с правами администратора.
        self.assertTrue(self.client.login(username="staff", password="StaffUserPassword"))
        response = self.client.get(self.url)
        self.assertContains(response, f"Вы вошли как {self.staff.username}")
        self.assertContains(response, "Выйти")
        self.assertContains(response, "Администрирование")
        self.assertNotContains(response, "Войти")
        self.assertNotContains(response, "Регистрация")

        # Проверить отобржаение блоков меню навигации для суперпользователя.
        self.assertTrue(self.client.login(username="superuser", password="SuperUserSecretPassword"))
        response = self.client.get(self.url)
        self.assertContains(response, f"Вы вошли как {self.superuser.username}")
        self.assertContains(response, "Выйти")
        self.assertContains(response, "Администрирование")
        self.assertNotContains(response, "Войти")
        self.assertNotContains(response, "Регистрация")

        # Деавторизоваться и вновь проверить отображение блоков меню навигации для неавторизованного пользователя.
        self.client.logout()
        response = self.client.get(self.url)
        self.assertNotContains(response, "Администрирование")
        self.assertNotContains(response, "Вы вошли как")
        self.assertNotContains(response, "Выйти")
        self.assertContains(response, "Войти")
        self.assertContains(response, "Регистрация")


class UserManagementRoutesTest(TestCase):
    """
    Тестирование ссылок системы авторизации.
    """

    @classmethod
    def setUpTestData(cls):
        User.objects.create_user(username="testuser", password="TestPassword123", email="test@example.com")

    def test_login_url(self):
        """
        Тестирование ссылки для входа на сайт.
        """
        url = "/accounts/login/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, "registration/login.html")
        self.assertTemplateUsed(response, "base.html")
        self.assertContains(response, "Вход на сайт")
        self.assertContains(response, "Забыли пароль?")

    def test_logout_url(self):
        """
        Тестирование ссылки для выхода с сайта.
        """
        url = "/accounts/logout/"
        response = self.client.post(url)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(
            response,
            "/",
            status_code=HTTPStatus.FOUND,
            target_status_code=HTTPStatus.MOVED_PERMANENTLY,
        )

    def test_signup_url(self):
        """
        Тестирование ссылки для регистрации на сайте.
        """
        url = "/accounts/signup/"
        resolver = resolve(url)
        reverse_url = reverse("accounts:signup")
        reverse_resolver = resolve(reverse_url)
        response = self.client.get(url)
        reverse_response = self.client.get(reverse_url)
        self.assertEqual(resolver.func, signup)
        self.assertEqual(reverse_resolver.func, signup)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(reverse_response.status_code, HTTPStatus.OK)
        self.assertEqual(response.templates, reverse_response.templates)
        self.assertTemplateUsed(response, "registration/signup.html")
        self.assertTemplateUsed(response, "registration/login.html")
        self.assertTemplateUsed(response, "base.html")
        self.assertContains(response, "Зарегистрироваться")
        self.assertNotContains(response, "Вы уже зарегистрированы.")
        self.client.login(username="testuser", password="TestPassword123")
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertNotContains(response, "Зарегистрироваться")
        self.assertContains(response, "Вы уже зарегистрированы.")

    def test_password_reset(self):
        """
        Тестирование ссылки для сброса пароля.
        """

        # Проверить успешность логина на сайте со старым паролем, после чего выйти с сайта.
        self.assertTrue(self.client.login(username="testuser", password="TestPassword123"))
        self.client.logout()

        # Запросить форму для сброса пароля и ввести адрес электронной почты.
        password_reset_form_url = "/accounts/password_reset/"
        response = self.client.get(password_reset_form_url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, "registration/password_reset_form.html")
        self.assertTemplateUsed(response, "registration/login.html")
        self.assertTemplateUsed(response, "base.html")
        self.assertContains(response, "Адрес электронной почты")
        self.assertContains(response, "Сбросить")
        response = self.client.post(password_reset_form_url, data={"email": "test@example.com"})

        # Проверить результат: переадресация на следующую страницу, генерация токена и отправка письма.
        self.assertRedirects(
            response,
            "/accounts/password_reset/done/",
            status_code=HTTPStatus.FOUND,
            target_status_code=HTTPStatus.OK,
        )
        token = response.context[0]["token"]
        uid = response.context[0]["uid"]
        reset_url = f"/accounts/reset/{uid}/{token}/"
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "Сброс пароля на example.com")
        self.assertIn(reset_url, mail.outbox[0].body)

        # Перейти по ссылке из письма, должна открыться форма для создания и подтверждения нового пароля.
        response = self.client.get(reset_url)
        set_password_url = f"/accounts/reset/{uid}/set-password/"
        self.assertRedirects(
            response,
            set_password_url,
            status_code=HTTPStatus.FOUND,
            target_status_code=HTTPStatus.OK,
        )

        # Ввести в форму новый пароль и подтверждение нового пароля, после чего проверить результат: должна быть переадресация на следующую страницу.
        new_password = get_random_string(10)
        response = self.client.post(
            set_password_url,
            data={"new_password1": new_password, "new_password2": new_password},
        )
        self.assertRedirects(
            response,
            "/accounts/reset/done/",
            status_code=HTTPStatus.FOUND,
            target_status_code=HTTPStatus.OK,
        )

        # Проверить, что со старым паролем авторизоваться не удается, но с новым паролем авторизоваться удается.
        self.assertFalse(self.client.login(username="testuser", password="TestPassword123"))
        self.assertTrue(self.client.login(username="testuser", password=new_password))
