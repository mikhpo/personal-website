#!/bin/bash
#
# Выполнение миграций, установка зависимостей и запуск сервера.

# Остановиться в случае ошибки.
set -e

# Адрес хоста и номер порта сервера определяются из аргументов командной строки.
readonly HOST="$1"
readonly PORT="$2"

# Адрес корневого каталога проекта определяется по адресу скрипта.
readonly website_dir="$(dirname "$(readlink -f "$0")")"
readonly root_dir="$(dirname $website_dir)"
readonly manage="$website_dir/manage.py"
readonly python="$root_dir/.venv/bin/python"

# Собрать статические файлы, выполнить миграции и запустить сервер.
$python $manage migrate
$python $manage collectstatic --noinput
$python $manage runserver $HOST:$PORT