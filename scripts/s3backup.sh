#!/bin/bash
#
# Создание бэкапа файлового хранилища или медиа-бакета S3.
# При STORAGE_TYPE=filesystem копирует из локального STORAGE_ROOT в бакет бэкапов.
# При STORAGE_TYPE=s3 копирует из медиа-бакета S3 в бакет бэкапов (S3→S3).

# Выйти в случае ошибки.
set -e

# Зафиксировать дату и время выполнения.
now=$(date '+%Y-%m-%d %H:%M:%S')
echo "Cоздание бэкапа файлового хранилища или медиа-бакета S3. Дата и время выполнения: $now"

# Прочитать переменные окружения из файла .env.
# Путь к .env можно задать через переменную окружения DOTENV_PATH.
project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
readonly dotenv="${DOTENV_PATH:-$project_root/.env}"
if [ -f "$dotenv" ]; then
    eval export "$(grep -v '^#' "$dotenv" | grep -v '^$')"
    echo "Переменные окружения загружены из файла $dotenv"
fi

# Проверить тип хранилища и установить источник.
if [ "$STORAGE_TYPE" = "s3" ]; then
    # Источник — медиа-бакет S3.
    if [ -z "$AWS_STORAGE_BUCKET_NAME" ]; then
        echo "Ошибка: AWS_STORAGE_BUCKET_NAME не задана в .env при STORAGE_TYPE=s3"
        exit 1
    fi
    SOURCE="$MINIO_ALIAS/$AWS_STORAGE_BUCKET_NAME"
    echo "Источник бэкапа: бакет S3 $SOURCE"
else
    # Источник — локальное файловое хранилище.
    SOURCE="$STORAGE_ROOT"
    echo "Адрес файлового хранилища: $SOURCE"
fi

# Определить размер источника.
if [ "$STORAGE_TYPE" = "s3" ]; then
    storage_size=$($MC_PATH du "$SOURCE" 2>/dev/null | awk '{print $1}')
else
    storage_size=$(du -sh "$SOURCE" | cut -f1 | tr -d ' ')
fi
echo "Размер источника: $storage_size"

# Создать бакет в S3, если не существует.
readonly S3_BUCKET="$MINIO_ALIAS/$BACKUP_BUCKET"
$MC_PATH mb --ignore-existing "$S3_BUCKET"
readonly TARGET="$S3_BUCKET/storage"

# Выполнить резервное копирование.
# Файлы, отсутствующие в источнике, удаляются в целевом ресурсе.
echo "Выполнение резервного копирования в $TARGET"
$MC_PATH mirror \
    --overwrite \
    --remove \
    "$SOURCE" \
    "$TARGET"
