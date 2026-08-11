#!/bin/bash
#
# Идемпотентная загрузка SSL-сертификата CA для подключения к Managed PostgreSQL.
# Сертификат скачивается один раз при первичной установке либо при обновлении
# (флаг --force). Путь загрузки определяется приоритетом (см. ниже):
#   POSTGRES_SSL_CERT_HOST_PATH -> POSTGRES_SSL_ROOT_CERT_PATH -> ~/.postgresql/root.crt.
# Скрипт вызывается из scripts/server/deploy.sh и scripts/server/update.sh,
# но также пригоден к самостоятельному запуску.

# Выйти в случае ошибки.
set -e

# Корневой каталог проекта и файл переменных окружения.
project_root="$(dirname "$(dirname "$(readlink -f "$0")")")"
readonly dotenv="$project_root/.env"
if [ -f "$dotenv" ]; then
    eval export "$(cat "$dotenv")"
    echo "Переменные окружения загружены из файла $dotenv"
fi

# Если URL сертификата не задан, то SSL не используется — пропуск загрузки.
if [ -z "$POSTGRES_SSL_CERT_URL" ]; then
    echo "POSTGRES_SSL_CERT_URL не задан — загрузка SSL-сертификата пропущена"
    exit 0
fi

# Полный путь к файлу сертификата. Приоритет:
#   1. POSTGRES_SSL_CERT_HOST_PATH — путь на хосте (Docker, когда пути хоста и контейнера различаются).
#   2. POSTGRES_SSL_ROOT_CERT_PATH — канонический путь, который читает Django (bare-metal, общий случай).
#   3. Дефолт ~/.postgresql/root.crt (конвенция libpq, см. документацию PostgreSQL, раздел 32.19.1).
readonly cert_path="${POSTGRES_SSL_CERT_HOST_PATH:-${POSTGRES_SSL_ROOT_CERT_PATH:-$HOME/.postgresql/root.crt}}"
mkdir -p "$(dirname "$cert_path")"

# Идемпотентность: если сертификат уже на месте и не запрошен --force, то пропуск.
if [ -f "$cert_path" ] && [ "$1" != "--force" ]; then
    echo "SSL-сертификат уже на месте: $cert_path (используйте --force для обновления)"
    exit 0
fi

# Загрузка сертификата при помощи curl.
echo "Загрузка SSL-сертификата из $POSTGRES_SSL_CERT_URL в $cert_path"
curl -fsSL "$POSTGRES_SSL_CERT_URL" --output "$cert_path"
chmod 0644 "$cert_path"
echo "SSL-сертификат сохранён: $cert_path"
