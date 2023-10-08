#!/bin/bash
#
# Установка зависимостей Python, Node.js и статических файлов.

repository_root="$(dirname "$(dirname "$(readlink -fm "$0")")")"
project_name="personal_website"
cd $repository_root
echo "Установка зависимостей Python"
poetry install
echo "Установка зависимостей Node.js"
npm install
echo "Сбор статических файлов"
poetry run python $project_name/manage.py collectstatic --noinput
