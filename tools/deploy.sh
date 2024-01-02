#!/bin/bash
#
# Скрипт для первоначального развертывания через Gunicorn и Nginx.

# Остановиться в случае ошибки.
set -e

# Определение рабочих каталогов проекта.
project_root="$(dirname "$(dirname "$(readlink -f "$0")")")"
readonly config_dir="$project_root/config"

#######################################
# Первоначальная установка Gunicorn.
# Активирует сокет и создает службу.
#######################################
function setup_gunicorn() {
    
    readonly socket="$config_dir/gunicorn.socket"
    readonly service="$config_dir/gunicorn.service"
    readonly DESTINATION_DIR="/etc/systemd/system/"

    sudo cp "$socket" "$service" $DESTINATION_DIR
    sudo systemctl start gunicorn.socket
    sudo systemctl enable gunicorn.socket

}

#######################################
# Первоначальная установка Nginx. Устанавливает Nginx,
# добавляет конфигурационные файлы Nginx, перезапускает Nginx и 
# разрешает доступ через Uncomplicated Firewall.
#######################################
function setup_nginx() {

    readonly WEBSITE_NAME="personal-website"
    readonly NGINX_CONF="nginx.conf"
    readonly SITES_AVAILABLE="/etc/nginx/sites-available"
    readonly SITES_ENABLED="/etc/nginx/sites-enabled"
    readonly available_conf="$SITES_AVAILABLE/$WEBSITE_NAME"
    readonly enabled_conf="$SITES_ENABLED/$WEBSITE_NAME"

    sudo apt-get update
    sudo apt-get install nginx ufw -y
    sudo systemctl enable nginx
    sudo ufw enable
    sudo ufw status

    if [ -f $available_conf ]; then
        sudo rm $available_conf
    fi
    sudo cp "$config_dir/$NGINX_CONF" $SITES_AVAILABLE
    sudo mv "$SITES_AVAILABLE/$NGINX_CONF" $available_conf

    if [ -L $enabled_conf ]; then
        sudo rm $enabled_conf
    fi
    sudo ln -s $available_conf /etc/nginx/sites-enabled

    sudo nginx -t
    sudo systemctl restart nginx
    sudo ufw allow 'Nginx Full'
    sudo ufw status

}

#######################################
# Последовательный вызов основных функций скрипта.
#######################################
function main() {
    setup_gunicorn
    setup_nginx
}

main