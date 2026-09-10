---
name: github-workflow
description: Работа с GitHub через CLI gh - создание и закрытие задач (issues) и pull request'ов, прикрепление скриншотов и вложений к задачам и PR, запуск и мониторинг CI/CD workflows
---

## Предназначение

Скилл описывает типовой цикл работы с репозиторием на GitHub через утилиту `gh`: задача -> ветка -> фикс -> PR -> проверка CI -> merge -> деплой. Все заголовки и описания задач и PR - на русском языке.

## Подготовка

- Репозиторий определяется автоматически, если текущий каталог - git-репозиторий с GitHub remote. Явно указать репо: `-R OWNER/REPO`.
- Проверить аутентификацию: `gh auth status`
- Посмотреть свои PR: `gh pr status`

## Задачи (issues)

### Создать задачу

Многострочное описание удобно передавать через heredoc, чтобы избежать проблем с кавычками и переносами:

```bash
gh issue create --title "Заголовок задачи" --assignee @me --body "$(cat <<'EOF'
Описание задачи на русском.

Симптомы, корневая причина, предлагаемый фикс.
EOF
)"
```

Параметры: `--title`, `--body`, `--label`, `--assignee`, `--milestone`.

Пользователя сразу указывать исполнителем: `--assignee @me` в каждой создаваемой задаче.

Запомнить номер задачи из вывода для связи с PR.

### Закрыть задачу

В типовом цикле задача закрывается сама: ключевое слово `Closes #N` в описании PR закрывает задачу при merge в основную ветку. Ручное закрытие (без merge):

```bash
gh issue close <N> --reason completed   # или "not planned"
gh issue close <N> --duplicate-of <M>   # дубликат
```

Прочее: `gh issue view <N>`, `gh issue list`, `gh issue comment <N> --body "..."`.

## Pull request'ы

### Создать PR

```bash
gh pr create --title "fix: краткое описание" --base main --head <ветка> --assignee @me --body "$(cat <<'EOF'
Что менялось, причина, как проверено.

Closes #N
EOF
)"
```

Параметры: `--base` (целевая ветка, по умолчанию main), `--head` (исходная ветка, по умолчанию текущая), `--draft`, `--reviewer`, `--label`, `--assignee`, `--web`. Черновик переводится в готовый: `gh pr ready <N>`.

Пользователя сразу указывать исполнителем: `--assignee @me` в каждом создаваемом PR.

Ключевое слово `Closes #N` (также `Fixes #N`, `Resolves #N`) в теле PR автоматически закрывает задачу при merge - отдельный шаг закрытия не нужен.

### Прикрепить скриншоты к PR или задаче

Кадры загружаются недокументированным эндпоинтом, эквивалентным drag-and-drop в веб-интерфейсе: GitHub хранит вложение постоянно (user-attachments), загрузка и правки комментариев не триггерят workflows, релизы не затрагиваются.

```bash
REPOSITORY=OWNER/REPO
TOKEN=$(gh auth token)
RID=$(gh api repos/$REPOSITORY --jq .id)

curl -s "https://uploads.github.com/user-attachments/assets?name=<file>.png&content_type=image/png&repository_id=$RID" \
  -X POST -H "Authorization: Bearer $TOKEN" -H "Accept: application/json" \
  --data-binary "@<file>.png"
```

Ответ - JSON с постоянной ссылкой: `{"url": "https://github.com/user-attachments/assets/<uuid>"}`. Извлечь `url` из того же ответа: каждый POST создает новый экземпляр вложения, поэтому повторная загрузка файла ради парсинга ответа оставляет невидимые дубликаты.

Встроить ссылку в комментарий или описание:

```bash
gh pr comment <N> --body "Заголовок

![Подпись](<URL из ответа>)"
```

Правка последнего собственного комментария: `gh pr comment <N> --edit-last --body "..."`.

### Проверить статус CI

```bash
gh pr checks <N>          # таблица checks: имена, статусы, ссылки на runs
gh pr view <N> --json state,mergeable,reviewDecision
```

Код возврата `gh pr checks` равен 8, пока checks выполняются, - в скриптах различать состояния по коду, а не только по выводу.

### Обработка комментариев ревью (опционально)

Опциональный этап между успешным CI и merge. Применяется по запросу пользователя перед merge, когда ревьюер оставил замечания, которые нужно разобрать.

Два типа комментариев:

- обычные (верхний уровень PR): список - `gh pr view <N> --json comments`, ответ - `gh pr comment <N> --body "..."`;
- инлайн-ревью к строкам кода (threads): `gh api repos/{owner}/{repo}/pulls/<N>/comments`.

