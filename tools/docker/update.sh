#!/bin/bash
#
# Скрипт для перезапуска контейнеров после изменения кода проекта.

# Выйти в случае ошибки.
set -e

project_root="$(dirname "$(dirname "$(dirname "$(readlink -fm "$0")")")")"
cd "$project_root" || exit

# Вытянуть изменения основной ветки
git fetch origin
git checkout main
git pull

# Вытянуть новую версию образа, пересоздать контейнеры,
# запустить контейнеры в фоновом режиме, удалить
# неиспользуемые контейнеры и образы.
docker-compose pull
docker-compose up \
    --detach \
    --build \
    --force-recreate \
    --remove-orphans
docker-compose ps
docker image prune
