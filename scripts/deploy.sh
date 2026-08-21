#!/bin/bash
#
# Общий диспетчер деплоя: единый вход для CI/CD и ручного обновления.
# Читает .env, выполняет резервное копирование и вызывает скрипт деплоя
# механизма, заданного переменной DEPLOY_MODE. Рабочую копию обновляет
# вызываемый скрипт, поэтому свежий диспетчер вступает в силу со следующего
# запуска.

# Выйти в случае ошибки.
set -e

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
    echo "Файл с переменными окружения $dotenv не существует" >&2
    exit 1
fi

# Отсутствующее или пустое значение DEPLOY_MODE - текущий механизм compose:
# развертывание продолжает работать без правки .env.
readonly mode="${DEPLOY_MODE:-compose}"
case "$mode" in
    compose|systemd) ;;
    *)
        echo "Ошибка: неизвестный механизм развертывания DEPLOY_MODE=\"$mode\"." >&2
        echo "Допустимые значения: compose, systemd." >&2
        exit 1
        ;;
esac

# Резервное копирование медиафайлов до изменений развертывания.
bash "$project_root/scripts/s3backup.sh"

case "$mode" in
    compose)
        bash "$project_root/scripts/docker/deploy.sh"
        ;;
    systemd)
        bash "$project_root/scripts/server/deploy.sh"
        ;;
esac
