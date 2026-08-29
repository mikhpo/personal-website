#!/bin/bash
#
# Продление сертификатов Let's Encrypt контейнерного nginx (профиль nginx):
# docker compose run --rm certbot renew --webroot + перезагрузка конфигурации
# nginx. Вызывается по cron хоста (scripts/cronjobs.sh). При неактивном
# профиле nginx (хостовой прокси) скрипт ничего не делает: сертификаты
# хостового certbot обслуживает certbot.timer.

set -e

project_root="$(dirname "$(dirname "$(dirname "$(readlink -f "$0")")")")"
dotenv="$project_root/.env"
cd "$project_root" || exit

if [ -f "$dotenv" ]; then
    set -a
    # shellcheck disable=SC1090
    . "$dotenv"
    set +a
fi

case ",${COMPOSE_PROFILES:-}," in
    *,nginx,*) ;;
    *) exit 0 ;;
esac

if docker compose version >/dev/null 2>&1; then
    compose="docker compose"
else
    compose="docker-compose"
fi

$compose run --rm certbot renew --webroot -w /var/www/certbot
$compose exec -T nginx nginx -s reload
