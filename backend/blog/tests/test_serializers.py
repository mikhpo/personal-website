"""Тесты для сериализаторов блога."""

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from blog.factories import ArticleFactory, CategoryFactory, CommentFactory, SeriesFactory, TopicFactory
from blog.serializers import ArticleSerializer, ArticleWriteSerializer, CommentSerializer

User = get_user_model()


class TestCommentSerializer(APITestCase):
    """Тесты для CommentSerializer."""

    def test_comment_serializer_includes_author_username(self) -> None:
        """Сериализатор комментария должен включать username автора через поле author_username."""
        user = User.objects.create_user(username="test_author", password="testpass123")
        article = ArticleFactory(author=user)
        comment = CommentFactory(article=article, author=user, content="Тестовый комментарий")

        serializer = CommentSerializer(instance=comment)
        data = serializer.data

        self.assertIn("author_username", data)
        self.assertEqual(data["author_username"], "test_author")

    def test_comment_serializer_author_and_posted_are_read_only(self) -> None:
        """Поля author и posted в сериализаторе комментария должны быть только для чтения."""
        serializer = CommentSerializer()
        self.assertTrue(serializer.fields["author"].read_only)
        self.assertTrue(serializer.fields["posted"].read_only)


class TestArticleSerializer(APITestCase):
    """Тесты для ArticleSerializer."""

    def test_article_serializer_includes_author_username(self) -> None:
        """Сериализатор статьи должен включать username автора через поле author_username."""
        user = User.objects.create_user(username="test_author", password="testpass123")
        article = ArticleFactory(author=user, title="Статья", content="Содержание")

        serializer = ArticleSerializer(instance=article)
        data = serializer.data

        self.assertIn("author_username", data)
        self.assertEqual(data["author_username"], "test_author")


class TestArticleWriteSerializer(APITestCase):
    """Тесты для ArticleWriteSerializer."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Подготовка тестовых данных."""
        cls.user = User.objects.create_user(username="writer", password="testpass123", is_staff=True)
        cls.category = CategoryFactory(name="Категория", public=True)
        cls.topic = TopicFactory(name="Тема", public=True)
        cls.series = SeriesFactory(name="Серия", public=True)
        super().setUpTestData()

    def test_m2m_writable_by_pk(self) -> None:
        """Связи M2M записываются списками первичных ключей."""
        serializer = ArticleWriteSerializer(
            data={
                "title": "Статья через запись",
                "content": "<p>Контент</p>",
                "public": "false",
                "categories": [self.category.pk],
                "topics": [self.topic.pk],
                "series": [self.series.pk],
            },
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        article = serializer.save(author=self.user)
        self.assertEqual(list(article.categories.all()), [self.category])
        self.assertEqual(list(article.topics.all()), [self.topic])
        self.assertEqual(list(article.series.all()), [self.series])
        self.assertFalse(article.public)

    def test_server_fields_not_writable(self) -> None:
        """Автор, слаг и даты отсутствуют среди записываемых полей."""
        serializer = ArticleWriteSerializer()
        for field in ("author", "slug", "published_at", "modified_at"):
            self.assertNotIn(field, serializer.fields)

    def test_to_representation_delegates_to_read_serializer(self) -> None:
        """Представление записи совпадает с полным представлением чтения."""
        article = ArticleFactory(title="Статья", author=self.user)
        article.categories.add(self.category)

        write_data = ArticleWriteSerializer(article).data
        read_data = ArticleSerializer(article).data

        self.assertEqual(write_data, read_data)
        self.assertEqual(write_data["url"], article.get_absolute_url())

    def test_remove_image_flag_validates(self) -> None:
        """Флаг remove_image принимается при валидации и не мешает сохранению."""
        serializer = ArticleWriteSerializer(
            data={"title": "Без обложки", "content": "<p>Контент</p>", "remove_image": "true"},
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertTrue(serializer.validated_data["remove_image"])
        article = serializer.save(author=self.user)
        self.assertFalse(bool(article.image))
