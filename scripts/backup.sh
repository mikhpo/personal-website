#!/bin/bash
#
# Хостовый вход системы резервного копирования: запускает management-команды
# для бэкапирования и восстановления базы данных и файлового хранилища,
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

# Версия совпадает с закрепленной в Dockerfile и CI.
readonly UV_VERSION=0.13.6

# Синхронизировать окружение с uv.lock: интерпретатор .venv должен
# удовлетворять requires-python, uv скачает нужную версию Python сам.
function ensure_uv_environment() {
    if [ ! -x "$HOME/.local/bin/uv" ]; then
        echo "uv не найден, установка версии $UV_VERSION..."
        curl -LsSf "https://astral.sh/uv/$UV_VERSION/install.sh" | sh
    fi
    export PATH="$HOME/.local/bin:$PATH"
    uv sync --frozen --no-dev --directory "$project_root"
}

case "$mode" in
    compose)
        docker compose exec -T application /srv/website/.venv/bin/python backend/manage.py "$@"
        ;;
    systemd)
        ensure_uv_environment
        uv run --no-sync --directory "$project_root" python "$project_root/backend/manage.py" "$@"
        ;;
    *)
        echo "Ошибка: неизвестный механизм развертывания DEPLOY_MODE=\"$mode\"." >&2
        echo "Допустимые значения: compose, systemd." >&2
        exit 1
        ;;
esac
