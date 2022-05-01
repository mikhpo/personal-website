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
cd $project_root
git pull
sh ./tools/install_dependencies.sh
$project_root/.venv/bin/python $project_root/manage.py migrate 
sudo systemctl restart gunicorn
echo "Gunicorn перезапущен"
sudo nginx -t
sudo systemctl restart nginx
echo "Nginx перезапущен"