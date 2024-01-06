#!/bin/bash
#
# Получение сертификата Let's Encrypt при помощи Certbot.

# Получить SSL сертификат.
certbot \
    --nginx \
    --email "$EMAIL_HOST_USER" \
    --agree-tos \
    --no-eff-email \
    --noninteractive \
    -d "$DOMAIN_NAME" \
    -d www."$DOMAIN_NAME"

# Показать расписание обновления сертификата.
cat /etc/cron.d/certbot

# Проверить процесс обновления сертификата.
certbot renew --dry-run
