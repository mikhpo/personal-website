"""Template tags for React component integration."""

import hashlib
import json

from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def react_component(component_name: str, **props) -> str:
    """
    Рендерит placeholder для React-компонента, который может быть смонтирован фронтенд-кодом.

    Использование в шаблоне:
    {% react_component "ComponentName" prop1=value1 prop2=value2 %}
    """
    # Создаём уникальный ID для этого экземпляра компонента
    props_str = json.dumps(props, sort_keys=True)
    unique_id = hashlib.sha256(f"{component_name}{props_str}".encode()).hexdigest()[:12]
    element_id = f"react-component-{unique_id}"

    # Преобразуем props в JSON для фронтенда
    props_json = json.dumps(props)

    # Создаём HTML placeholder с data-атрибутами
    html = f"""
<div id="{element_id}"
     class="react-component"
     data-component-name="{component_name}"
     data-component-props='{props_json}'>
</div>
    """

    return mark_safe(html.strip())
