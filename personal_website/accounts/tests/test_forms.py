from django.test import TestCase
from django.contrib.auth.models import User
from accounts.forms import SignUpForm
from accounts.tests.utils import generate_unique_username

class SignUpFormTest(TestCase):
    '''Тестирование формы регистрации на сайте.'''

    signup_url = '/accounts/signup/'

    valid_credentials = {
        'username': 'test_user',
        'password1': 'test-password',
        'password2': 'test-password',
        'first_name': 'Тест',
        'last_name': 'Тестов',
        'email': 'test@example.com'
    }

    @classmethod
    def setUpTestData(cls):
        User.objects.create_user(username='testuser', password='TestPassword123')

    def test_signup_form_fields(self):
        '''Тестирует корректность полей формы регистрации пользователя.'''
        form = SignUpForm()
        form_fields = form.fields
        for field in ('username', 'first_name', 'last_name', 'email', 'password1', 'password2'):
            self.assertIn(field, form_fields)
            self.assertEqual(form_fields[field].initial, None)

    def test_signup_form_valid_credentials(self):
        '''Проверить успешность создания пользователя с корректными значениями в форме регистрации.'''
        form = SignUpForm(data=self.valid_credentials)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.clean(), form.cleaned_data)
        form.save()
        self.assertTrue(User.objects.filter(username=self.valid_credentials['username']).exists())

    def test_signup_form_invalid_password(self):
        '''Проверить, что нельзя создать пользователя с некорректной длиной пароля (менее 8 символов).'''
        # Сначала отправить форму с паролем некорректной длины.
        invalid_credentials = self.valid_credentials
        invalid_credentials['username'] = generate_unique_username()
        invalid_credentials['password1'] = 'pass'
        invalid_credentials['password2'] = invalid_credentials['password1']
        self.assertFalse(SignUpForm(data=invalid_credentials).is_valid())

        # Теперь исправить значение пароля и заново отправить форму.
        invalid_credentials['password1'] = 'test-password'
        invalid_credentials['password2'] = invalid_credentials['password1']
        self.assertTrue(SignUpForm(data=invalid_credentials).is_valid())

    def test_signup_form_matching_passwords(self):
        '''Проверить, что нельзя создать пользователя если пароль и подтверждение пароля не совпадают.'''
        # Сначала отправить форму с несовпадающими паролем и подтверждением пароля.
        invalid_credentials = self.valid_credentials
        invalid_credentials['username'] = generate_unique_username()
        invalid_credentials['password1'] = 'test-password'
        invalid_credentials['password2'] = invalid_credentials['password1'] + '-invalid'
        self.assertFalse(SignUpForm(data=invalid_credentials).is_valid())

        # Теперь исправить подтверждение пароля и заново отправить форму.
        invalid_credentials['password2'] = invalid_credentials['password1']
        self.assertTrue(SignUpForm(data=invalid_credentials).is_valid())

    def test_signup_form_invalid_email(self):
        '''Проверяет корректность формата значения адреса электронной почты.'''
        #  Сначала отправить форму с некорректным адресом электронной почты и убедиться, что валидация не пройдена.
        invalid_credentials = self.valid_credentials
        invalid_credentials['username'] = generate_unique_username()
        invalid_credentials['email'] = 'example'
        self.assertFalse(SignUpForm(data=invalid_credentials).is_valid())

        #  Исправить формат значения адреса электронной почты и убедиться, что валидация пройдена.
        invalid_credentials['email'] = 'test@example.com'
        self.assertTrue(SignUpForm(data=invalid_credentials).is_valid())

    def test_signup_form_fields_required(self):
        '''Проверить, что без заполнения обязательных полей форма не принимается.'''
        valid_form  = SignUpForm(data=self.valid_credentials)
        self.assertTrue(valid_form.is_valid())
        invalid_credentials = {
            'username': generate_unique_username(),
            'password1': 'test-password',
            'password2': 'test-password',
            'first_name': '',
            'last_name': '',
            'email': ''
        }
        self.assertFalse(SignUpForm(data=invalid_credentials).is_valid())

    def test_signup_form_email_unique(self):
        pass # TODO

    def test_signup_form_first_and_last_names_not_match(self):
        pass # TODO
