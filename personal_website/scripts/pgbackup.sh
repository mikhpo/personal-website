#!/bin/bash
#
# Создание дампа базы данных PostgreSQL при помощи утилиты pg_dump.

# Выйти в случае ошибки.
set -e

# Зафиксировать дату и время выполнения.
today=$(date '+%Y-%m-%d')
now=$(date '+%Y-%m-%d %H:%M:%S')
echo "Cоздание бэкапа базы данных PostgreSQL. Дата и время выполнения: $now"

# Прочитать переменные окружения из файла .env в корневом каталоге проекта.
project_root="$(dirname "$(dirname "$(dirname "$(readlink -f "$0")")")")"
readonly dotenv="$project_root/.env"
if [ -f "$dotenv" ]; then
    eval export "$(cat "$dotenv")"
    echo "Переменные окружения загружены из файла $dotenv"
fi

# Определить имя и полный путь дампа, состоящий из имени базы данных и текущей даты.
readonly dump_name="${POSTGRES_DB}_${today}.dump"
readonly dump_dir="database/$POSTGRES_DB"
readonly dump_path="$BACKUP_ROOT/$dump_dir/$dump_name"
echo "Дамп базы данных будет сохранен по адресу $dump_path"
mkdir -p "$BACKUP_ROOT/$dump_dir"

# Если сегодня дамп уже создавался, то его следует удалить.
if [ -f "$dump_path" ]; then
    echo "Сегодня уже был создан дамп $dump_path, ранее созданный дамп будет удален"
    rm "$dump_path"
fi

# Подстановка переменных окружения в параметры выполнения программы pg_dump.
connection="host=$POSTGRES_HOST port=$POSTGRES_PORT dbname=$POSTGRES_DB user=$POSTGRES_USER"
echo "Выполнение программы pg_dump с параметрами подключения: $connection"
export PGPASSWORD=$POSTGRES_PASSWORD
pg_dump \
    "$connection" \
    -Fc \
    --no-privileges \
    --no-subscriptions \
    --no-publications \
    -f "$dump_path"

# Проверить успешность создания дампа.
if [ -f "$dump_path" ]; then
    echo "Дамп по адресу $dump_path был создан"
else
    echo "Не удалось создать дамп базы данных"
    exit
fi

# Вывести размер дампа в человекочитаемой форме и без лишних пробелов.
filesize=$(du -h "$dump_path" | cut -f 1 | tr -d ' ')
echo "Размер дампа: $filesize"

# Создать бакет в S3, если не существует.
readonly S3_BUCKET="$MINIO_ALIAS/$BACKUP_BUCKET"
$MC_PATH mb --ignore-existing "$S3_BUCKET"

# Скопировать файл дампа из локальной файловой системы в бакет S3.
# Созданный ранее объект с тем же именем удаляется.
readonly object_name="$dump_dir/$dump_name"
readonly target_path="$S3_BUCKET/$object_name"
if [[ $($MC_PATH ls "$target_path") ]]; then
    $MC_PATH rm "$target_path"
fi
$MC_PATH cp "$dump_path" "$target_path"
echo "Создан объект в S3 с именем $object_name"

# Удалить локальный файл дампа.
rm "$dump_path"
echo "Удален локальный файл $dump_path"
