import os
import random
from django.test import TestCase
from django.urls import resolve, reverse
from django.utils.crypto import get_random_string
from django.contrib.auth import get_user
from django.contrib.auth.models import User
from blog.models import Article, Comment, Category, Topic, Series
from blog.views import blog, ArticleDetailView, category, topic, series
from blog.tests.utils import generate_random_text
from personal_website.settings import TEMPLATES

class BlogIndexPageTest(TestCase):
    '''Тесты главной страницы блога.'''

    blog_index_url = '/blog/'
    reverse_blog_index_url = 'blog:blog'
    article_list_template = 'blog/blog_index.html'
    base_template = 'base.html'

    @classmethod
    def setUpTestData(cls):
        for n in range(21):
            Article.objects.create(title=f'Article {n}', slug=f'article-{n}', public=random.choice([True, False]))

    def test_blog_index_url(self):
        '''Тестирование ссылки на главную страницу блога.'''
        resolver = resolve(self.blog_index_url)
        response = self.client.get(self.blog_index_url)
        self.assertEqual(resolver.func, blog)
        self.assertEqual(response.status_code, 200)

    def test_blog_index_reverse_url(self):
        '''Тестирование именной ссылки на главную страницу блога.'''
        response = self.client.get(self.blog_index_url)
        url = reverse(self.reverse_blog_index_url)
        resolver = resolve(url)
        reverse_response = self.client.get(url)
        self.assertEqual(resolver.func, blog)
        self.assertEqual(reverse_response.status_code, 200)
        self.assertEqual(response.templates, reverse_response.templates)
    
    def test_blog_index_template(self):
        '''Тестирование корректности загрузки шаблона для списка статей.'''
        response = self.client.get(self.blog_index_url)
        self.assertTemplateUsed(response, self.article_list_template)
        self.assertTemplateUsed(response, self.base_template)

    def test_blog_index_template_elements(self):
        '''Тестирование наличия в шаблоне главной страницы блога HTML-элементов для карточки статьи и паджинации.'''
        response = self.client.get(self.blog_index_url)
        self.assertContains(response, 'class="card-body"')
        self.assertContains(response, 'class="card-title"')
        self.assertContains(response, 'class="card-text"')
        self.assertContains(response, 'class="pagination"')

    def test_blog_index_pagination(self):
        '''Проверка на корректность паджинации статей блога на главной странице блога.'''
        response = self.client.get(self.blog_index_url)
        self.assertTrue('page_obj' in response.context)
        self.assertLessEqual(len(response.context['page_obj']), 5)
    
    def test_blog_index_content_filter(self):
        '''Тест на фильтрацию контента на главной странице блога.'''
        response = self.client.get(self.blog_index_url)
        all([self.assertTrue(article.public) for article in response.context['page_obj']])

    def test_blog_index_text_truncated(self):
        '''Проверяет, что текст статьи скрыт за катом, если длина текста более 200 слов.'''
        Article.objects.filter(public=True).update(public=False)
        Article.objects.create(title='Long article', slug='long-article', public=True, content=generate_random_text(201)) 
        response = self.client.get(self.blog_index_url)
        self.assertContains(response, '>Читать дальше<')

    def test_blog_index_text_not_truncated(self):
        '''Проверяет, что текст статьи не скрыт за катом, если длина текста менее 200 слов.'''
        Article.objects.filter(public=True).update(public=False)
        Article.objects.create(title='Short article', slug='short-article', public=True, content=generate_random_text(101)) 
        response = self.client.get(self.blog_index_url)
        self.assertNotContains(response, '>Читать дальше<')

    def test_blog_index_content_safe(self):
        '''Проверяет, что в HTML-шаблоне блога содержание статей показывается без HTML-разметки.'''
        templates_dir = TEMPLATES[0]['DIRS'][0]
        template_location = os.path.join(templates_dir, self.article_list_template)
        with open(template_location, 'r') as f:
            self.assertIn('article.content|safe', f.read())

    def test_blog_index_article_order(self):
        '''Проверяет, что статьи на главной странице блога отсортированы в правильном порядке.'''
        response = self.client.get(self.blog_index_url)
        target_articles = Article.objects.filter(public=True).order_by('-published')[:5]
        response_articles = response.context['page_obj']
        self.assertQuerysetEqual(target_articles, response_articles)

