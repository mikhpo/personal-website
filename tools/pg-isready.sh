
#!/bin/bash
#
# Скрипт для проверки готовности базы данных PostgreSQL
#
# Этот скрипт ожидает, когда база данных PostgreSQL будет готова к подключениям.
# Он использует утилиту pg_isready для проверки статуса подключения и выполняет
# повторные попытки до максимального количества с интервалом 1 секунда между попытками.
#
# Переменные окружения:
#   POSTGRES_HOST - Хост базы данных PostgreSQL (по умолчанию: localhost)
#   POSTGRES_PORT - Порт базы данных PostgreSQL (по умолчанию: 5432)
#   POSTGRES_USER - Имя пользователя базы данных для подключения (по умолчанию: postgres)
#   POSTGRES_DB   - Имя базы данных для подключения (по умолчанию: postgres)

max_attempts=30
attempt=0

until
    attempt=$((attempt + 1))
    echo "Ожидание готовности PostgreSQL (попытка $attempt)..."
    pg_isready \
    -h ${POSTGRES_HOST:-localhost} \
    -p ${POSTGRES_PORT:-5432} \
    -U ${POSTGRES_USER:-postgres} \
    -d ${POSTGRES_DB:-postgres}; do
    if [ $attempt -ge $max_attempts ]; then
        echo "PostgreSQL не готов к подключению в течение заданного времени"
        exit 1
    fi
    sleep 1
done

echo "PostgreSQL готов к подключению!"
