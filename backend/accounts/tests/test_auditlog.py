"""Тесты журналирования событий доступа и аудита пользователей."""

from auditlog.models import LogEntry
from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.contrib.contenttypes.models import ContentType
from rest_framework.test import APITestCase

from blog.factories import ArticleFactory, CommentFactory

User = get_user_model()


class TestSignupAuditLog(APITestCase):
    """Тесты регистрации: журнал и запись аудита о создании пользователя."""

    def test_signup_logs_info_and_audit_entry(self) -> None:
        """Регистрация фиксируется в журнале и в auditlog без автора."""
        data = {
            "username": "newuser",
            "first_name": "Иван",
            "last_name": "Иванов",
            "email": "newuser@example.com",
            "password1": "StrongPassword123",
            "password2": "StrongPassword123",
        }
        with self.assertLogs(settings.PROJECT_NAME, level="INFO") as logs:
            response = self.client.post("/accounts/signup/", data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(any("Зарегистрирован пользователь newuser" in message for message in logs.output))
        user = User.objects.get(username="newuser")
        content_type = ContentType.objects.get_for_model(User)
        entry = LogEntry.objects.get(content_type=content_type, object_id=user.pk, action=LogEntry.Action.CREATE)
        self.assertIsNone(entry.actor)
        self.assertNotIn("StrongPassword123", str(entry.changes))


class TestTokenAuditLog(APITestCase):
    """Тесты журналирования выдачи JWT-токенов."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Подготовка тестовых данных."""
        cls.user = User.objects.create_user(username="tokenuser", password="testpass123")
        cls.url = "/api/auth/token/"
        super().setUpTestData()

    def test_successful_token_issue_logs_info(self) -> None:
        """Успешная выдача JWT-токена фиксируется в журнале."""
        with self.assertLogs(settings.PROJECT_NAME, level="INFO") as logs:
            response = self.client.post(self.url, {"username": "tokenuser", "password": "testpass123"})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(any("Выдан JWT-токен пользователю tokenuser" in message for message in logs.output))

    def test_failed_token_issue_logs_warning_without_access_denied_duplicate(self) -> None:
        """Неудачная выдача токена фиксируется сигналом, без дублирования middleware."""
        with self.assertLogs(settings.PROJECT_NAME, level="WARNING") as logs:
            response = self.client.post(self.url, {"username": "tokenuser", "password": "wrongpass"})
        self.assertEqual(response.status_code, 401)
        self.assertTrue(
            any("Неудачная попытка авторизации пользователя tokenuser" in message for message in logs.output),
        )
        self.assertFalse(any("Отказ доступа" in message for message in logs.output))

    def test_authenticate_without_request_logs_warning(self) -> None:
        """Неудачная попытка без запроса также попадает в журнал."""
        with self.assertLogs(settings.PROJECT_NAME, level="WARNING") as logs:
            result = authenticate(username="tokenuser", password="wrongpass")
        self.assertIsNone(result)
        self.assertTrue(any("Неудачная попытка авторизации пользователя tokenuser" in m for m in logs.output))


class TestAccessDeniedLog(APITestCase):
    """Тесты журналирования отказов в доступе (401 и 403)."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Подготовка тестовых данных."""
        cls.staff_user = User.objects.create_user(username="staffuser", password="testpass123", is_staff=True)
        cls.other_user = User.objects.create_user(username="otheruser", password="testpass123")
        cls.article = ArticleFactory(title="Статья для теста отказов", author=cls.staff_user)
        cls.comment = CommentFactory(article=cls.article, author=cls.staff_user, content="Чужой комментарий")
        super().setUpTestData()

    def test_unauthenticated_delete_logs_401(self) -> None:
        """Неаутентифицированная попытка удаления фиксируется с пометкой анонима."""
        url = f"/api/blog/comments/{self.comment.pk}/"
        with self.assertLogs(settings.PROJECT_NAME, level="WARNING") as logs:
            response = self.client.delete(url)
        self.assertEqual(response.status_code, 401)
        self.assertTrue(any("Отказ доступа" in message and "аноним" in message for message in logs.output))

    def test_non_author_delete_logs_403_with_username(self) -> None:
        """Попытка удаления чужого комментария фиксируется с именем пользователя."""
        url = f"/api/blog/comments/{self.comment.pk}/"
        self.client.force_authenticate(user=self.other_user)
        with self.assertLogs(settings.PROJECT_NAME, level="WARNING") as logs:
            response = self.client.delete(url)
        self.assertEqual(response.status_code, 403)
        self.assertTrue(
            any("Отказ доступа" in message and "otheruser" in message for message in logs.output),
        )
