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
readonly python="$project_root/.venv/bin/python"
readonly manage="$project_root/$PROJECT_NAME/manage.py"
readonly config_dir="$project_root/personal_website/config"
readonly gunicorn_dir="$config_dir/gunicorn"
readonly gunicorn_socket="$gunicorn_dir/gunicorn.socket"
readonly gunicorn_service="$gunicorn_dir/gunicorn.service"
readonly DESTINATION_DIR="/etc/systemd/system/"

cd "$project_root" || exit

# Вытянуть изменения из удаленного репозитория.
git fetch origin
git checkout main
git pull

# Обновить зависимости.
npm install
poetry install

# Собрать статические файлы.
$python "$manage" collectstatic --noinput

# Выполнить миграции базы данных.
$python "$manage" migrate

# Обновить конфигурационные файлы Gunicorn.
sudo cp -f "$gunicorn_socket" $DESTINATION_DIR
export WORK_DIR="$project_root"
envsubst < "$gunicorn_service" > "$DESTINATION_DIR"/gunicorn.service
systemctl daemon-reload

# Перезапустить сервисы.
bash "$project_root"/personal_website/scripts/server/restart.sh -f

# Обновить задачи в cron.
bash "$project_root"/personal_website/scripts/cronjobs.sh
