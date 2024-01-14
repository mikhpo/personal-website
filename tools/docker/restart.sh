#!/bin/bash
#
# Скрипт для перезапуска контейнеров после изменения конфигурации.

# Выйти в случае ошибки.
set -e

# Пересоздать и запустить контейнеры в фоновом режиме.
docker-compose up \
    --detach \
    --build \
    --force-recreate
docker-compose ps
