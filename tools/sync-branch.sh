#!/bin/bash
#
# Синхронизировать ветку между репозиториями github и sourcecraft.
#
# Имя ветки может быть передано скрипту в аргументах командной строки.
# Если имя ветки не передано при вызове скрипта, то будет использована ветка main.

branch_name=${1:-main}

echo "Синхронизация ветки $branch_name между репозиториями github и sourcecraft..."

# Отправить ветку в репозиторий github
echo "Отправка ветки $branch_name в репозиторий github..."
git push github "$branch_name"

# Отправить ветку в репозиторий sourcecraft
echo "Отправка ветки $branch_name в репозиторий sourcecraft..."
git push sourcraft "$branch_name"

echo "Синхронизация завершена."
