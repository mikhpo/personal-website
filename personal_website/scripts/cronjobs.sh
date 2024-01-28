#!/bin/bash
#
# Скрипт для добавления задач cron в файл crontab.
# Бизнес-логика скрипта:
#   1. Считывает содержимое текущего crontab.
#   2. Проверяет наличие целевых задач cron.
#   3. Если задачи ещё не добавлены, то добавляет задачи в crontab.

# Определение символа перехода на новую строку.
readonly NEWLINE=$'\n'

# Определение путей файлов.
bash=$(which bash)
project_root="$(dirname "$(dirname "$(dirname "$(readlink -fm "$0")")")")"
scripts="$project_root/personal_website/scripts"
default_logs_dir="$project_root/logs"

# Считывание переменных окружения из файла .env.
dotenv="$project_root/.env"
if [ -f "$dotenv" ]; then
    eval export "$(cat "$dotenv")"
    echo "Переменные окружения загружены из файла $dotenv"
fi

# Проверка на наличие переменной окружения, в которой указан корневой адрес логов.
# Если переменная окружения не указана, то устанавливается значение по умолчанию.
if [ -z "$LOGS_ROOT" ]; then
    logs=$default_logs_dir
else
    logs="$LOGS_ROOT"
fi

# Массив задач на добавление.
cron_jobs=(
    "0 23 * * * $bash $scripts/pgbackup.sh >> $logs/pgbackup.log 2>&1"
    "1 23 * * * $bash $scripts/s3backup.sh >> $logs/s3backup.log 2>&1"
)

# Получение содержимого текущего crontab файла.
cron=$(crontab -l 2>/dev/null)

# Цикл для каждого элемента из массива задач на добавление.
for job in "${cron_jobs[@]}"; do

    # Проверка на то, добавлена ли уже задача в crontab.
    # Если задача уже в crontab, то ничего не надо делать.
    # Если задача не найдена в crontab, то она добавляется
    # к текущему crontab в новой строке.
    if [[ "$cron" != *"$job"* ]]; then

        # Если в данный момент crontab пуст или не создан,
        # то задача записывается в первую строку файла.
        if [[ -z "$cron" ]]; then
            cron="${job}"

        # Если файл не пуст, то задача добавляется с новой строки.
        else
            cron="${cron}${NEWLINE}${job}"

        fi
    fi
done

# Обязательное добавление пустой строки в конец crontab.
cron="${cron}${NEWLINE}"

# Сохранение результата в crontab.
echo "$cron" | crontab -

echo "Актуальное содержание crontab:${NEWLINE}${cron}"
