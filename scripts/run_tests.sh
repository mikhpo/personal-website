#!/bin/bash
#
# Запуск тестов проекта.
# Адреса исполняемых файлов определяются автоматически.

repository_root="$(dirname "$(dirname "$(readlink -f "$0")")")"
website_root="$repository_root/personal_website"
python=$repository_root/.venv/bin/python
$python $website_root/manage.py test main