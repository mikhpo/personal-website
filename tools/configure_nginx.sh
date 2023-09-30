#!/bin/bash
#
# Скрипт для первоначальной настройки Nginx.
project_root="$(dirname "$(dirname "$(readlink -f "$0")")")"
website_name="personal-website"
nginx_dir="$project_root/nginx"
nginx_conf="nginx.conf"
sites_available="/etc/nginx/sites-available"
sites_enabled="/etc/nginx/sites-enabled"

available_conf="$sites_available/$website_name"
if [ -f $available_conf ]; then
    sudo rm $available_conf
fi
sudo cp "$nginx_dir/$nginx_conf" $sites_available
sudo mv "$sites_available/$nginx_conf" $available_conf

enabled_conf="$sites_enabled/$website_name"
if [ -L $enabled_conf ]; then
    sudo rm $enabled_conf
fi
sudo ln -s $available_conf /etc/nginx/sites-enabled

sudo nginx -t
sudo systemctl restart nginx
sudo ufw allow 'Nginx Full'