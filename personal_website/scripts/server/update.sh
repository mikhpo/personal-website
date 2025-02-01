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
# Актуально для развертывания серевисов в системе хоста.

project_root="$(dirname "$(dirname "$(dirname "$(dirname "$(readlink -f "$0")")")")")"
cd "$project_root" || exit

readonly PROJECT_NAME="personal_website"
readonly dotenv="$project_root/.env"
readonly python="$project_root/.venv/bin/python"
readonly manage="$project_root/$PROJECT_NAME/manage.py"
readonly config_dir="$project_root/personal_website/config"
readonly gunicorn_dir="$config_dir/gunicorn"
readonly gunicorn_socket="$gunicorn_dir/gunicorn.socket"
readonly gunicorn_service="$gunicorn_dir/gunicorn.service"
readonly DESTINATION_DIR="/etc/systemd/system/"

cd "$project_root" || exit

eval export "$(cat "$dotenv")"

git fetch origin
git checkout main
git pull
npm install
poetry install

$python "$manage" collectstatic --noinput
$python "$manage" migrate

sudo cp -f "$gunicorn_socket" $DESTINATION_DIR
envsubst < "$gunicorn_service" > "$DESTINATION_DIR"/gunicorn.service

bash "$project_root"/personal_website/scripts/server/restart.sh -f
bash "$project_root"/personal_website/scripts/cronjobs.sh
