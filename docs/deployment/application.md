# Запуск приложения

Ось «Приложение»: Docker Compose, docker run без Compose, systemd Gunicorn
на хосте. Все значения равноправны и комбинируются с остальными осями
(БД, хранилище, прокси, бэкапы). Автоматизация первичной настройки:
Docker Compose - scripts/docker/setup.sh, systemd - scripts/server/setup.sh.

Содержание:

1. Контракт приложения
2. Docker Compose
3. docker run без Compose
4. systemd Gunicorn на хосте
5. Взаимодействие с прокси

## 1. Контракт приложения

Единый для всех режимов запуска:

- приложение слушает порт DJANGO_PORT; контейнерные режимы публикуют его
  только на 127.0.0.1 хоста, systemd-режим слушает 127.0.0.1 напрямую -
  внешний трафик всегда проходит через прокси-слой;
- миграции и сбор статики выполняются при каждом старте (entrypoint.sh
  в контейнере, ExecStartPre в systemd-юните);
- статика и медиа приложением через прокси не раздаются: в filesystem-режиме
  статику обслуживает WhiteNoise, при STORAGE_TYPE=s3 - объектное хранилище;
- живость - эндпоинт /health/ (проверочный SELECT 1, 200 при доступной БД,
  503 при ошибке): им пользуется healthcheck контейнера и диагностика;
- конфигурация - один файл .env.

Экранирование символа доллара в значениях .env зависит от режима:
Docker Compose интерполирует переменные .env, поэтому каждый $
в значении удваивается ($$); docker run --env-file и systemd
EnvironmentFile читают значения буквально - экранирование не нужно.
Подробности - в [CONTRIBUTING.md](../CONTRIBUTING.md), раздел
«Экранирование символа доллара».

## 2. Docker Compose

Основной режим. Конфигурация - единый compose.yaml; инфраструктурные
сервисы (postgres, minio, traefik) подключаются собственными профилями
через COMPOSE_PROFILES, пустое значение означает полностью внешнюю
инфраструктуру (поднимается только приложение). Сводная матрица профилей
и эталонные конфигурации - в [matrix.md](./matrix.md).

Запуск и обновление:

```bash
docker compose up -d
bash scripts/deploy.sh    # бэкап + обновление по DEPLOY_MODE
```

## 3. docker run без Compose

Режим для окружений с Docker, но без Docker Compose (например, один
контейнер на слабой ВМ). Полная команда (переменные из .env, файл
загружается в оболочку заранее: set -a; . ./.env; set +a):

```bash
docker run -d \
    --name personal-website \
    --restart always \
    --env-file .env \
    -e STORAGE_ROOT=/srv/website/storage \
    -e STATIC_ROOT=/srv/website/static \
    -e BACKUP_ROOT=/srv/website/backups \
    -e LOGS_ROOT=/srv/website/logs \
    -e TEMP_ROOT=/srv/website/temp \
    -p "127.0.0.1:${DJANGO_PORT}:${DJANGO_PORT}" \
    -v "${STORAGE_ROOT}:/srv/website/storage:rw" \
    -v "${STATIC_ROOT}:/srv/website/static:rw" \
    -v "${BACKUP_ROOT}:/srv/website/backups:rw" \
    -v "${LOGS_ROOT}:/srv/website/logs:rw" \
    -v "${TEMP_ROOT}:/srv/website/temp:rw" \
    -v "${POSTGRES_SSL_CERT_HOST_PATH:-/root/.postgresql/root.crt}:${POSTGRES_SSL_ROOT_CERT_PATH:-/root/.postgresql/root.crt}:ro" \
    --add-host host.docker.internal:host-gateway \
    --network personal-website \
    docker.io/mikhpo/personal_website:latest
```

Назначение флагов:

- -e с корневыми каталогами /srv/website/... - те же значения, что
  compose.yaml задает в environment. Без них в контейнер попали бы
  хостовые пути из .env (например /srv/personal-website/storage),
  которых внутри контейнера не существует;
- bind-монты каталогов данных - по образцу compose.yaml (mount
  htmlcov/ там - артефакт разработки, здесь опущен);
- сертификат PostgreSQL монтируется read-only: путь хоста
  POSTGRES_SSL_CERT_HOST_PATH, путь контейнера
  POSTGRES_SSL_ROOT_CERT_PATH (его читает Django);
- публикация только на 127.0.0.1 - внешний трафик терминирует прокси;
- --add-host host.docker.internal:host-gateway - доступ
  к systemd-сервисам хоста (systemd-PostgreSQL) с Linux;
- --network - сеть до инфраструктурных контейнеров (см. ниже);
- имя образа - как публикует CI (см. compose.yaml, DOCKER_REGISTRY).

Сеть до БД и хранилища:

- инфраструктура в контейнерах того же хоста - создается общая сеть,
  контейнеры postgres/minio запускаются с тем же --network,
  в .env POSTGRES_HOST и AWS_S3_ENDPOINT_URL указывают имена контейнеров:

  ```bash
  docker network create personal-website
  ```

