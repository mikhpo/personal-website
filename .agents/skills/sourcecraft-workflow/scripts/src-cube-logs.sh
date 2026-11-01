#!/bin/bash
#
# Получить логи выполнения куба SourceCraft CI через REST API.
#
# `src` умеет показывать только сводные статусы workflow, но не отдаёт
# логи конкретного куба. Этот скрипт дёргает endpoint логов напрямую:
#   GET /repos/{org}/{repo}/cicd/logs/{run}/{workflow}/{task}/{cube}
#
# Использование:
#   tools/src-cube-logs.sh <run> <workflow> <task> <cube>
#
# Пример:
#   tools/src-cube-logs.sh 144 test-workflow python-test pytest
#
# Токен берётся из keychain macOS (сервис `sourcecraft-cli`, PAT обёрнут в base64).
# Репозиторий определяется по git remote `origin`.

set -euo pipefail

if [ "$#" -ne 4 ]; then
    echo "Использование: $0 <run> <workflow> <task> <cube>" >&2
    exit 1
fi

RUN="$1"
WF="$2"
TASK="$3"
CUBE="$4"

# Извлечь токен из keychain (хранится как base64-обёрнутый PAT).
TOKEN=$(/usr/bin/security find-generic-password -s "sourcecraft-cli" -w \
        | sed 's/^go-keyring-base64://' \
        | base64 -d)

# Определить org/repo по git remote origin.
REPO=$(git remote get-url origin 2>/dev/null \
        | sed -E 's#.*sourcecraft\.dev[:/]([^/]+)/([^/.]+).*#\1/\2#')

if [ -z "${REPO:-}" ]; then
    echo "Не удалось определить репозиторий по git remote origin." >&2
    exit 1
fi

# Запрос логов и извлечение текста из JSON-поля "logs".
/usr/bin/curl -sL -H "Authorization: Bearer ${TOKEN}" \
    "https://api.sourcecraft.tech/repos/${REPO}/cicd/logs/${RUN}/${WF}/${TASK}/${CUBE}" \
    | python3 -c "import sys, json; print(json.load(sys.stdin).get('logs', ''), end='')"
