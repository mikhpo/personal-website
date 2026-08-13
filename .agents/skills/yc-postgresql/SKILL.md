---
name: yc-postgresql
description: Управление кластером Managed PostgreSQL в Yandex Cloud через yc — параметры подключения, настройка внешнего доступа, проверка подключения, управление пользователями и паролями.
---

## Предназначение

Скилл для управления кластером Managed PostgreSQL в Yandex Cloud через CLI `yc`: где брать параметры кластера, как включить внешний доступ, как проверить подключение и как менять пароли пользователей (включая типовые подводные камни с connection manager и Lockbox).

Документация:

- CLI: <https://yandex.cloud/ru/docs/managed-postgresql/cli-ref/>
- Managed PostgreSQL: <https://yandex.cloud/ru/docs/managed-postgresql/>
- Подключение: <https://yandex.cloud/ru/docs/managed-postgresql/operations/connect>

## Параметры целевой среды (откуда брать)

Источники информации о кластере:

- `yc config list` — текущий cloud-id, folder-id, subject-id.
- `yc managed-postgresql cluster list` — список кластеров папки.
- `yc managed-postgresql cluster get <имя> --full` — полная конфигурация: версия, ресурсы, access, connection manager, сеть, группы безопасности.
- `yc managed-postgresql host list --cluster-name <имя>` — хосты, зоны, роли и PUBLIC IP (ключевое поле для внешнего доступа).
- `yc managed-postgresql user list --cluster-name <имя>` — пользователи, их БД и conn_limit.
- `yc managed-postgresql database list --cluster-name <имя>` — базы и владельцы.

## Анализ кластера (read-only)

```bash
# Краткий список кластеров
yc managed-postgresql cluster list

# Полная конфигурация кластера
yc managed-postgresql cluster get postgresql --full

# Хосты: FQDN, роль, зона, наличие публичного IP
yc managed-postgresql host list --cluster-name postgresql

# Пользователи и базы
yc managed-postgresql user list --cluster-name postgresql
yc managed-postgresql database list --cluster-name postgresql

# Группы безопасности кластера (None — используются default-SG сети)
yc managed-postgresql cluster get postgresql --format json | \
  python3 -c "import sys,json; print('security_group_ids:', json.load(sys.stdin).get('security_group_ids'))"

# Сеть и default-SG
yc vpc network get <network-id>
yc vpc security-group get <default-sg-id>
```

## Настройка внешнего доступа

Для подключения извне Yandex Cloud (локальная машина, другое облако) нужно:

1. Публичный IP у хоста (ключевой блокер). Проверить:

   ```bash
   yc managed-postgresql host list --cluster-name postgresql
   ```

   Колонка `PUBLIC IP` должна быть `true`.

2. Назначить публичный IP, если его нет:

   ```bash
   yc managed-postgresql host update <FQDN> \
     --cluster-name postgresql --assign-public-ip
   ```

   После этого FQDN начинает резолвиться в публичный адрес:

   ```bash
   dig +short <FQDN>
   ```

3. Группы безопасности. Если к кластеру не привязаны SG (`security_group_ids: None`), действует default-SG сети. Проверить, что default-SG разрешает входящий TCP на 6432 из нужного диапазона (например, `0.0.0.0/0`). Для текущего проекта default-SG уже открыта (`INGRESS ANY из 0.0.0.0/0`) — дополнительно менять ничего не нужно.

Если нужно ограничить доступ конкретными IP, привязать к кластеру отдельную SG правилом `INGRESS TCP 6432 из <CIDR>`:

```bash
yc managed-postgresql cluster update postgresql --security-group-ids <sg-id>
```

## Проверка подключения

Проверка по слоям (сетевой уровень → SSL → аутентификация):

