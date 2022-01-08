#!/bin/bash

# Скрипт для добавления задач cron в файл crontab.
# Бизнес-логика скрипта:
#   1. Считывает содержимое текущего crontab.
#   2. Проверяет наличие целевых задач cron.
#   3. Если задачи ещё не добавлены, то добавляет задачи в crontab.

# Получение содержимого текущего crontab файла.
cron=`crontab -l 2> /dev/null`

# Массив задач на добавление.
cron_jobs=(
    "@reboot (cd /home/mikhpo/personal-website/ && source .venv/bin/activate && python3 root/manage.py run_scheduler)"
)

# Определение символа перехода на новую строку. 
NEWLINE=$'\n'

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
            if [[ -z "$cron" ]]; then
                # Если в данный момент crontab пуст или не создан, 
                # то задача записывается в первую строку файла.
                cron="${job}"
            else
                # Если файл не пуст, то задача добавляется с новой строки.
                cron="${cron}${NEWLINE}${job}"
            fi
            echo "Задача \""$job"\" добавлена в crontab"           
        fi
    done

# Обязательное добавление пустой строки в конец crontab.
cron="${cron}${NEWLINE}"

# Сохранение результата в crontab.
echo "$cron" | crontab -