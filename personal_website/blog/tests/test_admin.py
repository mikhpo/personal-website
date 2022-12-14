from django.test import TestCase
from django.contrib.auth.models import User
from blog.apps import BlogConfig
from blog.models import Article, Comment, Series, Topic, Category
from blog.tests.utils import generate_random_text, localize_datetime

class BlogAdminTest(TestCase):

    admin_url = '/admin/'

    @classmethod
    def setUpTestData(cls):
        cls.superuser: User = User.objects.create_superuser(username='testadmin', password='12345')
        cls.series: Series = Series.objects.create(name='Test series', image='series_image.jpg')
        cls.topic: Topic = Topic.objects.create(name='Test topic', image='topic_image.jpg')
        cls.category: Category = Category.objects.create(name='Test category', image='category_image.jpg')
        cls.article: Article = Article.objects.create(title='Test article', content=generate_random_text(50), author=cls.superuser)
        cls.comment: Comment = Comment.objects.create(article=cls.article, author=cls.superuser, content=generate_random_text(10))

    def setUp(self):
        self.client.login(username='testadmin', password='12345')

    def test_blog_admin_page_displayed(self):
        '''Проверяет, что в административной панели отображется раздел блога.'''
        app_verbose_name = BlogConfig.verbose_name
        response = self.client.get(self.admin_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, app_verbose_name)
        response = self.client.get(self.admin_url + 'blog/')
        self.assertEqual(response.status_code, 200)
        for action in ['Добавить', 'Изменить']:
            self.assertContains(response, action)

    def test_article_admin_page_displayed(self):
        '''Проверяет, что в административной панели отображается модель статьи.'''
        articles_verbose_name = Article._meta.verbose_name_plural
        self.assertNotEqual(articles_verbose_name, None)
        response = self.client.get(self.admin_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, articles_verbose_name)
        response = self.client.get(self.admin_url + 'blog/article/')
        self.assertEqual(response.status_code, 200)

    def test_comment_admin_page_displayed(self):
        '''Проверяет, что в административной панели отображается модель комментария.'''
        comments_verbose_name = Comment._meta.verbose_name_plural
        self.assertNotEqual(comments_verbose_name, None)
        response = self.client.get(self.admin_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, comments_verbose_name)
        response = self.client.get(self.admin_url + 'blog/comment/')
        self.assertEqual(response.status_code, 200)

    def test_series_admin_page_displayed(self):
        '''Проверяет, что в административной панели отображается модель серии.'''
        series_verbose_name = Series._meta.verbose_name_plural
        self.assertNotEqual(series_verbose_name, None)
        response = self.client.get(self.admin_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, series_verbose_name)
        response = self.client.get(self.admin_url + 'blog/series/')
        self.assertEqual(response.status_code, 200)
    
    def test_topic_admin_page_displayed(self):
        '''Проверяет, что в административной панели отображается модель темы.'''
        topics_verbose_name = Topic._meta.verbose_name_plural
        self.assertNotEqual(topics_verbose_name, None)
        response = self.client.get(self.admin_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, topics_verbose_name)
        response = self.client.get(self.admin_url + 'blog/topic/')
        self.assertEqual(response.status_code, 200)

    def test_category_admin_page_displayed(self):
        '''Проверяет, что в административной панели отображается модель категории.'''
        categories_verbose_name = Category._meta.verbose_name_plural
        self.assertNotEqual(categories_verbose_name, None)
        response = self.client.get(self.admin_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, categories_verbose_name)
        response = self.client.get(self.admin_url + 'blog/category/')
        self.assertEqual(response.status_code, 200)

    def test_articles_admin_list_displayed(self):
        '''Проверяет, что список статей в административной панели отображает нужные поля.'''
        response = self.client.get(self.admin_url + 'blog/article/')
        self.assertEqual(response.status_code, 200)
        print(response.content.decode('utf-8'))
        for value in [self.article.title, localize_datetime(self.article.published), localize_datetime(self.article.modified), self.article.public, self.article.author]:
            self.assertContains(response, value)

    def test_comments_admin_list_displayed(self):
        '''Проверяет, что список комментариев в административной панели отображает нужные поля.'''
        response = self.client.get(self.admin_url + 'blog/comment/')
        self.assertEqual(response.status_code, 200)
        for value in [self.comment.article, self.comment.author, localize_datetime(self.comment.posted)]:
            self.assertContains(response, value)

    def test_series_admin_list_displayed(self):
        '''Проверяет, что список серий в административной панели отображает нужные поля.'''
        response = self.client.get(self.admin_url + 'blog/series/')
        self.assertEqual(response.status_code, 200)
        for value in [self.series.name, self.series.slug, self.series.image, self.series.public]:
            self.assertContains(response, value)

    def test_topic_admin_list_displayed(self):
        '''Проверяет, что список тем в административной панели отображает нужные поля.'''
        response = self.client.get(self.admin_url + 'blog/topic/')
        self.assertEqual(response.status_code, 200)
        for value in [self.topic.name, self.topic.slug, self.topic.image, self.topic.public]:
            self.assertContains(response, value)
        
    def test_category_admin_list_displayed(self):
        '''Проверяет, что список категорий в административной панели отображает нужные поля.'''
        response = self.client.get(self.admin_url + 'blog/category/')
        self.assertEqual(response.status_code, 200)
        for value in [self.category.name, self.category.slug, self.category.image, self.category.public]:
            self.assertContains(response, value)

    def test_article_created_via_admin(self):
        '''Проверяет успешность добавления статьи через административную панель.'''
        response = self.client.post(self.admin_url + 'blog/article/add/', data={'title': 'Test article 2'})
        self.assertEqual(response.status_code, 200)
        response = self.client.post(self.admin_url + 'blog/article/add/', data={'content': generate_random_text(50)})
        self.assertEqual(response.status_code, 200)
        response = self.client.post(self.admin_url + 'blog/article/add/', data={'title': 'Test article 2', 'content': generate_random_text(50)})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Article.objects.filter(title='Test article 2').exists())
        self.assertNotEqual(Article.objects.get(title='Test article 2').published, None)

    def test_comment_created_via_admin(self):
        '''Проверяет успешность добавления комментария через административную панель.'''
        response = self.client.post(self.admin_url + 'blog/comment/add/', data={'content': 'Test comment', 'article': self.article.pk, 'author': self.superuser.pk})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Comment.objects.filter(content='Test comment', article=self.article, author=self.superuser).exists())

    def test_series_created_via_admin(self):
        '''Проверяет успешность добавления серии через административную панель.'''
        response = self.client.post(self.admin_url + 'blog/series/add/', data={'name': 'Test series 2'})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Series.objects.filter(name='Test series 2').exists())

    def test_topic_created_via_admin(self):
        '''Проверяет успешность добавления темы через административную панель.'''
        response = self.client.post(self.admin_url + 'blog/topic/add/', data={'name': 'Test topic 2'})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Topic.objects.filter(name='Test topic 2').exists())

    def test_category_created_via_admin(self):
        '''Проверяет успешность добавления категории через административную панель.'''
        response = self.client.post(self.admin_url + 'blog/category/add/', data={'name': 'Test category 2'})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Category.objects.filter(name='Test category 2').exists())

