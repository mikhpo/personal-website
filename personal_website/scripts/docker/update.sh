#!/bin/bash
#
# Скрипт для перезапуска контейнеров после изменения кода проекта.

# Выйти в случае ошибки.
set -e

project_root="$(dirname "$(dirname "$(dirname "$(dirname "$(readlink -f "$0")")")")")"
cd "$project_root" || exit

# Создать резервную копию базы данных и загруженных файлов.
bash "$project_root"/personal_website/scripts/pgbackup.sh
bash "$project_root"/personal_website/scripts/pgrestore.sh

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
    --force-recreate \
    --remove-orphans
docker-compose ps
docker image prune
