"""Тесты локализации журнала аудита через переводческий каталог проекта."""

from auditlog.models import LogEntry
from django.apps import apps
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import TestCase
from django.utils import translation

User = get_user_model()


class TestAuditlogLocalization(TestCase):
    """Русские названия журнала аудита: приложение, модель, индекс админки."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Подготовка тестовых данных."""
        cls.staff_user = User.objects.create_user(username="staffuser", password="testpass123", is_staff=True)
        permission = Permission.objects.get(content_type__app_label="auditlog", codename="view_logentry")
        cls.staff_user.user_permissions.add(permission)
        super().setUpTestData()

    def test_app_label_unchanged(self) -> None:
        """Метка приложения остается auditlog: от нее зависят миграции и contenttypes."""
        config = apps.get_app_config("auditlog")
        self.assertEqual(config.label, "auditlog")

    def test_app_verbose_name_in_russian(self) -> None:
        """Название приложения в админке переводится каталогом проекта."""
        with translation.override("ru"):
            config = apps.get_app_config("auditlog")
            self.assertEqual(str(config.verbose_name), "Журнал аудита")

    def test_model_verbose_names_in_russian(self) -> None:
        """Названия модели переводятся каталогом проекта."""
        # _meta - штатный способ доступа к метаданным модели Django
        opts = LogEntry._meta  # noqa: SLF001
        with translation.override("ru"):
            self.assertEqual(str(opts.verbose_name), "Запись аудита")
            self.assertEqual(str(opts.verbose_name_plural), "Записи аудита")

    def test_admin_index_contains_section(self) -> None:
        """Индекс админки отображает раздел с русским названием."""
        self.client.force_login(self.staff_user)
        with translation.override("ru"):
            response = self.client.get("/admin/")
        self.assertContains(response, "Журнал аудита")
