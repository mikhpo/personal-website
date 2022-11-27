from django.test import TestCase
from django.urls import reverse, resolve
from blog.models import Category, Series
from main.views import main

class MainPageTest(TestCase):
    '''Тесты загрузки главной страницы сайта.'''

    url = '/main/'
    reverse_url = 'main:main'
    template = 'main/main.html'
    base_template = 'base.html'

    @classmethod
    def setUpTestData(cls):
        Category.objects.bulk_create([
            Category(name='Category 1', slug='category-1', image='image_1.jpg', public=True),
            Category(name='Category 2', slug='category-2', image='image_2.jpg', public=False),
            Category(name='Category 3', slug='category-3', image='', public=True)
        ])
        Series.objects.bulk_create([
            Series(name='Series 1', slug='series-1', image='image_1.jpg', public=True),
            Series(name='Series 2', slug='series-2', image='image_1.jpg', public=False),
            Series(name='Series 3', slug='series-3', image='', public=True)
        ])
    
    def test_main_page_redirect_url(self):
        '''Тестирование редиректа на главную страницу.'''
        response = self.client.get('/')
        self.assertRedirects(response, self.url, status_code=301, target_status_code=200)

    def test_main_page_url(self):
        '''Тестирование ссылки на главную страницу.'''
        resolver = resolve(self.url)
        response = self.client.get(self.url)
        self.assertEqual(resolver.func, main)
        self.assertEqual(response.status_code, 200)

    def test_main_page_reverse_url(self):
        '''Тестирование именной ссылки на главную страницу.'''
        url = reverse(self.reverse_url)
        resolver = resolve(url)
        response = self.client.get(url)
        self.assertEqual(resolver.func, main)
        self.assertEqual(response.status_code, 200)
    
    def test_main_page_template(self):
        '''Тестирование загрузки правильного шаблона.'''
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, self.template)
        self.assertTemplateUsed(response, self.base_template)

    def test_main_page_categories_filter(self):
        '''Проверка на корректность фильтрации категорий для главной страницы.'''
        response = self.client.get(self.url)
        target_categories = Category.objects.filter(public=True).exclude(image='')
        self.assertQuerysetEqual(target_categories, response.context['categories'])

    def test_main_page_series_filter(self):
        '''Проверка на корректность фильтрации серий для главной страницы.'''
        response = self.client.get(self.url)
        target_series = Series.objects.filter(public=True).exclude(image='')
        self.assertQuerysetEqual(target_series, response.context['series'])
        