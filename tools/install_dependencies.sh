#!/bin/bash
#
# Установка зависимостей Python, Node.js и статических файлов.

project_root="$(dirname "$(dirname "$(readlink -fm "$0")")")" # определение адреса корневого каталога проекта
cd $project_root # изменение текущей директории на корневую директорию проекта
echo "Установка зависимостей Python"
poetry install # установка зависимостей Python
cd static
echo "Установка зависимостей Node.js"
npm install # установка зависимостей Node.js
cd $project_root
echo "Сбор статических файлов"
poetry run python manage.py collectstatic --noinput # сбор статических файлов без запроса подтверждения
