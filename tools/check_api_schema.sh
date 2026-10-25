#!/usr/bin/env bash
# Проверка свежести артефактов конвейера схемы API.
#
# Перегенерирует указанный артефакт и падает, если закоммиченный файл
# отличается от результата перегенерации. Используется pre-commit хуками:
#   tools/check_api_schema.sh export  - схема бэкенда (docs/schemas/schema.yaml)
#   tools/check_api_schema.sh types   - типы фронтенда (frontend/src/types/api-schema.ts)

set -euo pipefail

mode=${1:?Укажите режим: export или types}

case "$mode" in
  export)
    poetry run python backend/manage.py spectacular --file docs/schemas/schema.yaml
    target="docs/schemas/schema.yaml"
    hint="task schema-export"
    ;;
  types)
    npm run api-types
    target="frontend/src/types/api-schema.ts"
    hint="task api-types"
    ;;
  *)
    echo "Неизвестный режим: $mode (допустимо: export, types)" >&2
    exit 1
    ;;
esac

if ! git diff --exit-code -- "$target" > /dev/null; then
  echo "Файл $target отличается от результата перегенерации." >&2
  echo "Выполните ${hint} и добавьте обновленный файл в коммит." >&2
  exit 1
fi
