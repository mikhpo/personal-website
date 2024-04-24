#!/bin/bash
#
# Создание бэкапа системного файлового хранилища при помощи утилиты MinIO Client.

# Выйти в случае ошибки.
set -e

# Зафиксировать дату и время выполнения.
now=$(date '+%Y-%m-%d %H:%M:%S')
echo "Cоздание бэкапа файлового хранилища. Дата и время выполнения: $now"

# Прочитать переменные окружения из файла .env в корневом каталоге проекта.
project_root="$(dirname "$(dirname "$(dirname "$(readlink -f "$0")")")")"
readonly dotenv="$project_root/.env"
if [ -f "$dotenv" ]; then
    eval export "$(cat "$dotenv")"
    echo "Переменные окружения загружены из файла $dotenv"
fi

# Определить полный адрес копируемого каталога.
readonly SOURCE="$STORAGE_ROOT"
echo "Адрес файлового хранилища: $SOURCE"

# Определение размера копируемого каталога.
storage_size=$(du -sh "$SOURCE" | cut -f 1 | tr -d ' ')
echo "Размер файлового хранилища: $storage_size"

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
