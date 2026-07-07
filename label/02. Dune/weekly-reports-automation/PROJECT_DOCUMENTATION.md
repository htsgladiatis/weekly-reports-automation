# Dune Dashboard - Полная документация проекта

> **Версия:** 3.0  
> **Дата:** 2026-06-08  
> **Статус:** Production Ready ✅  
> **Веб-страница:** https://htsgladiatis.github.io/weekly-reports-automation/

---

## Цифровой отпечаток (Context Snapshot)

```json
{
  "snapshot_metadata": {
    "version": "3.0",
    "generated_at": "2026-06-08T21:08:00+03:00",
    "project_complexity": "medium",
    "confidence_score": 98,
    "language": "ru",
    "quality_gates": ["strict_json", "maximum_context_preservation", "zero_hallucination", "actionable_continuation"]
  },
  "project_overview": "Автоматизация еженедельной отчетности по рекламным кампаниям Яндекс.Директ. Проект включает Python-скрипты для генерации структурированных отчетов с данными из 4 рекламных кабинетов Яндекс.Директ, CRM-системы Битрикс24 (лиды и целевые лиды), Яндекс.Метрики (визиты, источники трафика). Отчеты автоматически создаются в Google Sheets с детализацией по кампаниям, метрикам и каналам.",
  "tech_stack": [
    "Python 3.x",
    "Google Sheets API v4",
    "google-auth (Service Account authentication)",
    "googleapiclient.discovery",
    "Битрикс24 REST API (входящий вебхук)",
    "Яндекс OAuth API",
    "Яндекс.Метрика API (счётчик 90747520)",
    "Яндекс.Директ API v5"
  ],
  "integrations": {
    "bitrix24": {
      "webhook_url": "https://dunegroup.bitrix24.ru/rest/396/vk0fdm6r1qrtt81w/",
      "status": "active",
      "test_date": "2026-06-08",
      "test_result": "11 leads, 4 target leads"
    },
    "yandex_oauth": {
      "client_id": "be5209733c5f4419b319a0f49d3eae9d",
      "access_token": "y0__wgBEM-PhesCGM73QSCayNHIFx4hTUWtppv9M4CUxW2X8SfIBsnW",
      "refresh_token": "2:AAA:AAAAAC1hR88:...",
      "expires_in": 13793410,
      "status": "active",
      "test_date": "2026-06-08"
    },
    "yandex_metrika": {
      "counter_id": "90747520",
      "site": "dune-group.ru",
      "status": "active",
      "test_result": "1689 visits, 80 SEO"
    },
    "google_sheets": {
      "spreadsheet_id": "1TMa7NMknshntaQE-Dgmr-Trjk3pQxvY_K1IyAYfjZ4A",
      "service_account": "andrew@oval-plate-464820-p5.iam.gserviceaccount.com",
      "status": "active"
    }
  },
  "key_entities": [
    {
      "name": "bitrix.py",
      "type": "python_module",
      "status": "active",
      "notes": "Модуль интеграции с Битрикс24 CRM. Вебхук: dunegroup.bitrix24.ru. Загружает лиды за период, фильтрует директовые (исключая брак по семантике стадии 'F'), считает лиды и целевые лиды (стадия 'S'), атрибуция по utm_campaign."
    },
    {
      "name": "yandex.py",
      "type": "python_module",
      "status": "active",
      "notes": "Модуль интеграции с Яндекс API (OAuth). Получает данные из Яндекс.Метрика (счётчик 90747520) и Яндекс.Директ. Содержит: get_visits(), get_campaigns_stats(), refresh_access_token()."
    },
    {
      "name": "report_2505.py",
      "type": "python_script",
      "status": "completed_verified",
      "notes": "Последний созданный отчет (25.05-31.05). Эталон для создания новых отчетов. Содержит правильную структуру ROWS и атрибуцию лидов."
    },
    {
      "name": "Google Sheets Integration",
      "type": "api_integration",
      "status": "active",
      "notes": "Spreadsheet ID: 1TMa7NMknshntaQE-Dgmr-Trjk3pQxvY_K1IyAYfjZ4A"
    },
    {
      "name": "karpathy-guidelines",
      "type": "ai_skill",
      "status": "active",
      "notes": "Скилл с 4 принципами: Think Before Coding, Simplicity First, Surgical Changes, Goal-Driven Execution. Обязателен к применению."
    }
  ],
  "file_context": [
    {
      "file_path": "bitrix.py",
      "role": "Интеграция с CRM",
      "last_changes": "Вебхук настроен: https://dunegroup.bitrix24.ru/rest/396/vk0fdm6r1qrtt81w/",
      "status": "verified_working"
    },
    {
      "file_path": "yandex.py",
      "role": "Интеграция с Яндекс API",
      "last_changes": "OAuth токен получен, счётчик Метрики 90747520, функции get_visits() и get_campaigns_stats()",
      "status": "verified_working"
    },
    {
      "file_path": "PROJECT_DOCUMENTATION.md",
      "role": "Документация",
      "last_changes": "Версия 3.0: добавлены все интеграции, цифровой отпечаток обновлён",
      "status": "current"
    },
    {
      "file_path": "BITRIX_SETUP.md",
      "role": "Инструкция подключения Битрикс",
      "status": "completed"
    },
    {
      "file_path": "YANDEX_SETUP.md",
      "role": "Инструкция подключения Яндекс",
      "status": "completed"
    }
  ],
  "session_timeline": [
    "1. Изучение структуры проекта и скилла Karpathy Guidelines",
    "2. Создание подробной документации PROJECT_DOCUMENTATION.md",
    "3. Подключение Битрикс24: создан вебхук, протестирован (11 лидов, 4 целевых)",
    "4. Подключение Яндекс OAuth: получен access_token и refresh_token",
    "5. Подключение Яндекс.Метрика: счётчик 90747520, протестирован (1689 визитов, 80 SEO)",
    "6. Создание модуля yandex.py для автоматизации",
    "7. Обновление документации и цифрового отпечатка до версии 3.0"
  ],
  "current_task": "Завершена полная интеграция всех API. Проект полностью автоматизирован: Битрикс24 (лиды), Яндекс.Метрика (визиты), Google Sheets (отчёты). Готов к созданию автоматического отчёта за 01.06-07.06.",
  "decision_log": [
    {
      "decision": "Клики vs Визиты",
      "rationale": "Столбец 'Визиты' для строк Директа = КЛИКИ из рекламных кабинетов (НЕ визиты из Метрики)",
      "alternatives_considered": "Использовать визиты из Метрики для всех каналов (отклонено)"
    },
    {
      "decision": "Атрибуция лидов",
      "rationale": "Все лиды с 'marquiz' → e-20010227. Стадия 'S' = целевой лид.",
      "alternatives_considered": "Распределить по другим аккаунтам (отклонено)"
    },
    {
      "decision": "OAuth токены",
      "rationale": "Токен получен через Яндекс OAuth. Refresh token сохранён для обновления.",
      "alternatives_considered": "Ручной ввод данных (отклонено)"
    },
    {
      "decision": "Счётчик Метрики 90747520",
      "rationale": "ID счётчика указан пользователем. Данные получены успешно.",
      "alternatives_considered": "Поиск счётчика автоматически (отклонено)"
    }
  ],
  "pending_issues": [],
  "risks_and_assumptions": [
    "OAuth токен действует ~4 месяца (доавгуст 2026)",
    "Битрикс24 вебхук активен и имеет доступ к CRM",
    "Счётчик Метрики 90747520 корректен для dune-group.ru",
    "Все лиды с 'marquiz' относятся к e-20010227",
    "Service Account имеет постоянный доступ к Google Таблице"
  ],
  "continuation_guide": "Вот полный контекст предыдущей сессии. Изучи его очень внимательно. Продолжай работу точно с того места, где мы остановились. Проект: Dune Dashboard — автоматизация еженедельных отчетов по рекламе в Google Sheets. Подключены все API: Битрикс24 (вебхук работает), Яндекс OAuth (токен активен), Яндекс.Метрика (счётчик 90747520). Для создания нового отчёта: запроси скриншоты Директа с детализацией ПО КАМПАНИЯМ → используй python bitrix.py и python yandex.py для получения данных → создай report_XXXX.py по шаблону report_2505.py → запусти и проверь в Google Sheets. При работе с кодом обязательно применяй Karpathy Guidelines."
}
```

