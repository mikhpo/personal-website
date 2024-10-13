#!/bin/bash
#
# Скрипт для первоначального развертывания через Docker.

# Выйти в случае ошибки.
set -e

# Определение рабочих файлов проекта.
project_root="$(dirname "$(dirname "$(dirname "$(dirname "$(readlink -f "$0")")")")")"
readonly dotenv="$project_root/.env"
cd "$project_root" || exit

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
        ufw \
        ca-certificates \
        curl \
        gnupg
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
# Установить Docker в соответствии с рекомендуемым порядком действий
# на странице документации: https://docs.docker.com/engine/install/debian/
#######################################
function install_docker() {
    # Добавить официальный GPG-ключ Docker.
    sudo install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    sudo chmod a+r /etc/apt/keyrings/docker.gpg

    # Добавить репозиторий Docker в источники Apt.
    # shellcheck disable=SC1091
    echo \
        "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian \
        $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | sudo tee /etc/apt/sources.list.d/docker.list >/dev/null
    sudo apt-get update

    # Установить пакеты Docker.
    sudo apt-get install -y \
        docker-ce \
        docker-ce-cli \
        containerd.io \
        docker-buildx-plugin \
        docker-compose-plugin

    # Установить авто-запуск службы Docker.
    sudo systemctl enable docker.service
    sudo systemctl enable containerd.service

    sudo chmod 666 /var/run/docker.sock
}

#######################################
# Авторизоваться в Docker с использованием
# логина и пароля из переменных окружения.
# Адрес хоста может быть пустым - в таком
# случае будет подключение к Docker Hub.
#######################################
function login_docker() {
    docker login \
        --username="$DOCKER_USERNAME" \
        --password="$DOCKER_PASSWORD" \
        "$DOCKER_REGISTRY"
}

#######################################
# Запустить контейнеры при помощи Docker Compose,
# вытянув образ основного контейнера из репозитория
# и выполнив сборку остальных контейнеров.
#######################################
function compose_up() {
    docker compose pull
    docker compose up -d
    docker compose ps
}

#######################################
# Последовательный вызов основных функций скрипта.
#######################################
function main() {
    confirm_dotenv
    load_dotenv
    install_packages
    enable_ufw
    install_docker
    login_docker
    compose_up
}

main
