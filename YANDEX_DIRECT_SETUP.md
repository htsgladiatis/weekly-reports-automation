# 🔑 Настройка API Яндекс.Директ для автоматизации

## Шаг 1: Получение OAuth токена

### Вариант A: Через Яндекс OAuth (рекомендуется)

1. **Зарегистрируйте приложение:**
   - Откройте: https://oauth.yandex.ru/client/new
   - Название: "Dune Group Weekly Reports"
   - Права доступа (Scopes):
     - ✅ `direct:api` — доступ к API Директа
   - Callback URL: `https://oauth.yandex.ru/verification_code`
   
2. **Получите Client ID:**
   - После создания приложения скопируйте `Client ID`

3. **Получите OAuth токен:**
   ```
   https://oauth.yandex.ru/authorize?response_type=token&client_id=<ВАШ_CLIENT_ID>
   ```
   - Откройте эту ссылку в браузере (замените <ВАШ_CLIENT_ID>)
   - Авторизуйтесь
   - Скопируйте токен из URL (после #access_token=)

4. **Сохраните токен:**
   - Создайте файл `.env` в корне проекта:
     ```
     YANDEX_DIRECT_TOKEN=ваш_токен_здесь
     ```
   - Добавьте `.env` в `.gitignore`

### Вариант B: Ручная выгрузка (временное решение)

Если не можете получить токен сразу, используйте CSV выгрузки:

1. Зайдите в Яндекс.Директ → Статистика
2. Выберите период (например, 08.06-14.06)
3. Экспорт → CSV
4. Сохраните как `direct_DDMM.csv`

---

## Шаг 2: Формат CSV для ручной выгрузки

### Требуемая структура:

```csv
Account,Campaign,Impressions,Clicks,Spend
e-20010227,МК ТК // Ремонт // remont.dune-group.ru,50382,470,27820
e-20010227,РСЯ// типовой ремонт // Синяя кухня,15,1,0
e-17228851,МК Товарная - Мутуа дизайна,1051,15,2074
e-17228851,МК Товарная кампания ремонт,3202,27,0
dune-group,ЕПК РСЯ Риелторы - Яндекс.Услуги,0,0,0
porg-3uieikjn,МК // Строительство // СРА (Ф+ТГ),156,7,0
```

### Как создать этот CSV:

#### Вариант 1: Из интерфейса Яндекс.Директ

1. Зайдите в каждый из 4 кабинетов
2. Статистика → Кампании
3. Выберите период
4. Скопируйте данные в Excel:
   - Название кампании
   - Показы
   - Клики
   - Расход
5. Добавьте столбец "Account" с названием кабинета
6. Сохраните как CSV (UTF-8)

#### Вариант 2: Из Excel выгрузок (автоматизированный)

Если у вас есть выгрузки в формате:
```
2026-06-08_22-11-46_e-17228851.xlsx
```

Я могу создать скрипт для парсинга этих файлов!

---

## Шаг 3: Использование автоматического скрипта

### С CSV файлом (ручная выгрузка):

```bash
python auto_weekly_report.py 2026-06-08 2026-06-14 direct_0806.csv
```

### С API токеном (полная автоматизация):

```bash
# Сначала создайте .env файл с токеном
python auto_weekly_report.py 2026-06-08 2026-06-14 --use-api
```

---

## Шаг 4: API Яндекс.Директ (для разработчиков)

### Endpoints:

**Получить список кампаний:**
```
POST https://api.direct.yandex.com/json/v5/campaigns
Headers:
  Authorization: Bearer YOUR_TOKEN
  Accept-Language: ru

Body:
{
  "method": "get",
  "params": {
    "SelectionCriteria": {},
    "FieldNames": ["Id", "Name", "State"]
  }
}
```

**Получить статистику:**
```
POST https://api.direct.yandex.com/json/v5/reports
Headers:
  Authorization: Bearer YOUR_TOKEN
  Accept-Language: ru
  processingMode: auto
  returnMoneyInMicros: false

Body:
{
  "params": {
    "SelectionCriteria": {
      "DateFrom": "2026-06-08",
      "DateTo": "2026-06-14"
    },
    "FieldNames": ["Date", "CampaignName", "Impressions", "Clicks", "Cost"],
    "ReportName": "Weekly Report",
    "ReportType": "CAMPAIGN_PERFORMANCE_REPORT",
    "DateRangeType": "CUSTOM_DATE",
    "Format": "TSV",
    "IncludeVAT": "YES"
  }
}
```

---

## Troubleshooting

### Ошибка: "Invalid token"
- Проверьте, что токен скопирован полностью
- Убедитесь, что токен не истек (токены живут 1 год)
- Пересоздайте токен через OAuth

### Ошибка: "Access denied"
- Проверьте, что у токена есть scope `direct:api`
- Убедитесь, что у вашего аккаунта есть доступ к кабинетам

### Ошибка при чтении CSV
- Убедитесь, что файл в UTF-8
- Проверьте, что заголовки совпадают с шаблоном
- Удалите лишние пробелы в названиях столбцов

---

## Roadmap

- [x] Создать структуру для CSV импорта
- [ ] Реализовать API клиент для Директа
- [ ] Добавить кеширование токенов
- [ ] Создать UI для настройки токенов
- [ ] Автоматическое обновление токенов

---

**Дата создания**: 2026-06-16  
**Статус**: В разработке ⚙️  
**Автор**: Kiro AI

