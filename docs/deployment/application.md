# Запуск приложения

Способ запуска приложения выбирается независимо от остальных параметров
развертывания (база данных, хранилище, прокси, бэкапы): Docker Compose,
docker run без Compose или systemd с Gunicorn на хосте. Первичная
настройка автоматизирована скриптами: для Docker Compose -
[scripts/docker/setup.sh](../../scripts/docker/setup.sh), для systemd -
[scripts/server/setup.sh](../../scripts/server/setup.sh).

## 1. Контракт приложения

Контракт одинаков для всех способов запуска, поэтому прокси-слой
и инфраструктура не зависят от выбранного режима.

Приложение слушает порт `DJANGO_PORT`. Контейнерные режимы публикуют
его только на 127.0.0.1 хоста, systemd-режим слушает 127.0.0.1 напрямую;
внешний трафик всегда проходит через прокси-слой. Миграции и сбор
статики выполняются автоматически при каждом старте: в контейнере
их делает entrypoint.sh, в systemd-режиме - директивы ExecStartPre
юнита.

Статические файлы и медиа приложение само по себе не проксирует.
Статику в filesystem-режиме обслуживает WhiteNoise из процесса
приложения, а при `STORAGE_TYPE=s3` она лежит в том же бакете,
что и медиа, и раздается объектным хранилищем. Медиа при s3 тоже
отдает объектное хранилище, а при filesystem их раздает прокси-слой
напрямую с диска, и запросы медиа не нагружают воркеры приложения:
хостовой и контейнерный nginx делают это одинаково - через
location /media/ с alias на `STORAGE_ROOT` (в контейнере каталог
хранилища монтируется прямо в прокси; подробнее -
[proxy.md](./proxy.md)).

Работоспособность приложения проверяется эндпоинтом /health/: он
выполняет проверочный SELECT 1 и отвечает 200 при доступной базе
данных либо 503 при ошибке подключения. Эндпоинт используют healthcheck
контейнера и диагностика. Вся конфигурация приложения - один файл .env.

## 2. Docker Compose

Основной способ запуска. Конфигурация - единый compose.yaml;
инфраструктурные сервисы (postgres, minio, nginx) подключаются
собственными профилями через `COMPOSE_PROFILES`, а пустое значение
означает полностью внешнюю инфраструктуру - поднимается только
приложение. Сводная матрица профилей и типовые сценарии развертывания
собраны в [matrix.md](./matrix.md).

```bash
docker compose up -d
bash scripts/deploy.sh    # бэкап + обновление по DEPLOY_MODE
```

При работе с Compose помнить об особенностях чтения .env: Compose
интерполирует переменные при подстановке значений в compose.yaml,
поэтому каждый символ доллара в значении переменной удваивается
(`$$`). Прочие режимы запуска читают .env буквально: docker run
с флагом --env-file и systemd с директивой EnvironmentFile не требуют
экранирования. Подробное описание поведения - в
[CONTRIBUTING.md](../CONTRIBUTING.md), раздел «Экранирование символа
доллара».

## 3. docker run без Compose

Режим рассчитан на окружения, где есть Docker, но нет Docker Compose -
например, один контейнер на слабой виртуальной машине. Полная команда
приведена ниже; перед её запуском переменные из .env загружаются
в оболочку командой `set -a; . ./.env; set +a`.

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

Смысл флагов следующий. Переменные -e с корневыми каталогами
/srv/website/... задают те же значения, что compose.yaml прописывает
в environment: без них контейнер получил бы хостовые пути из .env
(например /srv/personal-website/storage), которых внутри контейнера
не существует. Каталоги данных подключаются с хоста механизмом bind
mount - путь хоста привязывается к пути внутри контейнера - по образцу
compose.yaml. Сертификат PostgreSQL монтируется read-only: путь на
хосте берется из `POSTGRES_SSL_CERT_HOST_PATH`, путь внутри контейнера -
из `POSTGRES_SSL_ROOT_CERT_PATH` (его читает Django). Порт
публикуется только на 127.0.0.1, потому что внешний трафик
терминирует прокси. Флаг --add-host host.docker.internal:host-gateway
дает контейнеру доступ по имени host.docker.internal к сервисам хоста,
например к PostgreSQL под systemd. Наконец, --network подключает
контейнер к сети `personal-website`, через которую он достигает
инфраструктурных контейнеров, а последний аргумент - имя образа
в том виде, в каком его публикует CI (см. compose.yaml, DOCKER_REGISTRY).

