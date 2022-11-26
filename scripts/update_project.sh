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

project_name="personal_website"
repository_root="$(dirname "$(dirname "$(readlink -fm "$0")")")"
python="$project_root/.venv/bin/python"
cd $repository_root
git fetch origin
git pull
bash ./scripts/install_dependencies.sh
$python $repository_root/$project_name/manage.py migrate 
bash ./scripts/add_cron_jobs.sh
bash ./scripts/restart_services.sh