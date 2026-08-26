# Прокси и сертификаты

Слой терминирования HTTPS выбирается независимо от остальных параметров
развертывания (база данных, хранилище, способ запуска приложения).
Контракт приложения для любого варианта прокси - порт на 127.0.0.1
(см. [application.md](./application.md)), поэтому прокси-слой заменяется
без изменений приложения.

Содержание:

1. Рекомендация и обоснование
2. Рецепт хостового nginx + certbot
3. Режим Traefik в Docker Compose
4. Пост-мортем: nginx-в-контейнере
5. Неподдерживаемые варианты

## 1. Рекомендация и обоснование

Основной путь - nginx на хосте операционной системы с сертификатами
certbot. Обоснование:

- мультипроектный хост: один nginx обслуживает vhost'ы всех проектов
  и единолично занимает порты 80/443, прокси-слой проекта ничего
  не занимает (см. профиль traefik ниже);
- равноправие способов запуска: nginx одинаково проксирует контейнерные
  бэкенды (Docker Compose, docker run) и systemd-бэкенды - для него
  разницы нет, все они слушают 127.0.0.1:${DJANGO_PORT};
- решение пользователя: при функциональной эквивалентности Traefik
  и nginx предпочтение отдается nginx (больше опыта работы
  и документации).

Traefik в Docker Compose - поддерживаемый вариант одиночного сервера
«все в Docker»: без плейсхолдеров и внешних файлов, сертификаты
выпускаются автоматически. Рецепт - в разделе 3.

## 2. Рецепт хостового nginx + certbot

### Установка

```bash
sudo apt-get install -y nginx certbot
```

Плагин python3-certbot-nginx не используется: конфигурация nginx
принадлежит администратору, certbot работает методом webroot
и не изменяет конфигурацию прокси.

### Vhost проекта

Файл /etc/nginx/sites-available/personal-website (ставит
scripts/server/setup.sh из шаблона
scripts/server/nginx/personal-website.conf.template, переменные
${DOMAIN_NAME} и ${DJANGO_PORT} подставляются из .env):

```nginx
# HTTP: проверка ACME и редирект на HTTPS.
server {
    listen 80;
    server_name example.com www.example.com;

    # Проверки ACME (HTTP-01) при выпуске и продлении сертификата.
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        return 301 https://$host$request_uri;
    }
}

# HTTPS: терминирование TLS и проксирование приложения.
server {
    listen 443 ssl http2;
    server_name example.com www.example.com;

    ssl_certificate /etc/letsencrypt/live/example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;

    # Лимит тела запроса: загрузка фотографий в галерею.
    client_max_body_size 50m;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }
}
```

Назначение директив:

- proxy_pass на 127.0.0.1:${DJANGO_PORT} - контракт приложения;
- Host, X-Forwarded-For, X-Forwarded-Proto - приложение за прокси
  собирает CSRF_TRUSTED_ORIGINS из домена и доверяет
  X-Forwarded-Proto при включенном SECURE_PROXY_SSL_HEADER
  (см. .env.example, блок безопасности);
- client_max_body_size 50m - загрузка фотографий галереи не проходит
  на дефолтном лимите 1m;
- статика и медиа через nginx не раздаются: в filesystem-режиме их
  обслуживает WhiteNoise, при STORAGE_TYPE=s3 - объектное хранилище.

Включение vhost:

```bash
sudo ln -sfn /etc/nginx/sites-available/personal-website /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

### Первичный выпуск сертификата (двухфазный)

nginx не стартует с директивой ssl_certificate на несуществующий файл,
поэтому сертификат выпускается до включения HTTPS-блока:

1. Временный vhost: только сервер HTTP с location
   /.well-known/acme-challenge/ (шаблон
   scripts/server/nginx/acme-bootstrap.conf.template).
2. Выпуск сертификата (см. ниже).
3. Замена vhost на полную конфигурацию и перезагрузка nginx.

scripts/server/setup.sh выполняет все три фазы автоматически.

### Выпуск и продление сертификата

```bash
sudo mkdir -p /var/www/certbot
sudo certbot certonly --webroot -w /var/www/certbot \
    -d example.com -d www.example.com \
    --email admin@example.com --agree-tos --no-eff-mail
```

Тестовые среды выпускают сертификат в ACME staging, чтобы не расходовать
лимиты продакшена Let's Encrypt: флаг --staging (setup.sh включает его
при CERTBOT_STAGING=True в .env или окружении). Сертификаты staging
не являются доверенными - схема проверяется, браузерные предупреждения
ожидаемы. Переход на продакшен: удалить тестовый сертификат
(sudo certbot delete --cert-name example.com) и повторить выпуск без
--staging.

Продление: пакет certbot поставляет systemd timer certbot.timer
(запуски дважды в сутки, продление - при истечении 1/3 срока).
Перезагрузка nginx после каждого обновления - deploy hook
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

Проверка DNS-01 требуется, когда порты 80/443 недоступны извне
(CGNAT, блокировка провайдером) или нужен wildcard-сертификат.
Выполняется плагином DNS-провайдера домена, например:

```bash
sudo apt-get install -y python3-certbot-dns-cloudflare
sudo certbot certonly --dns-cloudflare \
    --dns-cloudflare-credentials /root/.secrets/cloudflare.ini \
    -d example.com -d www.example.com \
    --email admin@example.com --agree-tos --no-eff-mail
```

Учетные данные плагина хранятся на сервере с правами 600
у пользователя root. Ручной режим (certbot certonly --manual)
для продления по расписанию не годится: требует подтверждения
в интерактиве при каждом продлении. При выборе DNS-01 vhost меняется
только отсутствием location ACME-проверки (проверки идут через DNS).

## 3. Режим Traefik в Docker Compose

Подключается профилем traefik (COMPOSE_PROFILES=traefik или
docker compose --profile traefik up). Конфигурация - labels сервиса
application в compose.yaml; отдельного файла конфигурации нет.

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

Состояние ACME-клиента - traefik/letsencrypt/acme.json (bind-mount,
переживает docker compose down -v). Перенос между серверами -
копированием каталога до первого старта Traefik.

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
   сопровождения (базовый образ, версии certbot, безопасности
   обновления).
5. Продление сертификатов привязано к циклу деплоев (перезапусков
   контейнера), а не к расписанию.
6. Отсутствие dev-режима: без домена и публичного адреса схема
   не работала вовсе.

Вывод: каждый слой получает подходящий инструмент - в контейнере
Traefik (декларативные labels, автоматический ACME), на хосте -
nginx + certbot (systemd timer, deploy hooks).

## 5. Неподдерживаемые варианты

- Общий Traefik-стек сервера (Traefik в отдельном compose-проекте,
  обслуживающий проекты через внешние сети). Потребовал бы
  external-сетей и разбиения единого compose.yaml - осознанно нет;
  сценарий мультипроектного проксирования закрыт хостовым nginx.
- Nginx-в-контейнере - см. пост-мортем в разделе 4.
- Socket-proxy для docker.sock. Traefik с примонтированным
  /var/run/docker.sock эквивалентен правам root на хосте; при желании
  усилить изоляцию используется образ tecnativa/docker-socket-proxy
  (read-only прокси Docker API), но это опция усиления, а не
  поддерживаемый путь проекта: основной вариант прокси (хостовый nginx)
  docker.sock не получает вовсе.
