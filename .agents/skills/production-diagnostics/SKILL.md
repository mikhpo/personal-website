---
name: production-diagnostics
description: Диагностика продакшен-сервера - параметры среды и доступ, поиск и чтение логов, проверка состояния сервисов и эндпоинтов
---

## Предназначение

Скилл для диагностики состояния продакшена: где искать параметры среды и домен сайта, как подключиться, где лежат логи и как их читать, как проверить состояние сервисов и работоспособность эндпоинтов.

## Параметры целевой среды (откуда брать)

Источники информации о среде деплоя (хост, способ подключения, путь проекта, конфигурация):

- Окружения SourceCraft: `src envs` - список доступных сред; переключение флагом `--env <name>`, текущее видно в `src auth status`.
- Скрипты деплоя в репозитории: `scripts/deploy.sh` (общий вход: бэкап и диспетчеризация по DEPLOY_MODE из .env) и ветви `scripts/docker/`, `scripts/server/` - путь проекта на сервере и последовательность деплоя.
- Конфигурация стекa: `compose.yaml` - сервисы (application, traefik, postgres, minio; инфраструктурные подключаются профилями через COMPOSE_PROFILES).
- Способ запуска: DEPLOY_MODE в .env на сервере - compose (контейнеры, диагностика через docker compose) или systemd (systemctl/journalctl юнита personal-website; скилл server-setup).
- CI-конфиг деплоя (`.sourcecraft/ci.yaml`, workflow `deploy-workflow`; зеркально `.github/workflows/deploy.yml`) - шаги деплоя и используемые секреты сервера (хост, пользователь, ключ).
- `~/.ssh/config` - алиас подключения к серверу.
- `.env` на сервере - актуальные переменные среды (DOMAIN_NAME, STORAGE_TYPE, DEBUG, DEPLOY_MODE, GUNICORN_WORKERS, TRAEFIK_ACME_CASERVER, параметры БД и хранилища; секция «Бэкапы»: BACKUP_DB_TARGETS, BACKUP_MEDIA_TARGETS, цели BACKUP_TARGET_<ИМЯ>).
- Публичный адрес сайта (домен/URL) для проверки в браузере: переменная `DOMAIN_NAME` в `.env` на сервере.

## Доступ и расположение

- Подключение по алиасу из `~/.ssh/config`: `ssh <алиас>`.
- Путь проекта на сервере: `/srv/personal-website`. При compose-режиме приложение выполняется в контейнере Docker Compose (сервис `application`), проксирование и TLS - контейнер `traefik` либо хостовый nginx (по DEPLOY_MODE и COMPOSE_PROFILES).
- Порт приложения публикуется только на 127.0.0.1 (DJANGO_PORT): весь внешний трафик проходит через прокси-слой.

## Логи

### Источники логов

Применяется комбинированная стратегия: stdout/stderr контейнеров собирает Docker (driver json-file, ротация 10 МБ x 3 файла), детальные логи приложения пишутся в файлы через volume.

- Приложение и Gunicorn (access + ошибки воркеров, старт, краши): `docker compose logs application` или `docker logs <контейнер>`; в systemd-режиме - `journalctl -u personal-website`.
- Traefik (маршрутизация, ACME, сертификаты): `docker compose logs traefik`.
- Лог приложения (Django, файловый handler с ежедневной ротацией): каталог `logs/` проекта на хосте (volume `${LOGS_ROOT:-./logs/}` -> `/srv/website/logs` внутри контейнера).
- Резервное копирование: `${LOGS_ROOT}/backup.log` на хосте (задача cron хоста или systemd timer, `scripts/backup.sh backup`).

### Поиск ошибок в логах

```bash
# docker logs: строки с ошибками/traceback
docker compose logs application --since 2h | grep -iE "error|traceback|exception"

# Traefik: проблемы маршрутизации и сертификатов
docker compose logs traefik --since 2h | grep -iE "error|acme|certificate"

# Django-лог на хосте: traceback и 500
grep -nE "Traceback|Internal Server Error|Error|Exception" logs/<project>.log | tail -40

# Полный блок последнего traceback
tail -n 4000 logs/<project>.log | grep -A 35 "Traceback (most recent call last)" | tail -70

# Бэкапы: ошибки и пропуски запусков
tail -n 200 ${LOGS_ROOT}/backup.log | grep -iE "error|exception|traceback"
```

## Состояние сервисов

```bash
cd /srv/personal-website

# Первичная проверка живости - эндпоинт /health/ (SELECT 1):
# 200 - БД доступна, 503 - ошибка подключения
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:${DJANGO_PORT}/health/

# Список контейнеров и их статус
docker compose ps

# Статус отдельного сервиса
docker inspect --format '{{.Name}} {{.State.Status}} (health: {{.State.Health.Status}})' $(docker compose ps -q application)

# systemd-режим: состояние юнитов приложения и nginx
systemctl status personal-website nginx

# Перезапуск отдельного сервиса (только по явному разрешению)
# docker compose restart application
```

## Проверка эндпоинтов (read-only)

### Через публичный домен

Основной способ - запрос по публичному домену сайта (домен брать из `DOMAIN_NAME`, см. раздел «Параметры целевой среды»). Это именно то, что видит пользователь:

```bash
# внешний запрос
curl -sS -o /dev/null -w "%{http_code}\n" -H "Accept: text/html" "https://<домен>/api/<endpoint>/"

# то же с сервера
ssh <алиас> 'curl -sS -o /dev/null -w "%{http_code}\n" -H "Accept: text/html" "https://<домен>/api/<endpoint>/"'
```

Для просмотра тела ответа убрать `-o /dev/null`.

### Различение формата ответа

DRF выбирает рендерер по заголовку `Accept`:

- `Accept: application/json` - JSONRenderer.
- `Accept: text/html` - BrowsableAPIRenderer (HTML-рендеринг, строит filter-формы для viewset'ов с `filterset_fields`).
- `Accept: */*` - первый рендерер из `DEFAULT_RENDERER_CLASSES` (обычно JSON).

Если 500 возникает только для одного из форматов - проблема в соответствующем рендерере/шаблоне, а не в queryset/сериализации.

### Изоляция слоя Django (в обход прокси)

Применяется, когда нужно отделить проблемы Django от слоя прокси (редирект http->https, сертификаты, маршрутизация). Приложение слушает только 127.0.0.1:${DJANGO_PORT}, поэтому запрос выполняется с сервера напрямую или внутри контейнера:

```bash
curl -sS -o /dev/null -w "%{http_code}\n" -H "Accept: application/json" "http://127.0.0.1:${DJANGO_PORT}/api/<endpoint>/"

docker compose exec application curl -sS -o /dev/null -w "%{http_code}\n" -H "Accept: application/json" "http://localhost:${DJANGO_PORT}/api/<endpoint>/"
```

### In-process traceback через Django test client

Когда лог не пишет полный traceback (например, при `DEBUG=False`), получить точную причину in-process (GET-запрос, без записи в БД):

```bash
docker compose exec application bash -c 'cd /srv/website/backend && poetry run python manage.py shell' << 'PYEOF'
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

- Для диагностики использовать только чтение: `docker compose logs/ps`, `docker inspect`, `tail`, `grep`, `curl` GET, `manage.py shell` с GET-запросами.
- Не читать `.env` без явной необходимости - там секреты; переменные окружения узнавать через `manage.py shell` (`settings.*`) или `docker compose exec application env | grep -v -iE 'key|password|secret'`.
- Не перезапускать сервисы и не менять конфиги без отдельного разрешения.