Сеть до базы данных и хранилища выбирается по их размещению:

- если инфраструктура работает в контейнерах того же хоста, создается
  общая сеть `docker network create personal-website`, контейнеры
  postgres/minio запускаются с тем же флагом --network, а в .env
  `POSTGRES_HOST` и `AWS_S3_ENDPOINT_URL` указывают имена контейнеров;
- если это systemd-сервисы хоста, используется
  `POSTGRES_HOST=host.docker.internal` (работает запись --add-host
  из команды выше);
- удаленным сервисам (managed-кластер, публичное S3) дополнительная
  сеть не нужна - используется сеть bridge по умолчанию.

Обновление в этом режиме сводится к `docker pull`, `docker rm -f
personal-website` и повторному запуску команды: миграции и collectstatic
выполнит entrypoint.sh при старте.

## 4. systemd с Gunicorn на хосте

Режим без Docker: приложение выполняется из рабочей копии репозитория
под Gunicorn и управляется systemd. Требования к памяти ниже, чем
в контейнерных режимах, поэтому вариант рассчитан на слабое железо
домашнего сервера.

Установка автоматизирована scripts/server/setup.sh и состоит
из следующих шагов:

- устанавливаются системные пакеты: python3, pipx с poetry (окружение
  .venv создается poetry в каталоге проекта), node для сборки фронтенда
  при деплое, postgresql-client-17 для дампов и восстановления
  бэкапов, nginx и certbot для прокси-слоя, rclone и mc для целей
  бэкапов;
- в корень рабочей копии помещается .env с `DEPLOY_MODE=systemd` -
  по этой переменной диспетчеры деплоя и бэкапов выбирают ветку
  поведения (экранирование символа доллара, в отличие от Compose,
  не требуется);
- расписание бэкапов добавляет scripts/cronjobs.sh.

Юнит /etc/systemd/system/personal-website.service рендерится setup.sh
из шаблона scripts/server/systemd/personal-website.service.template:
значения ${WORK_DIR} и ${SERVICE_USER} подставляются при установке.
Ниже приведен вид юнита для рабочей копии /srv/personal-website.

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
ExecStartPre=/srv/personal-website/.venv/bin/python backend/manage.py migrate --noinput
ExecStartPre=/srv/personal-website/.venv/bin/python backend/manage.py collectstatic --noinput
ExecStart=:/bin/bash -c 'exec /srv/personal-website/.venv/bin/gunicorn \
    --bind=127.0.0.1:${DJANGO_PORT:-8000} \
    --workers=${GUNICORN_WORKERS:-$((2 * $(nproc --all) + 1))} \
    --max-requests=500 \
    --max-requests-jitter=50 \
    --access-logfile=- \
    --error-logfile=- \
    --pythonpath=/srv/personal-website/backend \
    personal_website.wsgi:application'
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
```

Включение юнита:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now personal-website.service
```

Логи сервиса пишет journal (Gunicorn направляет access- и error-логи
в stdout/stderr):

```bash
journalctl -u personal-website -f
journalctl -u personal-website --since today
```

У режима есть особенности, о которых стоит знать.

Переменные читаются из .env директивой EnvironmentFile: значения
берутся буквально, одинарные и двойные кавычки значений отбрасываются.

Префикс ":" в ExecStart отключает подстановку переменных окружения
самим systemd - строка передается bash без изменений. Благодаря этому
выражения ${DJANGO_PORT:-8000} и ${GUNICORN_WORKERS:-...} вычисляет
bash при старте процесса, а не systemd при загрузке юнита.

Ожидание внешней базы данных, которое в контейнере выполняет
entrypoint.sh, здесь недоступно: порядок старта обеспечивается
директивой After=network-online.target и автоматическими рестартами
(Restart=on-failure) до успешного подключения.

