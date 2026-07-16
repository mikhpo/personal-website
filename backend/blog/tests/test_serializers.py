"""Тесты для сериализаторов блога."""

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from blog.factories import ArticleFactory, CommentFactory
from blog.serializers import ArticleSerializer, CommentSerializer

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
