#!/bin/bash
#
# Скрипт для первоначальной настройки сервера под systemd-развертывание:
# приложение под Gunicorn, обратный прокси nginx и сертификаты certbot
# в операционной системе хоста (DEPLOY_MODE=systemd). Выполняется один раз;
# повторный запуск безопасен. Для обновления приложения использовать
# scripts/deploy.sh. Рецепты развертывания - docs/deployment/application.md
# и docs/deployment/proxy.md.

# Выйти в случае ошибки.
set -e

# Определение рабочих файлов проекта.
project_root="$(dirname "$(dirname "$(dirname "$(readlink -f "$0")")")")"
readonly dotenv="$project_root/.env"
readonly systemd_template="$project_root/scripts/server/systemd/personal-website.service.template"
readonly nginx_template="$project_root/scripts/server/nginx/personal-website.conf.template"
readonly nginx_bootstrap_template="$project_root/scripts/server/nginx/acme-bootstrap.conf.template"
# Определение параметров установки.
readonly WEBSITE_NAME="personal-website"
readonly service_file="/etc/systemd/system/${WEBSITE_NAME}.service"
readonly sites_available="/etc/nginx/sites-available/$WEBSITE_NAME"
readonly sites_enabled="/etc/nginx/sites-enabled/$WEBSITE_NAME"
readonly certbot_webroot="/var/www/certbot"
cd "$project_root" || exit

readonly POSTGRES_VERSION=17
readonly NODE_VERSION=22

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
        echo "Файл с переменными окружения $dotenv не существует" >&2
        exit 1
    fi
}

#######################################
# Предупредить о несоответствии механизма развертывания:
# скрипты backup.sh и deploy.sh диспетчеризируют по DEPLOY_MODE.
#######################################
function check_deploy_mode() {
    if [ "${DEPLOY_MODE:-compose}" != "systemd" ]; then
        echo "Внимание: DEPLOY_MODE не равен systemd - скрипты backup.sh" >&2
        echo "и deploy.sh будут работать как для Docker Compose." >&2
    fi
}

#######################################
# Установить системные пакеты.
# rclone требуется для целей бэкапов вне S3 (локальные каталоги,
# облачные диски); mc - для S3-целей (установка отдельной функцией);
# gettext-base - утилита envsubst для рендеринга шаблонов конфигураций.
#######################################
function install_packages() {
    sudo apt-get update
    sudo apt-get upgrade -y
    sudo apt-get install -y \
        cron \
        curl \
        git \
        gnupg \
        ca-certificates \
        ufw \
        locales \
        gettext-base \
        python3 \
        python3-venv \
        pipx \
        "postgresql-client-${POSTGRES_VERSION}" \
        nginx \
        certbot \
        rclone
}

