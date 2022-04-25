#!/bin/bash
#
# Установка зависимостей Python, Node.js и статических файлов.

project_root="$(dirname "$(dirname "$(readlink -fm "$0")")")"
cd $project_root
echo "Установка зависимостей Python"
poetry install
cd static
echo "Установка зависимостей Node.js"
npm install
cd $project_root
echo "Сбор статических файлов"
poetry run python manage.py collectstatic --noinput
