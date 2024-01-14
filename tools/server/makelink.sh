#!/bin/bash
#
# Создает символическую ссылку на node_modules в папке static.
# Адрес корневого каталога проекта определяется автоматически.

repository_root="$(dirname "$(dirname "$(readlink -f "$0")")")"
readonly PROJECT_NAME="personal_website"
readonly source_path=$repository_root/$PROJECT_NAME/static/node_modules
readonly destination_path=$repository_root/node_modules

echo "Создание символической ссылки на директорию node_modules"
echo "Адрес символической ссылки: $source_path"
echo "Адрес пути назначения символической ссылки: $destination_path"
cd "$repository_root" || exit
ln -s "$destination_path" "$source_path"