class ArticleDetailPageTest(TestCase):
    '''Тесты детального просмотра статей.'''

    article_detail_url = '/blog/article/'
    reverse_article_detail_url = 'blog:article'
    article_detail_template = 'blog/article_detail.html'
    base_template = 'base.html'
    logger = 'personal_website'

    @classmethod
    def setUpTestData(cls):
        User.objects.create_user(username='testuser', email='testuser@example.com', password='12345')
        Article.objects.create(title='Test article', slug='article-test', content=get_random_string(250))        
    
    def test_article_detail_url(self):
        '''Тестирование ссылки на детальный просмотр статьи блога.'''
        article = Article.objects.get(title='Test article')
        url = self.article_detail_url + article.slug + '/'
        resolver = resolve(url)
        response = self.client.get(url)
        self.assertEqual(resolver.func.view_class, ArticleDetailView)
        self.assertEqual(response.status_code, 200) 

    def test_article_detail_reverse_url(self):
        '''Тестирование обратной ссылки на детальный просмотр статьи блога.'''
        article = Article.objects.get(title='Test article')
        url = self.article_detail_url + article.slug + '/'
        response = self.client.get(url)
        reverse_url = reverse(self.reverse_article_detail_url, args=(article.slug,))
        resolver = resolve(reverse_url)
        reverse_response = self.client.get(reverse_url)
        self.assertEqual(resolver.func.view_class, ArticleDetailView)
        self.assertEqual(reverse_response.status_code, 200)
        self.assertEqual(response.templates, reverse_response.templates)

    def test_article_detail_template(self):
        '''Тестирование корректности загрузки шаблона для просмотра статьи.'''
        article = Article.objects.get(title='Test article')
        url = self.article_detail_url + article.slug + '/'
        response = self.client.get(url)
        self.assertTemplateUsed(response, self.article_detail_template)
        self.assertTemplateUsed(response, self.base_template)

    def test_article_detail_template_elements(self):
        '''Тестирование наличия в шаблоне просмотра статьи HTML-элементов для атрибутов статьи и паджинации.'''
        article = Article.objects.get(title='Test article')
        url = reverse(self.reverse_article_detail_url, args=(article.slug,))
        response = self.client.get(url)
        self.assertContains(response, 'class="card-body"')
        self.assertContains(response, 'class="card-title"')
        self.assertContains(response, 'class="card-text"')
        self.assertContains(response, 'class="card-footer"')
        self.assertContains(response, 'id="comments_section"')

    def test_article_page_content(self):
        '''Тестирование соответствия содержания статьи контексту, переданному в шаблон.'''
        article = Article.objects.get(title='Test article')
        url = reverse(self.reverse_article_detail_url, args=(article.slug,))
        response = self.client.get(url)
        context: Article = response.context['article']
        self.assertEqual(article.title, context.title)
        self.assertEqual(article.content, context.content)
        self.assertEqual(article.published, context.published)
        self.assertEqual(article.modified, context.modified)

    def test_article_comment_button_access(self):
        '''Тестирование добавления и вывода комментариев к статьям в блоге.'''
        article = Article.objects.get(title='Test article')
        url = reverse(self.reverse_article_detail_url, args=(article.slug,))
        self.assertFalse(get_user(self.client).is_authenticated)
        response = self.client.get(url)
        self.assertNotContains(response, "Добавить комментарий")
        self.client.login(username='testuser', password='12345')
        self.assertTrue(get_user(self.client).is_authenticated)
        response = self.client.get(url)
        self.assertContains(response, "Добавить комментарий")

    def test_comments_post(self):
        '''Проверка на обязательность авторизации перед созданием комментария.'''
        article = Article.objects.get(title='Test article')
        url = reverse(self.reverse_article_detail_url, args=(article.slug,))
        with self.assertRaises(ValueError):
            response = self.client.post(url, data={'content': 'test comment'})
        self.client.login(username='testuser', password='12345')
        response = self.client.post(url, data={'content': 'test comment'})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Comment.objects.filter(content='test comment').exists())

    def test_comments_logging(self):
        '''Проверка на запись в лог факта создания нового комментария.'''
        article = Article.objects.get(title='Test article')
        url = reverse(self.reverse_article_detail_url, args=(article.slug,))
        self.client.login(username='testuser', password='12345')
        with self.assertLogs(logger=self.logger, level='INFO') as cm:
            response = self.client.post(url, data={'content': 'test comment'})
            user = response.context['user']
            self.assertIn(f'INFO:{self.logger}:Пользователь {user} оставил комментарий к статье "{article}"', cm.output)
        
    def test_comments_ordered_by_posted(self):
        '''Проверка порядка показа комментариев.'''
        article = Article.objects.get(title='Test article')
        user = User.objects.get(username='testuser')
        for i in range(1, 6):
            Comment.objects.create(article=article, author=user, content=f'test comment {i}')
        url = reverse(self.reverse_article_detail_url, args=(article.slug,))
        response = self.client.get(url)
        target_comments = Comment.objects.filter(article=article).order_by('posted')
        response_comments = response.context['comments']
        self.assertQuerysetEqual(target_comments, response_comments)
        self.assertEqual(response_comments[0].content, 'test comment 1')
        
    def test_article_content_safe(self):
        '''Проверяет, что в HTML-шаблоне статьи содержание статьи показывается '''
        templates_dir = TEMPLATES[0]['DIRS'][0]
        template_location = os.path.join(templates_dir, self.article_detail_template)
        with open(template_location, 'r') as f:
            self.assertIn('article.content|safe', f.read())

