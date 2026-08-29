# Прокси и сертификаты

Прокси-сервер выбирается независимо от остальных параметров
развертывания (база данных, хранилище, способ запуска приложения).
Контракт приложения для любого варианта прокси - порт на 127.0.0.1
(см. [application.md](./application.md)), поэтому прокси-слой заменяется
без изменений приложения.

## 1. Инструмент

Прокси-инструмент один для всех вариантов - nginx. Он работает либо
в контейнере Docker Compose (профиль nginx, рецепт в разделе 3), либо
в операционной системе хоста с сертификатами certbot (раздел 2).

nginx раздает медиа filesystem-хранилища с локального диска, работает
с сертификатами любого удостоверяющего центра (меняются только
PEM-файлы) и проксирует бэкенды обоих способов запуска: контейнерные
и systemd слушают один и тот же 127.0.0.1:${DJANGO_PORT}.

## 2. Рецепт хостового nginx + certbot

### Установка

```bash
sudo apt-get install -y nginx certbot
```

Плагин python3-certbot-nginx не используется: конфигурация nginx
принадлежит администратору, certbot работает методом webroot и ничего
в конфигурации прокси не меняет.

### Конфигурация сайта проекта

Файл /etc/nginx/sites-available/personal-website устанавливается
scripts/server/setup.sh из шаблона
scripts/server/nginx/personal-website.conf.template. Подстановка
значений выполняется утилитой envsubst (пакет gettext-base) по списку
переменных:

```bash
envsubst "$DOMAIN_NAME $DJANGO_PORT $STORAGE_ROOT" \
    < personal-website.conf.template > personal-website.conf
```

setup.sh выполняет подстановку этими же переменными из .env
и требует sudo для записи в /etc/nginx/sites-available/.

```nginx
server {
    listen 80;
    server_name example.com www.example.com;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        return 301 https://$host$request_uri;
    }
}

server {
    listen 443 ssl http2;
    server_name example.com www.example.com;

    ssl_certificate /etc/letsencrypt/live/example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;

    client_max_body_size 50m;

    location /media/ {
        alias /srv/personal-website/storage/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }
}
```

Назначение директив следующее. HTTP-сервер выполняет редирект 301
на HTTPS для всех запросов, кроме /.well-known/acme-challenge/:
на них отвечает certbot (проверки HTTP-01 при выпуске и продлении),
а root /var/www/certbot совпадает с аргументом -w команды certbot
ниже. Директива proxy_pass ведет на 127.0.0.1:${DJANGO_PORT} - это
и есть контракт приложения. Заголовки Host, X-Forwarded-For
и X-Forwarded-Proto нужны приложению за прокси: из домена собирается
CSRF_TRUSTED_ORIGINS, а X-Forwarded-Proto доверяется при включенном
SECURE_PROXY_SSL_HEADER (см. .env.example, блок безопасности).
Директива client_max_body_size 50m поднимает дефолтный лимит 1m,
иначе загрузка фотографий галереи не проходит.

Location /media/ раздает медиафайлы filesystem-хранилища напрямую
с диска: alias указывает на каталог STORAGE_ROOT, и nginx читает
файлы сам, не задействуя воркеры приложения (при STORAGE_TYPE=s3
медиа отдает объектное хранилище, и этот location молча не совпадает
ни с одним запросом). Чтобы раздача работала, каталог STORAGE_ROOT
и файлы в нем должны быть читаемы пользователю nginx (www-data):
приложение создает файлы с правами 644 и каталоги 755 по умолчанию,
чего достаточно. Контейнерный nginx раздает медиа так же - каталог
хранилища монтируется прямо в прокси (раздел 3).

При запуске приложения в systemd-режиме с unix-сокетом адресация
меняется на `proxy_pass http://unix:/run/personal-website.sock`,
остальные директивы конфигурации сайта не меняются (вариант сокета -
[application.md](./application.md), раздел 4).

Включение конфигурации сайта:

```bash
sudo ln -sfn /etc/nginx/sites-available/personal-website /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

### Первичный выпуск сертификата (двухфазный)

nginx не стартует с директивой ssl_certificate, указывающей
на несуществующий файл, поэтому сертификат выпускается до включения
HTTPS-блока. Порядок такой:

1. ставится временная конфигурация сайта - только сервер HTTP
   с location /.well-known/acme-challenge/ (шаблон
   scripts/server/nginx/acme-bootstrap.conf.template); прочие запросы
   получают 503;
2. выпускается сертификат (команда ниже);
3. временная конфигурация заменяется полной и nginx перезагружается.

scripts/server/setup.sh выполняет все три фазы автоматически.

### Выпуск и продление сертификата

```bash
sudo mkdir -p /var/www/certbot
sudo certbot certonly --webroot -w /var/www/certbot \
    -d example.com -d www.example.com \
    --email admin@example.com --agree-tos --no-eff-mail
