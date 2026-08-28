# Матрица развертывания

Проект настраивается не набором готовых конфигураций, а пятью
независимыми параметрами развертывания: способ запуска приложения,
размещение базы данных, тип хранилища, вариант прокси, конфигурация
бэкапов. Каждый настраивается отдельно; точка сборки - один .env
с секциями (см. [.env.example](../../.env.example)). Код приложения
по режимам развертывания не ветвится.

Содержание:

1. Параметры развертывания
2. Эталонные сценарии
3. Чеклисты эталонов
4. Что поддерживается и что осознанно нет

Документы по параметрам: [application.md](./application.md),
[database.md](./database.md), [storage.md](./storage.md),
[proxy.md](./proxy.md), [backups.md](./backups.md).

## 1. Параметры развертывания

| Параметр | Варианты | Переменные .env |
| --- | --- | --- |
| Запуск приложения | Docker Compose / docker run / systemd Gunicorn | DEPLOY_MODE, DJANGO_PORT, GUNICORN_WORKERS |
| База данных | managed-кластер / контейнер compose / systemd на хосте | POSTGRES_*, профиль postgres |
| Хранилище | filesystem / S3 удаленный / MinIO локальный | STORAGE_TYPE, AWS_*, профиль minio |
| Прокси | Traefik в compose / хостовый nginx + certbot | COMPOSE_PROFILES, TRAEFIK_*, ACME_EMAIL |
| Бэкапы | источники x цели (mc:, rclone:), расписание | BACKUP_*, cron/systemd timer |

Бэкапы настраиваются независимо от остальных параметров в любом
сценарии. Сочетания вариантов образуют сценарии развертывания;
поддерживаемые зафиксированы эталонами ниже - тестируется это, а не
все N x M комбинации.

## 2. Эталонные сценарии

| Параметр | A «dev-local» | B «облако-соло» | C «homelab» | D «bare-metal» |
| --- | --- | --- | --- | --- |
| Запуск приложения | Compose (разработка) | Compose | Compose | systemd Gunicorn |
| База данных | контейнер compose | managed | контейнер compose | systemd-PG |
| Хранилище | filesystem | S3 удаленный | MinIO локальный (s3) | filesystem |
| Прокси | Traefik в compose | Traefik в compose | хостовый nginx + certbot | хостовый nginx + certbot |
| COMPOSE_PROFILES | postgres,minio,traefik | traefik | postgres,minio | - (Docker нет) |
| Проверка | task test-integration | релизный деплой CI | compose config + тестовый хост | чеклист + тестовый хост |

Сценарий B - действующий прод: проверяется каждым релизным деплоем
(цепочка release-deploy CI), отдельной джобы не имеет. Сценарии C и D
обкатываются на тестовом хосте перед использованием; сценарий A -
локальная разработка и интеграционные тесты.

## 3. Чеклисты эталонов

### A «dev-local»

1. `COMPOSE_PROFILES='postgres,minio,traefik'`, `STORAGE_TYPE='filesystem'`,
   `TRAEFIK_CERT_RESOLVER=''` (self-signed, обращений к Let's Encrypt нет);
2. `docker compose up -d --wait` - все сервисы healthy;
3. `curl -s http://127.0.0.1:${DJANGO_PORT}/health/` - 200;
4. `task test-integration` - интеграционные тесты проходят
   (маршрутизация traefik, robots.txt, favicon, API);
5. признаки пассивного ACME: `traefik/letsencrypt/acme.json` отсутствует
   или пуст.

### B «облако-соло»

1. Профили: только traefik; POSTGRES_* - FQDN managed-кластера,
   `POSTGRES_SSL_MODE='verify-full'`, сертификат доставлен pgcert.sh;
2. `STORAGE_TYPE='s3'`, AWS_* - бакет провайдера; статика - из бакета;
3. `TRAEFIK_CERT_RESOLVER='le'`, `ACME_EMAIL` задан;
4. деплой `bash scripts/deploy.sh` (вызывается deploy-workflow CI):
   бэкап, обновление, контейнеры пересозданы;
5. `https://<домен>/health/` - 200, сертификат валиден;
6. бэкапы настроены ([backups.md](./backups.md)): `backup --verify`
   проходит по всем целям.

### C «homelab»

1. Профили postgres,minio; хостовый nginx + certbot по рецепту
   [proxy.md](./proxy.md) (vhost проекта, сертификат certonly webroot;
   тестовые среды - ACME staging);
2. `docker compose config` без предупреждений (валидация сочетания
   переменных);
3. приложение и инфраструктура подняты, `/health/` - 200 через vhost;
4. статика и медиа читаются из MinIO (адреса S3 в HTML);
5. бэкапы: цели настроены, `backup --verify` проходит.

### D «bare-metal»

1. systemd Gunicorn по рецепту [application.md](./application.md)
   (раздел 4), при мультипроектном хосте - вариант unix-сокета;
2. systemd-PG по рецепту [database.md](./database.md) (раздел 4):
   каталог данных, scram-sha-256, доступ приложения;
3. nginx + certbot: vhost и сертификат ([proxy.md](./proxy.md));
4. `STORAGE_TYPE='filesystem'`, пути каталогов данных на хосте;
5. деплой `bash scripts/deploy.sh` при `DEPLOY_MODE='systemd'`;
6. `/health/` - 200, `journalctl -u personal-website` - без ошибок;
7. бэкапы: cron (cronjobs.sh) или systemd timer, цели, verify.

## 4. Что поддерживается и что осознанно нет

Поддерживается:

- перечисленные варианты пяти параметров и их сочетания в рамках
  эталонных сценариев;
- хостовые скрипты автоматизации повторяющихся шагов (setup, deploy,
  backup, cronjobs);
- systemd timer как альтернатива cron для расписания бэкапов.

Осознанно не поддерживается:

- общий Traefik-стек сервера с external-сетями (мультипроектное
  проксирование закрывает хостовый nginx);
- nginx-в-контейнере (пост-мортем - [proxy.md](./proxy.md), раздел 4);
- overlay-файлы compose - единый compose.yaml с профилями;
- шифрование бэкапов и restic (файлы в целях остаются обычными);
- модели заданий бэкапов и админка бэкапов - только management-команды
  и расписание;
- Kubernetes, Ansible, Terraform, панели типа Dokploy/Coolify;
- разбиение settings.py и дробление .env на файлы;
- значение по умолчанию для DOMAIN_NAME (домен не попадает в git).

Vendor-lock сместился в Docker Compose - осознанное ограничение:
матрица фиксирует «что поддерживается», а не «что мыслимо»;
сценарий D показывает путь без Docker вовсе.
