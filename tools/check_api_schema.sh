#!/usr/bin/env bash
# Проверка свежести артефактов конвейера схемы API.
#
# Перегенерирует указанный артефакт и падает, если закоммиченный файл
# отличается от результата перегенерации. Используется pre-commit хуками:
#   tools/check_api_schema.sh export  - схема бэкенда (docs/schemas/openapi.yaml)
#   tools/check_api_schema.sh types   - типы фронтенда (frontend/src/types/api-schema.ts)

set -euo pipefail

mode=${1:?Укажите режим: export или types}

case "$mode" in
  export)
    poetry run python backend/manage.py spectacular --file docs/schemas/openapi.yaml
    target="docs/schemas/openapi.yaml"
    reason="не соответствует коду бэкенда"
    ;;
  types)
    npm run api-types
    target="frontend/src/types/api-schema.ts"
    reason="не соответствует схеме API"
    ;;
  *)
    echo "Неизвестный режим: $mode (допустимо: export, types)" >&2
    exit 1
    ;;
esac

if ! git diff --exit-code -- "$target" > /dev/null; then
  echo "$target $reason." >&2
  echo "Перегенерируйте артефакт и добавьте обновленный файл в коммит; конвейер описан в docs/CONTRIBUTING.md." >&2
  exit 1
fi
