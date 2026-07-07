"""
Интеграция с Яндекс API (OAuth).

Модуль для получения данных из Яндекс.Директ и Яндекс.Метрика.

Токен сохраняется в переменной окружения YANDEX_ACCESS_TOKEN
Для обновления используется YANDEX_REFRESH_TOKEN

Полученные токены:
- access_token: y0__wgBEM-PhesCGM73QSCayNHIFx4hTUWtppv9M4CUxW2X8SfIBsnW
- refresh_token: 2:AAA:AAAAAC1hR88:1:80emErMeCFuz9-Kh:cDUnouTpklblKqbOwXity3Jgt56f-NuBAmArOfVXsUdI3YnLjwIvbBJxQWq7XmWyl3oU4KXxcQ:I_oeWLExoxevtGvP4O8Szw
- expires_in: ~13793410 секунд (~4 месяца)
"""

import json
import os
import sys
import urllib.request
import urllib.parse

# --- Токены ---------------------------------------------------------------

# Основной access_token (получен 2026-06-08)
ACCESS_TOKEN = "y0__wgBEM-PhesCGM73QSCayNHIFx4hTUWtppv9M4CUxW2X8SfIBsnW"

# Refresh token для обновления access_token
REFRESH_TOKEN = "2:AAA:AAAAAC1hR88:1:80emErMeCFuz9-Kh:cDUnouTpklblKqbOwXity3Jgt56f-NuBAmArOfVXsUdI3YnLjwIvbBJxQWq7XmWyl3oU4KXxcQ:I_oeWLExoxevtGvP4O8Szw"

# OAuth данные приложения Dune Dashboard
CLIENT_ID = "be5209733c5f4419b319a0f49d3eae9d"
CLIENT_SECRET = "810ceb8110124b849cfd59448b1cfe75"


# --- OAuth ---------------------------------------------------------------

def refresh_access_token():
    """Обновляет access_token используя refresh_token."""
    data = urllib.parse.urlencode({
        "grant_type": "refresh_token",
        "refresh_token": REFRESH_TOKEN,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }).encode("utf-8")
    
    req = urllib.request.Request(
        "https://oauth.yandex.ru/token",
        data=data,
        method="POST"
    )
    
    with urllib.request.urlopen(req, timeout=30) as resp:
        result = json.loads(resp.read().decode("utf-8"))
    
    return result.get("access_token")


# --- Яндекс.Директ API --------------------------------------------------

def direct_api(method, params=None):
    """Вызов API Яндекс.Директ."""
    url = "https://api.direct.yandex.com/json/v5/reports"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Accept-Language": "ru",
        "Content-Type": "application/json; charset=utf-8"
    }
    
    body = {
        "method": method,
        "params": params or {}
    }
    
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))


def get_campaigns_stats(date_from, date_to):
    """
    Получает статистику кампаний за период.
    
    Args:
        date_from: Начало периода (YYYY-MM-DD)
        date_to: Конец периода (YYYY-MM-DD)
    
    Returns:
        Список кампаний с показами, кликами, расходом
    """
    # Фильтр по 4 аккаунтам
    logins = ["e-20010227", "e-17228851", "dune-group", "porg-3uieikjn"]
    
    body = {
        "SelectionCriteria": {
            "DateFrom": date_from,
            "DateTo": date_to,
            "Filter": [
                {"Field": "Impressions", "Operator": "GREATER_THAN", "Values": ["0"]}
            ]
        },
        "FieldNames": [
            "Date",
            "CampaignId",
            "CampaignName",
            "Login",
            "Impressions",
            "Clicks",
            "Cost"
        ],
        "PageSize": 10000
    }
    
    result = direct_api("get", body)
    return result.get("result", {}).get("data", [])


# --- Яндекс.Метрика API -------------------------------------------------

def metrica_api(method, params=None):
    """Вызов API Яндекс.Метрика."""
    url = f"https://api-metrika.yandex.net/{method}"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}"
    }
    
    if params:
        url += "?" + urllib.parse.urlencode(params)
    
    req = urllib.request.Request(url, headers=headers)
    
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def get_visits(date_from, date_to):
    """
    Получает визиты за период.
    
    Args:
        date_from: Начало периода (YYYY-MM-DD)
        date_to: Конец периода (YYYY-MM-DD)
    
    Returns:
        Общее количество визитов и разбивка по источникам
    """
    # ID счётчика Метрики для dune-group.ru
    COUNTER_ID = "90747520"
    
    params = {
        "id": COUNTER_ID,
        "date1": date_from,
        "date2": date_to,
        "metrics": "ym:s:visits,ym:s:users",
        "dimensions": "ym:s:SourceEngine",
        "limit": 10000
    }
    
    result = metrica_api("stat/v1/data", params)
    return result


# --- CLI -----------------------------------------------------------------

def main():
    if len(sys.argv) < 3:
        print("Использование: python yandex.py YYYY-MM-DD YYYY-MM-DD")
        print("Пример: python yandex.py 2026-06-01 2026-06-07")
        return 1
    
    date_from, date_to = sys.argv[1], sys.argv[2]
    
    print(f"\n📊 Яндекс Метрика: {date_from} — {date_to}")
    print("=" * 60)
    
    # Получаем визиты из Метрики
    result = get_visits(date_from, date_to)
    
    total = result.get("totals", [0])[0]
    data = result.get("data", [])
    
    print(f"\nВсего визитов: {int(total)}")
    print(f"\nИсточники трафика:")
    print(f"{'Источник':<40} {'Визиты':>10}")
    print("-" * 52)
    
    for row in data:
        dims = row.get("dimensions", [{}])
        name = dims[0].get("name", "Unknown") if dims else "Unknown"
        visits = int(row.get("metrics", [0])[0])
        print(f"{name:<40} {visits:>10}")
    
    # SEO визиты (internal сайты)
    seo_visits = 0
    for row in data:
        dims = row.get("dimensions", [{}])
        name = dims[0].get("name", "") if dims else ""
        if "dune-group.ru" in name and "direct" not in name.lower():
            seo_visits += int(row.get("metrics", [0])[0])
    
    print(f"\n🔍 SEO визиты: {seo_visits}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())