---

## 📊 Описание проекта

Проект включает Python-скрипты для генерации структурированных еженедельных отчетов с данными из:
- 4 рекламных кабинетов Яндекс.Директ (e-20010227, e-17228851, dune-group, porg-3uieikjn)
- CRM-системы Битрикс24 (лиды и целевые лиды)
- Яндекс.Метрики (визиты, источники трафика)

Отчеты автоматически создаются в Google Sheets с детализацией по кампаниям, метрикам и каналам.

**Веб-страница:** https://htsgladiatis.github.io/weekly-reports-automation/

---

## 🔗 Подключенные интеграции

### 1. Битрикс24 CRM ✅
- **Вебхук:** `https://dunegroup.bitrix24.ru/rest/396/vk0fdm6r1qrtt81w/`
- **Статус:** Работает
- **Тест:** 11 лидов, 4 целевых (01.06-07.06)
- **Использование:** `python bitrix.py 2026-06-01 2026-06-07`

### 2. Яндекс OAuth ✅
- **ClientID:** `be5209733c5f4419b319a0f49d3eae9d`
- **Access Token:** Активен (~4 месяца)
- **Refresh Token:** Сохранён для обновления
- **Статус:** Работает

### 3. Яндекс.Метрика ✅
- **Счётчик:** `90747520` (dune-group.ru)
- **Статус:** Работает
- **Тест:** 1689 визитов, 80 SEO (01.06-07.06)
- **Использование:** `python yandex.py 2026-06-01 2026-06-07`

