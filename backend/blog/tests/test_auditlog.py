"""Тесты аудита изменений моделей блога через django-auditlog."""

from typing import TYPE_CHECKING

from auditlog.models import LogEntry
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from rest_framework.test import APITestCase

from blog.factories import ArticleFactory, CategoryFactory, CommentFactory
from blog.models import Article, Comment

if TYPE_CHECKING:
    from django.db.models.query import QuerySet

User = get_user_model()


class TestArticleAuditLog(APITestCase):
    """Тесты аудита статей: операции через API фиксируются с автором."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Подготовка тестовых данных."""
        cls.staff_user = User.objects.create_user(username="staffuser", password="testpass123", is_staff=True)
        cls.article = ArticleFactory(title="Тестовая статья", author=cls.staff_user)
        super().setUpTestData()

    def _entries(self, article: Article) -> "QuerySet[LogEntry]":
        """Записи аудита для статьи."""
        content_type = ContentType.objects.get_for_model(Article)
        return LogEntry.objects.filter(content_type=content_type, object_id=article.pk)

    def test_create_article_logs_entry_with_actor(self) -> None:
        """Создание статьи через API фиксируется записью аудита с автором."""
        self.client.force_authenticate(user=self.staff_user)
        url = "/api/blog/articles/"
        data = {"title": "Новая статья", "content": "<p>Текст новой статьи</p>"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 201)
        article = Article.objects.get(title="Новая статья")
        entry = self._entries(article).get(action=LogEntry.Action.CREATE)
        self.assertEqual(entry.actor, self.staff_user)

    def test_update_article_logs_changes(self) -> None:
        """Изменение статьи фиксируется записью с измененным полем и автором."""
        self.client.force_authenticate(user=self.staff_user)
        url = f"/api/blog/articles/{self.article.pk}/"
        response = self.client.patch(url, {"title": "Измененный заголовок"})
        self.assertEqual(response.status_code, 200)
        entry = self._entries(self.article).filter(action=LogEntry.Action.UPDATE).latest("timestamp")
        self.assertEqual(entry.actor, self.staff_user)
        self.assertIn("title", entry.changes)

    def test_delete_article_logs_entry_with_actor(self) -> None:
        """Удаление статьи фиксируется записью аудита с автором."""
        self.client.force_authenticate(user=self.staff_user)
        url = f"/api/blog/articles/{self.article.pk}/"
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)
        entry = self._entries(self.article).get(action=LogEntry.Action.DELETE)
        self.assertEqual(entry.actor, self.staff_user)

    def test_m2m_change_logs_entry(self) -> None:
        """Изменение категорий статьи (m2m) фиксируется записью аудита."""
        category = CategoryFactory(name="Аудит-категория")
        self.article.categories.add(category)
        entry = self._entries(self.article).filter(action=LogEntry.Action.UPDATE).latest("timestamp")
        self.assertIn("categories", entry.changes)

    def test_write_not_logged_without_permission(self) -> None:
        """Отказ в правах не создает записей аудита об изменении."""
        regular_user = User.objects.create_user(username="regular", password="testpass123")
        entries_before = self._entries(self.article).count()
        self.client.force_authenticate(user=regular_user)
        url = f"/api/blog/articles/{self.article.pk}/"
        response = self.client.patch(url, {"title": "Новый заголовок"})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(self._entries(self.article).count(), entries_before)


class TestCommentAuditLog(APITestCase):
    """Тесты аудита комментариев: автор комментария фиксируется в записях."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Подготовка тестовых данных."""
        cls.staff_user = User.objects.create_user(username="staffuser", password="testpass123", is_staff=True)
        cls.commenter = User.objects.create_user(username="commenter", password="testpass123")
        cls.article = ArticleFactory(title="Статья с комментариями", author=cls.staff_user)
        super().setUpTestData()

    def test_create_comment_logs_entry_with_actor(self) -> None:
        """Создание комментария через API фиксируется с автором комментария."""
        self.client.force_authenticate(user=self.commenter)
        url = "/api/blog/comments/"
        data = {"article": self.article.pk, "content": "Комментарий для аудита"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 201)
        comment = Comment.objects.get(content="Комментарий для аудита")
        content_type = ContentType.objects.get_for_model(Comment)
        entry = LogEntry.objects.get(content_type=content_type, object_id=comment.pk, action=LogEntry.Action.CREATE)
        self.assertEqual(entry.actor, self.commenter)

    def test_delete_foreign_comment_by_staff_logs_entry(self) -> None:
        """Удаление комментария администратором фиксируется с его авторством."""
        comment = CommentFactory(article=self.article, author=self.commenter, content="Чужой комментарий")
        self.client.force_authenticate(user=self.staff_user)
        url = f"/api/blog/comments/{comment.pk}/"
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)
        content_type = ContentType.objects.get_for_model(Comment)
        entry = LogEntry.objects.get(content_type=content_type, object_id=comment.pk, action=LogEntry.Action.DELETE)
        self.assertEqual(entry.actor, self.staff_user)
