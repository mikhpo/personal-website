#!/bin/bash
#
# Обновление проекта из Git и перезапуск сервера.
# Выполнение bash команд:
# 1. Вытягивание изменений из Git.
# 2. Обновление зависимостей.
# 3. Миграция базы данных.
# 4. Перезапуск Gunicorn.
# 5. Перезапуск Nginx. 
# Адрес корневого каталога проекта определяется автоматически.

readonly project_root="$(dirname "$(dirname "$(readlink -fm "$0")")")"
readonly PROJECT_NAME="personal_website"
readonly python="$project_root/.venv/bin/python"
readonly manage="$project_root/$PROJECT_NAME/manage.py"
readonly config_dir="$project_root/config"
readonly gunicorn_socket="$config_dir/gunicorn.socket"
readonly gunicorn_service="$config_dir/gunicorn.service"
readonly DESTINATION_DIR="/etc/systemd/system/"

cd $project_root

git fetch origin
git pull
npm install
poetry install

$python $manage collectstatic --noinput
$python $manage migrate

sudo cp -f $gunicorn_socket $gunicorn_service $DESTINATION_DIR

bash $project_root/tools/restart.sh -f
bash $project_root/tools/cronjobs.sh