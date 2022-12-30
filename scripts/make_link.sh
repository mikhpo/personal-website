#!/bin/bash
#
# Создает символическую ссылку на зависимость Node.js - Bootstrap - в папке static.
# Адрес корневого каталога проекта определяется автоматически.

repository_root="$(dirname "$(dirname "$(readlink -f "$0")")")"
project_name="personal_website"
cd $repository_root
source_path=$repository_root/$project_name/static/node_modules
destination_path=$repository_root/node_modules
echo "Создание символической ссылки на директорию node_modules"
echo "Адрес символической ссылки: $source_path"
echo "Адрес пути назначения символической ссылки: $destination_path"
ln -s $destination_path $source_path