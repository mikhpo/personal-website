"""Миксины представлений Blog приложения."""

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.mixins import AccessMixin
from django.http import HttpRequest, HttpResponse


class StaffRequiredMixin(AccessMixin):
    """Доступ только для администраторов сайта."""

    def dispatch(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Не пропускать дальше пользователей без признака администратора."""
        # isinstance сужает тип из django-stubs: у AbstractBaseUser нет is_staff
        if not (isinstance(request.user, AbstractBaseUser) and request.user.is_staff):
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)
