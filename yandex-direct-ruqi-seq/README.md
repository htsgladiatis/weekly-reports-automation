# 📊 Яндекс.Директ — RUQI + Секвойя

**Проект:** Управление рекламными кампаниями Яндекс.Директ для двух проектов  
**RUQI:** ruqi.ru — аутсорсинг линейного персонала  
**Секвойя:** sequoia-service.ru — аутсорсинг персонала  
**Бюджет мая 2026:** 250 000 ₽ с НДС (200к RUQI + 50к Секвойя)  
**Последнее обновление:** 15.06.2026

---

## 📁 Структура проекта

```
yandex-direct-ruqi-seq/
├── README.md              ← Главный документ (вы здесь)
├── docs/                  ← Документация, снапшоты, планы
│   ├── PROJECT_CONTEXT.json       ← Цифровой отпечаток текущей сессии
│   ├── ruqi_snapshot_2026-05-21.md
│   └── ...
├── data/                  ← Данные: выгрузки, отчёты, JSON
│   ├── roistat_result.json
│   ├── roistat_summary.json
│   ├── roistat_columns.json
│   └── project_225433_report-*.xlsx
├── dashboards/            ← HTML-дашборды для GitHub Pages
│   ├── dashboard.html     ← Главный дашборд (июнь)
│   ├── dashboard_may.html ← Дашборд мая
│   ├── roistat_may.html   ← Детализация Roistat май
│   └── roistat_june.html  ← Детализация Roistat июнь
├── scripts/               ← Скрипты автоматизации
│   ├── api/               ← API Яндекс.Директ
│   ├── roistat/           ← Roistat API + парсеры
│   ├── reports/           ← Генераторы отчётов
│   └── utils/             ← Утилиты
├── archive/               ← Старые отчёты, аудиты, бэкапы
└── .env.yandex_direct     ← Токены (НЕ в git!)
```

---

## 🔑 Токены и доступы

| Сервис | Токен / Ключ | Проект / Логин |
|--------|-------------|----------------|
| RUQI Директ | `y0__xCJkPzcBRijg0AgrJW_gBdA2r0WSmm50ZSBl2-JK2R4wNZozg` | e-16908818 |
| Секвойя Директ | `y0__xCWk628BBijg0Ags_nyjhfdsbSqn6kSthlGE4XfkitZgndWJQ` | — |
| Метрика (только чтение) | `y0__xCWk628BBjDyT4gpevy0RasROXadsoFZpyZ80RT1K-i2DL8Lg` | ClientID: 258d8d1d23ec498b985414cb0041d10d |
| Roistat | `d894875529eb1a633bcc07f6b6785a84` | Проект 225433 |

---

## 📊 Балансы кабинетов (актуально на 15.06.2026)

| Кабинет | Счёт | Баланс (без НДС) | С НДС |
|---------|------|-----------------|-------|
| RUQI | 69184724 | 52 660 ₽ | 64 246 ₽ |
| Секвойя | 69184724 | 54 076 ₽ | 65 973 ₽ |

---

## 📈 KPI за июнь 2026 (1–15 июня)

### RUQI
| Метрика | Директ API | Roistat | Комментарий |
|---------|-----------|---------|-------------|
| Расход | 120 480 ₽ | 119 094 ₽ | ✅ Совпадает |
| Конверсии/Заявки | 47 | 26 | ⚠️ Разные методологии |
| CPA/CPL | 2 563 ₽ | 4 581 ₽ | ⚠️ Директ: цель, Roistat: заявки |
| Целевые лиды | — | 2 | ℹ️ Только Roistat |
| Продажи | — | 0 | ⚠️ Проверить CRM |

### Секвойя
| Метрика | Значение |
|---------|---------|
| Расход | 20 264 ₽ |
| Конверсии | 31 |
| CPA | 654 ₽ |
| Активных РК | 3 (из 147) |

---

## 🚨 Критические решения (требуют действий)

1. **Баланс RUQI 52 660 ₽** — хватит на ~6–7 дней. Пополнить минимум на 100–150к ₽.
2. **МК // CPA Цель (708408079)** — SUSPENDED. В мае дала 22 конв · CPA 1 902 ₽. **Включить обратно.**
3. **Омск — бюджет 8 000 ₽/день** — снизить до 2 000–3 000 ₽/день.
4. **Аутсорсинг.СПб** — CPA вырос с 876 ₽ → 3 999 ₽. Снизить ставки на 30–50%.
5. **Roistat: потеря 45% заявок** — 47 конверсий Директа → 26 заявок Roistat. Проверить интеграцию форм → CRM.

---

## 🔗 Дашборды на GitHub Pages

| Страница | URL |
|----------|-----|
| Главный (июнь) | https://htsgladiatis.github.io/weekly-reports-automation/dashboard.html |
| Май | https://htsgladiatis.github.io/weekly-reports-automation/dashboard_may.html |
| Roistat май | https://htsgladiatis.github.io/weekly-reports-automation/roistat_may.html |
| Roistat июнь | https://htsgladiatis.github.io/weekly-reports-automation/roistat_june.html |

---

## 🛠 Как обновить данные

### 1. Директ API (расход, конверсии, статусы)
```bash
node scripts/api/get_june_report.js      # Текущий месяц
node scripts/api/get_may_full.js         # Полный месяц
node scripts/api/check_campaigns_status.js  # Статусы РК
```

### 2. Roistat (заявки, ЦЛ, продажи)
```bash
node scripts/roistat/build_roistat_pages.js      # Генерация HTML из xlsx
node scripts/roistat/extract_roistat_summary.js  # Summary JSON
```

### 3. Обновить дашборды
```bash
# Вручную обновить dashboard.html и dashboard_may.html
# Запушить в ветку gh-pages:
git checkout gh-pages
git add -f dashboards/*.html
git commit -m "Update dashboards"
git push origin gh-pages
```

---

## 📋 Журнал изменений

| Дата | Событие |
|------|---------|
| 21.05.2026 | Исправлена цель МК CPA (utm_sourse → Заявка 304226839) |
| 21.05.2026 | Включены кампании с лучшим CPA, приостановлены убыточные |
| 25.05.2026 | Последнее обновление дашборда (данные до 24.05) |
| 15.06.2026 | Восстановлена работа, обновлены данные за май и июнь, добавлены Roistat выгрузки |

---

## ⚠️ Важные замечания

- **Все суммы с НДС** (по умолчанию в API Директа)
- **Roistat не атрибутирует Директ** — 66% лидов без источника
- **Баланс кабинета недоступен через API** — запрашивать вручную из интерфейса
- **Данные Директа с задержкой до 3 часов**
- **Токены хранятся в `.env.yandex_direct`** — не коммитить в git!

---

*Сгенерировано: 15.06.2026 · Автоматизация Яндекс.Директ RUQI + Секвойя*
