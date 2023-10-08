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
project_root="$(dirname "$(dirname "$(readlink -fm "$0")")")"
project_name="personal_website"
python="$project_root/.venv/bin/python"
script="$project_root/$project_name/manage.py"
cd $project_root
git fetch origin
git pull
bash $project_root/tools/install_dependencies.sh
$python $script migrate 
bash $project_root/tools/add_cron_jobs.sh
bash $project_root/tools/restart_services.sh
