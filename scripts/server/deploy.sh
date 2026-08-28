#!/bin/bash
#
# Деплой обновления приложения при systemd-развертывании (DEPLOY_MODE=systemd).
# Выполняется на сервере (в том числе из CI/CD через scripts/deploy.sh):
# 1. Вытягивание изменений из Git.
# 2. Обновление зависимостей и сборка фронтенда.
# 3. Переустановка systemd-юнита и конфигурации сайта nginx
#    из шаблонов репозитория.
# 4. Перезапуск приложения и nginx.
# Миграции и collectstatic выполняются юнитом при старте (ExecStartPre).

# Выйти в случае ошибки.
set -e

# Определение рабочих файлов проекта.
project_root="$(dirname "$(dirname "$(dirname "$(readlink -f "$0")")")")"
readonly dotenv="$project_root/.env"
readonly systemd_template="$project_root/scripts/server/systemd/personal-website.service.template"
readonly nginx_template="$project_root/scripts/server/nginx/personal-website.conf.template"
readonly service_file="/etc/systemd/system/personal-website.service"
readonly sites_available="/etc/nginx/sites-available/personal-website"
cd "$project_root" || exit

#######################################
# Загрузить переменные окружения из .env файла
# или выйти, если файл не существует.
#######################################
function load_dotenv() {
    if [ -f "$dotenv" ]; then
        set -a
        # shellcheck disable=SC1090
        . "$dotenv"
        set +a
        echo "Переменные окружения загружены из файла $dotenv"
    else
        echo "Файл с переменными окружения $dotenv не существует" >&2
        exit 1
    fi
}

#######################################
# Обновить файлы проекта из основной ветки репозитория.
#######################################
function pull_repository() {
    git fetch origin
    git checkout main
    git pull
}

#######################################
# Обновить зависимости и собрать фронтенд.
# .env загружается до сборки: WEBPACK_PUBLIC_PATH определяет
# адрес бандлов в webpack-stats.json.
#######################################
function build_project() {
    npm install
    npm run build
    poetry install
}

#######################################
# Переустановить systemd-юнит и конфигурацию сайта nginx
# из шаблонов репозитория (изменения шаблонов вступают
# в силу вместе с деплоем).
#######################################
function install_configs() {
    local user="${SUDO_USER:-$(id -un)}"
    export WORK_DIR="$project_root"
    export SERVICE_USER="$user"
    export DOMAIN_NAME="$DOMAIN_NAME"
    export DJANGO_PORT="${DJANGO_PORT:-8000}"
    export STORAGE_ROOT="${STORAGE_ROOT:-$project_root/storage}"
    envsubst "\$WORK_DIR \$SERVICE_USER" <"$systemd_template" | sudo tee "$service_file" >/dev/null
    envsubst "\$DOMAIN_NAME \$DJANGO_PORT \$STORAGE_ROOT" <"$nginx_template" | sudo tee "$sites_available" >/dev/null
    sudo systemctl daemon-reload
}

#######################################
# Последовательный вызов основных функций скрипта.
#######################################
function main() {
    load_dotenv
    pull_repository
    build_project
    install_configs
    bash "$project_root/scripts/server/restart.sh" -f
    bash "$project_root/scripts/cronjobs.sh"
}

main
