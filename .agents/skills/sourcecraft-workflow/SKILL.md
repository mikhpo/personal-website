---
name: sourcecraft-workflow
description: Работа с SourceCraft через CLI src - создание и закрытие задач (issues) и pull request'ов, запуск и мониторинг CI/CD workflows
---

## Предназначение

Скилл описывает типовой цикл работы с репозиторием на SourceCraft через утилиту `src`: задача -> ветка -> фикс -> PR -> проверка CI -> merge -> деплой. Все заголовки и описания задач и PR - на русском языке.

## Подготовка

- Репозиторий определяется автоматически, если текущий каталог - git-репозиторий с SourceCraft remote. Явно указать репо: `-R OWNER/REPO`.
- Проверить аутентификацию: `src auth status`
- Посмотреть активные PR и runs: `src status`

## Задачи (issues)

### Создать задачу

Многострочное описание удобно передавать через heredoc, чтобы избежать проблем с кавычками и переносами:

```bash
src issue create --title "Заголовок задачи" --priority critical --description "$(cat <<'EOF'
Описание задачи на русском.

Симптомы, корневая причина, предлагаемый фикс.
EOF
)"
```

Параметры: `--title`, `--description`, `--priority` (trivial/minor/normal/critical/blocker), `--status` (open/inProgress/paused/closed/declined/duplicate), `--labels`, `--assignee`, `--milestone`, `--visibility`.

Запомнить slug (номер) задачи из вывода для связи с PR.

### Закрыть задачу

```bash
src issue edit <N> --status closed
```

Прочее: `src issue get <N>`, `src issue list`, `src issue add-comment <N>`.

## Pull request'ы

### Создать PR

```bash
src pr create --title "fix: краткое описание" --base main --head <ветка> --description "$(cat <<'EOF'
Что менялось, причина, как проверено.
Ссылка на issue: #N
EOF
)"
```

Параметры: `--base` (целевая ветка, по умолчанию main), `--head` (исходная ветка, по умолчанию текущая), `--draft`, `--reviewer`, `--web`.

Опции автоудаления исходной ветки при создании PR в CLI нет - особенности удаления ветки см. в разделе «Смержить PR».

### Проверить статус CI

```bash
src pr checks <N>   # сводные merge-checks: STATUS + CODE REVIEW + CONFLICTS + CI WORKFLOWS
src pr get <N>      # статус PR (open/merged/closed)
```

`src pr checks` показывает итоговый `STATUS:` (success / in_progress / failed) и статусы отдельных workflows (lint/test/build).

### Обработка комментариев ревью (опционально)

Опциональный этап между успешным CI и merge. Применяется по запросу пользователя перед закрытием PR, когда ревьюер оставил замечания, которые нужно разобрать.

Получить список комментариев:

```bash
src pr list-comments <N>            # табличный вывод
src pr list-comments <N> --json     # id, parent_id, body, author.slug
```

Каждый комментарий содержит `id` (используется как `--parent-id` для ответа в той же ветке) и `parent_id` (пустой у комментариев верхнего уровня).

Порядок разбора:

1. По списку комментариев отделить замечания ревьюера от собственных.
2. Оценить обоснованность каждого замечания ревьюера.
3. По обоснованным замечаниям - внести правки, прогнать тесты и линтеры, закоммитить и запушить; дождаться CI (см. «Дождаться CI для PR»).
4. Ответить на каждое замечание ревьюера оценкой обоснованности и выполненными действиями.

Ответ в ветку комментария (threaded reply):

```bash
src pr add-comment <N> --parent-id <comment_id> --body "$(cat <<'EOF'
Оценка замечания и выполненные действия.
Ссылка на коммит с исправлением.
EOF
)"
```

Замечания, не требующие правок, тоже закрываются ответом с обоснованием, почему изменение не нужно.

### Смержить PR

Важно: выполнять merge только после явного подтверждения пользователя. Одобрения общего плана или зелёного CI недостаточно: merge - это отдельный рубеж, по которому нужно отдельно спросить «мержить?» и дождаться явного «да». До подтверждения следует сообщить статус (CI зелёный, конфликтов нет) и остановиться.

```bash
src pr merge <N>
```

Важно: флаг `--wait` в неинтерактивном (headless) режиме падает с ошибкой `could not open a new TTY: open /dev/tty: device not configured`. При этом сам merge успевает выполниться. Использовать merge без `--wait`, а статус проверить отдельно: `src pr get <N>` (должен показать `STATUS: merged`).

Важно: в headless-режиме флаг `--delete-branch` исходную ветку не удаляет (пост-шаг удаления не выполняется). Слитые ветки удалять вручную: `git push origin --delete <ветка>`.

Стратегии слияния: `--squash` (даёт единый коммит вида `... (!N)`), `--rebase`, по умолчанию merge commit.

## Workflows (CI/CD)

### Типовые workflows

- `lint-workflow`, `test-workflow`, `build-workflow` - запускаются автоматически на обновление PR (event `pr_update`)
- `release-workflow` - запускается автоматически на push в main (после merge)
- `deploy-workflow` - ручной запуск (event `manual`); деплоит указанный ref на сервер

### Просмотр runs

```bash
src run list        # последние runs: SLUG, STATUS, WORKFLOWS, EVENT TYPE, TRIGGERED BY
src run get <N>     # детали конкретного run
```

### Запустить workflow вручную

```bash
src run trigger deploy-workflow --ref main
```

Параметры: `--ref` (ветка), `--commit`, `--tag`. В выводе содержится `SLUG` созданного run.

