from django.contrib.auth.models import User
from django.db.utils import IntegrityError
from django.test import TestCase
from django.utils.crypto import get_random_string

from blog.models import Article, Category, Comment, Series, Topic
from utils import generate_random_text


class ArticleModelTest(TestCase):
    """
    Тесты модели статьи.
    """

    @classmethod
    def setUpTestData(cls):
        cls.user_1 = User.objects.create_user(
            username="testuser-1",
            email="testuser-1@example.com",
            password=get_random_string(5),
        )
        cls.article = Article.objects.create(title="Test article", author=cls.user_1)

    def test_article_title_unique(self):
        """
        Проверка на то, что невозможно создать несколько статей с одним заголовком.
        """
        with self.assertRaises(IntegrityError):
            Article.objects.create(title="Test article")

    def test_article_auto_slug(self):
        """
        Проверка на то, что слаг статьи создается автоматически, когда не указан вручную,
        транслитерируется автоматически, уникальность достигается добавлением идентификатора.
        """
        first_article = Article.objects.create(title="First test article")
        self.assertEqual(first_article.slug, "first-test-article")
        second_article = Article.objects.create(title="Вторая тестовая статья")
        self.assertEqual(second_article.slug, "vtoraya-testovaya-statya")
        third_article = Article.objects.create(
            title="Третья тестовая статья", slug="third-test-article"
        )
        self.assertEqual(third_article.slug, "third-test-article")
        fourth_article = Article.objects.create(title="Third test article")
        self.assertEqual(fourth_article.slug, "third-test-article-2")

    def test_article_absolute_url(self):
        """
        Проверяется корректность создания абсолютной ссылки на статью.
        """
        url = "/blog/article/" + self.article.slug + "/"
        absolute_url = self.article.get_absolute_url()
        self.assertEqual(url, absolute_url)

    def test_article_saved_on_author_delete(self):
        """
        Проверяет, что статья не удаляется при удалении автора статьи.
        """
        self.assertTrue(User.objects.filter(username="testuser-1").exists())
        self.assertTrue(Article.objects.filter(title="Test article").exists())
        self.user_1.delete()
        self.assertFalse(User.objects.filter(username="testuser-1").exists())
        self.assertTrue(Article.objects.filter(title="Test article").exists())

    def test_comments_deleted_on_author_delete(self):
        """
        Проверяет, что комментарии удаляются при удалении автора комментариев.
        """
        user_2 = User.objects.create_user(
            username="testuser-2",
            email="testuser-2@example.com",
            password=get_random_string(5),
        )
        for _ in range(1, 6):
            Comment.objects.create(
                article=self.article, author=user_2, content=generate_random_text(10)
            )
        self.assertTrue(User.objects.filter(username="testuser-2").exists())
        self.assertGreater(self.article.number_of_comments, 0)
        user_comments_count = Comment.objects.filter(author=user_2).count()
        self.assertEqual(self.article.number_of_comments, user_comments_count)
        user_2.delete()
        self.assertFalse(User.objects.filter(username="testuser-2").exists())
        self.assertEqual(self.article.number_of_comments, 0)

    def test_article_saved_on_series_delete(self):
        """
        Проверяет, что статья не удаляется при удалении cерии.
        """
        series = Series.objects.create(name="Test series")
        self.article.series.add(series)
        self.assertTrue(Series.objects.filter(name="Test series").exists())
        self.assertTrue(Article.objects.filter(title="Test article").exists())
        self.assertTrue(series in self.article.series.all())
        series.delete()
        self.assertFalse(Series.objects.filter(name="Test series").exists())
        self.assertTrue(Article.objects.filter(title="Test article").exists())
        self.assertFalse(series in self.article.series.all())

    def test_article_saved_on_topic_delete(self):
        """
        Проверяет, что статья не удаляется при удалении темы.
        """
        topic = Topic.objects.create(name="Test topic")
        self.article.topics.add(topic)
        self.assertTrue(Topic.objects.filter(name="Test topic").exists())
        self.assertTrue(Article.objects.filter(title="Test article").exists())
        self.assertTrue(topic in self.article.topics.all())
        topic.delete()
        self.assertFalse(Topic.objects.filter(name="Test topic").exists())
        self.assertTrue(Article.objects.filter(title="Test article").exists())
        self.assertFalse(topic in self.article.topics.all())

    def test_article_saved_on_category_delete(self):
        """
        Проверяет, что статья не удаляется при удалении категории.
        """
        category = Category.objects.create(name="Test category")
        self.article.categories.add(category)
        self.assertTrue(Category.objects.filter(name="Test category").exists())
        self.assertTrue(Article.objects.filter(title="Test article").exists())
        self.assertTrue(category in self.article.categories.all())
        category.delete()
        self.assertFalse(Category.objects.filter(name="Test category").exists())
        self.assertTrue(Article.objects.filter(title="Test article").exists())
        self.assertFalse(category in self.article.categories.all())

    def test_comments_deleted_on_article_delete(self):
        """
        Проверяет, что комментарии удаляются при удалении статьи.
        """
        user_3 = User.objects.create_user(
            username="testuser-3",
            email="testuser-3@example.com",
            password=get_random_string(5),
        )
        for _ in range(1, 6):
            Comment.objects.create(
                article=self.article, author=user_3, content=generate_random_text(10)
            )
        self.assertTrue(User.objects.filter(username="testuser-3").exists())
        self.assertGreater(self.article.number_of_comments, 0)
        self.assertEqual(
            self.article.number_of_comments,
            Comment.objects.filter(author=user_3).count(),
        )
        self.article.delete()
        self.assertFalse(Article.objects.filter(title="Test article").exists())
        self.assertEqual(Comment.objects.filter(author=user_3).count(), 0)


