"""Миксины представлений API."""

from auditlog.context import set_actor


class AuditlogActorMixin:
    """Связывает записи аудита с пользователем JWT-запроса.

    AuditlogMiddleware определяет пользователя до выполнения представления,
    тогда как JWT-аутентификация DRF происходит внутри представления, поэтому
    middleware оставляет actor пустым. Миксин оборачивает операции сохранения
    и удаления контекстом set_actor: записи auditlog получают автора и
    IP-адрес запроса.
    """

    def _actor_context(self) -> set_actor:
        """Контекст текущего пользователя и его IP-адреса."""
        remote_addr = self.request.META.get("HTTP_X_REAL_IP")
        return set_actor(self.request.user, remote_addr=remote_addr)

    def perform_create(self, serializer) -> None:  # noqa: ANN001
        """Сохранить объект в контексте пользователя."""
        with self._actor_context():
            super().perform_create(serializer)

    def perform_update(self, serializer) -> None:  # noqa: ANN001
        """Обновить объект в контексте пользователя."""
        with self._actor_context():
            super().perform_update(serializer)

    def perform_destroy(self, instance) -> None:  # noqa: ANN001
        """Удалить объект в контексте пользователя."""
        with self._actor_context():
            super().perform_destroy(instance)
