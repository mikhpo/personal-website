#!/bin/bash
#
# Запуск тестов проекта Python с формированием отчета Coverage и тестов JavaScript.

#######################################
# Вывести в терминал линию для разделения
# этапов выполнения скрипта.
#######################################
function print_line() {
    printf %"$(tput cols)"s | tr " " "="
}

#######################################
# Смена директории на корневую директорию проекта.
#######################################
function change_dir() {
    repository_root="$(dirname "$(dirname "$(dirname "$(readlink -f "$0")")")")"
    cd "$repository_root" || exit
}

#######################################
# Запустить тесты Node.js.
#######################################
function run_npm_test() {
    print_line
    echo "Выполнение тестов Node.js"
    npm test
}

#######################################
# Запустить тесты проекта Django при помощи Pytest.
#######################################
function run_project_tests() {
    print_line
    echo "Выполнение тестов Django"
    poetry run coverage run -m pytest
    poetry run coverage html
}

#######################################
# Основная бизнес-логика скрипта.
#######################################
function main() {
    change_dir
    run_npm_test
    run_project_tests
}

main "$@"
