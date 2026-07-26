---
name: production-diagnostics
description: Диагностика продакшен-сервера — параметры среды и доступ, поиск и чтение логов, проверка состояния сервисов и эндпоинтов
---

## Предназначение

Скилл для диагностики состояния продакшена: где искать параметры среды и домен сайта, как подключиться, где лежат логи и как их читать, как проверить состояние сервисов и работоспособность эндпоинтов.

## Параметры целевой среды (откуда брать)

Источники информации о среде деплоя (хост, способ подключения, путь проекта, конфигурация):

- Окружения SourceCraft: `src envs` — список доступных сред; переключение флагом `--env <name>`, текущее видно в `src auth status`.
- Скрипты деплоя в репозитории: `scripts/server/` (deploy.sh, update.sh, restart.sh) — содержат путь проекта на сервере (WORK_DIR) и последовательность деплоя (git pull + migrate + collectstatic + restart сервиса).
- Конфиги сервиса в репозитории: `backend/config/gunicorn/`, `backend/config/nginx/` — как запущено приложение (systemd-юнит, сокет, прокси).
- CI-конфиг деплоя (конфигурация SourceCraft CI или `.github/workflows/deploy.yml`) — шаги деплоя и используемые секреты сервера (хост, пользователь, ключ).
- `~/.ssh/config` — алиас подключения к серверу.
- `.env` на сервере — актуальные переменные среды (DOMAIN_NAME, STORAGE_TYPE, DEBUG, параметры БД и хранилища).
- Публичный адрес сайта (домен/URL) для проверки в браузере: переменная `DOMAIN_NAME` в `.env` на сервере и/или `server_name` в шаблоне `backend/config/nginx/`.

## Доступ и расположение

- Подключение по алиасу из `~/.ssh/config`: `ssh <алиас>`.
- Путь проекта на сервере и venv берутся из `scripts/server/update.sh` (WORK_DIR). Для этого проекта: проект `/root/personal-website`, venv `/root/personal-website/.venv`, приложение запускается из `backend/` (`personal_website.wsgi:application`).
- Запуск bare-metal через systemd (не Docker): `gunicorn.service` + `gunicorn.socket` (unix-сокет `/run/gunicorn.sock`), проксируется `nginx`, БД — системный `postgresql`.

## Логи

### Источники логов

- Gunicorn (access + stderr воркеров): `journalctl -u gunicorn.service` (также `journalctl -u gunicorn.socket`).
- Лог приложения (Django): файловый handler (`django.request`, `django.server`). Путь определяется переменной `LOGS_ROOT` в `.env` (`LOG_DIR = LOGS_ROOT/<project>`).
- Nginx: `/var/log/nginx/error.log`, `/var/log/nginx/access.log`.

### Как узнать точный путь Django-лога

Путь зависит от `LOGS_ROOT`, который может быть переопределён в `.env` (не совпадает с путём по умолчанию из кода). Уточнить in-process, не читая `.env` целиком:

```bash
ssh <алиас> 'cd /root/personal-website/backend && /root/personal-website/.venv/bin/python manage.py shell' << 'PYEOF'
from django.conf import settings
import logging
print("LOG_DIR =", settings.LOG_DIR)
rq = logging.getLogger("django.request")
print("django.request handlers:", [(type(h).__name__, getattr(h, "baseFilename", None)) for h in rq.handlers])
PYEOF
```

Либо поиском по файловой системе: `find / -name "*.log" 2>/dev/null`.

### Поиск ошибок в логах

```bash
# Gunicorn: строки с ошибками/traceback
journalctl -u gunicorn.service --since "2 hours ago" --no-pager | grep -iE "error|traceback|exception"

# Django-лог: traceback и 500
grep -nE "Traceback|Internal Server Error|Error|Exception" /<путь>/<лог>.log | tail -40

# Полный блок последнего traceback
tail -n 4000 /<путь>/<лог>.log | grep -A 35 "Traceback (most recent call last)" | tail -70
```

## Состояние сервисов

```bash
# Активность сервисов
systemctl is-active gunicorn.service gunicorn.socket nginx postgresql

# Подробный статус
systemctl status gunicorn.service gunicorn.socket nginx postgresql --no-pager

# Последние строки журнала gunicorn
journalctl -u gunicorn.service -n 200 --no-pager
```

## Проверка эндпоинтов (read-only)

### Через публичный домен

Основной способ — запрос по публичному домену сайта (домен брать из `DOMAIN_NAME` / `server_name`, см. раздел «Параметры целевой среды»). Это именно то, что видит пользователь:

```bash
# внешний запрос
curl -sS -o /dev/null -w "%{http_code}\n" -H "Accept: text/html" "https://<домен>/api/<endpoint>/"

# то же с сервера
ssh <алиас> 'curl -sS -o /dev/null -w "%{http_code}\n" -H "Accept: text/html" "https://<домен>/api/<endpoint>/"'
```

Для просмотра тела ответа убрать `-o /dev/null`.

### Различение формата ответа

DRF выбирает рендерер по заголовку `Accept`:

- `Accept: application/json` — JSONRenderer.
- `Accept: text/html` — BrowsableAPIRenderer (HTML-рендеринг, строит filter-формы для viewset'ов с `filterset_fields`).
- `Accept: */*` — первый рендерер из `DEFAULT_RENDERER_CLASSES` (обычно JSON).

Если 500 возникает только для одного из форматов — проблема в соответствующем рендерере/шаблоне, а не в queryset/сериализации.

### Изоляция слоя Django (в обход nginx)

Применяется, когда нужно отделить проблемы Django от слоя nginx (http→https redirect, default server, кэш, TLS). Запрос напрямую в gunicorn-сокет попадает в Django, минуя nginx:

```bash
ssh <алиас> 'curl -sS -o /dev/null -w "%{http_code}\n" --unix-socket /run/gunicorn.sock -H "Accept: application/json" "http://localhost/api/<endpoint>/"'
```

### In-process traceback через Django test client

Когда лог не пишет полный traceback (например, при `DEBUG=False`), получить точную причину in-process (GET-запрос, без записи в БД):

```bash
ssh <алиас> 'cd /root/personal-website/backend && /root/personal-website/.venv/bin/python manage.py shell' << 'PYEOF'
from django.test import Client
import traceback
c = Client()
for path in ["/api/<endpoint>/"]:
    print("==== %s ====" % path)
    try:
        r = c.get(path, HTTP_ACCEPT="text/html")
        _ = r.content
        print("STATUS", r.status_code, "len", len(r.content))
    except Exception:
        traceback.print_exc()
PYEOF
```

## Ограничения (read-only)

- Для диагностики использовать только чтение: `tail`, `grep`, `journalctl`, `systemctl status`/`is-active`, `curl` GET, `manage.py shell` с GET-запросами.
- Не читать `.env` без явной необходимости — там секреты; переменные окружения узнавать через `manage.py shell` (`settings.*`).
- Не перезапускать сервисы и не менять конфиги без отдельного разрешения.
