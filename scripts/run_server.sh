#!/bin/bash
#
# Запуск веб-сервера в режиме разработки.
# Адрес корневого каталога проекта определяется автоматически.

repository_root="$(dirname "$(dirname "$(readlink -fm "$0")")")"
project_name="personal_website"
$repository_root/.venv/bin/python $repository_root/$project_name/manage.py runserver