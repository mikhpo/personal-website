#!/bin/bash
#
# Скрипт для генерации диаграмм моделей проекта и приложений в отдельности.
# Для успешного выполнения скрипта должны быть выполнены следующие условия:
# 1. В системе должен быть установлен пакет Graphviz.
# 2. Для управления зависимостями проекта используется Poetry.
# 2. В виртуальном окружении должна быть установлена библиотека django-extensions.

# Определить корневой путь репозитория.
project_root="$(dirname "$(dirname "$(readlink -f "$0")")")"

# Папка для экспорта диаграмм.
output_dir="$project_root"/docs/images

# Создать папку, если она не существует.
mkdir -p "$output_dir"

# Экспортировать диаграмму всех моделей проекта, включая используемые модели из модуля django.contrib.
output_path="$output_dir"/project_models.png
poetry run python personal_website/manage.py graph_models -a -g -o "$output_path"
echo "Экспортирована диаграмма всех моделей проекта по адресу $output_path"

# Приложения прокта, в которых определены дополнительные модели.
declare -a apps=("blog" "gallery")

# Экспортировать диаграмму моделей из всех приложений проекта вместе.
output_path="$output_dir"/apps_models.png
poetry run python personal_website/manage.py graph_models "${apps[@]}" -g -o "$output_path"
echo "Экспортирована диаграмма моделей приложений ${apps[*]} по адресу $output_path"

# Экспортировать диаграмму моделей каждого приложения в отдельности.
for app in "${apps[@]}"; do
    output_path="$output_dir"/"${app}"_models.png
    poetry run python personal_website/manage.py graph_models "$app" -o "$output_path"
    echo "Экспортирована диаграмма моделей приложения $app по адресу $output_path"
done
