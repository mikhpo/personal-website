#!/bin/bash
#
# Запуск веб-сервера в режиме разработки.
# Адрес корневого каталога проекта определяется автоматически.

repository_root="$(dirname "$(dirname "$(readlink -f "$0")")")"
website_root="$repository_root/personal_website"
python=$repository_root/.venv/bin/python
$python $website_root/manage.py runserver