# Skill: server-setup

## Предназначение

Первоначальная настройка нового сервера под Docker-развертывание проекта (миграция на новый сервер, разворот тестовой среды). Скилл дополняет scripts/docker/setup.sh знанием об окружении, которое скрипт не учитывает.

Сервером может быть как виртуальная машина облачного провайдера, так и физический сервер: целевая схема развертывания едина — Docker Compose, отличий в порядке настройки нет. Провайдер-специфичных шагов скилл не содержит: параметры сервера (IP, пользователь, ресурсы) берутся из консоли провайдера или от администратора железа.

Границы применения: настройка сервера и запуск контейнеров. Не применяется для: деплоя обновлений (scripts/docker/deploy.sh), диагностики прода (скилл production-diagnostics), переключения DNS и демонтажа старого сервера. Скрипты scripts/server/ (запуск без Docker) к скиллу не относятся.

## Предусловия

- Целевой сервер существует, SSH-доступ настроен (алиас в `~/.ssh/config`).
- ОС: Debian/Ubuntu x86_64. Рекомендуемые ресурсы: 2 vCPU / 4 ГиБ RAM; диск от 20 ГиБ.
- Перед запуском проверить, что имя Docker-образа в compose.yaml совпадает с публикуемым в CI, а entrypoint.sh совместим с STORAGE_TYPE=s3 (симптомы — в типовых проблемах ниже).

## Начальные вопросы пользователю

Перед началом работы спросить у пользователя:

1. Источник кода:
   - SourceCraft: `ssh://ssh.sourcecraft.dev/mikhpo/personal-website.git` — основной источник разработки, main всегда актуален.
   - GitHub: `git@github.com:mikhpo/personal-website.git` — зеркало; может отставать. Перед выбором сверить `git ls-remote` обоих репозиториев и предупредить пользователя при расхождении.
2. Назначение среды: продакшен или тестовая. От ответа зависят сертификаты (см. ограничения) и cron бэкапов.

Ответ на источник определяет remote origin сервера: все последующие обновления (deploy.sh) будут тянуться из выбранного репозитория.

## Порядок выполнения

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

Целевой каталог развертывания — `/srv/personal-website`. Создать заранее и передать пользователю владение (каталог /srv по умолчанию принадлежит root):

    sudo mkdir -p /srv/personal-website && sudo chown <пользователь>:<группа> /srv/personal-website

Клонирование (адрес — из выбранного источника):

    git clone ssh://ssh.sourcecraft.dev/mikhpo/personal-website.git /srv/personal-website

### 4. Файл .env

Источник значений - .env действующего сервера (перенести по SSH между серверами). Корректировки для Docker-среды:

- Удалить абсолютные пути хоста (STORAGE_ROOT, STATIC_ROOT, BACKUP_ROOT, LOGS_ROOT, TEMP_ROOT) — контейнеру задаются compose-переменные.
- Экранировать каждый `$` удвоением (`$$`) во всех значениях с `$` (например SECRET_KEY): compose выполняет интерполяцию значений .env, неэкранированный фрагмент молча заменяется пустой строкой. Проверка: `docker compose config` не выдаёт предупреждений вида `The "x" variable is not set`.
- Добавить: `DOCKER_ENV=True`, `TRAEFIK_HTTP_PORT=80`, `DJANGO_PORT=8000`, `ACME_EMAIL=<email>`.
- `TRAEFIK_CERT_RESOLVER`: пустая строка для тестовых сред (ACME пассивен, self-signed); `le` для продакшена.
- `POSTGRES_SSL_CERT_HOST_PATH=<домашний каталог>/.postgresql/root.crt` — путь на хосте для bind-mount (если пользователь не root).
- Не задавать `COMPOSE_PROFILES` при внешних PostgreSQL и S3.

`chmod 600 .env`.

### 5. Сертификат PostgreSQL, каталоги

    bash scripts/pgcert.sh
    mkdir -p storage static backups logs temp traefik/letsencrypt

### 6. Запуск контейнеров

    sg docker -c "docker compose pull"
    sg docker -c "docker compose up -d"

Cron бэкапов (cronjobs.sh) добавлять только на основной сервер: на параллельном сервере тот же mirror в общий бакет бэкапов конфликтует с основной средой.

### 7. Проверка

    sg docker -c "docker compose ps"                        # оба контейнера healthy
    sg docker -c "docker compose logs website"              # нет tracebacks, секретов в выводе

Сквозная проверка через Traefik без DNS (переменные: `ip` — адрес сервера, `domain` — домен из DOMAIN_NAME):

    curl -sI --resolve ${domain}:80:${ip} http://${domain}/                  # 301 -> https
    curl -sk -o /dev/null -w "%{http_code}\n" --resolve ${domain}:443:${ip} https://${domain}/main/   # 200

При self-signed (TRAEFIK_CERT_RESOLVER пуст): издатель сертификата CN=TRAEFIK DEFAULT CERT, файл traefik/letsencrypt/acme.json отсутствует, обращений к Let's Encrypt нет. Работа с БД подтверждается строкой миграций в логах; с S3 — S3-адресами статики в HTML.

## Типовые проблемы

- `docker compose pull` падает object not found: имя образа в compose.yaml не совпадает с публикуемым в CI (дефис против подчёркивания). Обход — override-файл с верным именем; правильное решение — унификация имени в репозитории.
- Контейнер website уходит в crash-loop при STORAGE_TYPE=s3: mc admin info в entrypoint.sh применим только к настоящему MinIO. Обход — патченный entrypoint через volume mount; правильное решение — фикс в репозитории.
- Значения переменных с `$` искажаются: неэкранированы в .env. Симптом — предупреждение вида `The "x" variable is not set` в выводе compose.
- Секреты в `docker compose logs`: признак eval export от несуществующего .env внутри контейнера в entrypoint.sh.

## Ограничения

- Не выпускать сертификаты Let's Encrypt на тестовых средах (TRAEFIK_CERT_RESOLVER пуст).
- Не переключать DNS и не трогать действующий прод во время настройки параллельного сервера.
- Не добавлять cron бэкапов на тестовые серверы.
- Деструктивные операции (удаление сервера, сброс БД) — только с явного разрешения пользователя.
