# База данных

Размещение PostgreSQL выбирается независимо от остальных параметров
развертывания (способ запуска приложения, хранилище, прокси, бэкапы).
Варианты: managed-кластер провайдера / контейнер compose (профиль
postgres) / systemd на хосте. Для приложения варианты неотличимы:
подключение всегда через переменные `POSTGRES_HOST/PORT/USER/PASSWORD/DB`,
SSL - `POSTGRES_SSL_MODE` и `POSTGRES_SSL_ROOT_CERT_PATH`.

Содержание:

1. Подключение и SSL
2. Managed-кластер
3. Контейнер compose
4. systemd-PostgreSQL на хосте
5. Мажорный апгрейд
6. Резервное копирование

## 1. Подключение и SSL

Переменные .env (секция «База данных»):

- `POSTGRES_HOST` - имя хоста: `postgres` внутри compose-сети,
  `host.docker.internal` для systemd-PostgreSQL со стороны контейнеров
  (запись extra_hosts в compose.yaml уже добавлена), `localhost` для
  процессов хоста, FQDN managed-кластера;
- `POSTGRES_PORT`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` -
  порт, пользователь, пароль, база;
- `POSTGRES_SSL_MODE` - режим SSL libpq: `prefer` для локалки,
  `verify-full` для managed-сервисов;
- `POSTGRES_SSL_ROOT_CERT_PATH` - канонический путь сертификата CA,
  который читает Django (sslrootcert); дефолт `~/.postgresql/root.crt`
  (конвенция libpq);
- `POSTGRES_SSL_CERT_HOST_PATH` - путь на хосте для bind-mount
  (только в Docker, когда пути хоста и контейнера различаются);
- `POSTGRES_SSL_CERT_URL` - URL загрузки сертификата скриптом
  [scripts/pgcert.sh](../../scripts/pgcert.sh): непустое значение -
  триггер, загрузка идемпотентна, принудительное обновление -
  `bash scripts/pgcert.sh --force`.

Доставка сертификата по средам:

- systemd-режим: достаточно `POSTGRES_SSL_ROOT_CERT_PATH` - общая
  файловая система;
- Docker Compose: compose монтирует сертификат в контейнер (путь хоста
  `POSTGRES_SSL_CERT_HOST_PATH` -> путь контейнера
  `POSTGRES_SSL_ROOT_CERT_PATH`);
- docker run: монтирование флагом `-v` (см. [application.md](./application.md),
  раздел 3).

Ожидание готовности БД при старте выполняет функция wait_for_port
в entrypoint.sh (depends_on не используется: сервис может быть внешним).

## 2. Managed-кластер

Удаленный кластер провайдера (Yandex Cloud Managed PostgreSQL и
совместимые). Особенности:

- публичный доступ требует SSL с проверкой сертификата CA:
  `POSTGRES_SSL_MODE='verify-full'`;
- порт управляемых соединителей отличается от дефолтного (Yandex Cloud -
  6432);
- сертификат CA скачивается pgcert.sh по `POSTGRES_SSL_CERT_URL`
  (у Yandex Cloud - `https://storage.yandexcloud.net/cloud-certs/CA.pem`);
- автоматические бэкапы провайдера не заменяют собственные: данные
  покидают инфраструктуру провайдера только системой бэкапов проекта
  ([backups.md](./backups.md)).

Смена провайдера - обновление переменных подключения в .env и сертификата
(`pgcert.sh --force`), перенос данных - дамп/восстановление
(скиллы postgresql-dump / postgresql-restore).

## 3. Контейнер compose

Сервис postgres подключается профилем postgres (`COMPOSE_PROFILES=postgres`
или `docker compose up -d postgres`). База, пользователь и пароль создаются
образом автоматически из `POSTGRES_USER/POSTGRES_PASSWORD/POSTGRES_DB`.
Имя хоста для соседних сервисов compose - `postgres`; порт публикуется
только на 127.0.0.1 хоста (внешний доступ к БД не предусмотрен).

Данные живут в именованном томе `postgres-data`: `docker compose down`
том сохраняет, `docker compose down -v` - удаляет (вместе с данными
minio-data). Смена мажорной версии образа тома не переживает - раздел 5.

## 4. systemd-PostgreSQL на хосте

Локальный кластер без Docker (эталон D; также допустимое сочетание -
приложение в контейнере, БД на хосте). Установка из пакета дистрибутива
(Debian/Ubuntu, репозиторий PGDG для свежих мажорных версий):

```bash
sudo apt-get install -y postgresql-17
```

Кластер создается пакетом (`pg_lsclusters` - статус). Каталог данных
на выбранном диске задается при создании кластера:

```bash
sudo pg_dropcluster --stop 17 main   # кластер по умолчанию пуст
sudo mkdir -p /srv/pgdata
sudo chown postgres:postgres /srv/pgdata
sudo pg_createcluster 17 main -d /srv/pgdata
sudo systemctl enable --now postgresql@17-main
```

Доступ из Docker-контейнеров: контейнеры адресуют хост именем
`host.docker.internal` (запись `host.docker.internal:host-gateway`
в compose.yaml), соединения приходят с адреса шлюза docker-подсети.
Разрешить их в pg_hba.conf и включить прослушивание:

`/etc/postgresql/17/main/postgresql.conf`:

```text
listen_addresses = 'localhost, 172.17.0.1'
password_encryption = scram-sha-256
```

`/etc/postgresql/17/main/pg_hba.conf` (адрес подсети - вывод
`ip addr show docker0`; при нескольких compose-проектах добавить запись
для каждой подсети):

```text
host  all  all  172.17.0.0/16  scram-sha-256
```

Пользователь и база приложения:

```bash
sudo -u postgres psql -c "CREATE USER website WITH PASSWORD '<пароль>';"
sudo -u postgres psql -c "CREATE DATABASE personal_website OWNER website ENCODING 'UTF8';"
```

После смены `password_encryption` пароль задается заново (существующие
записи остаются в старом формате md5 и отклоняются проверкой scram).

В .env: `POSTGRES_HOST=localhost` (приложение на хосте) или
`POSTGRES_HOST=host.docker.internal` (приложение в контейнере),
`POSTGRES_SSL_MODE='prefer'` (шифрование локальных соединений не требуется).

## 5. Мажорный апгрейд

Формат каталога данных не совместим между мажорными версиями PostgreSQL:
том/каталог данных с данными версии N не поднимается образом/пакетом
версии N+1. Апгрейд - dump/restore, не смена версии на живых данных:

1. Снять дамп работающей версии (скилл postgresql-dump или
   `bash scripts/backup.sh backup_db` - свежий дамп появится
   в `${BACKUP_ROOT}/db` и в целях);
2. compose: остановить стек, удалить том `postgres-data`
   (`docker compose down postgres` и `docker volume rm`), обновить тег
   образа postgres в compose.yaml, поднять снова - база создается
   заново из переменных окружения; systemd: установить новую версию,
   создать пустой кластер `pg_createcluster`;
3. Восстановить дамп в новую базу (скилл postgresql-restore или
   `bash scripts/backup.sh restore_db <путь>`); правило совместимости -
   pg_restore не ниже версии сервера-источника;
4. Проверить счетчики таблиц и `django_migrations`, живость приложения -
   эндпоинт `/health/`.

## 6. Резервное копирование

Дампы БД, расписание, цели и ретеншн - [backups.md](./backups.md).
Разовые операции переноса между кластерами выполняются утилитами
pg_dump/pg_restore напрямую (скиллы postgresql-dump, postgresql-restore).