class CategoryPageTest(TestCase):
    '''Тесты страницы просмотра статей по определенной категории.'''

    category_url = '/blog/category/'
    reverse_category_url = 'blog:category'
    category_template = 'blog/blog_index.html'
    base_template = 'base.html'

    @classmethod
    def setUpTestData(cls):
        cls.test_category = Category.objects.create(name='Test category', slug='test-category')
        for n in range(20):
            article = Article.objects.create(title=f'Article {n}', slug=f'article-{n}', public=random.choice([True, False]))
            article.categories.add(cls.test_category)

    def test_category_url(self):
        '''Тестирование ссылки на категорию.'''
        url = self.category_url + self.test_category.slug + '/'
        resolver = resolve(url)
        response = self.client.get(url)
        self.assertEqual(resolver.func, category)
        self.assertEqual(response.status_code, 200)

    def test_category_reverse_url(self):
        '''Тестирование именной ссылки на категорию.'''
        url = self.category_url + self.test_category.slug + '/'
        response = self.client.get(url)
        reverse_url = reverse(self.reverse_category_url, args=(self.test_category.slug,))
        resolver = resolve(reverse_url)
        reverse_response = self.client.get(reverse_url)
        self.assertEqual(resolver.func, category)
        self.assertEqual(reverse_response.status_code, 200)
        self.assertEqual(response.templates, reverse_response.templates)
    
    def test_category_template(self):
        '''Тестирование корректности загрузки шаблона для списка статей в категории.'''
        url = reverse(self.reverse_category_url, args=(self.test_category.slug,))
        response = self.client.get(url)
        self.assertTemplateUsed(response, self.category_template)
        self.assertTemplateUsed(response, self.base_template)

    def test_category_template_elements(self):
        '''Тестирование наличия в шаблоне категории HTML-элементов для карточки статьи и паджинации.'''
        url = reverse(self.reverse_category_url, args=(self.test_category.slug,))
        response = self.client.get(url)
        self.assertContains(response, 'class="card-body"')
        self.assertContains(response, 'class="card-title"')
        self.assertContains(response, 'class="card-text"')
        self.assertContains(response, 'class="pagination"')

    def test_category_pagination(self):
        '''Проверка на корректность паджинации статей в категории.'''
        url = reverse(self.reverse_category_url, args=(self.test_category.slug,))
        response = self.client.get(url)
        self.assertTrue('page_obj' in response.context)
        self.assertLessEqual(len(response.context['page_obj']), 5)
    
    def test_category_content_filter(self):
        '''Тест на фильтрацию контента на странице просмотра категории.'''
        url = reverse(self.reverse_category_url, args=(self.test_category.slug,))
        response = self.client.get(url)
        all([self.assertTrue(article.public) for article in response.context['page_obj']])

    def test_category_page_text_truncated(self):
        '''Проверяет, что текст статьи в категории скрыт за катом, если длина текста более 200 слов.'''
        Article.objects.filter(public=True, categories=self.test_category).update(public=False)
        article = Article.objects.create(title='Long article', slug='long-article', public=True, content=generate_random_text(201))
        article.categories.add(self.test_category)
        url = reverse(self.reverse_category_url, args=(self.test_category.slug,))
        response = self.client.get(url)
        self.assertContains(response, '>Читать дальше<')

    def test_category_page_text_not_truncated(self):
        '''Проверяет, что текст статьи в категории не скрыт за катом, если длина текста менее 200 слов.'''
        Article.objects.filter(public=True, categories=self.test_category).update(public=False)
        article = Article.objects.create(title='Short article', slug='short-article', public=True, content=generate_random_text(101))
        article.categories.add(self.test_category) 
        url = reverse(self.reverse_category_url, args=(self.test_category.slug,))
        response = self.client.get(url)
        self.assertNotContains(response, '>Читать дальше<')

    def test_category_content_safe(self):
        '''Проверяет, что в HTML-шаблоне списка статей в категории содержание статей показывается без HTML-разметки.'''
        templates_dir = TEMPLATES[0]['DIRS'][0]
        template_location = os.path.join(templates_dir, self.category_template)
        with open(template_location, 'r') as f:
            self.assertIn('article.content|safe', f.read())

    def test_category_article_order(self):
        '''Проверяет, что статьи в категории отсортированы в правильном порядке.'''
        url = reverse(self.reverse_category_url, args=(self.test_category.slug,))
        response = self.client.get(url)
        target_articles = Article.objects.filter(public=True, categories=self.test_category).order_by('-published')[:5]
        response_articles = response.context['page_obj']
        self.assertQuerysetEqual(target_articles, response_articles)