```bash
# Резолвинг FQDN в публичный IP
dig +short <FQDN>

# Доступность TCP-порта 6432
nc -vz -w 10 <FQDN> 6432

# SSL-рукопожатие: сертификат валиден, CN совпадает с FQDN
openssl s_client -starttls postgres -connect <FQDN>:6432 -CAfile ~/.postgresql/root.crt </dev/null 2>&1 \
  | grep -iE "subject|issuer|Verify return code"
# Ожидаемо: subject=CN=<FQDN>, issuer=...YandexCLCA, Verify return code: 0 (ok)

# Полная проверка с аутентификацией
PGPASSWORD=<пароль> psql \
  "host=<fqdn> port=6432 dbname=<dbname> user=<user> \
   sslmode=verify-full sslrootcert=$HOME/.postgresql/root.crt" \
  -c "SELECT current_user, current_database();"
```

Особенность вывода: при подключении через Odyssey `inet_server_addr()/inet_server_port()` возвращают `127.0.0.1:5432` (пулер проксирует на локальный PostgreSQL) — это нормально, не признак ошибки.

## Управление паролями

Внимание: может быть включён connection manager (Odyssey), поэтому пароль хранится в Lockbox-секрете `connection-<connection_id>`.

### Важный подводный камень с --generate-password

Команда `yc managed-postgresql user update <user> --generate-password` для пользователя с connection manager сохраняет пароль в Lockbox-секрете типа `password_payload_specification`. Значение НЕ отображается в выводе yc и нечитаемо:

- В yc нет команды чтения payload секрета.
- Lockbox GetPayload API возвращает `404` для секретов этого типа.
- В метаданных операции пароль также отсутствует.

### Рекомендуемый способ — явный алфавитно-цифровой пароль

Сгенерировать пароль без спецсимволов (не требует экранирования нигде) и задать его одной командой (переменные не сохраняются между вызовами shell — задавать в той же команде):

```bash
PW=$(openssl rand -base64 48 | tr -dc 'A-Za-z0-9' | head -c 24) && \
echo "NEW_PASSWORD=$PW" && \
yc managed-postgresql user update <user> --cluster-name postgresql --password "$PW" && \
PGPASSWORD="$PW" psql \
  "host=<fqdn> port=6432 dbname=db1 user=<user> sslmode=verify-full sslrootcert=$HOME/.postgresql/root.crt" \
  -c "SELECT 1;"
```

### Экранирование паролей со спецсимволами

Если пароль содержит спецсимволы — использовать одинарные кавычки (в zsh/bash всё внутри одинарных кавычек буквально, без раскрытия глобов и истории). Одинарная кавычка внутри пароля вставляется последовательностью `'\''`:

```bash
PW='пароль'\''с_одинарной_кавычкой'
```

Перед применением проверить, что значение разобрано верно:

```bash
printf 'len=%s\n' "${#PW}"
```

## Полезные операции

```bash
# Список бэкапов
yc managed-postgresql cluster list-backups postgresql

# Создать бэкап
yc managed-postgresql cluster backup postgresql

# Операции над кластером (история изменений)
yc managed-postgresql cluster list-operations postgresql --limit 10

# Перезапуск хоста / failover
yc managed-postgresql cluster start-failover postgresql --host <FQDN>

# Обновить конфигурацию PostgreSQL
yc managed-postgresql cluster update-config postgresql ...

# Секреты Lockbox (где хранится пароль connection manager)
yc lockbox secret list --folder-id <folder-id>
yc lockbox secret get --id <secret-id>
```

## Рекомендации

- Перед изменениями анализировать кластер read-only: `cluster get/host list/user list`.
- Для внешнего доступа назначать публичный IP через `host update --assign-public-ip`.
- Группы безопасности: по умолчанию default-SG открыта из `0.0.0.0/0`; при необходимости ограничивать привязкой отдельной SG с правилом на 6432 для конкретных CIDR.
- Все команды yc выполняются в рамках folder-id из `yc config list`; ключи `--cluster-name`/`--cluster-id` взаимозаменяемы.

## Ограничения

- Перед изменением пароля убедиться, что нет активных приложений, использующих старый пароль (после сброса их подключение сломается).
- Деструктивные операции (`delete`, `stop`, `start-failover`) выполнять только с явного разрешения.
