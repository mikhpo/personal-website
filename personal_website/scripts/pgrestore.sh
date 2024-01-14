#!/bin/bash
#
# Скрипт для восстановления базы данных PostgreSQL из дампа при помощи утилиты pg_restore.

# Выйти в случае ошибки.
set -e

echo "Восстановление базы данных PostgreSQL из дампа"

# Предупредить пользователя о рисках и запросить подтверждение.
echo "Внимание! Выполнение данного скрипта может привести к потере данных!"
read -rp "Вы уверены, что желаете продолжить выполнение скрипта? [y/n] "
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Выполнение скрипта было отменено"
    exit
fi

# Получить адрес дампа, который может быть передан в качестве
# аргумента командной строки или введен в ходе выполнения скрипта.
if [ -z "$1" ]; then
    read -rp "Арес дампа: " dump_path
else
    dump_path="$1"
fi

# Проверить существование и размер указанного файла.
if [ -f "$dump_path" ]; then
    filesize=$(du -h "$dump_path" | cut -f 1 | tr -d ' ')
    echo "Размер дампа: $filesize"
else
    echo "Файл по адресу $dump_path не существует"
    exit
fi

# Прочитать переменные окружения из файла .env в корневом каталоге проекта.
project_root="$(dirname "$(dirname "$(dirname "$(readlink -f "$0")")")")"
readonly dotenv="$project_root/.env"
if [ -f "$dotenv" ]; then
    eval export "$(cat "$dotenv")"
    echo "Переменные окружения загружены из файла $dotenv"
fi

# Переменные окружения подставляются в команду для утилиты pg_restore.
echo "Выполнение программы pg_restore"
export PGPASSWORD=$POSTGRES_PASSWORD
pg_restore \
    -Fc \
    --single-transaction \
    --no-owner \
    --clean \
    -h "$POSTGRES_HOST" \
    -U "$POSTGRES_USER" \
    -p "$POSTGRES_PORT" \
    -d "$POSTGRES_NAME" \
    "$dump_path"

echo "База данных PostgreSQL восстановлена из дампа"
