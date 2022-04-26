#!/bin/bash
#
# Обновление проекта из Git и перезапуск сервера.
# Выполнение bash команд:
# 1. Вытягивание изменений из Git.
# 2. Обновление зависимостей.
# 3. Перезапуск Gunicorn.
# 4. Перезапуск Nginx. 
# Адрес корневого каталога проекта определяется автоматически.

project_root="$(dirname "$(dirname "$(readlink -fm "$0")")")"
cd $project_root
git pull
sh ./tools/install_dependencies.sh 
sudo systemctl restart gunicorn
echo "Gunicorn перезапущен"
sudo nginx -t
sudo systemctl restart nginx
echo "Nginx перезапущен"