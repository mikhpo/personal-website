# syntax=docker/dockerfile:1

# Определение базового образа.
FROM debian

# Обновление и установка общих системных пакетов.
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y \
    cron \
    curl \
    gnupg \
    locales \
    ca-certificates \
    postgresql-client \
    python3 \
    python3 \
    python3-pip \
    pipx \
    wkhtmltopdf

# Установить Poetry через pipx и обновить переменную PATH.
RUN pipx ensurepath && \
    pipx install poetry
ENV PATH="/root/.local/bin:$PATH"

# Установить пакеты для подключения к репозиторию NodeSource,
# после чего установить из репозитория заданную версию Node.js.
ENV NODE_MAJOR=20
RUN mkdir -p /etc/apt/keyrings && \
    curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg && \
    echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_$NODE_MAJOR.x nodistro main" | tee /etc/apt/sources.list.d/nodesource.list && \
    apt-get update && \
    apt-get install -y nodejs

# Установить локаль.
RUN rm -rf /var/lib/apt/lists/* && \
    localedef -i ru_RU -c -f UTF-8 -A /usr/share/locale/locale.alias ru_RU.UTF-8
ENV LANG=ru_RU.utf8

# Создать каталог для проекта и перейти в него.
WORKDIR /srv/website

# Установить зависимости Node.js через npm.
COPY package.json package-lock.json ./
RUN npm install

# Установить зависимости Python через Poetry.
COPY pyproject.toml poetry.toml poetry.lock ./
RUN poetry install

COPY . .

# Выполнить скрипт, запускающий сервер.
ENV PYTHONPATH=.
ENTRYPOINT ["/bin/bash", "personal_website/entrypoint.sh"]
CMD ["0.0.0.0", "8000"]
