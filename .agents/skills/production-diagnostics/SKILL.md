---
name: production-diagnostics
description: Диагностика продакшен-сервера - параметры среды и доступ, поиск и чтение логов, проверка состояния сервисов и эндпоинтов
---

## Предназначение

Скилл для диагностики состояния продакшена: где искать параметры среды и домен сайта, как подключиться, где лежат логи и как их читать, как проверить состояние сервисов и работоспособность эндпоинтов.

## Параметры целевой среды (откуда брать)

Источники информации о среде деплоя (хост, способ подключения, путь проекта, конфигурация):

- Окружения SourceCraft: `src envs` - список доступных сред; переключение флагом `--env <name>`, текущее видно в `src auth status`.
- Скрипты деплоя в репозитории: `scripts/deploy.sh` (общий вход: бэкап и диспетчеризация по DEPLOY_MODE) и `scripts/docker/` (setup.sh, deploy.sh) - путь проекта на сервере и последовательность деплоя (git pull + docker compose pull + up).
- Конфигурация стекa: `compose.yaml` - сервисы (website, traefik), тома, переменные окружения.
- CI-конфиг деплоя (`.sourcecraft/ci.yaml`, workflow `deploy-workflow`; зеркально `.github/workflows/deploy.yml`) - шаги деплоя и используемые секреты сервера (хост, пользователь, ключ).
- `~/.ssh/config` - алиас подключения к серверу.
- `.env` на сервере - актуальные переменные среды (DOMAIN_NAME, STORAGE_TYPE, DEBUG, параметры БД и хранилища).
- Публичный адрес сайта (домен/URL) для проверки в браузере: переменная `DOMAIN_NAME` в `.env` на сервере.

## Доступ и расположение

- Подключение по алиасу из `~/.ssh/config`: `ssh <алиас>`.
- Путь проекта на сервере: `/root/personal-website`. Приложение выполняется в контейнерах Docker Compose (сервис `website`), проксирование и TLS - контейнер `traefik`.
- Порт приложения 8000 не публикуется наружу: весь внешний трафик проходит через Traefik (порты 80/443).

## Логи

### Источники логов

Применяется комбинированная стратегия: stdout/stderr контейнеров собирает Docker (driver json-file, ротация 10 МБ x 3 файла), детальные логи приложения пишутся в файлы через volume.

- Приложение и Gunicorn (access + ошибки воркеров, старт, краши): `docker compose logs website` или `docker logs <контейнер>`.
- Traefik (маршрутизация, ACME, сертификаты): `docker compose logs traefik`.
- Лог приложения (Django, файловый handler с ежедневной ротацией): каталог `logs/` проекта на хосте (volume `${LOGS_ROOT:-./logs/}` -> `/srv/website/logs` внутри контейнера).
- Резервное копирование: `logs/backup.log` на хосте (задача cron хоста, `scripts/backup.sh backup`).

### Поиск ошибок в логах

```bash
# docker logs: строки с ошибками/traceback
docker compose logs website --since 2h | grep -iE "error|traceback|exception"

# Traefik: проблемы маршрутизации и сертификатов
docker compose logs traefik --since 2h | grep -iE "error|acme|certificate"

# Django-лог на хосте: traceback и 500
grep -nE "Traceback|Internal Server Error|Error|Exception" logs/<project>.log | tail -40

# Полный блок последнего traceback
tail -n 4000 logs/<project>.log | grep -A 35 "Traceback (most recent call last)" | tail -70
```

## Состояние сервисов

```bash
cd /root/personal-website

# Список контейнеров и их статус
docker compose ps

# Статус отдельного сервиса
docker inspect --format '{{.Name}} {{.State.Status}} (health: {{.State.Health.Status}})' $(docker compose ps -q website)

# Перезапуск отдельного сервиса (только по явному разрешению)
# docker compose restart website
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

### Изоляция слоя Django (в обход Traefik)

Применяется, когда нужно отделить проблемы Django от слоя Traefik (редирект http->https, сертификаты, маршрутизация). Публичный порт приложения не публикуется, поэтому запрос выполняется внутри контейнера:

```bash
docker compose exec website curl -sS -o /dev/null -w "%{http_code}\n" -H "Accept: application/json" "http://localhost:8000/api/<endpoint>/"
```

### In-process traceback через Django test client

Когда лог не пишет полный traceback (например, при `DEBUG=False`), получить точную причину in-process (GET-запрос, без записи в БД):

```bash
docker compose exec website bash -c 'cd /srv/website/backend && poetry run python manage.py shell' << 'PYEOF'
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
- Не читать `.env` без явной необходимости - там секреты; переменные окружения узнавать через `manage.py shell` (`settings.*`) или `docker compose exec website env | grep -v -iE 'key|password|secret'`.
- Не перезапускать сервисы и не менять конфиги без отдельного разрешения.
