# Knowledge — Dune Group Weekly Reports Automation

## What this is
Еженедельный отчётный конвейер для **Dune Group** (ремонт квартир под ключ, Ростов-на-Дону). Сводит данные из **4 кабинетов Яндекс.Директа + Bitrix24 CRM + Яндекс.Метрики**, создаёт вкладку в **Google Sheets** и публикует интерактивный дашборд на **GitHub Pages** → `https://htsgladiatis.github.io/weekly-reports-automation/`. В репо находятся Python-скрипты, недельные `report_DDMM.py`-шаблоны и один большой `index.html` (single-file dashboard).

**Operating Mode: "L99 Manual Mode"** (см. `weekly_report_prompt.json` v2.1) — AI-агент делает работу **вручную** через `read_files()` → расчёт формул руками → `str_replace()`/`write_file()` → показал сводку пользователю → `git push`. **Никаких Python/баsh/sub-агентов для бизнес-логики.**

> 🛠 Уточнение (w15, 18.08.2026): допускается использовать `python`/`node` **только для чтения и проверки** — парсинг CSV (лиды/Директ/Вебмастер) и валидация JS в index.html (`new Function`). Итоговые цифры и правки файлов — вручную, формулы перепроверяются вручную. Полный разбор — в разделе «Логика сборки w15» ниже.

## Stack
- Python 3 (стандартный `urllib`, без `requests`)
- Google Sheets API v4 (Service Account)
- Yandex.Metrika Reporting API
- Yandex.Direct API v5 (готовый клиент в коде, токен НЕ получен)
- Bitrix24 REST (входящий вебхук)
- GitHub Pages (`gh-pages` + `gh-pages-v2` branch)
- Один файл `index.html` со встроенным JS + Chart.js (нет бэкенда)

## Key constants
| Что | Значение | Где живёт |
|---|---|---|
| Bitrix24 webhook | `https://dunegroup.bitrix24.ru/rest/396/vk0fdm6r1qrtt81w/` | `bitrix_api.py:18` `WEBHOOK_URL` |
| Метрика counter | `90747520` (dune-group.ru) | `metrika_seo.py:16` `COUNTER_ID` |
| Метрика OAuth token | `y0__wgBEM-PhesCGM…` ⚠️ **захардкожен** | `metrika_seo.py:14` |
| Google Spreadsheet ID | `1TMa7NMknshntaQE-Dgmr-Trjk3pQxvY_K1IyAYfjZ4A` | `README.md`, в `report_*.py` |
| Service Account email | `andrew@oval-plate-464820-p5.iam.gserviceaccount.com` | `README.md` |
| GitHub repo | `htsgladiatis/weekly-reports-automation` | `deploy.sh` |
| 4 Direct accounts | `e-20010227` (ремонт), `e-17228851` (строит.), `dune-group` (риелторы), `porg-3uieikjn` (фото/тг) | везде |
| Креды Google | `c:\Users\user\Desktop\kiro\credentials.json` | `CLAUDE_CONTEXT.md` |

