---
name: server-setup
description: Первоначальная настройка нового сервера под развертывание проекта (Docker Compose или systemd Gunicorn) или миграция на новый сервер. Скрипты scripts/docker/setup.sh и scripts/server/setup.sh самодостаточны и выполняют установку после клонирования репозитория и заполнения .env; скилл описывает эти подготовительные шаги и проверку после запуска.
---

## Предназначение

Первоначальная настройка нового сервера под развертывание проекта (миграция
на новый сервер, разворот тестовой среды) одним из двух способов запуска
приложения:

- Docker Compose - scripts/docker/setup.sh, рецепты
  docs/deployment/application.md (раздел 2) и proxy.md;
- systemd Gunicorn на хосте (без Docker) - scripts/server/setup.sh, рецепты
  docs/deployment/application.md (раздел 4) и proxy.md (раздел 2).

Сервером может быть виртуальная машина облачного провайдера, физический
или домашний (homelab) сервер. Провайдер-специфичных шагов скилл не
содержит: параметры сервера берутся из консоли провайдера или от
администратора железа.

Границы применения: настройка сервера и запуск приложения. Не применяется
для: деплоя обновлений (scripts/deploy.sh), диагностики прода (скилл
production-diagnostics), операций бэкапов (скиллы backup-restore,
backup-audit), учебного восстановления (скилл restore-drill),
переключения DNS и демонтажа старого сервера.

## Типовые сценарии развертывания

Инфраструктурные сервисы compose.yaml относятся к собственным профилям:
postgres, minio, traefik (переменная COMPOSE_PROFILES в .env, пустое
значение - все внешние). Типовые сочетания параметров:

| Сценарий | COMPOSE_PROFILES | Прокси | БД | Хранилище |
| --- | --- | --- | --- | --- |
| Локальная разработка | postgres | нет | контейнер | filesystem |
| Разработка с S3 | postgres,minio | нет | контейнер | MinIO (s3) |
| Облако-соло (эталон B) | пусто | traefik в compose | managed | S3 удаленный |
| Homelab (эталон C) | postgres,minio | хостовый nginx+certbot | контейнер | MinIO (s3) |
| Bare-metal (эталон D) | Docker нет | хостовый nginx+certbot | systemd-PG или managed | filesystem |

Полная матрица параметров развертывания и эталонных сценариев -
docs/deployment/matrix.md.

## Два режима прокси

- Traefik в compose (профиль traefik) - вариант одиночного сервера
  «все в Docker»: занимает 80/443, сертификаты через TLS-ALPN-01
  (TRAEFIK_CERT_RESOLVER='le'). На тестовых средах ACME staging:
  TRAEFIK_ACME_CASERVER с адресом staging-каталога Let's Encrypt - не
  расходовать лимиты продакшена. В dev TRAEFIK_CERT_RESOLVER пуст -
  self-signed без обращений к Let's Encrypt.
- Хостовый nginx + certbot - основной путь, в том числе для
  мультипроектного homelab-хоста: vhost на проект, приложение всегда
  на 127.0.0.1:${DJANGO_PORT}, прокси-слой проекта ничего не занимает
  (профиль traefik не активируется). Рецепт и двухфазный выпуск
  сертификата - docs/deployment/proxy.md; тестовые среды выпускают
  сертификат в ACME staging (CERTBOT_STAGING=True для
  scripts/server/setup.sh).

Выбор фиксируется в .env набором профилей и (для хостового nginx)
конфигурацией nginx на сервере; контракт приложения не меняется.

## Предусловия

- Целевой сервер существует, SSH-доступ настроен (алиас в `~/.ssh/config`).
- ОС: Debian/Ubuntu x86_64. Рекомендуемые ресурсы: 2 vCPU / 4 ГиБ RAM
  (systemd-режим допускает слабее - без накладных расходов Docker);
  диск от 20 ГиБ.
- Для compose-варианта проверено, что имя Docker-образа в compose.yaml
  совпадает с публикуемым в CI.

## Начальные вопросы пользователю

Перед началом работы спросить у пользователя:

1. Источник кода:
   - SourceCraft: `ssh://ssh.sourcecraft.dev/mikhpo/personal-website.git` - основной источник разработки, main всегда актуален.
   - GitHub: `git@github.com:mikhpo/personal-website.git` - зеркало; может отставать. Перед выбором сверить `git ls-remote` обоих репозиториев и предупредить пользователя при расхождении.
