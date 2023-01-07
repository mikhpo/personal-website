#!/bin/bash
#
# Скрипт для добавления задач cron в файл crontab.
# Бизнес-логика скрипта:
#   1. Считывает содержимое текущего crontab.
#   2. Проверяет наличие целевых задач cron.
#   3. Если задачи ещё не добавлены, то добавляет задачи в crontab.

# Определение символа перехода на новую строку. 
newline=$'\n'

# Определение корневой директории проекта.
project_root="$(dirname "$(dirname "$(readlink -fm "$0")")")"
echo "Корневая директория проекта: ${project_root}"

# Определение пути исполняемого файла Python.
python="$project_root/.venv/bin/python"
echo "Путь до интерпретатора Python: ${python}"

# Массив задач на добавление.
cron_jobs=(
    "0 23 * * * $python $project_root/scripts/backup_database.py"
    "1 23 * * * $python $project_root/scripts/backup_storage.py"
)

# Получение содержимого текущего crontab файла.
cron=`crontab -l 2> /dev/null`

# Цикл для каждого элемента из массива задач на добавление.
for job in "${cron_jobs[@]}"
    do
        # Проверка на то, добавлена ли уже задача в crontab.
        if [[ "$cron" != *"$job"* ]]; then
            # Если задача уже в crontab, то ничего не надо делать.
            # Если задача не найдена в crontab, то она добавляется
            # к текущему crontab в новой строке.
            if [[ -z "$cron" ]]; then
                # Если в данный момент crontab пуст или не создан, 
                # то задача записывается в первую строку файла.
                cron="${job}"
            else
                # Если файл не пуст, то задача добавляется с новой строки.
                cron="${cron}${newline}${job}"
            fi            
        fi
    done

# Обязательное добавление пустой строки в конец crontab.
cron="${cron}${newline}"

# Сохранение результата в crontab.
echo "$cron" | crontab -
echo "Актуальное содержание crontab:${newline}${cron}"
