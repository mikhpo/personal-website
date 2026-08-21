#!/bin/bash
#
# Копирование медиафайлов в S3 при помощи MinIO Client.
# Источник определяется по STORAGE_TYPE: локальный каталог STORAGE_ROOT
# либо медиа-бакет S3. Приемник поддерживает точное зеркало: файлы,
# отсутствующие в источнике, удаляются в приемнике.
# Приемник по умолчанию - префикс storage бакета бэкапов (BACKUP_BUCKET).
# Первым аргументом можно указать другой адрес вида alias/бакет[/префикс] -
# например, медиа-бакет при переносе хранилища с filesystem на s3:
#   ./scripts/s3backup.sh "$MINIO_ALIAS/$AWS_STORAGE_BUCKET_NAME"
# Остальные аргументы передаются mc mirror (например, --dry-run).

# Выйти в случае ошибки.
set -e

# Зафиксировать дату и время выполнения.
now=$(date '+%Y-%m-%d %H:%M:%S')
echo "Копирование медиафайлов в S3. Дата и время выполнения: $now"

# Прочитать переменные окружения из файла .env.
# Путь к .env можно задать через переменную окружения DOTENV_PATH.
project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
readonly dotenv="${DOTENV_PATH:-$project_root/.env}"
if [ -f "$dotenv" ]; then
    set -a
    . "$dotenv"
    set +a
    echo "Переменные окружения загружены из файла $dotenv"
else
    echo "Ошибка: файл с переменными окружения $dotenv не существует" >&2
    exit 1
fi

# Проверить обязательные переменные окружения.
if [ -z "$MC_PATH" ]; then
    echo "Ошибка: MC_PATH не задана в .env" >&2
    exit 1
fi

# Проверить тип хранилища и установить источник.
if [ "$STORAGE_TYPE" = "s3" ]; then
    # Источник - медиа-бакет S3.
    if [ -z "$AWS_STORAGE_BUCKET_NAME" ]; then
        echo "Ошибка: AWS_STORAGE_BUCKET_NAME не задана в .env при STORAGE_TYPE=s3" >&2
        exit 1
    fi
    SOURCE="$MINIO_ALIAS/$AWS_STORAGE_BUCKET_NAME"
    echo "Источник: бакет S3 $SOURCE"
else
    # Источник - локальное файловое хранилище.
    SOURCE="$STORAGE_ROOT"
    echo "Источник: файловое хранилище $SOURCE"
fi

# Определить приемник: аргумент вида alias/бакет[/префикс] или бакет бэкапов.
if [ "$#" -gt 0 ]; then
    readonly TARGET="$1"
    shift
else
    readonly TARGET="$MINIO_ALIAS/$BACKUP_BUCKET/storage"
fi
# Адрес без алиаса (например, при незаданной переменной окружения в команде
# запуска) молча направляет копию не в тот ресурс, поэтому отвергается сразу.
if [[ ! "$TARGET" =~ ^[^/]+/.+ ]]; then
    echo "Ошибка: приемник \"$TARGET\" должен иметь вид alias/бакет[/префикс]" >&2
    exit 1
fi
echo "Приемник: $TARGET"

# Создать бакет приемника, если не существует.
bucket="${TARGET#*/}"
readonly bucket="${bucket%%/*}"
$MC_PATH mb --ignore-existing "$MINIO_ALIAS/$bucket"

# Определить размер источника.
if [ "$STORAGE_TYPE" = "s3" ]; then
    storage_size=$($MC_PATH du "$SOURCE" 2>/dev/null | awk '{print $1}')
else
    storage_size=$(du -sh "$SOURCE" | cut -f1 | tr -d ' ')
fi
echo "Размер источника: $storage_size"

# Выполнить копирование.
# Дополнительные аргументы передаются mc mirror.
$MC_PATH mirror \
    --overwrite \
    --remove \
    "$SOURCE" \
    "$TARGET" \
    "$@"

# Определить размер приемника. При пробном прогоне копирование
# не выполнялось, поэтому размер приемника не снимается.
if [[ " $* " == *" --dry-run "* ]]; then
    echo "Пробный прогон: копирование не выполнялось"
else
    echo "Размер приемника: $($MC_PATH du "$TARGET" | awk '{print $1}')"
fi
