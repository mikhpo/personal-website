# База данных

Размещение PostgreSQL выбирается независимо от остальных параметров
развертывания (способ запуска приложения, хранилище, прокси, бэкапы).
Варианты: managed-кластер провайдера, контейнер compose (профиль
postgres) или systemd-сервис на хосте. Для приложения варианты
неотличимы: подключение всегда описывается переменными
`POSTGRES_HOST/PORT/USER/PASSWORD/DB`, а SSL - переменными
`POSTGRES_SSL_MODE` и `POSTGRES_SSL_ROOT_CERT_PATH`.

## 1. Подключение и SSL

Переменные .env (секция «База данных»):

- `POSTGRES_HOST` - имя хоста: `postgres` внутри compose-сети,
  `host.docker.internal` для PostgreSQL под systemd со стороны
  контейнеров (запись extra_hosts в compose.yaml уже добавлена),
  `localhost` для процессов хоста, FQDN managed-кластера;
- `POSTGRES_PORT`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` -
  порт, пользователь, пароль, база;
- `POSTGRES_SSL_MODE` - режим SSL libpq: `prefer` для локальных
  подключений, `verify-full` для managed-сервисов;
- `POSTGRES_SSL_ROOT_CERT_PATH` - канонический путь сертификата CA,
  который читает Django (sslrootcert); дефолт `~/.postgresql/root.crt`
  (конвенция libpq);
- `POSTGRES_SSL_CERT_HOST_PATH` - путь сертификата на хосте
  для монтирования в контейнер (нужен только в Docker, когда пути
  хоста и контейнера различаются);
- `POSTGRES_SSL_CERT_URL` - URL загрузки сертификата скриптом
  [scripts/pgcert.sh](../../scripts/pgcert.sh): непустое значение -
  триггер, загрузка идемпотентна, принудительное обновление -
  `bash scripts/pgcert.sh --force`.

Доставка сертификата зависит от режима. В systemd-режиме достаточно
`POSTGRES_SSL_ROOT_CERT_PATH` - приложение и сертификат живут в одной
файловой системе. В Docker Compose сертификат монтируется в контейнер
автоматически: путь хоста берется из `POSTGRES_SSL_CERT_HOST_PATH`,
путь контейнера - из `POSTGRES_SSL_ROOT_CERT_PATH`. В docker run
монтирование задается флагом -v ([application.md](./application.md),
раздел 3).

Ожидание готовности базы при старте выполняет функция wait_for_port
в entrypoint.sh - директива depends_on не используется, потому что
база может быть внешним сервисом.

## 2. Managed-кластер

Удаленный кластер провайдера (Yandex Cloud Managed PostgreSQL
и совместимые). Особенности подключения:

- публичный доступ требует SSL с проверкой сертификата CA:
  `POSTGRES_SSL_MODE='verify-full'`;
- порт управляемых соединителей отличается от дефолтного (у Yandex
  Cloud - 6432);
- сертификат CA скачивается pgcert.sh по `POSTGRES_SSL_CERT_URL`
  (у Yandex Cloud -
  `https://storage.yandexcloud.net/cloud-certs/CA.pem`);
- автоматические бэкапы провайдера не заменяют собственные: данные
  покидают инфраструктуру провайдера только системой бэкапов проекта
  ([backups.md](./backups.md)).

Смена провайдера сводится к обновлению переменных подключения в .env
и сертификата (`pgcert.sh --force`); перенос данных выполняется
дампом и восстановлением (скиллы postgresql-dump / postgresql-restore).

## 3. Контейнер compose

Сервис postgres подключается профилем postgres
(`COMPOSE_PROFILES=postgres` или `docker compose up -d postgres`).
База, пользователь и пароль создаются образом автоматически
из `POSTGRES_USER/POSTGRES_PASSWORD/POSTGRES_DB`. Имя хоста для
соседних сервисов compose - `postgres`; порт публикуется только
на 127.0.0.1 хоста, внешний доступ к базе не предусмотрен.

