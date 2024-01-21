# syntax=docker/dockerfile:1

# Определение базового образа.
FROM debian

# Обновление и установка общих системных пакетов.
# Версия утилит PostgreSQL должна совпадать с версией кластера.
ENV POSTGRES_VERSION=15
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y \
    cron \
    curl \
    gnupg \
    locales \
    ca-certificates \
    postgresql-client-${POSTGRES_VERSION} \
    rsync \
    python3 \
    python3-pip \
    pipx \
    wget \
    wkhtmltopdf

# Установить Poetry через pipx и обновить переменную PATH.
RUN pipx ensurepath && \
    pipx install poetry
ENV PATH="/root/.local/bin:$PATH"

# Установить пакеты для подключения к репозиторию NodeSource,
# после чего установить из репозитория заданную версию Node.js.
ENV NODE_VERSION=20
RUN mkdir -p /etc/apt/keyrings && \
    curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg && \
    echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_${NODE_VERSION}.x nodistro main" | tee /etc/apt/sources.list.d/nodesource.list && \
    apt-get update && \
    apt-get install -y nodejs

# Установить локаль.
RUN rm -rf /var/lib/apt/lists/* && \
    localedef -i ru_RU -c -f UTF-8 -A /usr/share/locale/locale.alias ru_RU.UTF-8
ENV LANG=ru_RU.utf8

# Установить MinIO.
RUN wget https://dl.min.io/client/mc/release/linux-amd64/mc && \
    chmod +x mc && \
    mv mc /usr/local/bin/mc

# Создать каталог для проекта и перейти в него.
ENV WORK_DIR=/srv/website
WORKDIR $WORK_DIR

# Установить зависимости Node.js через npm.
COPY package.json package-lock.json ./
RUN npm install

# Установить зависимости Python через Poetry.
COPY pyproject.toml poetry.toml poetry.lock ./
RUN poetry install

# Скопировать в контейнер основное содержимое проекта.
COPY . .

# Установить расписание запуска скриптов в cron.
RUN bash personal_website/scripts/cronjobs.sh

# Выполнить скрипт, запускающий сервер.
ENV PYTHONPATH=.
ENTRYPOINT ["/bin/bash", "personal_website/entrypoint.sh"]
CMD ["0.0.0.0", "8000"]
