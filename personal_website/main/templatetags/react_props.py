"""Template tags для передачи данных в React компоненты."""

import json
from typing import Any

from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def react_props(data: dict[str, Any]) -> str:
    """
    Конвертирует Python словарь в JSON для использования в React компонентах.

    Использование в шаблоне:
    <div id="navbar-root" data-props="{% react_props navbar_data %}"></div>

    Args:
        data: Словарь с данными для React компонента

    Returns:
        JSON строка с данными
    """
    return mark_safe(json.dumps(data))
