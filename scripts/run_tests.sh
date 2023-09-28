#!/bin/bash
#
# Запуск тестов проекта.
# Адреса исполняемых файлов определяются автоматически.

# Вывести в терминал линию для разделения этапов выполнения скрипта.
function print_line() {
    printf %"$(tput cols)"s |tr " " "="
}

# Смена директории на корневую директорию проекта.
repository_root="$(dirname "$(dirname "$(readlink -f "$0")")")"
cd $repository_root

# Запустить тесты Node.js.
print_line
echo "Выполнение тестов Node.js"
npm test

# Запустить тесты Django при помощи Pytest.
print_line
echo "Выполнение тестов Django"
pytest
