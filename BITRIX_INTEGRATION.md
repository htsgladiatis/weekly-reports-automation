# 🔗 Интеграция Bitrix24 CRM с дашбордом

## Текущий статус

✅ **Подключено**: Вебхук Bitrix24 настроен  
📊 **Источник данных**: `leads_data.json` (статический файл)  
⚠️ **Обновление**: Вручную (пока)

---

## Файлы проекта

### 1. `bitrix_api.py` 
Python-модуль для получения лидов из Bitrix24 CRM через REST API.

**Функции:**
- `get_lead_stats(date_from, date_to)` — получает статистику лидов за период
- `fetch_leads(date_from, date_to)` — получает все лиды за период
- `classify_lead(lead)` — классифицирует лид по аккаунту и каналу

**Использование:**
```bash
# Тест подключения
python bitrix_api.py test 2026-06-01 2026-06-07

# Экспорт в JSON
python bitrix_api.py export 2026-06-01 2026-06-07 leads_w5.json
```

### 2. `leads_data.json`
JSON-файл с данными лидов по неделям. Используется дашбордом для отображения.

**Структура:**
```json
{
  "updated": "2026-06-09T12:00:00",
  "weeks": {
    "w1": {
      "period": {"from": "2026-05-04", "to": "2026-05-10"},
      "accounts": {
        "e-20010227": {"leads": 5, "target": 0},
        ...
      },
      "total": {"leads": 5, "target": 0}
    },
    ...
  }
}
```

---

## Как обновить данные лидов

### Вариант 1: Вручную (текущий)

1. Откройте `leads_data.json`
2. Найдите нужную неделю (например, `"w5"`)
3. Обновите значения `leads` и `target` для каждого аккаунта
4. Сохраните файл
5. Закоммитьте и запушьте в `gh-pages`:
   ```bash
   git add leads_data.json
   git commit -m "Update leads data for week X"
   git push origin gh-pages
   ```

### Вариант 2: Через Python скрипт (при работающем API)

```bash
# Получить данные за неделю 5
python bitrix_api.py export 2026-06-01 2026-06-07 temp_w5.json

# Вручную скопировать данные из temp_w5.json в leads_data.json
# (раздел "w5")

# Закоммитить
git add leads_data.json
git commit -m "Update leads data from Bitrix24"
git push origin gh-pages
```

### Вариант 3: Автоматический (будущее)

**GitHub Actions Workflow** для автоматического обновления:
1. Раз в день запускает `bitrix_api.py`
2. Обновляет `leads_data.json`
3. Автоматически коммитит изменения

---

## Проблемы и решения

### ❌ Проблема: SSL Timeout при подключении к Bitrix24

**Причина**: Файрвол или прокси блокирует исходящие HTTPS-запросы к bitrix24.ru

**Решения:**
1. **Использовать VPN** при запуске скрипта
2. **Запустить на сервере** с доступом к Bitrix24
3. **Обновлять данные вручную** из CRM Битрикс24

### ✅ Решение 1: Экспорт из Bitrix24 UI

1. Зайдите в https://dunegroup.bitrix24.ru/crm/lead/list/
2. Выберите период (Фильтр → Дата создания)
3. Экспорт → Excel/CSV
4. Откройте файл и подсчитайте лиды вручную
5. Обновите `leads_data.json`

### ✅ Решение 2: Использовать Postman/Insomnia

1. Установите [Postman](https://www.postman.com/) или [Insomnia](https://insomnia.rest/)
2. Создайте GET-запрос:
   ```
   https://dunegroup.bitrix24.ru/rest/396/vk0fdm6r1qrtt81w/crm.lead.list?filter[>=DATE_CREATE]=2026-06-01T00:00:00&filter[<=DATE_CREATE]=2026-06-07T23:59:59
   ```
3. Скопируйте JSON-ответ
4. Обработайте данные и обновите `leads_data.json`

---

## API Endpoints Bitrix24

### Получить список лидов
```
GET https://dunegroup.bitrix24.ru/rest/396/vk0fdm6r1qrtt81w/crm.lead.list
```

**Параметры:**
- `filter[>=DATE_CREATE]` — начало периода (ISO 8601)
- `filter[<=DATE_CREATE]` — конец периода (ISO 8601)
- `select[]` — поля для выборки (ID, TITLE, STATUS_ID, UTM_*)

**Пример:**
```
https://dunegroup.bitrix24.ru/rest/396/vk0fdm6r1qrtt81w/crm.lead.list?filter[>=DATE_CREATE]=2026-06-01T00:00:00&filter[<=DATE_CREATE]=2026-06-07T23:59:59&select[]=ID&select[]=TITLE&select[]=STATUS_ID&select[]=UTM_CAMPAIGN
```

---

## Roadmap

- [x] Создать `bitrix_api.py` модуль
- [x] Создать `leads_data.json` со статическими данными
- [ ] Исправить SSL timeout проблему
- [ ] Добавить JavaScript загрузчик для дашборда
- [ ] Создать GitHub Actions workflow для автообновления
- [ ] Добавить UI для ручного ввода данных лидов
- [ ] Интегрировать real-time обновление через WebSocket

---

## Документация Bitrix24 REST API

- **Официальная документация**: https://dev.1c-bitrix.ru/rest_help/
- **CRM Leads**: https://dev.1c-bitrix.ru/rest_help/crm/leads/index.php
- **Вебхуки**: https://dev.1c-bitrix.ru/rest_help/general/events_method/index.php

---

**Дата создания**: 2026-06-09  
**Статус**: В разработке ⚙️  
**Автор**: Kiro AI + Dune Group Team
