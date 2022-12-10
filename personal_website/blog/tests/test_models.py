from django.test import TestCase
from django.db.utils import IntegrityError
from blog.models import Article, Series, Topic, Category

class ArticleModelTest(TestCase):
    '''Тесты модели статьи.'''

    def test_article_title_unique(self):
        '''Проверка на то, что невозможно создать несколько статей с одним заголовком.'''
        Article.objects.create(title='Test article')
        with self.assertRaises(IntegrityError):
            Article.objects.create(title='Test article')
        
    def test_article_auto_slug(self):
        '''Проверка на то, что слаг статьи создается автоматически, когда не указан вручную, транслитерируется автоматически, уникальность достигается добавлением идентификатора.'''
        first_article = Article.objects.create(title='First test article')
        self.assertEqual(first_article.slug, 'first-test-article')
        second_article = Article.objects.create(title='Вторая тестовая статья')
        self.assertEqual(second_article.slug, 'vtoraya-testovaya-statya')
        third_article = Article.objects.create(title='Третья тестовая статья', slug='third-test-article')
        self.assertEqual(third_article.slug, 'third-test-article')
        fourth_article = Article.objects.create(title='Third test article')
        self.assertEqual(fourth_article.slug, 'third-test-article-2')

    def test_article_absolute_url(self):
        '''Проверяется корректность создания абсолютной ссылки на статью.'''
        article = Article.objects.create(title='Test article', slug='test-article')
        url = '/blog/article/' + article.slug + '/'
        absolute_url = article.get_absolute_url()
        self.assertEqual(url, absolute_url)

class SeriesModelTest(TestCase):
    '''Тесты модели серии статей.'''

    def test_series_name_unique(self):
        '''Проверка на то, что невозможно создать несколько серий с одним названием.'''
        Series.objects.create(name='Test series')
        with self.assertRaises(IntegrityError):
            Series.objects.create(name='Test series')

    def test_series_auto_slug(self):
        '''Проверка на то, что слаг серии создается автоматически, когда не указан вручную, транслитерируется автоматически, уникальность достигается добавлением идентификатора.'''
        first_series = Series.objects.create(name='First test series')
        self.assertEqual(first_series.slug, 'first-test-series')
        second_series = Series.objects.create(name='Вторая тестовая серия')
        self.assertEqual(second_series.slug, 'vtoraya-testovaya-seriya')
        third_series = Series.objects.create(name='Третья тестовая серия', slug='third-test-series')
        self.assertEqual(third_series.slug, 'third-test-series')
        fourth_series = Series.objects.create(name='Third test series')
        self.assertEqual(fourth_series.slug, 'third-test-series-2')

    def test_series_absolute_url(self):
        '''Проверяется корректность создания абсолютной ссылки на серию.'''
        series = Series.objects.create(name='Test series', slug='test-series')
        url = '/blog/series/' + series.slug + '/'
        absolute_url = series.get_absolute_url()
        self.assertEqual(url, absolute_url)

class TopicModelTest(TestCase):
    '''Тесты модели темы статей.'''

    def test_topic_name_unique(self):
        '''Проверка на то, что невозможно создать несколько тем с одним названием.'''
        Topic.objects.create(name='Test topic')
        with self.assertRaises(IntegrityError):
            Topic.objects.create(name='Test topic')

    def test_topic_auto_slug(self):
        '''Проверка на то, что слаг темы создается автоматически, когда не указан вручную, транслитерируется автоматически, уникальность достигается добавлением идентификатора.'''
        first_topic = Topic.objects.create(name='First test topic')
        self.assertEqual(first_topic.slug, 'first-test-topic')
        second_topic = Topic.objects.create(name='Вторая тестовая тема')
        self.assertEqual(second_topic.slug, 'vtoraya-testovaya-tema')
        third_topic = Topic.objects.create(name='Третья тестовая тема', slug='third-test-topic')
        self.assertEqual(third_topic.slug, 'third-test-topic')
        fourth_topic = Topic.objects.create(name='Third test topic')
        self.assertEqual(fourth_topic.slug, 'third-test-topic-2')
    
    def test_topic_absolute_url(self):
        '''Проверяется корректность создания абсолютной ссылки на тему.'''
        topic = Topic.objects.create(name='Test topic', slug='test-topic')
        url = '/blog/topic/' + topic.slug + '/'
        absolute_url = topic.get_absolute_url()
        self.assertEqual(url, absolute_url)

class CategoryModelTest(TestCase):
    '''Тесты модели категории статей.'''

    def test_category_name_unique(self):
        '''Проверка на то, что невозможно создать несколько категорий с одним названием.'''
        Category.objects.create(name='Test category')
        with self.assertRaises(IntegrityError):
            Category.objects.create(name='Test category')
    
    def test_category_auto_slug(self):
        '''Проверка на то, что слаг категории создается автоматически, когда не указан вручную, транслитерируется автоматически, уникальность достигается добавлением идентификатора.'''
        first_category = Category.objects.create(name='First test category')
        self.assertEqual(first_category.slug, 'first-test-category')
        second_category = Category.objects.create(name='Вторая тестовая категория')
        self.assertEqual(second_category.slug, 'vtoraya-testovaya-kategoriya')
        third_category = Category.objects.create(name='Третья тестовая категория', slug='third-test-category')
        self.assertEqual(third_category.slug, 'third-test-category')
        fourth_category = Category.objects.create(name='Third test category')
        self.assertEqual(fourth_category.slug, 'third-test-category-2')

    def test_category_absolute_url(self):
        '''Проверяется корректность создания абсолютной ссылки на категорию.'''
        category = Category.objects.create(name='Test category', slug='test-category')
        url = '/blog/category/' + category.slug + '/'
        absolute_url = category.get_absolute_url()
        self.assertEqual(url, absolute_url)