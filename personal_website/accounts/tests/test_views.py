from django.test import TestCase
from django.urls import reverse, resolve
from django.contrib.auth.models import User
from accounts.views import signup

class UserPersmissionsTest(TestCase):
    '''Проверка полномочий пользователя.'''

    url = '/main/'

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='user', password='UserPassword')
        cls.staff = User.objects.create_user(username='staff', is_staff=True, password='StaffUserPassword')
        cls.superuser = User.objects.create_superuser(username='superuser', password='SuperUserSecretPassword')

    def test_header_elements(self):
        '''Проверка информации и ссылок, отображаемых в меню навигации в зависимости от статуса пользователя.'''
        # Проверить отображение блоков меню навигации для неавторизованного пользователя.
        response = self.client.get(self.url)
        self.assertNotContains(response, "Администрирование")
        self.assertNotContains(response, "Вы вошли как")
        self.assertNotContains(response, "Выйти")       
        self.assertContains(response, "Войти")
        self.assertContains(response, "Регистрация")

        # Проверить отображение блоков меню навигации для обычного пользователя, который авторизовался.
        self.assertTrue(self.client.login(username='user', password='UserPassword'))
        response = self.client.get(self.url)
        self.assertContains(response, f"Вы вошли как {self.user.username}")
        self.assertContains(response, "Выйти")
        self.assertNotContains(response, "Войти")
        self.assertNotContains(response, "Регистрация")
        self.assertNotContains(response, "Администрирование")

        # Проверить отображение блоков меню навигации для пользователя с правами администратора.
        self.assertTrue(self.client.login(username='staff', password='StaffUserPassword'))
        response = self.client.get(self.url)
        self.assertContains(response, f"Вы вошли как {self.staff.username}")
        self.assertContains(response, "Выйти")
        self.assertContains(response, "Администрирование")
        self.assertNotContains(response, "Войти")
        self.assertNotContains(response, "Регистрация")

        # Проверить отобржаение блоков меню навигации для суперпользователя.
        self.assertTrue(self.client.login(username='superuser', password='SuperUserSecretPassword'))
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
    '''Тестирование ссылок системы авторизации.'''

    @classmethod
    def setUpTestData(cls):
        User.objects.create_user(username='testuser', password='TestPassword123')

    def test_login_url(self):
        '''Тестирование ссылки для входа на сайт.'''
        url = '/accounts/login/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/login.html')
        self.assertTemplateUsed(response, 'base.html')
        self.assertContains(response, 'Вход на сайт')
        self.assertContains(response, 'Забыли пароль?')

    def test_logout_url(self):
        '''Тестирование ссылки для выхода с сайта.'''
        url = '/accounts/logout/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/', status_code=302, target_status_code=301)

    def test_signup_url(self):
        '''Тестирование ссылки для регистрации на сайте.'''
        url = '/accounts/signup/'
        resolver = resolve(url)
        reverse_url = reverse('accounts:signup')
        reverse_resolver = resolve(reverse_url)
        response = self.client.get(url)
        reverse_response = self.client.get(reverse_url)
        self.assertEqual(resolver.func, signup)
        self.assertEqual(reverse_resolver.func, signup)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(reverse_response.status_code, 200)
        self.assertEqual(response.templates, reverse_response.templates)
        self.assertTemplateUsed(response, 'registration/signup.html')
        self.assertTemplateUsed(response, 'registration/login.html')
        self.assertTemplateUsed(response, 'base.html')
        self.assertContains(response, 'Зарегистрироваться')
        self.assertNotContains(response, 'Вы уже зарегистрированы.')
        self.client.login(username='testuser', password='TestPassword123')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Зарегистрироваться')
        self.assertContains(response, 'Вы уже зарегистрированы.')
