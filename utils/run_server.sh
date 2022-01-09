#!/bin/bash

# Запуск планировщика скриптов. 

# Смена текущей директории на корень проекта Django.
cd /home/mikhpo/personal-website && 

# Абсолютный путь до интерпретатора Python в виртуальном окружении, 
# абсолютный путь до модуля manage.py в корневом каталоге проекта
# и аргумент - наименование административной команды для запуска сервера со стандартными параметрами.
/home/mikhpo/personal-website/.venv/bin/python /home/mikhpo/personal-website/manage.py runserver