## Where key code lives
| Файл | Роль | Статус |
|---|---|---|
| `index.html` (~75 KB) | **ГЛАВНЫЙ дашборд** GitHub Pages. 4 inline JS-структуры: `weeks[]` (w1–w10), `months[]` (m1–m3), `seoWeeklyData{}`, `weeklyDailyData{}`. KPI/графики/таблица/SEO — всё в одном `<script>`. | active |
| `weekly_report_prompt.json` v2.1 | Операционная процедура «L99 Manual Mode»: 10 фаз от read_files до git push. ⚠️ Включает «golden rules»: никаких sub-агентов, никакого Python для парсинга, всегда показывать сводку + ждать «да». | active |
| `CLAUDE_CONTEXT.md` | Самодостаточный context для AI-агента: бренд, источники, 10 нед. фактических данных, формулы, устройство дашборда, чек-лист w11+. Держи максимально свежим. | active |
| `auto_weekly_report.py` | Оркестратор (`WeeklyReportBuilder`). Грузит Direct CSV → Bitrix24 → Metrika → печатает сводку. `generate_report_script()` — ⚠️ **TODO заглушка** (стр. 217–230). | half-done |
| `bitrix_api.py` | Bitrix24: `crm.lead.list` фильтр `>=DATE_CREATE/<=DATE_CREATE`, classifier по UTM `cabinet-XXXXX`/`marquiz`, STATUS_ID="S" = целевой. Траш-статусы: F/JUNK/SPAM. | ready |
| `metrika_seo.py` | Метрика: `ym:s:trafficSource=='organic'` → visits/users/bounceRate/pageDepth/avgDuration + topPages + searchQueries. ⚠️ Токен в исходнике (security hole). | ready |
| `yandex_direct_api.py` | Полноценный API-клиент Директа v5 (campaigns/statistics/manage) — 25 KB. ⚠️ OAuth не получен, поэтому данные идут вручную. | ready-but-no-token |
| `parse_direct_xlsx.py` | Парсер Excel выгрузок Директа. ⚠️ "В разработке" по README. | парсер-как-фича |
| `extract_daily_data.py` | Дневной разрез из xlsx → `/tmp/daily_data.json`. Реальные pattern только для **w9**. Остальное — выдуманные доли. | полу-готово |
| `embed_seo_and_daily.py` | Трансформер HTML: читает `seo_all_weeks.json` → инжектит `seoWeeklyData` и `weeklyDailyData` → правит `renderTopLandingPages`/`renderSearchQueries` + переключатель «по дням» для single-week. | active |
| `update_dashboards.py` | Legacy-апдейтер: regex по **UTF-16 LE** — вставляет `wN`-блок + dropdown + правки `months[]`. ⚠️ Хрупкий close-паттерн W8 (стр. 58-66), ломается если W8 нет. | legacy |
| `report_DDMM.py` × 14 | Недельные скрипты-шаблоны: `TAB_NAME="DD.MM-DD.MM"`, `ROWS[]`, `BOLD_ROWS[]`. Создают вкладку в Google Sheets на **позиции 0** через Service Account. Последний — `report_1608.py` (w15). | manual-copy-paste |
| `0. reports/<период>/` | Сырые выгрузки недели: CSV Директа × 4 аккаунта + LEAD_*.csv (CRM) + 2 Вебмастера (страницы/запросы). Свежая: `0. reports/10-16.08/`. | active |
| `deploy.sh` | Деплой: status → `cp dashboard.html index.html` → `git add+commit` → push в `gh-pages` **и** `gh-pages-v2` → `curl POST .../pages/builds` → poll build → CDN cache-buster `?v=deploy_$(date+%s)`. Требует `GITHUB_TOKEN`. | active |
| `pages_api.sh` | Диагностика GitHub Pages: scopes, config, последние 5 билдов, trigger. | active |
| `.kiro/skills/weekly-report.md` + `.kiro/specs/*` | ⚠️ **Папки пусты** в этом наборе файлов (хотя `README.md` ссылается на них). Specs concepts (requirements.md/design.md/tasks.md/bugfix.md) описаны в `README.md` §Контекст. | stale-refs |
| `test_report_0106_bug_exploration.py` + `test_report_0106_preservation.py` | PBT-тесты для cost-calculation-fix (w5). 20 тестов проходят. | active |

## Команды (Windows / Git Bash)

```bash
# 1. Сбор данных за неделю (если есть Direct CSV)
python auto_weekly_report.py 2026-06-08 2026-06-14 direct_0806.csv

# 2. Тест интеграций
python bitrix_api.py test 2026-06-08 2026-06-14
python metrika_seo.py test 2026-06-08 2026-06-14
python bitrix_api.py server                                 # localhost:8000 HTTP endpoint

# 3. Создать Google Sheets вкладку
python report_0806.py                                       # → новый TAB на позиции 0

# 4. Push в Google Sheets (CPA/CPL обновление существующей таблицы)
python update_sheets_cpa_cpl.py

# 5. Обновить дашборд и задеплоить
# edit index.html / dashboard.html → bash deploy.sh        # (ENV: GITHUB_TOKEN обязателен)

# 6. Диагностика GitHub Pages
bash pages_api.sh $GITHUB_TOKEN

# 7. Дневной разрез из xlsx-выгрузок
python extract_daily_data.py                                # → /tmp/daily_data.json (на Windows сломается!)
```

**Нет** `package.json`, **нет** `make`, **нет** CI в смысле автосборки. `pytest` используется только для PBT-тестов (`test_report_0106_*.py`).

## Бизнес-домен

**4 уровня строк отчёта:**
1. Итого (все каналы)
2. Яндекс Директ (Σ 4 аккаунтов)
3. 4 аккаунта: `e-20010227`, `e-17228851`, `dune-group`, `porg-3uieikjn` (каждый с детализацией по кампаниям)
4. SEO (отдельная строка, визиты из Метрики = `ym:s:trafficSource=='organic'`)
5. Рекомендации (звонки/сарафанное — лиды без показов/кликов)

**Столбцы:** `Показы | Визиты(=клики!) | CTR | CPC | Лиды | Конв. в Лид | CPA | Ц.Лиды | Конв. в Ц.Лид | CPL | Расход`

