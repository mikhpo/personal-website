#!/bin/bash
#
# Хостовый вход системы резервного копирования: запускает management-команды
# приложения backend/backup/ (backup, backup_db, backup_media, restore_db,
# restore_media) в контексте механизма развертывания. Читает .env и
# диспетчеризует по DEPLOY_MODE: compose - docker compose exec -T application,
# systemd - интерпретатор виртуального окружения на хосте.

# Выйти в случае ошибки.
set -e

# Прочитать переменные окружения из файла .env.
project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
readonly dotenv="${DOTENV_PATH:-$project_root/.env}"
if [ -f "$dotenv" ]; then
    set -a
    . "$dotenv"
    set +a
    echo "Переменные окружения загружены из файла $dotenv"
else
    echo "Файл с переменными окружения $dotenv не существует" >&2
    exit 1
fi

readonly mode="${DEPLOY_MODE:-compose}"
case "$mode" in
    compose)
        docker compose exec -T application /srv/website/.venv/bin/python backend/manage.py "$@"
        ;;
    systemd)
        "$project_root/.venv/bin/python" "$project_root/backend/manage.py" "$@"
        ;;
    *)
        echo "Ошибка: неизвестный механизм развертывания DEPLOY_MODE=\"$mode\"." >&2
        echo "Допустимые значения: compose, systemd." >&2
        exit 1
        ;;
esac