class TopicPageTest(TestCase):
    '''Тесты страницы просмотра статей, посвященных определенной теме.'''

    topic_url = '/blog/topic/'
    reverse_topic_url = 'blog:topic'
    topic_template = 'blog/blog_index.html'
    base_template = 'base.html'

    @classmethod
    def setUpTestData(cls):
        cls.test_topic = Topic.objects.create(name='Test topic', slug='test-topic')
        for n in range(20):
            article = Article.objects.create(title=f'Article {n}', slug=f'article-{n}', public=random.choice([True, False]))
            article.topics.add(cls.test_topic)

    def test_topic_url(self):
        '''Тестирование ссылки на тему.'''
        url = self.topic_url + self.test_topic.slug + '/'
        resolver = resolve(url)
        response = self.client.get(url)
        self.assertEqual(resolver.func, topic)
        self.assertEqual(response.status_code, 200)

    def test_topic_reverse_url(self):
        '''Тестирование именной ссылки на тему.'''
        url = self.topic_url + self.test_topic.slug + '/'
        response = self.client.get(url)
        reverse_url = reverse(self.reverse_topic_url, args=(self.test_topic.slug,))
        resolver = resolve(reverse_url)
        reverse_response = self.client.get(reverse_url)
        self.assertEqual(resolver.func, topic)
        self.assertEqual(reverse_response.status_code, 200)
        self.assertEqual(response.templates, reverse_response.templates)
    
    def test_topic_template(self):
        '''Тестирование корректности загрузки шаблона для списка статей по теме.'''
        url = reverse(self.reverse_topic_url, args=(self.test_topic.slug,))
        response = self.client.get(url)
        self.assertTemplateUsed(response, self.topic_template)
        self.assertTemplateUsed(response, self.base_template)

    def test_topic_template_elements(self):
        '''Тестирование наличия в шаблоне темы HTML-элементов для карточки статьи и паджинации.'''
        url = reverse(self.reverse_topic_url, args=(self.test_topic.slug,))
        response = self.client.get(url)
        self.assertContains(response, 'class="card-body"')
        self.assertContains(response, 'class="card-title"')
        self.assertContains(response, 'class="card-text"')
        self.assertContains(response, 'class="pagination"')

    def test_topic_pagination(self):
        '''Проверка на корректность паджинации статей по теме.'''
        url = reverse(self.reverse_topic_url, args=(self.test_topic.slug,))
        response = self.client.get(url)
        self.assertTrue('page_obj' in response.context)
        self.assertLessEqual(len(response.context['page_obj']), 5)
    
    def test_topic_content_filter(self):
        '''Тест на фильтрацию контента на странице просмотра темы.'''
        url = reverse(self.reverse_topic_url, args=(self.test_topic.slug,))
        response = self.client.get(url)
        all([self.assertTrue(article.public) for article in response.context['page_obj']])

    def test_topic_page_text_truncated(self):
        '''Проверяет, что текст статьи по теме скрыт за катом, если длина текста более 200 слов.'''
        Article.objects.filter(public=True, topics=self.test_topic).update(public=False)
        article = Article.objects.create(title='Long article', slug='long-article', public=True, content=generate_random_text(201))
        article.topics.add(self.test_topic)
        url = reverse(self.reverse_topic_url, args=(self.test_topic.slug,))
        response = self.client.get(url)
        self.assertContains(response, '>Читать дальше<')

    def test_topic_page_text_not_truncated(self):
        '''Проверяет, что текст статьи по теме не скрыт за катом, если длина текста менее 200 слов.'''
        Article.objects.filter(public=True, topics=self.test_topic).update(public=False)
        article = Article.objects.create(title='Short article', slug='short-article', public=True, content=generate_random_text(101))
        article.topics.add(self.test_topic) 
        url = reverse(self.reverse_topic_url, args=(self.test_topic.slug,))
        response = self.client.get(url)
        self.assertNotContains(response, '>Читать дальше<')

    def test_topic_content_safe(self):
        '''Проверяет, что в HTML-шаблоне списка статей по теме содержание статей показывается без HTML-разметки.'''
        templates_dir = TEMPLATES[0]['DIRS'][0]
        template_location = os.path.join(templates_dir, self.topic_template)
        with open(template_location, 'r') as f:
            self.assertIn('article.content|safe', f.read())

    def test_topic_article_order(self):
        '''Проверяет, что статьи по теме отсортированы в правильном порядке.'''
        url = reverse(self.reverse_topic_url, args=(self.test_topic.slug,))
        response = self.client.get(url)
        target_articles = Article.objects.filter(public=True, topics=self.test_topic).order_by('-published')[:5]
        response_articles = response.context['page_obj']
        self.assertQuerysetEqual(target_articles, response_articles)