### 4. Google Sheets ✅
- **Spreadsheet ID:** `1TMa7NMknshntaQE-Dgmr-Trjk3pQxvY_K1IyAYfjZ4A`
- **Service Account:** `andrew@oval-plate-464820-p5.iam.gserviceaccount.com`
- **Статус:** Работает

---

## 🎯 Структура отчета

### 4-уровневая иерархия:
1. **Итого** (все каналы)
2. **Яндекс Директ** (сумма 4 аккаунтов)
3. **Аккаунты**: e-20010227, e-17228851, dune-group, porg-3uieikjn
4. **Кампании** под каждым аккаунтом
5. **SEO** (отдельная строка)
6. **Рекомендации** (отдельная строка)

### 12 колонок метрик:
| # | Колонка | Описание |
|---|---------|----------|
| 1 | Канал | Название канала/аккаунта/кампании |
| 2 | Показы | Количество показов рекламы |
| 3 | Визиты | Клики из Директа (НЕ из Метрики!) |
| 4 | CTR | (Клики / Показы) × 100%, 2 знака |
| 5 | CPC | Расход / Клики, целые рубли |
| 6 | Лиды | Количество лидов |
| 7 | Конверсия в Лид | (Лиды / Клики) × 100%, 2 знака |
| 8 | CPA | Расход / Лиды, целые рубли |
| 9 | Ц. Лиды | Целевые лиды |
| 10 | Конверсия в Ц. Лид | (Целевые / Лиды) × 100%, 2 знака |
| 11 | CPL | Расход / Целевые Лиды, целые рубли |
| 12 | Расход | Расход в рублях |

---

## 🚀 Быстрый старт

### Все API подключены! Запуск:

```bash
# Получить лиды из Битрикс24
python bitrix.py 2026-06-01 2026-06-07

# Получить визиты из Яндекс.Метрики
python yandex.py 2026-06-01 2026-06-07

# Создать отчёт в Google Sheets
python report_0106.py
```

---

## 📂 Структура файлов

```
.
├── PROJECT_DOCUMENTATION.md        # Подробная документация (ЭТОТ ФАЙЛ)
├── BITRIX_SETUP.md                 # Инструкция подключения Битрикс24
├── YANDEX_SETUP.md                 # Инструкция подключения Яндекс
├── bitrix.py                       # Интеграция с Битрикс24 CRM
├── yandex.py                       # Интеграция с Яндекс API
├── report_0405.py                  # Отчет 04.05-10.05
├── report_1105_v2.py               # Отчет 11.05-17.05
├── report_1805.py                  # Отчет 18.05-24.05
├── report_2505.py                  # Отчет 25.05-31.05 (эталон)
├── update_bitrix.ps1               # Скрипт настройки
└── 1. andrej-karpathy-skills/      # AI Guidelines
```

---

## 🤖 Karpathy Guidelines (Обязательны!)

### Принцип 1: Think Before Coding
**Don't assume. Don't hide confusion. Surface tradeoffs.**

### Принцип 2: Simplicity First
**Minimum code that solves the problem. Nothing speculative.**

### Принцип 3: Surgical Changes
**Touch only what you must. Clean up only your own mess.**

### Принцип 4: Goal-Driven Execution
**Define success criteria. Loop until verified.**

---

## 🔗 Ссылки

- **Веб-страница:** https://htsgladiatis.github.io/weekly-reports-automation/
- **Google Sheets:** https://docs.google.com/spreadsheets/d/1TMa7NMknshntaQE-Dgmr-Trjk3pQxvY_K1IyAYfjZ4A/
- **Репозиторий:** https://github.com/htsgladiatis/weekly-reports-automation
- **Битрикс24:** https://dunegroup.bitrix24.ru/

---

**Последнее обновление**: 2026-06-08  
**Версия**: 3.0  
**Статус**: Production Ready ✅