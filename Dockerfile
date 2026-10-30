# syntax=docker/dockerfile:1

# Этап 1: Сборка Node.js для фронтенда React
FROM node:22-bookworm AS node-builder

# Создать каталог для проекта и перейти в него.
WORKDIR /app

# Скопировать конфигурационные файлы и зависимости Node.js
COPY package.json package-lock.json ./

# Скопировать конфигурационные файлы в frontend/ директорию
COPY frontend/webpack.config.js frontend/.babelrc frontend/jest.config.js frontend/jest.setup.js frontend/tsconfig.json ./frontend/

# Скопировать исходники frontend
COPY frontend/src ./frontend/src

# Установить зависимости Node.js через npm (создаст node_modules в /app)
RUN npm ci && \
    npm cache clean --force

# Сборка React приложения
RUN npm run build

# Этап 2: Приложение Python
FROM python:3.14-trixie

# Обновление и установка общих системных пакетов.
# Версия утилит PostgreSQL должна совпадать с версией кластера.
ENV POSTGRES_VERSION=17

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y \
    curl \
    gnupg \
    gettext \
    locales \
    ca-certificates \
    postgresql-client-${POSTGRES_VERSION} \
    rclone \
    rsync && \
    rm -rf /var/lib/apt/lists/*

# Установить uv (двоичные файлы из официального образа, версия закреплена).
COPY --from=ghcr.io/astral-sh/uv:0.13.6 /uv /uvx /bin/

# Установить локаль.
RUN localedef -i ru_RU -c -f UTF-8 -A /usr/share/locale/locale.alias ru_RU.UTF-8
ENV LANG=ru_RU.utf8

# Создать каталог для проекта и перейти в него.
ENV WORK_DIR=/srv/website
WORKDIR $WORK_DIR

# Метка, по которой scripts/docker/deploy.sh ограничивает docker image prune
# образами этого проекта, не затрагивая образы других проектов хоста.
LABEL org.opencontainers.image.title="personal-website"

# Установить зависимости Python через uv вместе с dev-зависимостями:
# тесты выполняются внутри контейнера на этапе CI.
COPY pyproject.toml uv.lock .python-version ./
RUN --mount=type=cache,target=/root/.cache/uv uv sync --frozen

# Скопировать в контейнер основное содержимое проекта.
COPY . .

# Копирование собранного React бандла
COPY --from=node-builder /app/frontend/dist $WORK_DIR/frontend/dist
COPY --from=node-builder /app/frontend/webpack-stats.json $WORK_DIR/frontend/webpack-stats.json

# Компиляция каталогов переводов проекта (backend/locale).
RUN cd backend && uv run --no-sync python manage.py compilemessages

# Выполнить скрипт, запускающий сервер.
ENV PYTHONPATH=.
ENTRYPOINT ["/bin/bash", "backend/entrypoint.sh"]