- systemd-сервисы хоста - POSTGRES_HOST=host.docker.internal
  (работает запись --add-host выше);
- managed-сервисы (удаленный кластер, публичное S3) - дополнительная
  сеть не нужна (используется сеть bridge по умолчанию).

Обновление в этом режиме: docker pull, docker rm -f personal-website
и повторный запуск команды (миграции и collectstatic выполнит
entrypoint.sh при старте).

## 4. systemd Gunicorn на хосте

Режим без Docker вовсе (эталон D): приложение выполняется из рабочей
копии репозитория под Gunicorn, управляется systemd. Требования к RAM
ниже контейнерных - режим рассчитан на слабое и homelab-железо.

Установка (автоматизировано scripts/server/setup.sh):

- системные пакеты: python3, pipx + poetry (окружение .venv создается
  poetry в каталоге проекта), node (сборка фронтенда при деплое),
  postgresql-client-17 (pg_dump/pg_restore бэкапов), nginx, certbot,
  rclone и mc (цели бэкапов);
- .env в корне рабочей копии: DEPLOY_MODE=systemd (диспетчер деплоя
  и бэкапов выбирают ветку по ней); экранирование $$ не нужно;
- cron бэкапов - scripts/cronjobs.sh (setup.sh добавляет).

Юнит /etc/systemd/system/personal-website.service (setup.sh рендерит
из шаблона scripts/server/systemd/personal-website.service.template,
${WORK_DIR} и ${SERVICE_USER} подставляются при установке; ниже - вид
для рабочей копии /srv/personal-website):

```ini
[Unit]
Description=personal-website (Django, Gunicorn)
After=network-online.target
Wants=network-online.target

[Service]
User=mikhpo
Group=www-data
WorkingDirectory=/srv/personal-website
EnvironmentFile=/srv/personal-website/.env
# Миграции и сбор статики выполняются при каждом старте сервиса -
# тот же контракт приложения, что у entrypoint.sh в контейнере.
ExecStartPre=/srv/personal-website/.venv/bin/python backend/manage.py migrate --noinput
ExecStartPre=/srv/personal-website/.venv/bin/python backend/manage.py collectstatic --noinput
# Префикс ":" отключает подстановку переменных окружения systemd: строка
# передается bash без изменений. Bash вычисляет число воркеров той же
# формулой, что и entrypoint.sh: GUNICORN_WORKERS, иначе (2 x CPU) + 1.
# Остальные переменные (DJANGO_PORT, GUNICORN_WORKERS) приходят из
# EnvironmentFile.
ExecStart=:/bin/bash -c 'exec /srv/personal-website/.venv/bin/gunicorn \
    --bind=127.0.0.1:${DJANGO_PORT:-8000} \
    --workers=${GUNICORN_WORKERS:-$((2 * $(nproc --all) + 1))} \
    --max-requests=500 \
    --max-requests-jitter=50 \
    --access-logfile=- \
    --error-logfile=- \
    --pythonpath=/srv/personal-website/backend \
    personal_website.wsgi:application'
# Ожидание готовности внешней БД (wait_for_port из entrypoint.sh) здесь
# недоступно: при старте раньше базы данных миграции завершатся ошибкой,
# сервис перезапустится с задержкой до успешного старта.
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
```

Включение:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now personal-website.service
```

Логи - journal (Gunicorn пишет access/error в stdout/stderr):

```bash
journalctl -u personal-website -f
journalctl -u personal-website --since today
```

Особенности режима:

- переменные читаются из .env директивой EnvironmentFile (значения
  буквально, одинарные/двойные кавычки значений отбрасываются);
- ожидание внешней БД средствами entrypoint.sh недоступно: порядок
  старта обеспечивается After=network-online.target и рестартами
  (Restart=on-failure) до успешного подключения;
- воркеры ограничиваются GUNICORN_WORKERS: формула (2 x CPU) + 1
  прожорлива к RAM на слабом железе (Pillow/ImageKit удерживают память;
  рециклинг --max-requests ограничивает дрейф RSS);
- локальный PostgreSQL под systemd (systemd-PG) - комбинация оси «БД»;
  рецепт появится в [database.md](./database.md), до этого используется
  managed-кластер или контейнер профиля postgres (БД в контейнере
  с приложением на хосте - допустимая комбинация осей).

## 5. Взаимодействие с прокси

Приложение во всех режимах доступно на 127.0.0.1:${DJANGO_PORT};
прокси-слой выбирается независимо и заменяется без изменений
приложения. Варианты и рецепты - [proxy.md](./proxy.md):

- хостовый nginx + certbot (основной путь, мультипроектный хост);
- Traefik в Docker Compose (одиночный сервер «все в Docker»).

Прокси ничего не знает о статике и медиа (см. контракт в разделе 1);
настройки безопасности за прокси (CSRF_TRUSTED_ORIGINS,
SECURE_PROXY_SSL_HEADER и остальные) описаны в .env.example.
