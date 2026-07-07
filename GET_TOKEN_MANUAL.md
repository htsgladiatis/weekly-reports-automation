# 🔑 Получение токена Яндекс.Директ API (Ручной способ)

## Способ 1: Через OAuth URL (Самый простой)

### Шаг 1: Откройте URL в браузере

Скопируйте и откройте эту ссылку:

```
https://oauth.yandex.ru/authorize?response_type=token&client_id=be5209733c5f4419b319a0f49d3eae9d
```

### Шаг 2: Авторизуйтесь

1. Войдите в свой аккаунт Яндекс (если не залогинены)
2. Разрешите доступ приложению

### Шаг 3: Скопируйте токен

После авторизации вы будете перенаправлены на страницу с URL вида:

```
https://oauth.yandex.ru/verification_code#access_token=ВАШТОКЕНЗДЕСЬ&token_type=bearer&expires_in=...
```

**Скопируйте всё между `access_token=` и `&token_type`** — это ваш токен!

### Шаг 4: Сохраните токен

Создайте файл `.env` со следующим содержимым:

```
YANDEX_DIRECT_TOKEN=вашскопированныйтокен
```

### Шаг 5: Проверьте

```bash
python yandex_direct_api.py test
```

---

## Способ 2: Использовать Postman/Insomnia

### Шаг 1: Создайте POST запрос

URL: `https://oauth.yandex.ru/token`

Headers:
```
Content-Type: application/x-www-form-urlencoded
```

Body (x-www-form-urlencoded):
```
grant_type: authorization_code
code: ВАШ_КОД_ПОДТВЕРЖДЕНИЯ
client_id: be5209733c5f4419b319a0f49d3eae9d
client_secret: 810ceb8110124b849cfd59448b1cfe75
```

### Шаг 2: Отправьте запрос

Ответ будет содержать:
```json
{
  "access_token": "y0_...",
  "expires_in": 13127965,
  "refresh_token": "2:AAA:...",
  "token_type": "bearer"
}
```

### Шаг 3: Сохраните `access_token` в `.env`

---

## Способ 3: Использовать существующий токен Метрики

Если у вас уже есть токен для Метрики с правами `direct:api`, вы можете использовать его:

```
YANDEX_DIRECT_TOKEN=y0__wgBEM-PhesCGM73QSCayNHIFx4hTUWtppv9M4CUxW2X8SfIBsnW
```

**Проверьте права токена:**
```bash
python yandex_direct_api.py test
```

Если выдаст ошибку "Access denied", значит токен не имеет прав `direct:api`.

---

## Проверка токена

После сохранения токена в `.env`:

```bash
# Проверка подключения
python yandex_direct_api.py test

# Список кампаний
python yandex_direct_api.py campaigns

# Статистика за период
python yandex_direct_api.py stats 2026-06-08 2026-06-14
```

---

## Troubleshooting

### Ошибка: "Invalid token"
- Токен скопирован не полностью
- Токен истек (живут ~152 дня)
- Получите новый токен

### Ошибка: "Access denied"
- У токена нет прав `direct:api`
- Создайте новое приложение с правами `direct:api`

### Ошибка: "Client not found"
- Неправильный Client ID
- Используйте: `be5209733c5f4419b319a0f49d3eae9d`

---

**Версия**: 1.0  
**Дата**: 2026-06-16