class SeriesModelTest(TestCase):
    """
    Тесты модели серии статей.
    """

    def test_series_name_unique(self):
        """
        Проверка на то, что невозможно создать несколько серий с одним названием.
        """
        Series.objects.create(name="Test series")
        with self.assertRaises(IntegrityError):
            Series.objects.create(name="Test series")

    def test_series_auto_slug(self):
        """
        Проверка на то, что слаг серии создается автоматически, когда не указан вручную,
        транслитерируется автоматически, уникальность достигается добавлением идентификатора.
        """
        first_series = Series.objects.create(name="First test series")
        self.assertEqual(first_series.slug, "first-test-series")
        second_series = Series.objects.create(name="Вторая тестовая серия")
        self.assertEqual(second_series.slug, "vtoraya-testovaya-seriya")
        third_series = Series.objects.create(
            name="Третья тестовая серия", slug="third-test-series"
        )
        self.assertEqual(third_series.slug, "third-test-series")
        fourth_series = Series.objects.create(name="Third test series")
        self.assertEqual(fourth_series.slug, "third-test-series-2")

    def test_series_absolute_url(self):
        """
        Проверяется корректность создания абсолютной ссылки на серию.
        """
        series = Series.objects.create(name="Test series", slug="test-series")
        url = "/blog/series/" + series.slug + "/"
        absolute_url = series.get_absolute_url()
        self.assertEqual(url, absolute_url)


class TopicModelTest(TestCase):
    """
    Тесты модели темы статей.
    """

    def test_topic_name_unique(self):
        """
        Проверка на то, что невозможно создать несколько тем с одним названием.
        """
        Topic.objects.create(name="Test topic")
        with self.assertRaises(IntegrityError):
            Topic.objects.create(name="Test topic")

    def test_topic_auto_slug(self):
        """
        Проверка на то, что слаг темы создается автоматически, когда не указан вручную,
        транслитерируется автоматически, уникальность достигается добавлением идентификатора.
        """
        first_topic = Topic.objects.create(name="First test topic")
        self.assertEqual(first_topic.slug, "first-test-topic")
        second_topic = Topic.objects.create(name="Вторая тестовая тема")
        self.assertEqual(second_topic.slug, "vtoraya-testovaya-tema")
        third_topic = Topic.objects.create(
            name="Третья тестовая тема", slug="third-test-topic"
        )
        self.assertEqual(third_topic.slug, "third-test-topic")
        fourth_topic = Topic.objects.create(name="Third test topic")
        self.assertEqual(fourth_topic.slug, "third-test-topic-2")

    def test_topic_absolute_url(self):
        """
        Проверяется корректность создания абсолютной ссылки на тему.
        """
        topic = Topic.objects.create(name="Test topic", slug="test-topic")
        url = "/blog/topic/" + topic.slug + "/"
        absolute_url = topic.get_absolute_url()
        self.assertEqual(url, absolute_url)


class CategoryModelTest(TestCase):
    """
    Тесты модели категории статей.
    """

    def test_category_name_unique(self):
        """
        Проверка на то, что невозможно создать несколько категорий с одним названием.
        """
        Category.objects.create(name="Test category")
        with self.assertRaises(IntegrityError):
            Category.objects.create(name="Test category")

    def test_category_auto_slug(self):
        """
        Проверка на то, что слаг категории создается автоматически, когда не указан вручную,
        транслитерируется автоматически, уникальность достигается добавлением идентификатора.
        """
        first_category = Category.objects.create(name="First test category")
        self.assertEqual(first_category.slug, "first-test-category")
        second_category = Category.objects.create(name="Вторая тестовая категория")
        self.assertEqual(second_category.slug, "vtoraya-testovaya-kategoriya")
        third_category = Category.objects.create(
            name="Третья тестовая категория", slug="third-test-category"
        )
        self.assertEqual(third_category.slug, "third-test-category")
        fourth_category = Category.objects.create(name="Third test category")
        self.assertEqual(fourth_category.slug, "third-test-category-2")

    def test_category_absolute_url(self):
        """
        Проверяется корректность создания абсолютной ссылки на категорию.
        """
        category = Category.objects.create(name="Test category", slug="test-category")
        url = "/blog/category/" + category.slug + "/"
        absolute_url = category.get_absolute_url()
        self.assertEqual(url, absolute_url)