**Формулы** (одинаковые в JS и Python):
```
CTR     = clicks / impressions × 100                (2 знака)
CPC     = round(spend / clicks)                     (целые)
CPA     = round(spend / leads)        | null ⇒ "—"
CPL     = round(spend / target)       | null ⇒ "—"
ConvЛ   = leads / clicks × 100       | null ⇒ "—"
ConvЦ.Л = target / leads × 100       | null ⇒ "—"
Расход  = X XXX ₽ (пробел как разделитель тысяч)
```

**Атрибуция лидов** (Bitrix24):
- `marquiz` ⇒ **e-20010227** (по умолчанию)
- `cabinet-e-XXXXXXX` UTM ⇒ конкретный аккаунт
- `STATUS_ID="S"` ⇒ целевой лид (главный KPI проекта)
- Исключить стадии: Дубль, Подрядчики реклама, Ошиблись номером, Вакансии (status F/JUNK/SPAM)

## Добавление новой недели (w11+) — «L99 Manual Mode»

> ⚠️ **Никакого** Python/баsh/sub-агентов для бизнес-логики. Только `read_files`/`write_file`/`str_replace`. И **всегда** спросить пользователя «да?» перед `git push`.

**10 фаз** (полная версия: `weekly_report_prompt.json`):

1. **Получение данных** — прочитать CSV/xlsx (Direct, SEO) + LEAD.html (Bitrix) через `read_files()`
2. **Парсинг CSV Директа** — Σ impressions/clicks/spend по 4 аккаунтам (блоками по 5-10 строк)
3. **Парсинг лидов** — totalLeads = directLeads + seoLeads + otherLeads; totalTarget аналогично
4. **Парсинг SEO** — totalSeoVisits = Σ clicks; top-10 pages/queries
5. **Расчёт метрик** — CTR/CPC/CPA/CPL/convLead/convTarget. Деление на 0 = `null`. Каждую формулу проверить обратным пересчётом (`CPA × leads ≈ spend`)
6. **Создать `report_DDMM.py`** — шаблон = самый свежий `report_*.py` в корне (например `report_1307.py`)
7. **Обновить дашборд `index.html`**: добавить `w{N+1}` в:
   - `weeks[]` (полный объект + accounts × 4)
   - `months[]` (нужный месяц или новый, обновить `dateRange`)
   - `seoWeeklyData{}` (stats + topPages×10 + searchQueries×10) + **вручную** пересчитать `'all'` (visits=Σ, остальные — взвешенные по visits, topPages/Queries объединить и переранжировать)
   - `weeklyDailyData{}` (опционально: pattern×7 + startDate)
8. **Верификация** — `weeks[id]` уникален; Σ `accounts` = `weeks.metrics`; `months.weeks` содержит новый id; `seoWeeklyData` ключи уникальны; читаем изменённые участки обратно через `read_files()`
9. **ПОДТВЕРЖДЕНИЕ** — вывести пользователю ПОЛНУЮ СВОДКУ (период, по аккаунтам таблицу, лиды по каналам, метрики) → ждать «да?»
10. **Публикация** — `git add index.html report_DDMM.py && git commit && git push origin gh-pages` (или `bash deploy.sh`)

## Gotchas / скрытые правила

- 🟥 **OAuth-токен Метрики в исходнике `metrika_seo.py:14`** — security hole. Если репо публичное, токен скомпрометирован. Перед коммитом → `.env` + `python-dotenv`.
- 🟥 **Столбец «Визиты» = КЛИКИ из Директа, НЕ визиты из Метрики.** Метрика-визиты — только строка SEO. (Решение в `README.md` §Важные решения-1.)
- 🟥 **`STATUS_ID="S"` = «Целевой лид»** — точное совпадение. **Не путать** с «QUALIFIED» в некоторых редакциях Bitrix24.
- 🟥 **`seoWeeklyData['all']`** обновляется **руками** при добавлении недели (visits=Σ по всем неделям, topPages/Queries — переранжировать топ-10).
- 🟥 **В `weeks[]` аккаунтов ВСЕГДА 4**, даже если все нули — dropdown и таблица каналов требуют полноты.
- 🟧 **`auto_weekly_report.generate_report_script()` TODO** — метод сейчас возвращает заглушку, реальной генерации нет.
- 🟧 **`update_dashboards.py`** работает с **UTF-16 LE** и regex по close-паттерну W8 — если в файле W8 нет, падает. Это legacy-скрипт для w9; новые недели лучше добавлять через `str_replace`.
- 🟧 **`extract_daily_data.py`** пишет в **`/tmp/daily_data.json`** — на Windows путь сломается, нужно править под `os.path.join(tempfile.gettempdir(), ...)`.
- 🟧 **`pull-secret Bitrix24 webhook`** — захардкожен в `bitrix_api.py:18`. Если репо публичное, доступ к CRM.
- 🟨 **Кампании в e-20010227 постоянно множатся** — нужны скриншоты **с детализацией по кампаниям** для КАЖДОЙ, не суммарно.
- 🟨 **Неделя = Пн–Вс, UTC+3**. Метка `ДД.ММ–ДД.ММ`.
- 🟨 **`index.html` и `dashboard.html`** параллельны как prod + dev; `deploy.sh` синхронизирует (`cp dashboard.html index.html`).
- 🟨 **GitHub Pages ветки: `gh-pages` И `gh-pages-v2`** — обе пушатся в `deploy.sh` (резерв).
- 🟨 **Спецификации (`.kiro/specs/*`)** пусты, README ссылается на них как на завершённые. Реальные артефакты — в `README.md` §«Context Snapshot» и `cost-calculation-fix` (см. git log).

