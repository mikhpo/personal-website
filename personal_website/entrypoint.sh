#!/bin/bash
#
# Выполнение миграций, установка зависимостей и запуск
# сервера в режиме разработки или воркеров Gunicorn.

# Остановиться в случае ошибки.
set -e

# Значения по умолчанию для адреса хоста и номера порта.
readonly DEFAULT_HOST="0.0.0.0"
readonly DEFAULT_PORT="8000"

#######################################
# Адрес хоста определяются из аргумента командной строки или устанавливается
# в соответствии со значением по умолчанию, если аргумент не передан.
# Глобальная переменная: DEFAULT_HOST - адрес хоста по умолчанию.
# Возвращаает: адрес хоста.
#######################################
function get_host() {
    if [ -z "$1" ]; then
        local host=$DEFAULT_HOST
    else
        local host="$1"
    fi
    echo "$host"
}

#######################################
# Номер порта определяются из аргумента командной строки или устанавливается
# в соответствии со значением по умолчанию, если аргумент не передан.
# Глобальная переменная: DEFAULT_PORT - номер порта по умолчанию.
# Возвращаает: номер порта.
#######################################
function get_port() {
    if [ -z "$1" ]; then
        local port=$DEFAULT_PORT
    else
        local port="$1"
    fi
    echo "$port"
}

#######################################
# Преобразование значения строки в логическое значение true/false.
# Значение аргумента преобразуется в нижний регистр, далее проверяется
# соответствие преобразованного значения регулярному выражению, 
# содержащему одно из изначений, означающих истину.
#######################################
function str_to_bool() {
    local PATTERN="^(true|1|yes|y|ok)$"
    lower_string="$(echo "$1" | tr '[:upper:]' '[:lower:]')"
    if [[ $lower_string =~ $PATTERN ]]; then
        echo true
    else
        echo false
    fi
}

#######################################
# Опрделение количество воркеров Gunicorn.
# Количество воркеров определяется по формуле: (2 * количество логических ядер CPU) + 1.
# Количество логических ядер CPU определяется разными способами в зависимости от оболочки:
#   - для оболочки bash: командой npoc
#   - для оболочки zsh: командой sysctl hw.logicalcpu
# Переменные окружения: SHELL - используемая оболочка.
# Возвращает: количество воркеров (целое число).
#######################################
function calculate_worker_count() {
    if [[ "$SHELL" == *"bash"* ]]; then
        num_cores=$(nproc --all)
    elif [[ "$SHELL" == *"zsh"* ]]; then
        num_cores=$(sysctl -n hw.logicalcpu)
    fi
    num_workers=$((2 * num_cores + 1))
    echo $num_workers
}

#######################################
# Основное тело скрипта.
#######################################
function main() {

    # Адреса каталогов и файлов проекта определяются по адресу скрипта.
    website_dir="$(dirname "$(readlink -f "$0")")"
    root_dir="$(dirname "$website_dir")"
    dotenv="$root_dir/.env"
    manage="$website_dir/manage.py"
    python="$root_dir/.venv/bin/python"
    gunicorn="$root_dir/.venv/bin/gunicorn"

    # Выполнить миграции и собрать статические файлы.
    $python "$manage" migrate
    $python "$manage" collectstatic --noinput

    # Загрузить переменные окружения из .env файла.
    eval export "$(cat "$dotenv")"

    # Определить адрес хоста и номер порта.
    host=$(get_host "$1")
    port=$(get_port "$2")

    # В зависимости от значения переменной окружения DEBUG определить способ запуска.
    debug_bool=$(str_to_bool "$DEBUG")
    if $debug_bool; then
        $python "$manage" runserver "$host":"$port"
    else
        num_workers=$(calculate_worker_count)
        $gunicorn \
            --bind="$host":"$port" \
            --workers="$num_workers" \
            --pythonpath="$website_dir" \
            "project.wsgi:application"
    fi
}

main "$@"
