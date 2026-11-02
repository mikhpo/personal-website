#!/bin/sh
#
# Запуск скрипта установленного скилла с проверкой его наличия.
# Использование: skill-hook.sh <скилл> <скрипт> [аргументы...]
#
# Скилл ищется в .agents/skills/ проекта. Отсутствующий скрипт завершает
# хук с ошибкой и командой восстановления вместо тихого пропуска проверки.

set -eu

if [ "$#" -lt 2 ]; then
    echo "Использование: $0 <скилл> <скрипт> [аргументы...]" >&2
    exit 2
fi

SKILL="$1"
SCRIPT="$2"
shift 2
TARGET=".agents/skills/$SKILL/scripts/$SCRIPT"

if [ ! -f "$TARGET" ]; then
    echo "Скилл $SKILL не установлен: $TARGET отсутствует." >&2
    echo "Восстановление: npx skills add mikhpo/skills --skill $SKILL -y" >&2
    exit 1
fi

exec python3 "$TARGET" "$@"