class SeriesPageTest(TestCase):
    '''Тесты страницы просмотра статей из определенной серии.'''

    series_url = '/blog/series/'
    reverse_series_url = 'blog:series'
    series_template = 'blog/blog_index.html'
    base_template = 'base.html'

    @classmethod
    def setUpTestData(cls):
        cls.test_series = Series.objects.create(name='Test series', slug='test-series')
        for n in range(20):
            article = Article.objects.create(title=f'Article {n}', slug=f'article-{n}', public=random.choice([True, False]))
            article.series.add(cls.test_series)

    def test_series_url(self):
        '''Тестирование ссылки на серию.'''
        url = self.series_url + self.test_series.slug + '/'
        resolver = resolve(url)
        response = self.client.get(url)
        self.assertEqual(resolver.func, series)
        self.assertEqual(response.status_code, 200)

    def test_series_reverse_url(self):
        '''Тестирование именной ссылки на серию.'''
        url = self.series_url + self.test_series.slug + '/'
        response = self.client.get(url)
        reverse_url = reverse(self.reverse_series_url, args=(self.test_series.slug,))
        resolver = resolve(reverse_url)
        reverse_response = self.client.get(reverse_url)
        self.assertEqual(resolver.func, series)
        self.assertEqual(reverse_response.status_code, 200)
        self.assertEqual(response.templates, reverse_response.templates)
    
    def test_series_template(self):
        '''Тестирование корректности загрузки шаблона для списка статей из серии.'''
        url = reverse(self.reverse_series_url, args=(self.test_series.slug,))
        response = self.client.get(url)
        self.assertTemplateUsed(response, self.series_template)
        self.assertTemplateUsed(response, self.base_template)

    def test_series_template_elements(self):
        '''Тестирование наличия в шаблоне серии HTML-элементов для карточки статьи и паджинации.'''
        url = reverse(self.reverse_series_url, args=(self.test_series.slug,))
        response = self.client.get(url)
        self.assertContains(response, 'class="card-body"')
        self.assertContains(response, 'class="card-title"')
        self.assertContains(response, 'class="card-text"')
        self.assertContains(response, 'class="pagination"')

    def test_series_pagination(self):
        '''Проверка на корректность паджинации статей из серии.'''
        url = reverse(self.reverse_series_url, args=(self.test_series.slug,))
        response = self.client.get(url)
        self.assertTrue('page_obj' in response.context)
        self.assertLessEqual(len(response.context['page_obj']), 5)
    
    def test_series_content_filter(self):
        '''Тест на фильтрацию контента на странице просмотра серии.'''
        url = reverse(self.reverse_series_url, args=(self.test_series.slug,))
        response = self.client.get(url)
        all([self.assertTrue(article.public) for article in response.context['page_obj']])

    def test_series_page_text_truncated(self):
        '''Проверяет, что текст статьи из серии скрыт за катом, если длина текста более 200 слов.'''
        Article.objects.filter(public=True, series=self.test_series).update(public=False)
        article = Article.objects.create(title='Long article', slug='long-article', public=True, content=generate_random_text(201))
        article.series.add(self.test_series)
        url = reverse(self.reverse_series_url, args=(self.test_series.slug,))
        response = self.client.get(url)
        self.assertContains(response, '>Читать дальше<')

    def test_series_page_text_not_truncated(self):
        '''Проверяет, что текст статьи из серии не скрыт за катом, если длина текста менее 200 слов.'''
        Article.objects.filter(public=True, series=self.test_series).update(public=False)
        article = Article.objects.create(title='Short article', slug='short-article', public=True, content=generate_random_text(101))
        article.series.add(self.test_series) 
        url = reverse(self.reverse_series_url, args=(self.test_series.slug,))
        response = self.client.get(url)
        self.assertNotContains(response, '>Читать дальше<')

    def test_series_content_safe(self):
        '''Проверяет, что в HTML-шаблоне списка статей из серии содержание статей показывается без HTML-разметки.'''
        templates_dir = TEMPLATES[0]['DIRS'][0]
        template_location = os.path.join(templates_dir, self.series_template)
        with open(template_location, 'r') as f:
            self.assertIn('article.content|safe', f.read())

    def test_series_article_order(self):
        '''Проверяет, что статьи из серии отсортированы в правильном порядке.'''
        url = reverse(self.reverse_series_url, args=(self.test_series.slug,))
        response = self.client.get(url)
        target_articles = Article.objects.filter(public=True, series=self.test_series).order_by('-published')[:5]
        response_articles = response.context['page_obj']
        self.assertQuerysetEqual(target_articles, response_articles)
