#!/bin/bash
#
# Вытягивание изменений из удаленного репозитория, 
# слияние ветки main с остальными ветками.

project_root="$(dirname "$(dirname "$(readlink -fm "$0")")")" # корневой путь проекта
working_branch="$(git branch --show-current)" # определение текущей рабочей ветки
main_branch="main" # имя основной ветки

###################################################
# Вытягивание изменений для каждой локальной ветки.
###################################################
function pull_branches () {
    git fetch origin
    declare -a branches
    branches="$(git branch --format='%(refname:short)')" # создание массива из списка всех локальных веток
    # Цикл для основных веток проекта: переключение на каждую ветку и вытягивание изменений.
    for branch in "${branches[@]}"; do
        git checkout $branch
        git pull
    done
}

#################################################
# Слияние ветки main с каждой из остальных веток.
#################################################
function merge_branches () {
    declare -a branches
    branches="$(git branch --format='%(refname:short)')" # создание массива из списка всех локальных веток
    branches=${branches[@]/$main_branch} # из массива всех веток удаляется основная ветка
    # Цикл для основных веток проекта: переключение на каждую ветку и слияние с ней main.
    for branch in "${branches[@]}"; do
        git checkout $branch
        git merge $main_branch
    done
}

cd $project_root # переход в корневую директорию проекта
pull_branches # вытягивание изменений для каждой ветки
merge_branches # слияние каждой ветки с main
git checkout $working_branch # возврат к рабочей ветке