## Что НЕ автоматизировано (= тех-долг)

| Проблема | Severity | Workaround сейчас |
|---|---|---|
| OAuth Директа не получен → Direct данные вручную (скриншоты или CSV) | High | `report_*.py` создаёт вкладку из захардкоженных чисел |
| `auto_weekly_report.generate_report_script()` — TODO | High | Manual copy-paste из `report_2505.py` |
| Секреты в исходниках (Metrika token, Bitrix webhook) | High | ⚠️ repo private, пока терпимо |
| GitHub Actions cron (понедельник 09:00) | Medium | `deploy.sh` руками |
| Web UI для загрузки xlsx Директа | Medium | Скриншоты + файлы в `week-DD-MM/` |
| `seoWeeklyData['all']` обновление ручное | Medium | Чек-лист в `CLAUDE_CONTEXT.md` §6 |
| `extract_daily_data.py` → `/tmp/` на Windows | Low | Запускать в WSL/Git Bash с правильным FS |

## Сводка за весь период (на сейчас)

15 недель (**04.05–16.08.2026**): **1 455 516** imp · **27 014** clk · **401 335 ₽** · **471** лид · **70** целевых · CPA **852 ₽** · CPL **5 733 ₽** · CTR **1,86%** · SEO-визитов **749**.

> ⚠️ Число лидов за неделю = **ВСЕ записи CRM за период** (включая Дубль / Подрядчики реклама / Нецелевые).
> Это конвенция пользователя, подтверждённая на w13 (47/47), w14 (43) и w15 (35/35) — см. раздел «Логика сборки w15» ниже.

По аккаунтам (Σ 15 нед.):

| Аккаунт | Показы | Клики | Расход | Лиды |
|---|---|---|---|---|
| **e-20010227** (ремонт) | 631 623 | 9 732 | **306 753 ₽** | **129** |
| e-17228851 (строит.) | 764 780 | 15 537 | 94 339 ₽ | 3 |
| dune-group (риелторы) | 23 797 | 853 | 244 ₽ | 0 |
| porg-3uieikjn (фото) | 35 316 | 892 | 0 ₽ | 0 |

Вывод: **e-20010227 — рабочая лошадка** (76% расходов, ~100% лидов Директа). Остальные три — экспериментальные.

---

## Логика сборки недели w15 (10.08–16.08) — эталон для w16+

> Задача от пользователя: «деплой новый отчет в гитхаб, данные в `C:\Users\user\Desktop\10-16D`».
> Папка перенесена в проект: **`0. reports/10-16.08/`** (конвенция: `0. reports/<период>/`).
> Результат: `report_1608.py` + дашборд w15 (коммиты `5feb81e`, `8a65c37` на `gh-pages`).

### 1. Исходники (7 файлов в `0. reports/10-16.08/`)

| Файл | Что даёт |
|---|---|
| `2026-08-18_10-08-25_e-20010227.csv` | Директ, аккаунт ремонта: imp/clicks/spend по кампаниям и дням |
| `2026-08-18_10-09-22_e-17228851.csv` | Директ, стройка |
| `2026-08-18_10-10-12_porg-3uieikjn.csv` | Директ, фото/ТГ |
| `2026-08-18_10-10-56_dune-group.csv` | Директ, риелторы |
| `LEAD_20260818_91aba817_6a840485499af.csv` | Bitrix24 CRM: лиды (разделитель `;`) |
| `dune-group.ru_6bae27022ee16b0aa6b26456.csv` | Вебмастер — страницы: Impressions/Clicks по Path |
| `dune-group.ru_96992f0a8112491212918001.csv` | Вебмастер — поисковые запросы |