2. Способ запуска приложения: Docker Compose (scripts/docker/setup.sh)
   или systemd Gunicorn (scripts/server/setup.sh, без Docker на хосте).
3. Назначение среды: продакшен или тестовая. От ответа зависят
   сертификаты (ACME staging на тестовых - Traefik и certbot) и cron
   бэкапов.

Ответ на источник определяет remote origin сервера: все последующие
обновления (scripts/deploy.sh) будут тянуться из выбранного репозитория.

## Порядок выполнения: Docker Compose

### 1. Базовая подготовка ОС

    sudo apt-get update && sudo apt-get install -y cron curl git gnupg ca-certificates ufw

Файрвол (порты 22, 80, 443):

    sudo ufw allow 22/tcp && sudo ufw allow 80/tcp && sudo ufw allow 443/tcp && echo y | sudo ufw enable

### 2. Docker

    curl -fsSL https://get.docker.com | sudo sh
    sudo usermod -aG docker <пользователь>
    sudo systemctl enable docker.service containerd.service

Не-root пользователю команды Docker выполнять через `sg docker -c "..."` (членство в группе применяется после нового логина).

### 3. Клонирование репозитория

SSH-ключ сервера и настройка подключения (ключ добавляется в аккаунт SourceCraft через веб-интерфейс или в профиль GitHub; API для этого нет):

    ssh-keygen -t ed25519 -N "" -f ~/.ssh/id_ed25519
    cat ~/.ssh/id_ed25519.pub

`~/.ssh/config` (для SourceCraft):

    Host ssh.sourcecraft.dev
      User git
      IdentityFile ~/.ssh/id_ed25519
      IdentitiesOnly yes

Целевой каталог развертывания - `/srv/personal-website`. Создать заранее и передать пользователю владение (каталог /srv по умолчанию принадлежит root):

    sudo mkdir -p /srv/personal-website && sudo chown <пользователь>:<группа> /srv/personal-website

Клонирование (адрес - из выбранного источника):

    git clone ssh://ssh.sourcecraft.dev/mikhpo/personal-website.git /srv/personal-website

### 4. Файл .env

Источник значений - .env действующего сервера (перенести по SSH между серверами). Корректировки для compose-среды:

- Удалить абсолютные пути хоста (STORAGE_ROOT, STATIC_ROOT, BACKUP_ROOT, LOGS_ROOT, TEMP_ROOT) - контейнеру задаются compose-переменные.
- Экранировать каждый `$` удвоением (`$$`) во всех значениях с `$` (например SECRET_KEY): compose интерполирует значения .env, неэкранированный фрагмент молча заменяется пустой строкой (в systemd-режиме экранирование не нужно). Проверка: `docker compose config` не выдаёт предупреждений вида `The "x" variable is not set`.
- Добавить: `DOCKER_ENV=True`, `TRAEFIK_HTTP_PORT=80`, `DJANGO_PORT=8000`, `ACME_EMAIL=<email>`.
- COMPOSE_PROFILES по сценарию из матрицы: пусто при внешних БД и S3
  с прокси на хосте; добавить traefik, если терминирование TLS выполняет
  Traefik в compose; postgres/minio - при локальных контейнерах.
- `TRAEFIK_CERT_RESOLVER`: пустая строка для тестовых сред (ACME пассивен,
  self-signed); `le` для продакшена. На тестовых средах с выпуском
  сертификатов - `TRAEFIK_ACME_CASERVER` со staging-URL.
- `POSTGRES_SSL_CERT_HOST_PATH=<домашний каталог>/.postgresql/root.crt` - путь на хосте для bind-mount (если пользователь не root).
- Секция «Бэкапы» (только основной сервер): цели `BACKUP_TARGET_<ИМЯ>`
  (префиксы mc:/rclone:) и списки BACKUP_DB_TARGETS/BACKUP_MEDIA_TARGETS;
  схема и настройка алиасов mc / remotes rclone -
  docs/deployment/backups.md.

`chmod 600 .env`.

### 5. Сертификат PostgreSQL, каталоги

    bash scripts/pgcert.sh
    mkdir -p storage static backups logs temp traefik/letsencrypt

Каталог traefik/letsencrypt нужен только при профиле traefik.

### 6. Запуск контейнеров

    sg docker -c "docker compose pull"
    sg docker -c "docker compose up -d"

Cron бэкапов (cronjobs.sh) добавлять только на основной сервер: на параллельном сервере те же цели бэкапов конфликтуют с основной средой.

