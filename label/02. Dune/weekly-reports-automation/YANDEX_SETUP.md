# Настройка Яндекс API (OAuth)

## Приложение "Dune Dashboard"
- **ClientID**: `be5209733c5f4419b319a0f49d3eae9d`
- **ClientSecret**: `810ceb8110124b849cfd59448b1cfe75`
- **Статус**: ✅ Приложение подключено

---

## 📋 Получение Access Token

### Шаг 1: Откройте ссылку авторизации

Откройте в браузере:
```
https://oauth.yandex.ru/authorize?response_type=code&client_id=be5209733c5f4419b319a0f49d3eae9d&redirect_uri=https://example.com
```

### Шаг 2: Авторизуйтесь и разрешите доступ
1. Войдите в аккаунт Яндекс
2. Нажмите **Разрешить**
3. Браузер перенаправит на `https://example.com/?code=XXXXX`

### Шаг 3: Скопируйте code из URL
Из адресной строки скопируйте значение после `code=` (до `&`):
```
code=AQBEXAMPLEXXXXX
```

### Шаг 4: Обменяйте code на access_token

Отправьте мне код, и я обменяю его на access_token.

Или выполните вручную:
```bash
curl -X POST https://oauth.yandex.ru/token \
  -d "grant_type=authorization_code" \
  -d "code=ВАШ_КОД" \
  -d "client_id=be5209733c5f4419b319a0f49d3eae9d" \
  -d "client_secret=810ceb8110124b849cfd59448b1cfe75"
```

---

## 🔑 Что даст access_token

С токеном можно получить:
- **Яндекс.Директ**: статистика кампаний, показы, клики, расход
- **Яндекс.Метрика**: визиты, источники трафика, SEO данные
- **Яндекс.Вебмастер**: данные о сайте

---

## ⚠️ Важно

- Токен действует ~1 год (refresh_token позволяет обновить)
- Токен нужно хранить безопасно (не публиковать в коде)
- Можно использовать переменную окружения `YANDEX_ACCESS_TOKEN`

---

**Статус:** ✅ Подключено и протестировано (2026-06-08)

### Полученные токены:
- **access_token**: `y0__wgBEM-PhesCGM73QSCayNHIFx4hTUWtppv9M4CUxW2X8SfIBsnW`
- **refresh_token**: `2:AAA:AAAAAC1hR88:1:80emErMeCFuz9-Kh:cDUnouTpklblKqbOwXity3Jgt56f-NuBAmArOfVXsUdI3YnLjwIvbBJxQWq7XmWyl3oU4KXxcQ:I_oeWLExoxevtGvP4O8Szw`
- **expires_in**: ~13793410 секунд (~4 месяца)

### Тестовый запуск:
```
python yandex.py 2026-06-01 2026-06-07

✅ Подключение настроено
Access token активен (~4 месяца)
```
