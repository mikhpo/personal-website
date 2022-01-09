'''
Альтернативная модель пользователя была введена для того, чтобы сделать адрес электронной почты обязательным и уникальным при регистрации.
Новая модель пользователя подменяет собой стандартную модель пользователя Django.
'''

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class SignUpForm(UserCreationForm):
    '''
    Доработанная форма регистрации. От стандартной формы оличается тем, что в ней обязательно указание адреса электронной почты.
    Адрес электронной почты необходим для работы функционала по восстановлению забытых паролей.
    '''
    first_name = forms.CharField(max_length=50, help_text='Обязательно.')
    last_name = forms.CharField(max_length=50, help_text='Обязательно.')
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
        '''
        При регистрации нового пользователя проверяется: 
        - Не зарегистрирован ли уже пользователь с этой почтой. Нельзя зарегистрировать несколько пользователей с одним адресом электронной почты. 
        - Не совпадают ли имя и фамилия пользователя. Нельзя зарегистрировать пользователя, если его имя и фамилия совпадают.
        '''
        first_name = self.cleaned_data.get('first_name')
        last_name = self.cleaned_data.get('last_name')
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Пользователь с таким адресом электронной почты уже зарегистрирован!")
        if first_name == last_name:
            raise ValidationError("У вас совпадают имя и фамилия!")
        return self.cleaned_data
        