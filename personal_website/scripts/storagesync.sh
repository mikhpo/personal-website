#!/bin/bash
#
# Создание бэкапа системного файлового хранилища при помощи утилиты rsync.

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
readonly source_dir="$STORAGE_ROOT/"
echo "Адрес файлового хранилища: $source_dir"

# Определение размера копируемого каталога.
source_size=$(du -sh "$source_dir" | cut -f 1 | tr -d ' ')
echo "Размер файлового хранилища: $source_size"

# Определить полный путь сохранения бэкапа.
readonly destination_dir="$BACKUP_ROOT/storage"
echo "Бэкап файлового хранилища будет сохранен по адресу $destination_dir"
mkdir -p "$destination_dir"

# Выполнить резервное копирование.
echo "Выполнение резервного копирования..."
rsync -r "$source_dir" "$destination_dir"

# Проверить размер резервной копии хранилища.
destination_size=$(du -sh "$destination_dir" | cut -f 1 | tr -d ' ')
echo "Размер резервной копии файлового хранилища: $destination_size"
