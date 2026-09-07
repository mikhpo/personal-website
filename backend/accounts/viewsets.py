"""ViewSet'ы для приложения accounts."""

from django.contrib.auth.models import User
from rest_framework import viewsets
from rest_framework.permissions import AllowAny, BasePermission, IsAuthenticatedOrReadOnly

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
        permission_classes: list[type[BasePermission]] = (
            [AllowAny] if self.action == "create" else [IsAuthenticatedOrReadOnly]
        )
        return [permission() for permission in permission_classes]
