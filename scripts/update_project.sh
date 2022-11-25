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

repository_root="$(dirname "$(dirname "$(readlink -fm "$0")")")"
project_name="personal_website"
cd $repository_root
git pull
sh ./scripts/install_dependencies.sh
$repository_root/.venv/bin/python $repository_root/$project_name/manage.py migrate 
sudo systemctl restart gunicorn
echo "Gunicorn перезапущен"
sudo nginx -t
sudo systemctl restart nginx
echo "Nginx перезапущен"