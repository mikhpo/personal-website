#!/bin/bash
#
# Автоматическое формирования коммита и отправка изменений в 
# удаленный репозиторий в основных ветках: main, dev, fix.

project_root="$(dirname "$(dirname "$(readlink -fm "$0")")")"
cd $project_root # переход в корневую директорию проекта
main_branch = "main" # имя основной ветки
working_branch="$(git branch --show-current)" # определение текущей рабочей ветки

################################################
# Формирует и отправляет коммит в текущей ветке.
################################################
function commit_changes () {
    local branch
    local now
    local message
    branch="$(git branch --show-current)" # определение текущей ветки
    now="$(date +'%d.%m.%Y %H:%M:%S')" # определение текущей даты-времени
    message="Commit to branch ${branch} at ${now} from ${HOSTNAME}" # формируется сообщение для коммита
    git add -A # добавить все новые файлы в отслеживание
    git commit -m "${message}" # сформировать коммит
    git push
}

######################################################################
# Создание коммитов и отправка в удаленный репозиторий для всех веток.
######################################################################
function push_branches () {
    declare -a branches
    branches="$(git branch --format='%(refname:short)')" # создание массива из списка всех локальных веток
    branches=${branches[@]/$working_branch} # из массива всех веток удаляется текущая ветка
    # Цикл для основных веток проекта: переключение на каждую ветку и вызов функции.
    for branch in "${branches[@]}"; do
        git checkout $branch
        commit_changes
    done
}

##################################################################################
# Слияние всех веток в main и отправка объединенной ветки в удаленный репозиторий.
##################################################################################
function merge_branches () {
    declare -a branches
    branches="$(git branch --format='%(refname:short)')" # создание массива из списка всех локальных веток
    branches=${branches[@]/$main_branch} # из массива всех веток удаляется основная ветка
    git checkout $main_branch # переключение на мастер-ветку
    for branch in "${branches[@]}"; do
        git merge $branch
        git push
    done
}

# Формирование и отправка коммита для текущей ветки.
commit_changes 

# Формирование и отправка коммитов для остальных веток.
push_branches

# Объединение веток в основную.
merge_branches

# Возврат к первоначальной рабочей ветке.
git checkout $working_branch
