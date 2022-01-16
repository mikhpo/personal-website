#!/bin/bash
#
# Запуск планировщика скриптов. 

# Адрес корневого каталога проекта определяется автоматически.
project_root="$(dirname "$(dirname "$(readlink -fm "$0")")")"

# Выполнение административной команды Django.
$project_root/.venv/bin/python $project_root/manage.py run_scheduler