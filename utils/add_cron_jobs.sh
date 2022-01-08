#!/bin/bash

# Скрипт для добавления задач cron в файл crontab.
# Бизнес-логика скрипта:
#   1. Считывает содержимое текущего crontab.
#   2. Проверяет наличие целевых задач cron.
#   3. Если задачи ещё не добавлены, то добавляет задачи в crontab.

# Получение содержимого текущего crontab файла.
cron=`crontab -l 2> /dev/null`

if [[ -z "$cron" ]]; then
    echo "У пользователя не создан crontab"
fi

# Массив задач на добавление.
cron_jobs=(
    "@reboot (cd /home/mikhpo/personal-website/ && source .venv/bin/activate && python3 root/manage.py run_scheduler)"
)

# Определение символа перехода на новую строку.
NEWLINE=$"\n"

# Цикл для каждого элемента из массива задач на добавление.
for job in "${cron_jobs[@]}"
    do
        # Проверка на то, добавлена ли уже задача в crontab.
        if [[ "$cron" == *"$job"* ]]; then
            # Если задача уже в crontab, то ничего не надо делать.
            echo "Задача \""$job"\" уже в crontab"
        else
            # Если задача не найдена в crontab, то она добавляется
            # к текущему crontab в новой строке.
            cron="${cron}${NEWLINE}${job}"
            echo "Задача \""$job"\" добавлена в crontab"
        fi
    done

# Сохранение результата в crontab.
echo "$cron" | crontab -