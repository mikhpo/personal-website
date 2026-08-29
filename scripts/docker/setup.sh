#!/bin/bash
#
# Скрипт для первоначальной настройки сервера под Docker-развертывание.
# Выполняется один раз на новом сервере: устанавливает системные пакеты,
# Docker, файрвол и запускает контейнеры. Повторный запуск безопасен.

# Выйти в случае ошибки.
set -e

#######################################
# Определить доступную команду Docker Compose.
# Приоритет отдается плагину V2 (`docker compose`),
# в случае его отсутствия используется V1 (`docker-compose`).
# Возвращает строку с командой через stdout.
#######################################
function detect_compose_cmd() {
    if docker compose version >/dev/null 2>&1; then
        echo "docker compose"
    elif command -v docker-compose >/dev/null 2>&1; then
        echo "docker-compose"
    else
        echo "Ошибка: Docker Compose не найден. Установите плагин docker-compose-plugin или Docker Compose V1." >&2
        exit 1
    fi
}

project_root="$(dirname "$(dirname "$(dirname "$(readlink -f "$0")")")")"
readonly dotenv="$project_root/.env"
cd "$project_root" || exit

#######################################
# Запросить подтверждение готовности
# файла с переменными окружения.
#######################################
function confirm_dotenv() {
    read -p "Файл .env уже заполнен? [y/n] " -n 1 -r
    echo
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
        set -a
        # shellcheck disable=SC1090
        . "$dotenv"
        set +a
        echo "Переменные окружения загружены из файла $dotenv"
    else
        echo "Файл с переменными окружения $dotenv не существует"
        exit 1
    fi
}

#######################################
# Установить системные пакеты.
# mc (MinIO Client) требуется для резервного копирования
# файлового хранилища по расписанию cron на хосте.
# rclone требуется для целей бэкапов вне S3 (локальные каталоги,
# облачные диски) при systemd-развертывании; в compose-режиме rclone и mc
# находятся в образе приложения. rclone устанавливается пакетом
# дистрибутива: версия стабильного Debian покрывает используемые операции
# (copy, sync, lsf, delete с фильтрами по возрасту), а обновления приходят
# вместе с системой; официальный установщик rclone.org дает более свежие
# версии ценой ручного сопровождения.
#######################################
function install_packages() {
    sudo apt-get update
    sudo apt-get upgrade -y
    local packages=(cron curl git gnupg ca-certificates ufw)
    if [ "$DEPLOY_MODE" = "systemd" ]; then
        packages+=(rclone)
    fi
    sudo apt-get install -y "${packages[@]}"

    # Установить MinIO Client, если еще не установлен.
    if ! command -v mc >/dev/null 2>&1; then
        local arch
        arch="$(dpkg --print-architecture)"
        curl -fsSL "https://dl.min.io/client/mc/release/linux-${arch}/mc" \
            -o /tmp/mc
        sudo install -m 0755 /tmp/mc /usr/local/bin/mc
        rm -f /tmp/mc
    fi
}

#######################################
# Выполнить настройку ufw (Uncomplicated Firewall).
# Разрешить трафик через следующие порты:
# - SSH
# - HTTP
# - HTTPS
#######################################
function enable_ufw() {
    sudo ufw enable
    sudo ufw allow 22
    sudo ufw allow 80
    sudo ufw allow 443
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
# Скачать SSL-сертификат PostgreSQL (идемпотентно).
#######################################
function load_postgres_cert() {
    bash "$project_root/scripts/pgcert.sh"
}

#######################################
# Создать каталоги хоста для bind-mounts Docker Compose.
#######################################
function create_docker_directories() {
    echo "Создание директорий для Docker volumes..."
    mkdir -p "$project_root/storage"
    mkdir -p "$project_root/static"
    mkdir -p "$project_root/backups"
    mkdir -p "$project_root/logs"
    mkdir -p "$project_root/temp"
    mkdir -p "$project_root/nginx/letsencrypt"
    mkdir -p "$project_root/nginx/acme-webroot"
    mkdir -p "${HOME}/.postgresql"
}

#######################################
# Выпустить сертификат Let's Encrypt для контейнерного nginx
# (профиль nginx): certbot standalone поднимает собственный HTTP-сервер
# на порту 80 до первого старта nginx, поэтому конфигурация nginx
# статична с самого начала. Тестовые среды выпускают сертификат
# в ACME staging (CERTBOT_STAGING=True в .env или окружении).
# Идемпотентно: при существующем сертификате выпуск пропускается.
#######################################
function issue_certificate() {
    case ",${COMPOSE_PROFILES:-}," in
        *,nginx,*) ;;
        *) return ;;
    esac
    local domain="${DOMAIN_NAME:?DOMAIN_NAME не задан в .env}"
    if [ -d "$project_root/nginx/letsencrypt/live/$domain" ]; then
        return
    fi
    local args=(
        certonly --standalone
        -d "$domain" -d "www.$domain"
        --email "${ACME_EMAIL:?ACME_EMAIL не задан в .env}"
        --agree-tos --no-eff-mail --noninteractive
    )
    case "$(echo "${CERTBOT_STAGING:-}" | tr '[:upper:]' '[:lower:]')" in
        true | 1 | yes | y) args+=(--staging) ;;
    esac
    local compose_cmd
    compose_cmd="$(detect_compose_cmd)"
    $compose_cmd run --rm -p 80:80 certbot "${args[@]}"
}

#######################################
# Установить задачи cron на хосте для резервного копирования.
#######################################
function add_cronjobs() {
    bash "$project_root/scripts/cronjobs.sh"
}

#######################################
# Запустить контейнеры при помощи Docker Compose,
# вытянув образ основного контейнера из репозитория.
#######################################
function compose_up() {
    COMPOSE_CMD="$(detect_compose_cmd)"
    readonly COMPOSE_CMD
    $COMPOSE_CMD pull
    $COMPOSE_CMD up -d
    $COMPOSE_CMD ps
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
    load_postgres_cert
    create_docker_directories
    issue_certificate
    add_cronjobs
    compose_up
}

main
