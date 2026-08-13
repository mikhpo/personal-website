#!/bin/bash
#
# Разовый логический дамп базы данных PostgreSQL через pg_dump.
# Без выгрузки во внешнее хранилище. Неинтерактивный.
#
# Параметры подключения — флагами или переменными окружения libpq
# (PGHOST, PGPORT, PGUSER, PGDATABASE, PGPASSWORD).
#
# Коды возврата:
#   0  успех
#   2  ошибка аргументов
#   3  ошибка pg_dump
#   4  файл назначения существует (используйте --force)

set -euo pipefail

#######################################
# Вывод справки по использованию скрипта.
#######################################
function usage() {
    cat <<'HELP'
Использование: pg-dump.sh [--host ХОСТ] [--port ПОРТ] [--user ПОЛЬЗОВАТЕЛЬ]
                       [--dbname БАЗА] [--output ПУТЬ] [--force] [-h]

Создаёт дамп БД в формате -Fc: <база>_<дата>.dump в текущем каталоге
(переопределяется через --output). Параметры подключения берутся из флагов
или переменных окружения libpq (PGHOST, PGPORT, PGUSER, PGDATABASE, PGPASSWORD).

Опции:
  --host ХОСТ         хост сервера БД (или PGHOST)
  --port ПОРТ         порт сервера БД (или PGPORT)
  --user ПОЛЬЗОВАТЕЛЬ пользователь БД (или PGUSER)
  --dbname БАЗА       имя базы данных (или PGDATABASE)
  --output ПУТЬ       путь файла дампа (по умолчанию <база>_<дата>.dump)
  --force             перезаписать существующий файл дампа
  -h, --help          показать эту справку

Коды возврата: 0 успех, 2 аргументы, 3 ошибка pg_dump, 4 файл существует.
HELP
}

# Параметры по умолчанию из переменных окружения libpq.
host="${PGHOST:-}"
port="${PGPORT:-}"
user="${PGUSER:-}"
dbname="${PGDATABASE:-}"
output=""
force=0

# Разбор аргументов командной строки.
while [ $# -gt 0 ]; do
    case "$1" in
    --host) host="$2"; shift 2 ;;
    --port) port="$2"; shift 2 ;;
    --user) user="$2"; shift 2 ;;
    --dbname) dbname="$2"; shift 2 ;;
    --output) output="$2"; shift 2 ;;
    --force) force=1; shift ;;
    -h | --help) usage; exit 0 ;;
    *) echo "ошибка: неизвестный аргумент: $1" >&2; usage >&2; exit 2 ;;
    esac
done

# База данных обязательна.
if [ -z "$dbname" ]; then
    echo "ошибка: не задана база данных (--dbname или PGDATABASE)" >&2
    exit 2
fi

# Имя файла по соглашению: <база>_<дата>.dump, если не задано --output.
today=$(date '+%Y-%m-%d')
output="${output:-${dbname}_${today}.dump}"

# Идемпотентность: не перезаписывать существующий файл без --force.
if [ -f "$output" ] && [ "$force" -ne 1 ]; then
    echo "ошибка: файл $output существует; используйте --force" >&2
    exit 4
fi

# Сборка флагов подключения из явно заданных значений.
dump_args=()
[ -n "$host" ] && dump_args+=(-h "$host")
[ -n "$port" ] && dump_args+=(-p "$port")
[ -n "$user" ] && dump_args+=(-U "$user")
dump_args+=(-d "$dbname")

echo "создание дампа -> $output" >&2
if ! pg_dump "${dump_args[@]}" -Fc --no-privileges --no-subscriptions --no-publications -f "$output"; then
    rm -f "$output"
    echo "ошибка: pg_dump завершился с ошибкой" >&2
    exit 3
fi

# Проверка, что дамп действительно создан и не пуст.
if [ ! -s "$output" ]; then
    echo "ошибка: дамп не создан (пустой файл)" >&2
    exit 3
fi

# Результат — одна структурированная строка в stdout; диагностика — в stderr.
size_bytes=$(wc -c < "$output" | tr -d ' ')
printf 'dump_path=%s\tdatabase=%s\tsize_bytes=%s\n' "$output" "$dbname" "$size_bytes"
