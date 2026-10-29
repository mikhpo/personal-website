#!/bin/bash
#
# Скрипт для выпуска self-signed сертификата локального nginx-стека.
# Для успешного выполнения скрипта должны быть выполнены следующие условия:
# 1. В системе должна быть установлена утилита openssl.
# 2. Домен сертификата можно задать переменной окружения DOMAIN_NAME (по умолчанию localhost).

# Определить корневой путь репозитория.
project_root="$(dirname "$(dirname "$(readlink -f "$0")")")"

# Домен сертификата из окружения или localhost по умолчанию.
domain="${DOMAIN_NAME:-localhost}"

# Папка сертификата: тот же путь, который использует certbot в продакшене,
# поэтому конфигурация nginx одна для всех сред.
cert_dir="$project_root"/nginx/letsencrypt/live/"$domain"

# Готовый сертификат не перевыпускать: задача выполняется перед каждым прогоном
# интеграционных тестов, и от нее нужен факт наличия сертификата, а не свежесть.
if [ -f "$cert_dir"/fullchain.pem ]; then
    echo "Сертификат nginx для домена $domain уже выпущен: $cert_dir/fullchain.pem"
    exit 0
fi

mkdir -p "$cert_dir"

openssl req -x509 -newkey rsa:2048 -nodes -days 365 \
    -subj "/CN=$domain" \
    -keyout "$cert_dir"/privkey.pem \
    -out "$cert_dir"/fullchain.pem
echo "Выпущен сертификат nginx для домена $domain: $cert_dir/fullchain.pem"