Данные живут в именованном томе postgres-data: `docker compose down`
том сохраняет, `docker compose down -v` - удаляет (вместе с данными
minio-data). Смена мажорной версии образа тома не переживает -
см. раздел 5.

## 4. systemd-PostgreSQL на хосте

Локальный кластер без Docker - вариант сценария «сервер без Docker»;
допустимо и сочетание «приложение в контейнере, база на хосте».
Установка выполняется из пакета дистрибутива (Debian/Ubuntu,
репозиторий PGDG для свежих мажорных версий):

```bash
sudo apt-get install -y postgresql-17
```

Кластер создается пакетом (статус показывает `pg_lsclusters`). Каталог
данных на выбранном диске задается при создании кластера:

```bash
sudo pg_dropcluster --stop 17 main   # кластер по умолчанию пуст
sudo mkdir -p /srv/pgdata
sudo chown postgres:postgres /srv/pgdata
sudo pg_createcluster 17 main -d /srv/pgdata
sudo systemctl enable --now postgresql@17-main
```

Если приложение работает в Docker-контейнерах, контейнеры адресуют
хост именем `host.docker.internal` (запись
`host.docker.internal:host-gateway` в compose.yaml), и соединения
приходят с адреса шлюза docker-подсети. Их нужно разрешить
в pg_hba.conf и включить прослушивание нужных адресов.

`/etc/postgresql/17/main/postgresql.conf`:

```text
listen_addresses = 'localhost, 172.17.0.1'
password_encryption = scram-sha-256
```

`/etc/postgresql/17/main/pg_hba.conf` (адрес подсети - вывод
`ip addr show docker0`; при нескольких compose-проектах добавьте
запись для каждой подсети):

```text
host  all  all  172.17.0.0/16  scram-sha-256
```

Пользователь и база приложения создаются так:

```bash
sudo -u postgres psql -c "CREATE USER website WITH PASSWORD '<пароль>';"
sudo -u postgres psql -c "CREATE DATABASE personal_website OWNER website ENCODING 'UTF8';"
```

После смены `password_encryption` пароль задается заново:
существующие записи остаются в старом формате md5 и отклоняются
проверкой scram.

В .env указываются `POSTGRES_HOST=localhost` (приложение на хосте)
или `POSTGRES_HOST=host.docker.internal` (приложение в контейнере)
и `POSTGRES_SSL_MODE='prefer'` - шифрование локальных соединений
не требуется.

## 5. Мажорный апгрейд

Формат каталога данных не совместим между мажорными версиями
PostgreSQL: том или каталог данных версии N не поднимется образом
или пакетом версии N+1. Поэтому апгрейд выполняется через dump/restore,
а не сменой версии на живых данных:

1. Снимите дамп работающей версии (скилл postgresql-dump или
   `bash scripts/backup.sh backup_db` - свежий дамп появится
   в `${BACKUP_ROOT}/db` и в целях).
2. Подготовьте пустую базу новой версии: в compose - остановить стек,
   удалить том `postgres-data` (`docker compose down postgres`
   и `docker volume rm`), обновить тег образа postgres в compose.yaml
   и поднять стек снова (база создается заново из переменных
   окружения); в systemd - установить новую версию и создать пустой
   кластер `pg_createcluster`.
3. Восстановите дамп в новую базу (скилл postgresql-restore или
   `bash scripts/backup.sh restore_db <путь>`). Правило совместимости:
   pg_restore не ниже версии сервера-источника.
4. Проверьте счетчики таблиц и примененные миграции `django_migrations`;
   работоспособность приложения подтвердите эндпоинтом `/health/`.

## 6. Резервное копирование

Дампы базы, расписание, цели и ретеншн описаны в
[backups.md](./backups.md). Разовые операции переноса между кластерами
выполняются утилитами pg_dump/pg_restore напрямую (скиллы
postgresql-dump, postgresql-restore).