### 7. Проверка

    sg docker -c "docker compose ps"                        # контейнеры healthy
    curl -s http://127.0.0.1:8000/health/                   # 200 ok
    sg docker -c "docker compose logs application"          # нет tracebacks, секретов в выводе

Сквозная проверка через Traefik без DNS (переменные: `ip` - адрес сервера, `domain` - домен из DOMAIN_NAME):

    curl -sI --resolve ${domain}:80:${ip} http://${domain}/                  # 301 -> https
    curl -sk -o /dev/null -w "%{http_code}\n" --resolve ${domain}:443:${ip} https://${domain}/main/   # 200

При self-signed (TRAEFIK_CERT_RESOLVER пуст): издатель сертификата CN=TRAEFIK DEFAULT CERT, файл traefik/letsencrypt/acme.json отсутствует, обращений к Let's Encrypt нет. Работа с БД подтверждается строкой миграций в логах; с S3 - S3-адресами статики в HTML.

## Порядок выполнения: systemd Gunicorn

1. Шаги 1 (без Docker), 3 (клонирование) - как выше; файрволу достаточно
   портов 22/80/443 (приложение и БД слушают только локальный интерфейс).
2. .env в корне рабочей копии: абсолютные пути каталогов данных
   (STORAGE_ROOT и остальные) на хосте, `DEPLOY_MODE=systemd`,
   экранирование `$$` не требуется (systemd читает значения буквально).
3. Запуск `bash scripts/server/setup.sh`: пакеты (python3, poetry, node,
   postgresql-client, nginx, certbot, rclone, mc), зависимости проекта,
   systemd-юнит personal-website.service, vhost nginx и сертификат
   certbot (двухфазно, webroot), cron бэкапов.

Проверка после установки:

    systemctl status personal-website nginx
    curl -s http://127.0.0.1:8000/health/         # 200 ok
    curl -sI http://${domain}/                     # 301 -> https (vhost nginx)
    journalctl -u personal-website -f              # логи Gunicorn

Рецепты и объяснения каждой настройки - docs/deployment/application.md
(раздел 4) и docs/deployment/proxy.md (раздел 2). Вариант systemd-режима
с unix-сокетом (socket activation, мультипроектный хост) - там же,
application.md раздел 4.

## Сценарий homelab (мультипроектный хост)

- Прокси-слой проекта не занимает 80/443: профиль traefik не
  активируется, терминирование TLS - общий хостовый nginx по рецепту
  docs/deployment/proxy.md (vhost на проект; рядом живут vhost'ы других
  проектов).
- Приложение публикуется только на 127.0.0.1:${DJANGO_PORT}; порт
  выбирается не занятым другими проектами хоста.
- База данных: контейнер профиля postgres, systemd-PG (рецепт
  docs/deployment/database.md) или managed-кластер - без изменений
  приложения.
- Файрвол: наружу открыты только 22/80/443; доступ к БД и хранилищу
  других проектов не открывается.

## Типовые проблемы

- `docker compose pull` падает object not found: имя образа в compose.yaml не совпадает с публикуемым в CI (дефис против подчёркивания). Обход - override-файл с верным именем; правильное решение - унификация имени в репозитории.
- Значения переменных с `$` искажаются в compose-среде: неэкранированы в .env. Симптом - предупреждение вида `The "x" variable is not set` в выводе compose. В systemd-среде наоборот: экранированные `$$` остаются в значении буквально.
- Сертификаты не выпускаются на тестовой среде: проверьте, что staging (TRAEFIK_ACME_CASERVER / certbot --staging) осознанно отключен перед переходом в продакшен, и что лимиты Let's Encrypt не исчерпаны.
- systemd-юнит падает на старте циклически: ExecStartPre не может подключиться к БД (внешняя база еще не готова) - юнит перезапустится сам (Restart=on-failure); устойчивый отказ смотреть в journalctl -u personal-website.

## Ограничения

- Не выпускать сертификаты Let's Encrypt продакшена на тестовых средах:
  Traefik - TRAEFIK_ACME_CASERVER со staging-URL или пустой
  TRAEFIK_CERT_RESOLVER, certbot - CERTBOT_STAGING=True.
- Не переключать DNS и не трогать действующий прод во время настройки параллельного сервера.
- Не добавлять cron бэкапов на тестовые серверы.
- Деструктивные операции (удаление сервера, сброс БД) - только с явного разрешения пользователя.
