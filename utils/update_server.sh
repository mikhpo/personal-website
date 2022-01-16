#!/bin/bash
#
# Обновление проекта из Git и перезапуск сервера.

# Адрес корневого каталога проекта определяется автоматически.
project_root="$(dirname "$(dirname "$(readlink -fm "$0")")")"

# Выполнение bash команд:
# 1. Вытягивание изменений из Git.
# 2. Перезапуск Gunicorn.
# 3. Перезапуск Nginx. 
cd $project_root && 
    git pull && 
    sudo systemctl restart gunicorn && 
    sudo systemctl daemon-reload && 
    sudo systemctl restart gunicorn.socket gunicorn.service && 
    sudo nginx -t && 
    sudo systemctl restart nginx