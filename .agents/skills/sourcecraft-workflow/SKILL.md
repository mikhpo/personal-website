---
name: sourcecraft-workflow
description: Работа с SourceCraft через CLI src — создание и закрытие задач (issues) и pull request'ов, запуск и мониторинг CI/CD workflows
---

## Предназначение

Скилл описывает типовой цикл работы с репозиторием на SourceCraft через утилиту `src`: задача → ветка → фикс → PR → проверка CI → merge → деплой. Все заголовки и описания задач и PR — на русском языке.

## Подготовка

- Репозиторий определяется автоматически, если текущий каталог — git-репозиторий с SourceCraft remote. Явно указать репо: `-R OWNER/REPO`.
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

Опции автоудаления исходной ветки при создании PR в CLI нет — особенности удаления ветки см. в разделе «Смержить PR».

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
3. По обоснованным замечаниям — внести правки, прогнать тесты и линтеры, закоммитить и запушить; дождаться CI (см. «Дождаться CI для PR»).
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

```bash
src pr merge <N>
```

Важно: флаг `--wait` в неинтерактивном (headless) режиме падает с ошибкой `could not open a new TTY: open /dev/tty: device not configured`. При этом сам merge успевает выполниться. Использовать merge без `--wait`, а статус проверить отдельно: `src pr get <N>` (должен показать `STATUS: merged`).

Важно: в headless-режиме флаг `--delete-branch` исходную ветку не удаляет (пост-шаг удаления не выполняется). Слитые ветки удалять вручную: `git push origin --delete <ветка>`.

Стратегии слияния: `--squash` (даёт единый коммит вида `... (!N)`), `--rebase`, по умолчанию merge commit.

## Workflows (CI/CD)

### Типовые workflows

- `lint-workflow`, `test-workflow`, `build-workflow` — запускаются автоматически на обновление PR (event `pr_update`)
- `release-workflow` — запускается автоматически на push в main (после merge)
- `deploy-workflow` — ручной запуск (event `manual`); деплоит указанный ref на сервер

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

## Мониторинг завершения (polling)

В headless-режиме нет автодожидания, статус опрашивается циклом. Bash-команды выполняются с увеличенным `timeout` (например 420000–600000 мс).

### Дождаться CI для PR

```bash
for i in $(seq 1 22); do
  out=$(src pr checks <N> 2>&1)
  echo "[$i] $(echo "$out" | grep -oE 'STATUS:\s+[a-zA-Z_]+' | head -1)"
  echo "$out" | grep -qE 'STATUS:\s+success' && { echo SUCCESS; break; }
  echo "$out" | grep -qE 'STATUS:\s+failed'  && { echo FAILED; break; }
  sleep 27
done
```

### Дождаться завершения отдельного run

```bash
for i in $(seq 1 24); do
  out=$(src run get <N> 2>&1)
  echo "[$i] $(echo "$out" | grep -oE 'STATUS:\s+[a-zA-Z_]+' | head -1)"
  echo "$out" | grep -qE 'STATUS:\s+success' && { echo SUCCESS; break; }
  echo "$out" | grep -qE 'STATUS:\s+failed'  && { echo FAILED; break; }
  sleep 20
done
```

### Дождаться нового auto-run (например release-workflow после merge)

```bash
for i in $(seq 1 18); do
  rel=$(src run list 2>&1 | grep "release-workflow" | head -1)
  slug=$(echo "$rel" | awk '{print $1}')
  st=$(echo "$rel" | grep -oE 'success|processing|created|failed' | head -1)
  echo "[$i] release-workflow run=$slug status=$st"
  [ "${slug:-0}" -gt <старый_slug> ] 2>/dev/null && { [ "$st" = success ] && { echo SUCCESS; break; }; [ "$st" = failed ] && { echo FAILED; break; }; }
  sleep 20
done
```

## Полный цикл (типовой)

1. Создать ветку от main: `git checkout main && git pull && git checkout -b fix/...`
2. Создать задачу: `src issue create ...` → запомнить `#N`
3. Внести изменения, тесты, CHANGELOG; закоммитить и запушить ветку
4. Создать PR со ссылкой на `#N`: `src pr create ...`
5. Дождаться CI: poll `src pr checks <N>` до `success`
6. (Опционально) Разобрать комментарии ревью: см. «Обработка комментариев ревью (опционально)»
7. Смержить: `src pr merge <N>`; убедиться через `src pr get <N>` → `merged`
8. Удалить слитую ветку: `git push origin --delete <ветка>`
9. Закрыть задачу: `src issue edit <N> --status closed`
10. Дождаться `release-workflow` (auto на push в main): poll `src run list` до success нового run
11. Запустить деплой: `src run trigger deploy-workflow --ref main`; дождаться success через poll `src run get <N>`
