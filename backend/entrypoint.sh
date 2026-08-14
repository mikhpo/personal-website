#!/bin/bash
#
# Выполнение миграций, установка зависимостей и запуск
# сервера в режиме разработки или воркеров Gunicorn.

# Остановиться в случае ошибки.
set -e

# Значения по умолчанию для адреса хоста и номера порта.
readonly DJANGO_HOST="0.0.0.0"
readonly DJANGO_PORT="8000"

#######################################
# Установить алиас для сервера MinIO.
# Параметры алиаса зависят из переменных окружения.
#######################################
function set_minio_alias() {
    mc=$(which mc)
    $mc alias set \
    "${MINIO_ALIAS}" \
    "${MINIO_SERVER_URL}" \
    "${MINIO_ACCESS_KEY}" \
    "${MINIO_SECRET_KEY}"
    $mc admin info "${MINIO_ALIAS}"
}

#######################################
# Дождаться открытия TCP-порта на хосте.
# Проверка выполняется средствами bash (/dev/tcp) без внешних зависимостей
# от клиентов баз данных. Используется для ожидания готовности сервисов
# до запуска миграций: PostgreSQL и MinIO могут предоставляться внешними
# сервисами или стартовать параллельно без depends_on. Каждая попытка
# соединения ограничена утилитой timeout, чтобы хосты с фильтрацией
# пакетов не блокировали цикл.
# Аргументы:
#   1. host — имя хоста или IP-адрес.
#   2. port — номер порта.
#   3. attempts — максимальное количество попыток (по умолчанию 30).
# Возвращает: 0 при успехе, 1 при исчерпании попыток.
#######################################
function wait_for_port() {
    local host="$1"
    local port="$2"
    local attempts="${3:-30}"
    for ((i = 1; i <= attempts; i++)); do
        if timeout 3 bash -c "(echo > /dev/tcp/${host}/${port})" 2>/dev/null; then
            echo "Хост $host:$port доступен (попытка $i)."
            return 0
        fi
        sleep 1
    done
    echo "Таймаут ожидания $host:$port (${attempts} попыток)." >&2
    return 1
}

#######################################
# Разобрать URL сервиса на имя хоста и номер порта.
# Из значения вида протокол://хост[:порт][/путь] извлекаются имя хоста
# и номер порта. Если порт не указан, возвращается порт 443.
# Аргументы:
#   1. url — адрес сервиса.
# Возвращает: строка "хост порт" для чтения через read.
#######################################
function parse_service_url() {
    local url="${1#*://}"
    local host="${url%%[:/]*}"
    local port="443"
    if [[ "$url" == *:* ]]; then
        port="${url#*:}"
        port="${port%%/*}"
    fi
    echo "$host $port"
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
# Адреса каталогов и файлов проекта определяются по адресу скрипта.
# Способ запуска контейнера определяется по переменной окружения DEBUG.
# Переменные окружения считываются из .env файла.
#######################################
function main() {
    website_dir="$(dirname "$(readlink -f "$0")")"
    root_dir="$(dirname "$website_dir")"
    dotenv="$root_dir/.env"
    manage="$website_dir/manage.py"
    python="$root_dir/.venv/bin/python"
    gunicorn="$root_dir/.venv/bin/gunicorn"

    # Дождаться готовности кластера PostgreSQL и объектного хранилища MinIO.
    # Если сервисы предоставляются вне Docker Compose, они обычно уже доступны
    # и ожидание завершается сразу. В противном случае контейнеры могут
    # стартовать параллельно без depends_on.
    wait_for_port "${POSTGRES_HOST}" "${POSTGRES_PORT}"

    # Извлечь хост и порт MinIO из значения переменной MINIO_SERVER_URL.
    read -r minio_host minio_port <<< "$(parse_service_url "${MINIO_SERVER_URL}")"
    wait_for_port "$minio_host" "$minio_port"

    # Выполнить миграции и собрать статические файлы.
    $python "$manage" migrate
    $python "$manage" collectstatic --noinput

    # Загрузить переменные окружения из .env файла.
    eval export "$(cat "$dotenv")"

    # Установить алиас для сервера MinIO.
    set_minio_alias

    # В зависимости от значения переменной окружения DEBUG определить способ запуска.
    debug_bool=$(str_to_bool "$DEBUG")
    if $debug_bool; then
        $python "$manage" runserver "$DJANGO_HOST":"$DJANGO_PORT"
    else
        num_workers=$(calculate_worker_count)
        $gunicorn \
            --bind="$DJANGO_HOST":"$DJANGO_PORT" \
            --workers="$num_workers" \
            --pythonpath="$website_dir" \
            "backend.personal_website.wsgi:application"
    fi
}

main "$@"
