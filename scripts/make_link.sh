#!/bin/bash
#
# Создает символическую ссылку на зависимость Node.js - Bootstrap - в папке static.
# Адрес корневого каталога проекта определяется автоматически.

repository_root="$(dirname "$(dirname "$(readlink -fm "$0")")")"
project_name="personal_website"
cd $repository_root
echo "Создание символической ссылки на директорию node_modules"
ln -s ../node_modules $project_name/static/node_modules
