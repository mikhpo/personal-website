"""Тесты форм системы авторизации пользователей."""

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils.crypto import get_random_string

from accounts.forms import SignUpForm
from accounts.utils import generate_unique_username

VALID_CREDENTIALS = {
    "username": "test_user",
    "password1": "test-password",
    "password2": "test-password",
    "first_name": "Тест",
    "last_name": "Тестов",
    "email": "test@example.com",
}


class SignUpFormTest(TestCase):
    """Тестирование формы регистрации на сайте."""

    signup_url = "/accounts/signup/"

    @classmethod
    def setUpTestData(cls) -> None:
        """Создать тестового пользователя."""
        User.objects.create_user(username="testuser", password="TestPassword123")

    def test_signup_form_fields(self) -> None:
        """Тестирует корректность полей формы регистрации пользователя."""
        form = SignUpForm()
        form_fields = form.fields
        for field in (
            "username",
            "first_name",
            "last_name",
            "email",
            "password1",
            "password2",
        ):
            self.assertIn(field, form_fields)
            self.assertEqual(form_fields[field].initial, None)

    def test_signup_form_valid_credentials(self) -> None:
        """Проверить успешность создания пользователя с корректными значениями в форме регистрации."""
        form = SignUpForm(data=VALID_CREDENTIALS)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.clean(), form.cleaned_data)
        form.save()
        self.assertTrue(User.objects.filter(username=VALID_CREDENTIALS["username"]).exists())

    def test_signup_form_invalid_password(self) -> None:
        """Проверить, что нельзя создать пользователя с некорректной длиной пароля (менее 8 символов)."""
        # Сначала отправить форму с паролем некорректной длины.
        invalid_credentials = VALID_CREDENTIALS.copy()
        invalid_credentials["username"] = generate_unique_username()
        invalid_credentials["password1"] = "pass"
        invalid_credentials["password2"] = invalid_credentials["password1"]
        self.assertFalse(SignUpForm(data=invalid_credentials).is_valid())

        # Теперь исправить значение пароля и заново отправить форму.
        invalid_credentials["password1"] = "test-password"
        invalid_credentials["password2"] = invalid_credentials["password1"]
        self.assertTrue(SignUpForm(data=invalid_credentials).is_valid())

    def test_signup_form_matching_passwords(self) -> None:
        """Проверить, что нельзя создать пользователя если пароль и подтверждение пароля не совпадают."""
        # Сначала отправить форму с несовпадающими паролем и подтверждением пароля.
        invalid_credentials = VALID_CREDENTIALS.copy()
        invalid_credentials["username"] = generate_unique_username()
        invalid_credentials["password1"] = "test-password"
        invalid_credentials["password2"] = invalid_credentials["password1"] + "-invalid"
        self.assertFalse(SignUpForm(data=invalid_credentials).is_valid())

        # Теперь исправить подтверждение пароля и заново отправить форму.
        invalid_credentials["password2"] = invalid_credentials["password1"]
        self.assertTrue(SignUpForm(data=invalid_credentials).is_valid())

    def test_signup_form_invalid_email(self) -> None:
        """Проверяет корректность формата значения адреса электронной почты."""
        #  Сначала отправить форму с некорректным адресом электронной почты и убедиться, что валидация не пройдена.
        invalid_credentials = VALID_CREDENTIALS.copy()
        invalid_credentials["username"] = generate_unique_username()
        invalid_credentials["email"] = "example"
        self.assertFalse(SignUpForm(data=invalid_credentials).is_valid())

        #  Исправить формат значения адреса электронной почты и убедиться, что валидация пройдена.
        invalid_credentials["email"] = "test@example.com"
        self.assertTrue(SignUpForm(data=invalid_credentials).is_valid())

    def test_signup_form_fields_required(self) -> None:
        """Проверить, что без заполнения обязательных полей форма не принимается."""
        valid_form = SignUpForm(data=VALID_CREDENTIALS)
        self.assertTrue(valid_form.is_valid())
        invalid_credentials = {
            "username": generate_unique_username(),
            "password1": "test-password",
            "password2": "test-password",
            "first_name": get_random_string(5),
            "last_name": get_random_string(5),
            "email": "",
        }
        self.assertFalse(SignUpForm(data=invalid_credentials).is_valid())

    def test_signup_form_email_unique(self) -> None:
        """Проверить, что нельзя создать двух пользователей с одним адресом электронной почты."""
        # Сначала создать первого пользователя с данным адресом электронной почты.
        form = SignUpForm(data=VALID_CREDENTIALS)
        self.assertTrue(form.is_valid())
        form.save()
        self.assertTrue(User.objects.filter(username=VALID_CREDENTIALS["username"]).exists())

        # Теперь создать второго пользователя с данным адресом электронной почты.
        invalid_credentials = {
            "username": generate_unique_username(),
            "password1": "test-password",
            "password2": "test-password",
            "first_name": get_random_string(5),
            "last_name": get_random_string(5),
            "email": VALID_CREDENTIALS["email"],
        }
        form = SignUpForm(data=invalid_credentials)
        self.assertFalse(form.is_valid())

    def test_signup_form_first_and_last_names_not_match(self) -> None:
        """Проверить, что имя и фамилия не могут совпадать."""
        invalid_credentials = VALID_CREDENTIALS.copy()
        invalid_credentials["last_name"] = invalid_credentials["first_name"]
        form = SignUpForm(data=invalid_credentials)
        self.assertFalse(form.is_valid())
        invalid_credentials["last_name"] = VALID_CREDENTIALS["last_name"]
        form = SignUpForm(data=invalid_credentials)
        self.assertTrue(form.is_valid())