Флага ответа в ветку у `gh pr comment` нет - ответ в thread только через API:

```bash
gh api repos/{owner}/{repo}/pulls/<N>/comments/<comment_id>/replies -f body="Текст ответа."
```

Порядок разбора:

1. По спискам комментариев отделить замечания ревьюера от собственных.
2. Оценить обоснованность каждого замечания ревьюера.
3. По обоснованным замечаниям - внести правки, прогнать тесты и линтеры, закоммитить и запушить; дождаться CI (см. «Мониторинг завершения»).
4. Ответить на каждое замечание оценкой обоснованности и выполненными действиями (ссылка на коммит с исправлением).

Замечания, не требующие правок, тоже закрываются ответом с обоснованием, почему изменение не нужно.

### Смержить PR

Важно: выполнять merge только после явного подтверждения пользователя. Одобрения общего плана или зелёный CI недостаточно: merge - это отдельный рубеж, по которому нужно отдельно спросить «мержить?» и дождаться явного «да». До подтверждения следует сообщить статус (CI зелёный, конфликтов нет) и остановиться.

Важно: merge выполнять только при успешном CI. Перед merge дождаться успешного завершения всех checks PR (`gh pr checks <N> --watch --fail-fast`). Если пользователь просит мержить, пока checks не завершены, - сначала дождаться их успеха и только потом мержить; при падении checks - не мержить, сообщить о падении и предложить исправление.

```bash
gh pr merge <N> --merge --delete-branch
```

Стратегия по умолчанию - merge commit (`--merge`); альтернативы: `--squash`, `--rebase`.

Флаг `--delete-branch` переключает на main и удаляет локальную ветку; удаленная ветка удаляется автоматически настройкой репо (delete branch on merge).

После merge задача из `Closes #N` закрывается сама.

## Workflows (CI/CD)

### Типовые workflows

- `Test code` - на открытие и обновление PR: линтеры, тесты, сборка Docker-образа
- `Release image` - на merge PR в main или вручную: публикация образа latest в GHCR и Docker Hub
- `Deploy to VPS` - вручную (workflow_dispatch): `gh workflow run deploy.yml --ref main`; автоматический запуск после `Release image` отключен

### Просмотр runs

```bash
gh run list                          # последние runs: STATUS, NAME, WORKFLOW, EVENT
gh run list --workflow "Test code"   # runs одного workflow
gh run view <id>                     # детали: jobs и шаги
gh run view <id> --log-failed        # логи упавших шагов
```

Логи шагов доступны напрямую (`--log-failed`, `--log`) - обходных путей через REST API не требуется.

### Запустить workflow вручную

```bash
gh workflow run release.yml --ref main
```

Команда не печатает id созданного run - узнать его: `gh run list --workflow "Release image" --limit 1`.

Перезапуск упавшего деплоя без пересборки образа: `gh run rerun <id>` на run деплоя.

## Мониторинг завершения

Встроенный watch заменяет polling-циклы. Bash-команды выполнять с увеличенным `timeout` (например 420000-600000 мс).

### Дождаться CI для PR

```bash
gh pr checks <N> --watch --fail-fast
```

Завершается итоговым статусом всех checks; код возврата ненулевой при падении. `--fail-fast` прерывает ожидание на первом упавшем check.

### Дождаться завершения run

```bash
gh run watch <id> --exit-status --compact
```

`--exit-status` дает ненулевой код при падении run; `--compact` выводит только значимые шаги. При падении смотреть логи: `gh run view <id> --log-failed`.

## Полный цикл (типовой)

1. Создать ветку от main: `git checkout main && git pull && git checkout -b fix/...`
2. Создать задачу: `gh issue create ...` -> запомнить `#N`
3. Внести изменения, тесты, CHANGELOG; закоммитить и запушить ветку
4. Создать PR с `Closes #N` в описании: `gh pr create ...`
5. Дождаться CI: `gh pr checks <N> --watch --fail-fast`
6. (Опционально) Разобрать комментарии ревью: см. «Обработка комментариев ревью (опционально)»
7. Смержить (только после явного подтверждения пользователя и зеленого CI из шага 5; при незавершенных checks - дождаться, при падении - не мержить): `gh pr merge <N> --merge --delete-branch`; задача закроется сама
8. Дождаться `Release image` (auto на merge в main): `gh run list --workflow "Release image"` -> `gh run watch <id> --exit-status`
9. При готовности доставить изменения запустить деплой вручную: `gh workflow run deploy.yml --ref main` -> найти run: `gh run list --workflow "Deploy to VPS" --limit 1` -> `gh run watch <id> --exit-status --compact`
