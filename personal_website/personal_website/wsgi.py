"""Интерфейсный модуль для поддержки стандарта WSGI."""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "personal_website.settings")

application = get_wsgi_application()
