from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=50, required=False, help_text='Необязательно.')
    last_name = forms.CharField(max_length=50, required=False, help_text='Необязательно.')
    email = forms.EmailField(max_length=254, help_text='Обязательно. Пожалуйста, предоставьте корректный адрес электронной почты.')

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', )
    
    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].label = 'Имя'
        self.fields['last_name'].label = 'Фамилия'
        self.fields['email'].label = 'Адрес электронной почты'
        self.fields['password1'].help_text = '''Пароль не должен быть слишком похож на другую вашу личную информацию.<br/>
                                                Ваш пароль должен содержать как минимум 8 символов.<br/>
                                                Пароль не должен представлять собой распространенные последовательности символов.<br/>
                                                Пароль не может состоять только из цифр.'''

    def clean(self):
       email = self.cleaned_data.get('email')
       if User.objects.filter(email=email).exists():
            raise ValidationError("Пользователь с таким адресом электронной почты уже зарегистрирован!")
       return self.cleaned_data
        