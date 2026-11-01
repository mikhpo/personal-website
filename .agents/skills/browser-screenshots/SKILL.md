---
name: browser-screenshots
description: "Скриншоты страниц сайта - dev-сервер и прод: статичные кадры через one-shot headless Chrome, мобильный вьюпорт и клики через python/playwright, кроп фрагментов через PIL"
---

## Предназначение

Визуальная проверка страниц сайта при демонстрации функциональности пользователю и при отладке: dev-окружение и продакшен. Полученные кадры показывать пользователю через инструмент Read - файлы возвращаются вложениями. Кадры в git не помещать: складывать во временный рабочий каталог (например `<tmp>/opencode/shots`).

## Выбор метода

- Статичный кадр страницы (десктоп, без взаимодействий) -> one-shot headless Chrome: один вызов bash, ноль зависимостей
- Мобильный вьюпорт, клики по элементам, ожидание анимаций, скриншот отдельного элемента -> python/playwright
- Рассмотреть фрагмент готового кадра крупнее (измерение зазоров, проверка деталей) -> кроп через PIL

## Подготовка окружения

1. Поднять dev-сервер проекта по его инструкциям и определить его адрес и порт.
2. После правок фронтенда пересобрать бандл, если дев-сервер не делает этого сам - автоперезагрузка бэкенда фронтенд-код не подхватывает.
3. При пустой базе сгенерировать демо-данные средствами проекта, если они предусмотрены.
4. Домен продакшена брать без подключения к серверу: homepage репозитория GitHub - `gh repo view --json homepageUrl`. Альтернативы: Sitemap-URL в robots.txt, `DOMAIN_NAME` в .env на сервере. Перед съемкой проверить живость: `curl -sS -o /dev/null -w "%{http_code}\n" "https://<домен>/"` - ожидать 200.

## One-shot headless Chrome

```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless --disable-gpu --hide-scrollbars --virtual-time-budget=12000 --window-size=1400,900 --screenshot=<path>.png "<URL>"
```

- `--virtual-time-budget=12000` дает странице выполнить клиентские выборки API до снимка; увеличивать при медленных запросах
- `--window-size` задает вьюпорт: 1400x900 для десктопа; для высокого кадра увеличивать высоту
- Кириллицу в query-параметрах кодировать: `python3 -c "import urllib.parse; print(urllib.parse.quote('путешествие'))"`
- На Linux путь к бинарнику другой (`google-chrome` или `chromium`); флаги те же

## Python + Playwright

Playwright устанавливается в окружение проекта (pip/uv); браузеры скачиваются командой `playwright install` в `~/Library/Caches/ms-playwright` (macOS). Скрипты запускать из каталога проекта: `uv run python <скрипт>.py`.

Эталонный скрипт мобильной съемки с раскрытием гамбургер-меню:

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    device = p.devices["iPhone 13"]  # viewport, DPR, touch и UA одним профилем
    context = browser.new_context(**device)
    page = context.new_page()
    page.goto("https://<домен>/", wait_until="networkidle")
    page.screenshot(path="<путь>/1-page.png")
    page.click(".navbar-toggler")
    page.wait_for_timeout(900)  # дождаться анимации раскрытия меню
    page.screenshot(path="<путь>/2-menu-open.png")
    browser.close()
```

- Готовые профили устройств: `p.devices["iPhone 13"]`, `p.devices["Pixel 7"]` и другие; ручная настройка - `new_context(viewport={"width": 390, "height": 844}, device_scale_factor=2, is_mobile=True, has_touch=True)`
- Полная страница: `page.screenshot(full_page=True)`; отдельный элемент: `page.locator(".navbar").screenshot(path=...)`
- Системный Chrome вместо скачанного chromium: `p.chromium.launch(channel="chrome", headless=True)`
- Ожидание загрузки данных страницы: `wait_until="networkidle"`; ожидание анимаций после клика: `page.wait_for_timeout(900)`

## Постобработка PIL

Рассмотреть фрагмент кадра крупнее (измерение зазоров, проверка деталей):

```bash
uv run python -c "
from PIL import Image
img = Image.open('<кадр>.png')
crop = img.crop((x1, y1, x2, y2)).resize(((x2 - x1) * 4, (y2 - y1) * 4), Image.NEAREST)
crop.save('<фрагмент>.png')
"
```