```

Тестовые среды выпускают сертификат в ACME staging, чтобы не расходовать
лимиты продакшена Let's Encrypt: флаг --staging включается setup.sh
автоматически при CERTBOT_STAGING=True в .env или окружении.
Сертификаты staging не являются доверенными - так проверяется сама
схема, а браузерные предупреждения ожидаемы. Для перехода
на продакшен тестовый сертификат удаляется
(`sudo certbot delete --cert-name example.com`) и выпуск повторяется
уже без --staging.

Продление выполняет systemd timer certbot.timer из пакета certbot:
запуски дважды в сутки, продление - при истечении трети срока.
Перезагрузку nginx после каждого обновления делает deploy hook
/etc/letsencrypt/renewal-hooks/deploy/nginx-reload.sh:

```bash
#!/bin/bash
systemctl reload nginx
```

Проверка продления:

```bash
sudo certbot renew --dry-run
systemctl list-timers certbot.timer
```

### Вариант DNS-01

Проверка DNS-01 требуется, когда порты 80/443 недоступны извне (CGNAT,
блокировка провайдером) или нужен wildcard-сертификат. Выполняется
она плагином DNS-провайдера домена, например:

```bash
sudo apt-get install -y python3-certbot-dns-cloudflare
sudo certbot certonly --dns-cloudflare \
    --dns-cloudflare-credentials /root/.secrets/cloudflare.ini \
    -d example.com -d www.example.com \
    --email admin@example.com --agree-tos --no-eff-mail
```

Учетные данные плагина хранятся на сервере с правами 600 у пользователя
root. Ручной режим (certbot certonly --manual) для продления
по расписанию не годится: при каждом продлении он требует интерактивного
подтверждения. При выборе DNS-01 конфигурация сайта меняется только
отсутствием location ACME-проверки - проверки идут через DNS.

## 3. Рецепт nginx + certbot в Docker Compose

Прокси подключается профилем nginx (`COMPOSE_PROFILES=nginx` или
`docker compose --profile nginx up`). Сервис использует официальный
образ nginx; конфигурация рендерится из шаблона
[nginx/personal-website.conf.template](../../nginx/personal-website.conf.template)
самим образом (envsubst по переменным окружения DOMAIN_NAME и DJANGO_PORT).
Она повторяет конфигурацию хостового варианта: редирект HTTP -> HTTPS,
webroot для проверок ACME, `location /media/` с alias на примонтированный
каталог хранилища (`STORAGE_ROOT` подключается в прокси read-only) и
proxy_pass на сервис application. Каталог nginx/letsencrypt с журналами
и сертификатами - bind mount, переживает `docker compose down -v`.

До первого выпуска сертификата nginx не стартует: директива
ssl_certificate указывает на файл, которого еще нет. Поэтому первичный
выпуск выполняется standalone-методом до подъема стека - certbot
поднимает собственный HTTP-сервер на порту 80:

```bash
docker compose run --rm -p 80:80 certbot certonly --standalone \
    -d example.com -d www.example.com \
    --email admin@example.com --agree-tos --no-eff-mail
```

Эту команду выполняет scripts/docker/setup.sh при активном профиле nginx
(идемпотентно: существующий сертификат пропускается; тестовые среды
добавляют --staging при CERTBOT_STAGING=True). После выпуска конфигурация
nginx не меняется никогда.

Продление работает через webroot: запущенный nginx отвечает на проверки
ACME из каталога nginx/acme-webroot, общий с certbot. Основной механизм -
cron хоста (добавляется scripts/cronjobs.sh): ежедневно в 04:17
запускается [scripts/docker/renew-cert.sh](../../scripts/docker/renew-cert.sh) -
`docker compose run --rm certbot renew --webroot -w /var/www/certbot`
с последующей перезагрузкой конфигурации nginx; при неактивном профиле
nginx скрипт ничего не делает. Логи - `${LOGS_ROOT}/cert-renew.log`.

Альтернатива для сред без хостового планировщика - контейнер certbot
с циклом продления и docker.sock для сигнала перезагрузки nginx:

```yaml
entrypoint: /bin/sh -c 'trap exit TERM; while :; do
  certbot renew --webroot -w /var/www/certbot --deploy-hook
  "docker kill --signal HUP nginx"; sleep 12h; done'
volumes:
  - /var/run/docker.sock:/var/run/docker.sock
```

Издержки варианта: контейнер certbot получает доступ к docker.sock,
эквивалентный правам root на хосте, поэтому основным выбран cron.

Ручной удостоверяющий центр (например, местный УЦ при недоступности
Let's Encrypt) не требует изменения схемы: файлы fullchain.pem
и privkey.pem укладываются в nginx/letsencrypt/live/<домен>/ (теми же
путями, что использует certbot), после чего выполняется
`docker compose exec nginx nginx -s reload`. Certbot в этом случае
не участвует вовсе.

Локальная разработка без домена использует self-signed сертификат -
задача `task dev-cert` генерирует его в nginx/letsencrypt/live/localhost/
теми же путями, поэтому конфигурация nginx одна для всех сред. Порты
прокси настраиваются переменными HTTP_PORT/HTTPS_PORT (полезно, если
80/443 хоста заняты). Проверка прокси после подъема стека:

```bash
curl -sk https://localhost/health/
curl -sk https://localhost/media/<файл>
```
