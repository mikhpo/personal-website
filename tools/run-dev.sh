#!/bin/bash

# Скрипт для автоматической пересборки фронтенда и запуска сервера разработки Django
# Использование: ./tools/run-dev.sh [--watch]

set -e  # Остановиться при любой ошибке

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Функция для вывода сообщений
print_message() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Проверка наличия необходимых инструментов
check_requirements() {
    if ! command -v npm &> /dev/null; then
        print_error "npm не найден. Пожалуйста, установите Node.js"
        exit 1
    fi

    if ! command -v poetry &> /dev/null; then
        print_error "Poetry не найден. Пожалуйста, установите Poetry"
        exit 1
    fi

    print_message "Все необходимые инструменты найдены"
}

# Пересборка фронтенда
build_frontend() {
    print_message "Пересборка фронтенда..."

    cd personal_website

    if [ "$1" = "--watch" ] || [ "$1" = "watch" ]; then
        print_message "Запуск в режиме наблюдения (watch mode)"
        npm run dev
    else
        print_message "Запуск однократной сборки"
        npm run build
    fi

    cd ..
    print_message "Фронтенд успешно собран"
}

# Запуск сервера разработки Django
run_django_server() {
    print_message "Запуск сервера разработки Django..."
    poetry run python personal_website/manage.py runserver
}

# Основная логика
main() {
    print_message "Запуск скрипта разработки Personal Website"

    check_requirements

    WATCH_MODE=false
    for arg in "$@"; do
        if [ "$arg" = "--watch" ] || [ "$arg" = "-w" ] || [ "$arg" = "watch" ]; then
            WATCH_MODE=true
        fi
    done

    if [ "$WATCH_MODE" = true ]; then
        print_message "Запуск в режиме наблюдения"
        # В режиме наблюдения запускаем сборку в фоне и сервер в основном процессе
        build_frontend --watch &
        BUILD_PID=$!
        sleep 5  # Даем время для первой сборки

        # Проверяем, что процесс сборки все еще жив
        if kill -0 $BUILD_PID 2>/dev/null; then
            print_message "Webpack запущен в режиме наблюдения (PID: $BUILD_PID)"
        else
            print_warning "Процесс webpack мог завершиться. Проверьте вывод выше."
        fi

        run_django_server
    else
        build_frontend
        print_message "Для запуска в режиме наблюдения используйте: ./tools/run-dev.sh --watch"
    fi
}

# Запуск основной функции с переданными аргументами
main "$@"