### 2. Директ (4 аккаунта, «Визиты» = клики!)

- Каждый CSV имеет строку **«Итого»** — берём её (imp / clicks / spend), а не сумму строк (в e-20010227 файл — день×объявление, суммировать опасно: клики считаются по объявлениям, а Итого уже свёрнут).
- w15: `e-20010227` 954/19/1586₽ · `e-17228851` 319/11/0 · `porg-3uieikjn` 1337/44/0 · `dune-group` 0/0/0 → **Директ итого: 2610 imp · 74 clk · 1586 ₽**.
- Кампания `117666311` = «МК ТК // Ремонт // remont.dune-group.ru» (сверка по `0. reports/20-26/…e-20010227.csv` — там колонка «Название кампании» есть, а в свежей выгрузке только №).

### 3. Лиды (CRM) — ВАЖНО: считаем ВСЕ

- Читаем `LEAD_*.csv` (delimiter `;`, encoding utf-8-sig).
- **Число лидов недели = число ВСЕХ строк CSV** (в w15 — 35). НЕ вычитаем «Дубль»/«Подрядчики реклама»/«Нецелевой лид» — это конвенция пользователя (w13: 47 записей → 47 лидов).
- **Целевые лиды** = стадия «Целевой лид» (в w15 — 2: Ирина Носкова/Технониколь «По рекомендации», Александр ТЦ «Золотой Вавилон» «Запросы по СЕО»).
- Атрибуция по источнику (`Источник` в CSV):
  - `Яндекс.Директ` → Директ (1 лид: «Заявка с сайта remont.dune-group.ru», UTM `design-remont` → e-20010227);
  - `Запросы по СЕО` → SEO (1 лид, он же целевой);
  - всё остальное (звонки, рекомендации, ТГ, Билайн АТС) → Другие/Рекомендации (33 лида, из них 1 целевой).
- Итог: **35 лидов · 2 целевых**; Директ 1/0 · SEO 1/1 · Другие 33/1.

### 4. SEO (Вебмастер, не Метрика!)

- `visits` = **клики** из поиска = сумма колонки `Clicks` в файле страниц (в w15 — **65**).
- Топ-10 страниц и запросов — по убыванию Clicks; `bounceRate: 0.0`, `users/bounce/pageDepth/avgDuration: null` (Вебмастер их не даёт — как в w13/w14).
- `seoWeeklyData['all']` пересчитывается: visits=Σ всех недель, topPages/searchQueries объединяются и переранжируются (скрипт в node, см. историю сессии; в w15 стал 582).

### 5. Метрики и скрипты

- Формулы — как в README §3; деление на 0 → «—» / null.
- Создан `report_1608.py` по шаблону `report_2707.py` (`ROWS[]`, `BOLD_ROWS`, Service Account) — вкладка `10.08-16.08` в Google Sheets, **запуск: `python report_1608.py`** (ещё не запускался).
- Дашборд: в `index.html` добавлен блок w15 в `weeks[]` (после w14, перед `];`), `months[]` (Август: w13–w15, dateRange `27.07–16.08`), `seoWeeklyData['w15']` + `'all'`, `weeklyDailyData['w15']`, шапка (ptIx/ptLabel, SEO-бейдж).

### 6. Проверка и деплой

1. `node` — распарсить `<script>` из index.html: `new Function()` → JS-синтаксис OK; суммы аккаунтов = totals недели (2610/74/1586 ✓).
2. `cp index.html dashboard.html` — deploy.sh копирует **dashboard.html → index.html**, поэтому dashboard должен быть синхронен (в нём были только w1–w9!).
3. Git был отключён (`.git_disabled`) → `mv .git_disabled .git`, `git add index.html dashboard.html report_1608.py`, commit, `git push origin gh-pages`.
4. Проверка лайва: `curl https://htsgladiatis.github.io/weekly-reports-automation/` → ищем `w15` / `leads: 35`; сборка Pages — через API `pages/builds`.

### 7. Грабли (запомнить!)

- ❌ НЕ вычитать «Дубль/Подрядчики» из лидов — пользователь хочет **все записи CRM** (был фикс-коммит `8a65c37`).
- ⚠️ `gh-pages-v2` (резерв) — remote впереди на 7 коммитов (исправления w13), НЕ пушить force; главная ветка — `gh-pages`.
- ⚠️ `index2.html` / `index_ghpages.html` — старые форматы без `weeks[]`, не трогать.
- ⚠️ В свежих CSV Директа нет колонки «Название кампании» — сверять № кампании со старыми выгрузками в `0. reports/`.

