#!/bin/bash
#
# Скрипт для первоначальной настройки Gunicorn.
project_root="$(dirname "$(dirname "$(readlink -f "$0")")")"
gunicorn_dir="$project_root/gunicorn"
socket="$gunicorn_dir/gunicorn.socket"
service="$gunicorn_dir/gunicorn.service"
destination_dir="/etc/systemd/system/"
sudo cp $socket $service $destination_dir
sudo systemctl start gunicorn.socket
sudo systemctl enable gunicorn.socket