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

### Проверить статус CI

```bash
src pr checks <N>   # сводные merge-checks: STATUS + CODE REVIEW + CONFLICTS + CI WORKFLOWS
src pr get <N>      # статус PR (open/merged/closed)
```

`src pr checks` показывает итоговый `STATUS:` (success / in_progress / failed) и статусы отдельных workflows (lint/test/build).

### Смержить PR

```bash
src pr merge <N> --squash
```

Важно: флаг `--wait` в неинтерактивном (headless) режиме падает с ошибкой `could not open a new TTY: open /dev/tty: device not configured`. При этом сам merge успевает выполниться. Использовать merge без `--wait`, а статус проверить отдельно: `src pr get <N>` (должен показать `STATUS: merged`).

Стратегии слияния: `--squash` (даёт единый коммит вида `... (!N)`), `--rebase`, по умолчанию merge commit. Флаг `--delete-branch` удаляет исходную ветку после merge.

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
6. Смержить: `src pr merge <N> --squash`; убедиться через `src pr get <N>` → `merged`
7. Закрыть задачу: `src issue edit <N> --status closed`
8. Дождаться `release-workflow` (auto на push в main): poll `src run list` до success нового run
9. Запустить деплой: `src run trigger deploy-workflow --ref main`; дождаться success через poll `src run get <N>`
10. Проверить результат на целевой среде (доступ, логи, состояние сервисов — см. скилл production-diagnostics)
