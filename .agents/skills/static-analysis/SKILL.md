---
name: static-analysis
description: Статический анализ кода с Ruff и MyPy для проверки стиля и типов
---

## Процесс выполнения

### 1. Подготовка окружения

```bash
poetry shell
poetry install
```

### 2. Проверка Ruff

```bash
poetry run ruff check . --fix
```

### 3. Проверка MyPy

```bash
poetry run mypy .
```

## Обработка ошибок

### Исправление ошибок Ruff

1. Изучить коды ошибок
2. Применить автоисправления (--fix)
3. Исправить оставшиеся вручную

### Исправление ошибок MyPy

1. Несоответствия типов: Проверить аннотации
2. Ошибки импорта: Исправить пути
3. Несовместимые типы: Преобразовать явно

### Запрещено

- Не использовать # type: ignore для подавления ошибок
- Не игнорировать сообщения об ошибках
- Не коммитить код с ошибками

### Рекомендации

- Явное преобразование типов, например: `dict(obj)`
- Корректные аннотации типов
- Правильные импорты

## Верификация

```bash
poetry run ruff check .
poetry run mypy .
```

## Пример

Ошибка MyPy:

```text
error: Dict entry 0 has incompatible type "str": "DBConfig"; expected "str": "dict[str, str]"
```

Неправильно:

```python
DATABASES = {"default": db_config}  # type: ignore[dict-item]
```

Правильно:

```python
DATABASES = {"default": dict(db_config)}
```