Число воркеров при старте вычисляется по формуле «значение
GUNICORN_WORKERS из .env, иначе (2 x CPU) + 1» - той же, что
и в entrypoint.sh контейнера. На слабом железе формула прожорлива
к памяти: воркеры удерживают память из-за Pillow и ImageKit,
а рабочий рециклинг (--max-requests) лишь ограничивает дрейф RSS.
Поэтому на слабом сервере GUNICORN_WORKERS лучше задать явно,
например 2.

Локальный PostgreSQL под systemd - один из вариантов размещения базы
данных; его рецепт появится в [database.md](./database.md), до этого
используется managed-кластер или контейнер профиля postgres (БД
в контейнере при приложении на хосте - допустимое сочетание
параметров развертывания).

### Вариант: unix-сокет вместо TCP-порта

По умолчанию systemd-режим использует TCP-порт на 127.0.0.1 - это
сохраняет единый контракт приложения со всеми способами запуска.
Когда Gunicorn и nginx работают в одной операционной системе
(мультипроектный bare-metal-хост), приложение можно перевести
на unix-сокет с активацией сокетом (systemd socket activation).
Это дает три преимущества:

- бесшовные рестарты - на время перезапуска сервиса соединения
  копятся в backlog сокета, а не отвергаются;
- мультипроектный хост - каждому приложению выделяется свой сокет,
  пул TCP-портов вести не нужно, nginx адресует сайты проектов путями
  сокетов;
- доступ ограничивается правами файла сокета (SocketGroup=www-data,
  SocketMode=0660), а не привязкой порта.

Ограничение варианта: он не сочетается с контейнерными прокси -
контейнер nginx не видит сокет хостовой операционной системы,
фактически вариант означает «только хостовой nginx». Кроме того,
для него не выполняется контракт порта DJANGO_PORT.
Комплект юнитов лежит в scripts/server/systemd/socket/ (setup.sh
устанавливает TCP-вариант; сокет подключается вручную). Юнит
personal-website.socket описывает сокет
ListenStream=/run/personal-website.sock с правами группы www-data.
Файл personal-website.service.template - сервисный юнит без --bind:
Gunicorn наследует готовый дескриптор сокета от systemd (переменные
LISTEN_FDS/LISTEN_PID) и рендерится envsubst по WORK_DIR
и SERVICE_USER, как основной шаблон выше.

Установка:

```bash
export WORK_DIR=/srv/personal-website SERVICE_USER=<пользователь>
envsubst "\$WORK_DIR \$SERVICE_USER" < personal-website.service.template |
    sudo tee /etc/systemd/system/personal-website.service >/dev/null
sudo cp personal-website.socket /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now personal-website.socket
```

Сервисный юнит активируется первым же соединением с сокетом - раздел
[Install] есть только у юнита сокета. Запрос после загрузки сервера
подождет ExecStartPre (миграции и collectstatic). Проверить вариант
можно так:

```bash
curl --unix-socket /run/personal-website.sock http://localhost/health/
```

В конфигурации сайта nginx адресация меняется на
`proxy_pass http://unix:/run/personal-website.sock`, остальные
директивы остаются прежними ([proxy.md](./proxy.md), раздел 2).

## 5. Взаимодействие с прокси

Во всех режимах приложение доступно на 127.0.0.1:${DJANGO_PORT}.
Прокси-слой выбирается независимо и заменяется без изменений
приложения; инструмент один - nginx, различается только размещение
(рекомендации и рецепты - в [proxy.md](./proxy.md)):

- nginx в Docker Compose (профиль nginx) с certbot отдельным
  контейнером - вариант одиночного сервера «все в Docker»;
- nginx на хосте с certbot - вариант мультипроектного хоста
  (сценарии «домашний сервер» и «сервер без Docker»).

Прокси не занимается статикой: о ней он ничего не знает (контракт -
в разделе 1). Медиа filesystem-режима - единственное, что прокси
раздает с диска сам. Настройки безопасности за прокси
(CSRF_TRUSTED_ORIGINS, SECURE_PROXY_SSL_HEADER и остальные) описаны
в .env.example.
