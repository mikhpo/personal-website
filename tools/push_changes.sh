#!/bin/bash
#
# Автоматическое формирования коммита и отправка изменений в 
# удаленный репозиторий в основных ветках: main, dev, fix.

# Переход в корневую директорию проекта.
project_root="$(dirname "$(dirname "$(readlink -fm "$0")")")"
cd $project_root

#######################################
# Формирует и отправляет коммит в текущей ветке.
#######################################
function git_push () {
    local branch
    local now
    branch="$(git branch --show-current)" # определение текущей ветки
    now="$(date +'%d.%m.%Y %H:%M:%S')" # определение текущей даты-времени
    message="Commit to branch ${branch} at ${now} from ${HOSTNAME}" # формируется сообщение для коммита
    git add -A # добавить все новые файлы в отслеживание
    git commit -m "${message}" # сформировать коммит
    git push
}

git_push # вызов функции для текущей ветки

# Цикл для основных веток проекта: переключение на каждую ветку и вызов функции.
declare -a branches=("main" "dev" "fix")
for branch in "${branches[@]}"; do
    git checkout $branch
    git_push
done