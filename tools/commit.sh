#!/bin/bash
#
# Подготавливает коммит, выполняя форматирование кода, 
# и отправляет изменения в удаленный репозиторий.

# Перейти в корневой каталог проекта.
project_root="$(dirname "$(dirname "$(readlink -f "$0")")")"
cd "$project_root" || exit

# Экспортировать зависимости Python в файл requirements.txt.
poetry export -f requirements.txt --output requirements.txt --without-hashes --with dev

# Выполнить сортировку импортов и форматирование кода.
isort .
black .

# Добавть все сообщения в коммит, запросить сообщение 
# для комиита и отправить в удаленный репозиторий.
git add .
git status
read -rp "Сообщение для коммита: " message
git commit -m "$message"
git push