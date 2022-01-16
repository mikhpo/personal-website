#!/bin/bash
#
# Запуск веб-сервера в режиме разработки.

# Адрес корневого каталога проекта определяется автоматически.
project_root="$(dirname "$(dirname "$(readlink -fm "$0")")")"

# Выполнение административной команды Django.
$project_root/.venv/bin/python $project_root/manage.py runserver