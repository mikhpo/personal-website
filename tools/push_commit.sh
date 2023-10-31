#!/bin/bash
#
# Подготавливает коммит, выполняя форматирование кода, 
# и отправляет изменения в удаленный репозиторий.
project_root="$(dirname "$(dirname "$(readlink -f "$0")")")"
cd $project_root
poetry export -f requirements.txt --output requirements.txt --without-hashes --with dev
isort .
black .
git add .
read -p "Сообщение для коммита: " message
git commit -m "$message"
git push