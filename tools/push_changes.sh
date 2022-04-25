#!/bin/bash
#
# Автоматическое формирования коммита и отправка изменений в 
# удаленный репозиторий в основных ветках: main, dev, fix.

################################################
# Формирует и отправляет коммит в текущей ветке.
################################################
function git_push () {
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

# Переход в корневую директорию проекта.
project_root="$(dirname "$(dirname "$(readlink -fm "$0")")")"
cd $project_root

branches="$(git branch --format='%(refname:short)')" # создание массива из списка всех локальных веток
working_branch="$(git branch --show-current)" # определение текущей рабочей ветки
branches=${branches[@]/$working_branch} # из массива всех веток удаляется текущая ветка

# Формирование и отправка коммита для текущей ветки.
git_push 

# Цикл для основных веток проекта: переключение на каждую ветку и вызов функции.
for branch in "${branches[@]}"; do
    git checkout $branch
    git_push
done

# Слияние всех веток в main и отправка объединенной ветки в удаленный репозиторий.
git checkout main
for branch in "${branches[@]}"; do
    git merge $branch
    git push
done

# Возврат к текущей рабочей ветке.
git checkout $working_branch
