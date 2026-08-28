# Персональный сайт

Проект по созданию персонального сайта. Конфигурация, функции, классы и шаблоны максимально абстрактными - так, чтобы можно было использовать проект в качестве шаблона для другого сайта.

## Функциональность сайта

![context](./docs/diagrams/out/context/context.svg)

Для сайта реализован следующий функционал:

* Блог: статьи и комментарии.
* Галерея: альбомы и фотографии.
* Скрипты: ручной и автоматический запуск, просмотр логов.
* Пользователи: регистрация и авторизация.
* Администрирование: CRUD, настройка ролей.

## Технологический стек

Проект использует следующие технологии:

* [Django](https://www.djangoproject.com/) (бэкенд)
* [Django REST Framework](https://www.django-rest-framework.com/) (REST API)
* [React](https://react.dev/) 19 (фронтенд)
* [Webpack](https://webpack.js.org/) 5 (сборка фронтенда)
* [Bootstrap](https://getbootstrap.com/) 5 (стили)
* [PostgreSQL](https://www.postgresql.org/) (база данных)
* [MinIO](https://min.io/) (объектное хранилище, S3-совместимое)

Проект адаптирован для развертывания на Linux. Для развертывания используются следующие технологии:

* [Gunicorn](https://gunicorn.org/) (HTTP-сервер)
* [Traefik](https://traefik.io/) (прокси-сервер, TLS-терминирование)
* [Docker](https://www.docker.com/) (контейнеризация)

![container](./docs/diagrams/out/container/container.svg)

## Структура проекта

Проект использует монорепозиторийную структуру с разделением на бэкенд и фронтенд:

    personal-website/           # корневая директория репозитория
    ├── .git/
    ├── .venv/
    ├── .gitignore
    ├── requirements.txt
    ├── pyproject.toml
    ├── package.json
    ├── compose.yaml           # сервисы Docker Compose (профили postgres, minio, traefik)
    ├── scripts/               # скрипты деплоя, бэкапов и первичной настройки сервера
    ├── tools/                 # вспомогательные скрипты для разработки
    ├── tests/                 # пакет интеграционных тестов
    ├── traefik/               # состояние ACME-клиента (сертификаты Let's Encrypt)
    ├── backend/                # Django бэкенд
    │   ├── manage.py
    │   ├── Dockerfile          # параметры сборки контейнера приложения
    │   ├── entrypoint.sh       # скрипт для запуска приложения в контейнере
    │   ├── personal_website/   # директория с настройками проекта
    │   │   ├── __init__.py
    │   │   ├── settings.py
    │   │   ├── urls.py
    │   │   ├── asgi.py
    │   │   ├── storages.py     # настройки файловых хранилищ (локальная файловая система, S3)
    │   │   └── wsgi.py
    │   ├── accounts/           # приложение Django (управление пользователями)
    │   ├── blog/               # приложение Django (блог)
    │   ├── gallery/            # приложение Django (галерея)
    │   ├── main/               # приложение Django (главная страница)
    │   ├── api/                # приложение Django (REST API)
    │   ├── backup/             # приложение Django (резервное копирование)
    │   ├── staticfiles/        # статические файлы Django
    │   ├── templates/          # шаблоны Django
    │   └── tests/              # пакет тестов бэкенда
    └── frontend/               # React фронтенд
        ├── src/                # исходный код React компонентов
        │   ├── components/     # React компоненты
        │   ├── index.js        # точка входа
        │   └── ...
        ├── webpack.config.js   # конфигурация Webpack
        ├── jest.config.js      # конфигурация Jest
        ├── eslint.config.mjs   # конфигурация ESLint
        ├── .babelrc            # конфигурация Babel
        └── package.json       # зависимости фронтенда (симлинк на корневой)

## Административные команды

Для запуска веб-сервера Django используется команда:

    python backend/manage.py runserver

После внесения изменений в модели необходимо произвести миграцию таблиц базы данных. Django имеет встроенный инструмент управления миграциями. Для проведения миграций используются команды:

    python backend/manage.py makemigrations
    python backend/manage.py migrate

В данном проекте созданы пользовательские административные команды, которые используются для выполнения обособленных скриптов. Вызываются аналогичным образом:

    python backend/manage.py <имя команды>

## Режим разработки

Для локальной разработки необходимо запускать фронтенд и бэкенд отдельно в режиме наблюдения за изменениями файлов.

Каждый инфраструктурный сервис в compose.yaml относится к собственному профилю: postgres, minio, traefik. Для типичной локальной разработки достаточно профиля postgres с файловым хранилищем. Профили активируются через переменную `COMPOSE_PROFILES` в файле `.env` (например, `postgres` или `postgres,minio`) или через флаг `docker compose --profile <имя>`. Без активных профилей поднимается только сервис application - использовать этот режим, если база данных, объектное хранилище и обратный прокси предоставляются вне Docker Compose.

### Запуск с использованием Taskfile (рекомендуется)

* Запустить сервер разработки с PostgreSQL: `task runserver`
* Запустить в режиме hot-reload: `task watch`
* Полный цикл тестирования: `task test`
* Статический анализ: `task check`

### Ручной запуск режима разработки

* Запустить базу данных PostgreSQL через Docker Compose: `docker compose up -d postgres`
* Применить миграции базы данных: `poetry run python backend/manage.py migrate`
* Собрать статические файлы: `poetry run python backend/manage.py collectstatic --noinput`
* Запустить сборку фронтенда в режиме наблюдения (в первом терминале): `npm run dev`
* Запустить сервер разработки Django (во втором терминале): `poetry run python backend/manage.py runserver`
* Открыть сайт в браузере: <http://localhost:8000> (админ-панель: <http://localhost:8000/admin/>)

Явное указание имени сервиса в команде активирует профиль автоматически, поэтому для запуска отдельных инфраструктурных сервисов флаг не требуется.

### Frontend разработка

* Сборка в режиме наблюдения: `npm run dev`
* Запуск Jest тестов: `npm test`
* Запуск тестов в режиме наблюдения: `npm run test:watch`
* Production сборка: `npm run build`
* Линтинг JavaScript: `npm run eslint`

### Остановка режима разработки

* Нажать `Ctrl+C` в обоих терминалах для остановки процессов
* Остановить контейнеры Docker: `docker compose down` (или `docker-compose down` для V1)

## Развертывание

Развертывание настраивается пятью независимыми параметрами: способ запуска приложения (Docker Compose / docker run / systemd Gunicorn), размещение базы данных (managed / контейнер / systemd), тип хранилища (filesystem / S3 / MinIO), вариант прокси (Traefik в compose / хостовый nginx + certbot) и конфигурация бэкапов. Поддерживаемые сочетания зафиксированы эталонными сценариями - [docs/deployment/matrix.md](./docs/deployment/matrix.md).

Конфигурация задается одним файлом `.env` с секциями по параметрам (полный список переменных - [.env.example](./.env.example)). Рецепты по параметрам:

* [Запуск приложения](./docs/deployment/application.md) - контракт приложения, Compose, docker run, systemd Gunicorn
* [База данных](./docs/deployment/database.md) - managed-кластер, контейнер, systemd-PG, SSL, мажорный апгрейд
* [Файловое хранилище](./docs/deployment/storage.md) - filesystem, S3, MinIO, статика
* [Прокси и сертификаты](./docs/deployment/proxy.md) - хостовый nginx + certbot, Traefik, перенос сертификатов
* [Резервное копирование](./docs/deployment/backups.md) - цели, расписание, восстановление, смена типа хранилища

Первичная настройка сервера автоматизирована: `bash scripts/docker/setup.sh` (Compose) или `bash scripts/server/setup.sh` (systemd); порядок действий описан в скилле server-setup. Обновление приложения выполняется общим диспетчером `bash scripts/deploy.sh` - им же пользуется CI/CD (механизм выбирается переменной `DEPLOY_MODE`).

Эндпоинт `/health/` (проверочный SELECT 1) - единая точка живости приложения во всех режимах запуска.

## Приложения проекта

Проект содержит следующие приложения:

* `accounts` - управление учетными записями
* `main` - главная страница сайта
* `blog` - блог
* `gallery` - галерея
* `backup` - резервное копирование БД и медиа

Модель данных проекта:

![apps_models.png](docs/images/apps_models.png)

### Контроль учетных записей

Приложение управляет процессом создания учетных записей. Базовая модель аутентификации пользователей Django слишком слабая для серьезного использования. Данное приложение не создает альтернативную модель пользователя, но накладывает дополнительные ограничения, расширяя функционал формы регистрации:

1. Обязательно указание адреса электронной почты.
2. Адрес электронной почты должен быть уникальным.
3. Имя и фамилия не должны совпадать.

### Главная

Управление главной страницей сайта. Главная страница служит витриной для перехода к другим разделам сайта.

### Блог

Одно из ключевых приложений сайта - управление блогом и комментариями к записям в нем.

В рамках блога используются следующие модели:

1. Статья - как единичная запись в блоге, ключевая модель приложения.
2. Комментарий - пользователи могут оставлять к статьям комментарии.
3. Серия - статьи могут объединяться в серии.
4. Тема - серии могут объединяться по темам.
5. Категория - темы могут объединяться по категориям.

Статьи можно создавать и редактировать через административный интерфейс. Тело статьи редактируется при помощи WYSIWYG-виджета TinyMCE. Статью можно создать, но не опубликовать - для этого есть специальный флаг. При помощи него же опубликованную статью можно снять с публикации.

### Галерея

Управление фотографиями и альбомами.

Модели галереи:

1. Фотография
1. Альбом
1. Тэг

Управлять альбомами, фотографиями и тэгами можно через административный интерфейс. Также через пользовательский интерфейс галереи доступна пакетная загрузка фотографий в альбом.

Фотографии и альбомы могут быть публичными и непубличными. Публичность объекта определяет его видимость для пользователя и поисковых машин.

Для фотографий реализован автоматический парсинг метаданных в формате EXIF.

### Резервное копирование

Резервное копирование БД и медиа реализовано приложением `backup` с management-командами: `backup`, `backup_db`, `backup_media` (с флагом `--verify` для проверки целей) создают копии, `restore_db`, `restore_media` - восстанавливают их. Команды запускаются хостовым скриптом `scripts/backup.sh` по расписанию cron (альтернатива - systemd timer). Цели бэкапов описываются в `.env` переменными `BACKUP_TARGET_<ИМЯ>` с префиксами `mc:` (MinIO Client) и `rclone:`. Настройка и семантика - [docs/deployment/backups.md](./docs/deployment/backups.md).

## REST API

Проект предоставляет REST API для взаимодействия с фронтендом и сторонними приложениями.

### Технологии API

* [Django REST Framework](https://www.django-rest-framework.org/) - фреймворк для создания REST API
* [djangorestframework-simplejwt](https://django-restframework-simplejwt.readthedocs.io/) - JWT аутентификация
* [drf-spectacular](https://drf-spectacular.readthedocs.io/) - генерация OpenAPI 3.0 схемы
* [django-filter](https://django-filter.readthedocs.io/) - фильтрация наборов данных

Документация работает в offline режиме за счет drf-spectacular-sidecar.

## Frontend

Фронтенд построен на React с использованием Webpack для сборки и интеграции с Django.

### Технологии фронтенда

* [React](https://react.dev/) 19 - UI библиотека
* [Bootstrap](https://getbootstrap.com/) 5 - стили
* [Webpack](https://webpack.js.org/) 5 - сборка
* [Babel](https://babeljs.io/) - транспиляция JSX и ES6+
* [Jest](https://jestjs.io/) - тестирование компонентов
* [django-webpack-loader](https://github.com/django-webpack/django-webpack-loader) - интеграция бандлов с Django

### Структура фронтенда

    frontend/
    ├── src/
    │   ├── components/     # React компоненты
    │   │   ├── Alert/      # Алерты и уведомления
    │   │   ├── Blog/       # Компоненты блога
    │   │   ├── Gallery/    # Компоненты галереи
    │   │   ├── Main/       # Компоненты главной страницы
    │   │   ├── Navbar/     # Навигация
    │   │   ├── Card/       # Базовый компонент карточки
    │   │   ├── Pagination/ # Пагинация
    │   │   └── Spinner/    # Индикатор загрузки
    │   ├── hooks/          # Кастомные React хуки
    │   ├── services/       # API сервисы
    │   ├── utils/          # Утилиты
    │   └── index.js        # Точка входа
    ├── dist/               # Production бандл
    └── webpack.config.js   # Конфигурация Webpack

### Команды фронтенда

| Команда              | Описание                   |
| -------------------- | -------------------------- |
| `npm run dev`        | Сборка в режиме наблюдения |
| `npm run build`      | Production сборка          |
| `npm test`           | Запуск Jest тестов         |
| `npm run test:watch` | Тесты в режиме наблюдения  |
| `npm run eslint`     | Проверка кода ESLint       |

### Интеграция с Django

React компоненты рендерятся в Django шаблонах через `django-webpack-loader`:

    {% load webpack_loader %}
    <script src="{% webpack_static 'frontend/dist/js/main.js' %}"></script>
    <div id="react-mount-point"></div>

## CI/CD

Проект использует две системы автоматизации: SourceCraft CI (основная - тестирование, сборка, релиз и деплой) и GitHub Actions (зеркало для проверки кода и сборки образов). Развертывание на сервере выполняет deploy-workflow SourceCraft вызовом `scripts/deploy.sh` (целевой каталог /srv/personal-website).

Workflows SourceCraft ([.sourcecraft/ci.yaml](./.sourcecraft/ci.yaml)):

1. lint-workflow - статический анализ и линтинг, при pull request
2. test-workflow - тестирование, при pull request
3. build-workflow - сборка и тестирование образа приложения, при pull request
4. release-workflow - релиз Docker-образа, при пуше в основную ветку
5. deploy-workflow - деплой приложения на сервер (release -> deploy), вручную

Workflows GitHub Actions ([.github/workflows/](./.github/workflows/)): test.yml - тестирование кода и контейнера, release.yml - публикация образа в реестры, deploy.yml - деплой на сервер.

Состав задач и требуемые секреты перечислены в комментариях файлов конфигурации соответствующих workflow.

## Дополнительная информация

* [Матрица развертывания и рецепты docs/deployment/](./docs/deployment/matrix.md)
* [Руководство по разработке](./docs/CONTRIBUTING.md)
* [История изменений](./docs/CHANGELOG.md)
