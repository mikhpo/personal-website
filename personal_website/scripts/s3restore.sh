#!/bin/bash
#
# Восстановление бэкапа системного файлового хранилища при помощи утилиты MinIO Client.

# Выйти в случае ошибки.
set -e

# Прочитать переменные окружения из файла .env в корневом каталоге проекта.
project_root="$(dirname "$(dirname "$(dirname "$(readlink -f "$0")")")")"
readonly dotenv="$project_root/.env"
if [ -f "$dotenv" ]; then
    eval export "$(cat "$dotenv")"
    echo "Переменные окружения загружены из файла $dotenv"
fi

# Определить адреса источника и целевого ресурса.
readonly S3_BUCKET="$MINIO_ALIAS/$BACKUP_BUCKET"
readonly SOURCE="$S3_BUCKET/storage"
readonly TARGET="$STORAGE_ROOT"
echo "Адрес файлового хранилища: $TARGET"

# Выполнить копирование резервной копии в локальную систему.
echo "Копирование бэкапа в $TARGET"
mc mirror \
    --limit-download 100M \
    "$SOURCE" \
    "$TARGET"

# Определение конечного размера хранилища.
storage_size=$(du -sh "$TARGET" | cut -f 1 | tr -d ' ')
echo "Размер файлового хранилища: $storage_size"
