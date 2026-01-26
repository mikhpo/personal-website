"""ViewSet'ы для приложения accounts."""

from django.contrib.auth.models import User
from rest_framework import viewsets
from rest_framework.permissions import AllowAny, BasePermission, IsAuthenticatedOrReadOnly
from rest_framework.serializers import BaseSerializer

from .serializers import UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet для управления пользователями."""

    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self) -> list[BasePermission]:
        """
        Установка прав доступа:
        - create: AllowAny (регистрация доступна всем)
        - list/retrieve: IsAuthenticatedOrReadOnly (чтение доступно всем, запись только аутентифицированным)
        - update/destroy: IsAuthenticatedOrReadOnly (чтение доступно всем, запись только аутентифицированным).
        """
        permission_classes = [AllowAny] if self.action == "create" else [IsAuthenticatedOrReadOnly]  # type: ignore[list-item]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer: BaseSerializer) -> None:
        """Переопределяем метод для корректного создания пользователя."""
        user: User = serializer.save()
        user.set_password(serializer.validated_data["password"])
        user.save()
