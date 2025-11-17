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
    repository_root="$(dirname "$(dirname "$(readlink -f "$0")")")"
    cd "$repository_root" || exit
}

#######################################
# Собрать, создать и запустить контейнеры сервиса.
#######################################
function containers_up() {
    docker-compose up --detach --wait --force-recreate postgres
}

#######################################
# Остановить и удалить контейнеры сервиса.
#######################################
function containers_down() {
    docker-compose down
}

#######################################
# Запустить тесты JavaScript (Node.js).
#######################################
function run_javascript_tests() {
    print_line
    echo "Выполнение тестов Node.js"
    npm test
}

#######################################
# Запустить тесты проекта Django при помощи Pytest.
#######################################
function run_python_tests() {
    print_line
    echo "Выполнение тестов Python/Django"
    poetry run coverage run -m pytest
    poetry run coverage html
}

#######################################
# Основная бизнес-логика скрипта.
#######################################
function main() {
    change_dir
    run_javascript_tests
    containers_up
    run_python_tests
    containers_down
}

main "$@"