### Получить логи выполнения куба

`src` не умеет отдавать логи кубов напрямую - только сводные статусы (`src run get`, `src pr checks`). Чтобы увидеть вывод конкретного куба при падении CI, нужно дёрнуть REST API SourceCraft напрямую.

Схема endpoint-а логов куба:

```text
GET /repos/{org}/{repo}/cicd/logs/{run}/{workflow}/{task}/{cube}
```

Полный список endpoint-ов CI: `GET https://api.sourcecraft.tech/docs` (Redoc, спецификация `./sourcecraft.swagger.json`).

Для многократного использования в репозитории есть готовая обёртка `tools/src-cube-logs.sh`, которая сама получает токен из keychain macOS (сервис `sourcecraft-cli`) и определяет `org/repo` по git remote:

```bash
tools/src-cube-logs.sh <run> <workflow> <task> <cube>
```

Пример:

```bash
tools/src-cube-logs.sh 144 test-workflow python-test pytest
# => Установка Node.js для сборки фронтенда
#    curl: (22) The requested URL returned error: 403
#    ...
```

Токен хранится в keychain macOS под сервисом `sourcecraft-cli` (base64-обёрнутый PAT). Если `tools/src-cube-logs.sh` недоступен (другая ОС или нет keyring), можно собрать запрос вручную:

```bash
TOKEN=$(/usr/bin/security find-generic-password -s "sourcecraft-cli" -w \
        | sed 's/^go-keyring-base64://' | base64 -d)
REPO=$(git remote get-url origin \
        | sed -E 's#.*sourcecraft\.dev[:/]([^/]+)/([^/.]+).*#\1/\2#')
/usr/bin/curl -sL -H "Authorization: Bearer $TOKEN" \
  "https://api.sourcecraft.tech/repos/${REPO}/cicd/logs/<RUN>/<WF>/<TASK>/<CUBE>" \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['logs'], end='')"
```

Порядок действий при падении CI:

1. `src pr checks <PR>` -> определить упавший workflow (например `test-workflow`).
2. `src run get <RUN>` -> убедиться, что нужный run известен (в выводе `src pr checks` он указан в строке workflow).
3. По имени workflow/task/cube из `.sourcecraft/ci.yaml` взять slug-и и вызвать `tools/src-cube-logs.sh <RUN> <WF> <TASK> <CUBE>`.
4. Если ответ пустой, а в `src run get` куб помечен failed - куб упал рано, логи короткие.

## Мониторинг завершения (polling)

В headless-режиме нет автодожидания, статус опрашивается циклом. Bash-команды выполняются с увеличенным `timeout` (например 420000–600000 мс).

### Дождаться CI для PR

Вывод `src pr checks` содержит строку `STATUS:` (верхний уровень - `success` или `failure`),
а также строки по каждому workflow (`success` / `failed`). Извлекать статус нужно из первой
строки `STATUS:`, беря последнее слово через `awk`, и сравнивать через `case` - это надёжнее
grep-паттернов с `\s`, которые не срабатывают на macOS (BSD grep) и при наличии ANSI-кодов.

```bash
for i in $(seq 1 22); do
  out=$(src pr checks <N> 2>&1)
  st=$(echo "$out" | grep 'STATUS:' | head -1 | awk '{print $NF}')
  echo "[$i] status=$st"
  case "$st" in
    success) echo "SUCCESS"; break ;;
    failure|failed) echo "FAILED"; break ;;
  esac
  sleep 27
done
```

### Дождаться завершения отдельного run

```bash
for i in $(seq 1 24); do
  out=$(src run get <N> 2>&1)
  st=$(echo "$out" | grep 'STATUS:' | head -1 | awk '{print $NF}')
  echo "[$i] status=$st"
  case "$st" in
    success) echo "SUCCESS"; break ;;
    failure|failed) echo "FAILED"; break ;;
  esac
  sleep 20
done
```

### Дождаться нового auto-run (например release-workflow после merge)

```bash
OLD_SLUG=<slug_последнего_run>
for i in $(seq 1 18); do
  rel=$(src run list 2>&1 | grep "release-workflow" | head -1)
  slug=$(echo "$rel" | awk '{print $1}')
  st=$(echo "$rel" | awk '{print $NF}')
  echo "[$i] release-workflow run=$slug status=$st"
  [ "${slug:-0}" -gt "$OLD_SLUG" ] 2>/dev/null && {
    case "$st" in
      success) echo "SUCCESS"; break ;;
      failure|failed) echo "FAILED"; break ;;
    esac
  }
  sleep 20
done
```

## Полный цикл (типовой)

1. Создать ветку от main: `git checkout main && git pull && git checkout -b fix/...`
2. Создать задачу: `src issue create ...` -> запомнить `#N`
3. Внести изменения, тесты, CHANGELOG; закоммитить и запушить ветку
4. Создать PR со ссылкой на `#N`: `src pr create ...`
5. Дождаться CI: poll `src pr checks <N>` до `success`
6. (Опционально) Разобрать комментарии ревью: см. «Обработка комментариев ревью (опционально)»
7. Смержить (только после явного подтверждения пользователя): `src pr merge <N>`; убедиться через `src pr get <N>` -> `merged`
8. Удалить слитую ветку: `git push origin --delete <ветка>`
9. Закрыть задачу: `src issue edit <N> --status closed`
10. Дождаться `release-workflow` (auto на push в main): poll `src run list` до success нового run
11. Запустить деплой: `src run trigger deploy-workflow --ref main`; дождаться success через poll `src run get <N>`
