# Прокси и сертификаты

Слой терминирования HTTPS выбирается независимо от остальных параметров
развертывания (база данных, хранилище, способ запуска приложения).
Контракт приложения для любого варианта прокси - порт на 127.0.0.1
(см. [application.md](./application.md)), поэтому прокси-слой заменяется
без изменений приложения.

## 1. Рекомендация и обоснование

Основной путь - nginx в операционной системе хоста с сертификатами
certbot. Выбор объясняется тремя соображениями.

Во-первых, это мультипроектный хост: один nginx обслуживает все проекты
сервера, каждому соответствует своя конфигурация сайта, и он единолично
занимает порты 80/443 - прокси-слой проекта ничего не занимает
(ср. профиль traefik ниже). Во-вторых, nginx равноправно проксирует
любой способ запуска: контейнерные бэкенды (Docker Compose, docker run)
и systemd-бэкенды для него одинаковы - все они слушают
127.0.0.1:${DJANGO_PORT}. Наконец, выбор пользователя: при функциональной
эквивалентности Traefik и nginx предпочтение отдается nginx как более
знакомому инструменту с большей накопленной документацией.

Traefik в Docker Compose остается поддерживаемым вариантом для
одиночного сервера «все в Docker»: он настраивается декларативными
labels и выпускает сертификаты автоматически, без плейсхолдеров
и внешних файлов. Рецепт - в разделе 3.

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
scripts/server/nginx/personal-website.conf.template; значения
${DOMAIN_NAME}, ${DJANGO_PORT} и ${STORAGE_ROOT} подставляются
из .env.

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
чего достаточно. Контейнерный Traefik раздает медиа аналогично -
через файловый сервер профиля media (раздел 3).

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

## 3. Режим Traefik в Docker Compose

Прокси подключается профилем traefik (`COMPOSE_PROFILES=traefik` или
`docker compose --profile traefik up`). Конфигурация - labels сервиса
application в compose.yaml, отдельного файла конфигурации нет.

Переменные окружения (.env):

- TRAEFIK_CERT_RESOLVER - имя сертификатного резолвера в labels
  маршрутизатора: 'le' в продакшене (выпуск через TLS-ALPN-01),
  пустая строка в разработке (ACME-клиент пассивен, HTTPS обслуживается
  встроенным self-signed сертификатом Traefik, обращений к Let's Encrypt
  нет);
- ACME_EMAIL - адрес регистрации аккаунта ACME и уведомлений;
- TRAEFIK_ACME_CASERVER - адрес ACME CA-сервера: пусто - продакшен
  Let's Encrypt (дефолт Traefik), для тестовых сред -
  <https://acme-staging-v02.api.letsencrypt.org/directory>
  (защита от исчерпания лимитов продакшена при повторных выпусках).

Состояние ACME-клиента хранится в traefik/letsencrypt/acme.json
(bind mount, переживает docker compose down -v). Перенос между
серверами - копированием каталога до первого старта Traefik.

Медиа filesystem-хранилища Traefik раздает через профиль media:
контейнер nginx монтирует каталог `STORAGE_ROOT` read-only
и обслуживает его как файловый сервер, а маршрутизатор
website-media (правило Host + PathPrefix(`/media/`), приоритетнее
хостового правила) направляет запросы медиа в него, минуя
приложение. Профиль включается в COMPOSE_PROFILES при
`STORAGE_TYPE=filesystem` с контейнерным прокси; при s3 медиа отдает
бакет, и профиль не нужен. Конфигурация - labels сервиса media
в compose.yaml.

Ограничение: настроен только challenge TLS-ALPN-01 - требуется
доступный извне порт 443. При недоступных 80/443 (CGNAT) Traefik
с текущей конфигурацией сертификаты выпускать не может; сценарий
закрывается хостовым nginx + certbot с DNS-01 (раздел 2).

## 4. Пост-мортем: nginx-в-контейнере

До коммита 692b9a94 (2026-08-15) прокси работал как кастомный образ
nginx с cron и certbot внутри контейнера: конфигурация генерировалась
из шаблона через envsubst, обновление сертификатов выполнял cron
контейнера, а плагин python3-certbot-nginx правил живой конфиг
в рантайме. Схема заменена на Traefik. Причины не воскрешать ее
(в том числе под видом «контейнерного nginx без Traefik»):

1. Два демона в одном контейнере (nginx + cron) нарушают модель
   «один главный процесс - один контейнер».
2. Падение cron внутри контейнера незаметно: продление сертификатов
   молча прекращается, проблема всплывает только при истечении
   сертификата.
3. Certbot с плагином nginx мутирует живую конфигурацию в рантайме -
   фактический конфиг расходится с шаблоном в репозитории.
4. Собственный инфраструктурный образ - отдельная единица
   сопровождения (базовый образ, версии certbot, обновления
   безопасности).
5. Продление сертификатов привязано к циклу деплоев (перезапусков
   контейнера), а не к расписанию.
6. Отсутствие dev-режима: без домена и публичного адреса схема
   не работала вовсе.

Вывод: каждый слой получает подходящий инструмент - в контейнере
Traefik (декларативные labels, автоматический ACME), на хосте -
nginx + certbot (systemd timer, deploy hooks). Пост-мортем относится
к nginx как прокси-слою с терминированием TLS; контейнер nginx
профиля media - не прокси, а файловый сервер медиа за Traefik, и на
него вывод не распространяется.

## 5. Неподдерживаемые варианты

- Общий Traefik-стек сервера (Traefik в отдельном compose-проекте,
  обслуживающий проекты через внешние сети). Потребовал бы
  external-сетей и разбиения единого compose.yaml - осознанно нет;
  сценарий мультипроектного проксирования закрыт хостовым nginx.
- Nginx-в-контейнере как прокси-слой - см. пост-мортем в разделе 4;
  контейнер nginx профиля media - файловый сервер медиа, не прокси.
- Socket-proxy для docker.sock. Traefik с примонтированным
  /var/run/docker.sock эквивалентен правам root на хосте; при желании
  усилить изоляцию используется образ tecnativa/docker-socket-proxy
  (read-only прокси Docker API), но это опция усиления, а не
  поддерживаемый путь проекта: основной вариант прокси (хостовый nginx)
  docker.sock не получает вовсе.
