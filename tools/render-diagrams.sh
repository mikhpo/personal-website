#!/bin/bash
#
# Скрипт для рендера архитектурных C4-диаграмм из PlantUML исходников.
# Для успешного выполнения скрипта должны быть выполнены следующие условия:
# 1. В системе должна быть установлена утилита PlantUML.
# 2. Для запуска PlantUML требуется среда выполнения Java (JRE).
# 3. Для отрисовки диаграмм требуется пакет Graphviz.
#
# Установка зависимостей на macOS:
#   brew install plantuml
# (формула plantuml автоматически установит openjdk и использует graphviz).

# Определить корневой путь репозитория.
project_root="$(cd "$(dirname "$0")/.." && pwd)"

# Папка с PlantUML исходниками.
src_dir="$project_root"/docs/diagrams/src

# Папка для экспорта диаграмм.
output_root="$project_root"/docs/diagrams/out

# Экспортировать каждую диаграмму из отдельного файла .puml.
shopt -s nullglob
for puml in "$src_dir"/*.puml; do
    # Имя диаграммы без расширения.
    name="$(basename "$puml" .puml)"

    # PlantUML создаёт файл с тем же именем, что и исходник.
    # Ключ -o задаёт папку вывода относительно каталога исходника,
    # поэтому команда запускается из каталога src.
    (cd "$src_dir" && plantuml -tsvg -o "../out/$name" "$name.puml")

    echo "Экспортирована диаграмма $name по адресу $output_root/$name/$name.svg"
done
