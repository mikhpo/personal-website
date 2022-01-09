#!/bin/bash

# Запуск планировщика скриптов. 

# Смена текущей директории на корень проекта Django.
cd /home/mikhpo/personal-website/root && 

# Абсолютный путь до интерпретатора Python в виртуальном окружении, 
# абсолютный путь до модуля manage.py в корневом каталоге проекта
# и название аргумента - наименование административной команды.
/home/mikhpo/personal-website/.venv/bin/python /home/mikhpo/personal-website/root/manage.py runserver