#######################################
# Выполнить настройку ufw (Uncomplicated Firewall).
# Разрешить трафик через порты SSH, HTTP и HTTPS. Порты PostgreSQL
# и объектного хранилища не открываются: сервер БД в этом варианте
# подключается через локальный интерфейс или управляется отдельно.
#######################################
function enable_ufw() {
    sudo ufw enable
    sudo ufw allow 22
    sudo ufw allow 80
    sudo ufw allow 443
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
# определяется в переменных окружения
# и совпадает с образом сборки фронтенда в Dockerfile.
#######################################
function install_node() {
    sudo mkdir -p /etc/apt/keyrings
    curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key |
        sudo gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg
    echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_${NODE_VERSION}.x nodistro main" |
        sudo tee /etc/apt/sources.list.d/nodesource.list >/dev/null
    sudo apt-get update
    sudo apt-get install -y nodejs
}

#######################################
# Установить клиент MinIO, если он еще не установлен.
# Требуется S3-целям бэкапов (префикс mc:).
#######################################
function install_minio() {
    if command -v mc >/dev/null 2>&1; then
        return
    fi
    local arch
    arch="$(dpkg --print-architecture)"
    curl -fsSL "https://dl.min.io/client/mc/release/linux-${arch}/mc" -o /tmp/mc
    sudo install -m 0755 /tmp/mc "${MC_PATH:-/usr/local/bin/mc}"
    rm -f /tmp/mc
}

#######################################
# Настроить системную локаль.
#######################################
function setup_locale() {
    sudo rm -rf /var/lib/apt/lists/*
    sudo localedef -i ru_RU -c -f UTF-8 -A /usr/share/locale/locale.alias ru_RU.UTF-8
}

#######################################
# Установить системную таймзону Europe/Moscow.
# Расписание cron-задач задается в локальном времени хоста
# (см. scripts/cronjobs.sh), поэтому таймзона должна быть
# зафиксирована до установки cron-задач.
#######################################
function setup_timezone() {
    sudo timedatectl set-timezone Europe/Moscow
}

#######################################
# Создать каталоги данных из .env, если они заданы абсолютными путями.
# Каталоги и их содержимое передаются сервис-пользователю: при переходе
# с контейнерного запуска внутри могут остаться файлы, созданные
# контейнером от root, - без этого старт systemd-сервиса завершается
# PermissionError на файлах журналов.
#######################################
function create_data_directories() {
    local user="${SUDO_USER:-$(id -un)}"
    local dir
    for dir in "${STORAGE_ROOT:-}" "${STATIC_ROOT:-}" "${BACKUP_ROOT:-}" "${LOGS_ROOT:-}" "${TEMP_ROOT:-}"; do
        if [ -n "$dir" ]; then
            sudo mkdir -p "$dir"
            sudo chown -R "$user" "$dir"
        fi
    done
}

#######################################
# Установить зависимости проекта и собрать фронтенд.
# Poetry создает виртуальное окружение в каталоге проекта (.venv).
#######################################
function install_project_dependencies() {
    echo "Установка зависимостей Node.js и сборка фронтенда..."
    npm install
    npm run build

    echo "Установка зависимостей Python..."
    poetry install
}

#######################################
# Скачать SSL-сертификат CA для Managed PostgreSQL.
# Идемпотентно: скрипт pgcert.sh самостоятельно читает .env
# и решает, нужна ли загрузка.
#######################################
function fetch_postgres_cert() {
    echo "Загрузка SSL-сертификата PostgreSQL (при необходимости)..."
    bash "$project_root/scripts/pgcert.sh"
}

#######################################
# Установить systemd-юнит приложения из шаблона
# (рецепт - docs/deployment/application.md).
#######################################
function install_systemd_unit() {
    local user="${SUDO_USER:-$(id -un)}"
    export WORK_DIR="$project_root"
    export SERVICE_USER="$user"
    envsubst "\$WORK_DIR \$SERVICE_USER" <"$systemd_template" | sudo tee "$service_file" >/dev/null
    sudo systemctl daemon-reload
    sudo systemctl enable personal-website.service
}

#######################################
# Установить временную конфигурацию nginx на период первичного
# выпуска сертификата (рецепт - docs/deployment/proxy.md).
#######################################
function install_nginx_bootstrap() {
    export DOMAIN_NAME="$DOMAIN_NAME"
    envsubst "\$DOMAIN_NAME" <"$nginx_bootstrap_template" | sudo tee "$sites_available" >/dev/null
    sudo ln -sfn "$sites_available" "$sites_enabled"
    sudo systemctl enable nginx
    sudo nginx -t
    sudo systemctl restart nginx
}

#######################################
# Выпустить сертификат Let's Encrypt при помощи certbot
# (метод webroot, без плагина nginx: конфигурация nginx
# принадлежит только администратору и certbot ее не меняет).
# Тестовые среды выпускают сертификат в ACME staging
# (CERTBOT_STAGING=True в .env или в окружении): staging не
# расходует лимиты продакшена, сертификат не является доверенным.
#######################################
function setup_certbot() {
    sudo mkdir -p "$certbot_webroot"

    # Продление сертификата сопровождается перезагрузкой nginx
    # (выполняется certbot'ом автоматически при каждом обновлении).
    sudo tee /etc/letsencrypt/renewal-hooks/deploy/nginx-reload.sh >/dev/null <<'EOF'
#!/bin/bash
systemctl reload nginx
EOF
    sudo chmod 755 /etc/letsencrypt/renewal-hooks/deploy/nginx-reload.sh

    local args=(
        certonly --webroot -w "$certbot_webroot"
        -d "$DOMAIN_NAME" -d "www.$DOMAIN_NAME"
        --email "$ACME_EMAIL" --agree-tos --no-eff-mail --noninteractive
    )
    case "$(echo "${CERTBOT_STAGING:-}" | tr '[:upper:]' '[:lower:]')" in
        true | 1 | yes | y) args+=(--staging) ;;
    esac
    sudo certbot "${args[@]}"

    # Расписание продления (поставляется пакетом certbot).
    sudo systemctl enable --now certbot.timer
    sudo certbot renew --dry-run
}

#######################################
# Установить полную конфигурацию сайта nginx
# (HTTPS, раздача медиа с диска
# и проксирование приложения).
# Каталог STORAGE_ROOT должен быть читаем пользователю nginx
# (www-data): файлы приложения создаются с правами 644
# и каталогами 755 по умолчанию.
#######################################
function install_nginx_site() {
    export DOMAIN_NAME="$DOMAIN_NAME"
    export DJANGO_PORT="${DJANGO_PORT:-8000}"
    export STORAGE_ROOT="${STORAGE_ROOT:-$project_root/storage}"
    envsubst "\$DOMAIN_NAME \$DJANGO_PORT \$STORAGE_ROOT" \
        <"$nginx_template" | sudo tee "$sites_available" >/dev/null
    sudo nginx -t
    sudo systemctl reload nginx
}

#######################################
# Запустить приложение и поставить скрипты
# бэкапа на расписание в cron.
#######################################
function start_services() {
    sudo systemctl restart personal-website.service
    bash "$project_root/scripts/cronjobs.sh"
}

#######################################
# Показать состояние сервисов, запущенных настройкой:
# приложение, nginx и timer продления сертификатов
# (аналог docker compose ps контейнерного развертывания).
#######################################
function show_services_status() {
    sudo systemctl status personal-website.service nginx.service certbot.timer --no-pager || true
}

#######################################
# Последовательный вызов основных функций скрипта.
#######################################
function main() {
    confirm_dotenv
    load_dotenv
    check_deploy_mode
    install_packages
    enable_ufw
    install_poetry
    install_node
    install_minio
    setup_locale
    setup_timezone
    create_data_directories
    install_project_dependencies
    fetch_postgres_cert
    install_systemd_unit
    install_nginx_bootstrap
    setup_certbot
    install_nginx_site
    start_services
    show_services_status
    echo
    echo "Настройка завершена."
}

main
