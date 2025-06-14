#!/bin/bash
#
# Скрипт для первоначального развертывания через Gunicorn и Nginx.
# Используется для сценария развертывания сервисов на сервере.

# Выйти в случае ошибки.
set -e

# Определение рабочих файлов проекта.
project_root="$(dirname "$(dirname "$(dirname "$(dirname "$(readlink -f "$0")")")")")"
readonly config_dir="$project_root/personal_website/config"
readonly dotenv="$project_root/.env"
cd "$project_root" || exit

# Определение параметров установки.
readonly WEBSITE_NAME="personal-website"
readonly POSTGRES_VERSION=15
readonly NODE_VERSION=20

#######################################
# Запросить подтверждение готовности
# файла с переменными окружения.
#######################################
function confirm_dotenv() {
    read -p "Файл .env уже заполнен? [y/n] " -n 1 -r
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit
    fi
}

#######################################
# Загрузить переменные окружения из .env файла
# или выйти, если файл не существует.
#######################################
function load_dotenv() {
    if [ -f "$dotenv" ]; then
        eval export "$(cat "$dotenv")"
        echo "Переменные окружения загружены из файла $dotenv"
    else
        echo "Файл с переменными окружения $dotenv не существует"
        exit
    fi
}

#######################################
# Установить системные пакеты.
#######################################
function install_packages() {
    sudo apt-get update
    sudo apt-get upgrade -y
    sudo apt-get install -y \
        cron \
        curl \
        gnupg \
        locales \
        ca-certificates \
        "postgresql-client-${POSTGRES_VERSION}" \
        rsync \
        python3 \
        python3-pip \
        pipx \
        wkhtmltopdf \
        nginx
}

#######################################
# Выполнить настройку ufw (Uncomplicated Firewall).
# Разрешить трафик через следующие порты:
# - SSH
# - HTTP
# - HTTPS
# - rsync
# - PostgreSQL
# - MinIO
#######################################
function enable_ufw() {
    sudo apt-get install -y ufw
    sudo ufw enable
    sudo ufw allow 22
    sudo ufw allow 80
    sudo ufw allow 443
    sudo ufw allow 873
    sudo ufw allow 5432
    sudo ufw allow 9000
    sudo ufw allow 9001
    sudo ufw status
}

#######################################
# Установить Poetry через pipx.
#######################################
function install_poetry() {
    pipx ensurepath
    pipx install poetry
}

#######################################
# Установить Node.js. Версия Node.js
# определяется в переменных окружения.
#######################################
function install_node() {
    sudo mkdir -p /etc/apt/keyrings
    curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg
    echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_$NODE_VERSION.x nodistro main" | tee /etc/apt/sources.list.d/nodesource.list
    sudo apt-get update
    sudo apt-get install -y nodejs
}

#######################################
# Установить клиент MinIO.
# Клиент скачивается с официального сайта MinIO.
# После установки путь добавляетя в переменную PATH.
#######################################
function install_minio() {
    wget https://dl.min.io/client/mc/release/linux-amd64/mc && \
    sudo chmod +x mc && \
    sudo mv mc "$MC_PATH"
}

#######################################
# Настроить системную локаль.
#######################################
function setup_locale() {
    sudo rm -rf /var/lib/apt/lists/*
    sudo localedef -i ru_RU -c -f UTF-8 -A /usr/share/locale/locale.alias ru_RU.UTF-8
}

#######################################
# Первоначальная установка Gunicorn.
# Активирует сокет и создает службу.
#######################################
function setup_gunicorn() {
    readonly gunicorn_dir="$config_dir/gunicorn"
    readonly socket="$gunicorn_dir/gunicorn.socket"
    readonly service="$gunicorn_dir/gunicorn.service"
    readonly DESTINATION_DIR="/etc/systemd/system/"

    # Скопировать файл сокета Gunicorn.
    sudo cp "$socket" $DESTINATION_DIR

    # Заполнить файл сервиса Gunicorn из шаблона переменными окружения.
    export WORK_DIR="$project_root"
    envsubst < "$service" > "$DESTINATION_DIR"/gunicorn.service

    # Включить Gunicorn.
    sudo systemctl start gunicorn.socket
    sudo systemctl enable gunicorn.socket
}

#######################################
# Первоначальная установка Nginx. Устанавливает Nginx,
# добавляет конфигурационные файлы Nginx, перезапускает Nginx и
# разрешает доступ через Uncomplicated Firewall.
#######################################
function setup_nginx() {
    readonly NGINX_CONF_TEMPLATE="nginx/default.conf.template"
    readonly SITES_AVAILABLE="/etc/nginx/sites-available"
    readonly SITES_ENABLED="/etc/nginx/sites-enabled"
    readonly available_conf="$SITES_AVAILABLE/$WEBSITE_NAME"
    readonly enabled_conf="$SITES_ENABLED/$WEBSITE_NAME"

    sudo systemctl enable nginx

    # Если конфигурационный файл уже существует, то удалить его.
    if [ -f $available_conf ]; then
        sudo rm $available_conf
    fi

    # Заполнить шаблон конфигурационного файла переменными окружения.
    export NGINX_PORT=$NGINX_PORT
    export DOMAIN_NAME=$DOMAIN_NAME
    export STORAGE_ROOT=$STORAGE_ROOT
    export STATIC_ROOT=$STATIC_ROOT
    export DJANGO_PORT=$DJANGO_PORT
    envsubst < "$config_dir/$NGINX_CONF_TEMPLATE" > $available_conf

    # Удалить ссылку на конфигурационный файл, если она уже создана.
    if [ -L $enabled_conf ]; then
        sudo rm $enabled_conf
    fi

    # Создать ссылку на конфигурацию, чтобы начать ее использование.
    sudo ln -s $available_conf /etc/nginx/sites-enabled

    sudo nginx -t
    sudo systemctl restart nginx
}

#######################################
# Установка сертификата Let's Encrypt при помощи Certbot.
#######################################
function setup_certbot() {
    sudo apt-get install -y \
        certbot \
        python3-certbot-nginx

    # Получить SSL сертификат.
    sudo certbot \
        --nginx \
        --email "$EMAIL_HOST_USER" \
        --agree-tos \
        --no-eff-email \
        --noninteractive \
        -d "$DOMAIN_NAME" \
        -d www."$DOMAIN_NAME"

    # Показать расписание обновления сертификата.
    sudo systemctl status certbot.timer

    # Проверить процесс обновления сертификата.
    sudo certbot renew --dry-run
}

#######################################
# Поставить скрипты на расписание в cron.
#######################################
function add_cronjobs() {
    bash "$project_root"/personal_website/scripts/cronjobs.sh
}

#######################################
# Последовательный вызов основных функций скрипта.
#######################################
function main() {
    confirm_dotenv
    load_dotenv
    install_packages
    enable_ufw
    install_poetry
    install_node
    install_minio
    setup_gunicorn
    setup_nginx
    setup_certbot
    add_cronjobs
}

main
