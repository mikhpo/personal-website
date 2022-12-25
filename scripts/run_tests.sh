#!/bin/bash
#
# Запуск тестов проекта.
# Адреса исполняемых файлов определяются автоматически.

#####################
# Вывести в терминал линию для разделения этапов выполнения скрипта.
#####################
function print_line() {
    printf %"$(tput cols)"s |tr " " "="
}

# Определение абсолютных путей директорий и исполняемых файлов.
repository_root="$(dirname "$(dirname "$(readlink -f "$0")")")"
website_root="$repository_root/personal_website"
python_executable=$repository_root/.venv/bin/python
print_line
echo "Корневая директория репозитория: ${repository_root}"
echo "Директория проекта Django: ${repository_root}"
echo "Путь до исполняемого файла Python: ${python_executable}"

# Выполнить юнит-тесты Python для проверки общих настроек проекта.
print_line
echo "Выполнение тестов Python"
$python_executable -m unittest

# Выполнить юнит-тесты Node.js для проверки общих настроек проекта.
print_line
echo "Выполнение тестов Node.js"
npm test

# Выполнить выполнить юнит-тесты Django для проверки функциональности проекта.
cd $website_root
print_line
echo "Выполнение тестов Django"
$python_executable manage.py test
