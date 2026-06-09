"""
Яндекс.Метрика SEO Analytics для Dashboard.

Модуль для получения SEO-метрик из Яндекс.Метрики:
- Органические визиты по неделям
- Топ посадочных страниц
- Поисковые запросы

Счётчик: 90747520 (dune-group.ru)
"""

import json
import sys
import urllib.request
import urllib.parse
from datetime import datetime

# Яндекс OAuth токен
ACCESS_TOKEN = "y0__wgBEM-PhesCGM73QSCayNHIFx4hTUWtppv9M4CUxW2X8SfIBsnW"
COUNTER_ID = "90747520"


def metrika_api(method, params=None):
    """Вызов API Яндекс.Метрика."""
    url = f"https://api-metrika.yandex.net/{method}"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "User-Agent": "Mozilla/5.0"
    }
    
    if params:
        url += "?" + urllib.parse.urlencode(params, doseq=True)
    
    req = urllib.request.Request(url, headers=headers)
    
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"❌ Ошибка API Метрики: {e}")
        return {"error": str(e)}


def get_seo_visits(date_from, date_to):
    """
    Получает органические визиты (SEO) за период.
    
    Returns:
        {"visits": 248, "users": 180, "bounce_rate": 45.2, ...}
    """
    params = {
        "id": COUNTER_ID,
        "date1": date_from,
        "date2": date_to,
        "metrics": "ym:s:visits,ym:s:users,ym:s:bounceRate,ym:s:pageDepth,ym:s:avgVisitDurationSeconds",
        "filters": "ym:s:trafficSource=='organic'",  # Только органический трафик
        "limit": 1
    }
    
    result = metrika_api("stat/v1/data", params)
    
    if "error" in result:
        return {"visits": 0, "users": 0, "bounce_rate": 0, "page_depth": 0, "avg_duration": 0}
    
    totals = result.get("totals", [0, 0, 0, 0, 0])
    
    return {
        "visits": int(totals[0]) if len(totals) > 0 else 0,
        "users": int(totals[1]) if len(totals) > 1 else 0,
        "bounce_rate": round(float(totals[2]), 2) if len(totals) > 2 else 0,
        "page_depth": round(float(totals[3]), 2) if len(totals) > 3 else 0,
        "avg_duration": int(totals[4]) if len(totals) > 4 else 0
    }


def get_top_landing_pages(date_from, date_to, limit=10):
    """
    Получает топ посадочных страниц из органического поиска.
    
    Returns:
        [{"url": "/services/remont", "visits": 45, "bounce_rate": 35.2, ...}, ...]
    """
    params = {
        "id": COUNTER_ID,
        "date1": date_from,
        "date2": date_to,
        "metrics": "ym:s:visits,ym:s:users,ym:s:bounceRate,ym:s:pageDepth,ym:s:avgVisitDurationSeconds",
        "dimensions": "ym:s:startURL",
        "filters": "ym:s:trafficSource=='organic'",
        "sort": "-ym:s:visits",
        "limit": limit
    }
    
    result = metrika_api("stat/v1/data", params)
    
    if "error" in result:
        return []
    
    pages = []
    for row in result.get("data", []):
        dims = row.get("dimensions", [{}])
        metrics = row.get("metrics", [0, 0, 0, 0, 0])
        
        url = dims[0].get("name", "") if dims else ""
        
        pages.append({
            "url": url,
            "visits": int(metrics[0]) if len(metrics) > 0 else 0,
            "users": int(metrics[1]) if len(metrics) > 1 else 0,
            "bounce_rate": round(float(metrics[2]), 2) if len(metrics) > 2 else 0,
            "page_depth": round(float(metrics[3]), 2) if len(metrics) > 3 else 0,
            "avg_duration": int(metrics[4]) if len(metrics) > 4 else 0
        })
    
    return pages


def get_search_queries(date_from, date_to, limit=10):
    """
    Получает топ поисковых запросов.
    
    Returns:
        [{"query": "ремонт квартир москва", "visits": 25, "users": 20, ...}, ...]
    """
    params = {
        "id": COUNTER_ID,
        "date1": date_from,
        "date2": date_to,
        "metrics": "ym:s:visits,ym:s:users,ym:s:bounceRate",
        "dimensions": "ym:s:searchPhrase",
        "filters": "ym:s:trafficSource=='organic'",
        "sort": "-ym:s:visits",
        "limit": limit
    }
    
    result = metrika_api("stat/v1/data", params)
    
    if "error" in result:
        return []
    
    queries = []
    for row in result.get("data", []):
        dims = row.get("dimensions", [{}])
        metrics = row.get("metrics", [0, 0, 0])
        
        query = dims[0].get("name", "") if dims else ""
        
        # Пропускаем пустые запросы
        if not query or query == "(not set)":
            continue
        
        queries.append({
            "query": query,
            "visits": int(metrics[0]) if len(metrics) > 0 else 0,
            "users": int(metrics[1]) if len(metrics) > 1 else 0,
            "bounce_rate": round(float(metrics[2]), 2) if len(metrics) > 2 else 0
        })
    
    return queries


def export_seo_data(date_from, date_to, output_file):
    """
    Экспортирует все SEO-данные в JSON файл.
    """
    print(f"\n📊 Сбор SEO данных: {date_from} — {date_to}")
    print("=" * 60)
    
    # 1. Общая статистика SEO
    print("🔍 Получение статистики визитов...")
    seo_stats = get_seo_visits(date_from, date_to)
    
    # 2. Топ посадочных страниц
    print("📄 Получение топ посадочных страниц...")
    top_pages = get_top_landing_pages(date_from, date_to, limit=10)
    
    # 3. Поисковые запросы
    print("🔎 Получение поисковых запросов...")
    search_queries = get_search_queries(date_from, date_to, limit=10)
    
    # Формируем итоговый JSON
    output_data = {
        "period": {"from": date_from, "to": date_to},
        "updated": datetime.now().isoformat(),
        "counter_id": COUNTER_ID,
        "seo_stats": seo_stats,
        "top_landing_pages": top_pages,
        "search_queries": search_queries
    }
    
    # Сохраняем в файл
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Данные сохранены в {output_file}")
    print(f"\n📈 Статистика:")
    print(f"   SEO визиты: {seo_stats['visits']}")
    print(f"   Уникальные посетители: {seo_stats['users']}")
    print(f"   Показатель отказов: {seo_stats['bounce_rate']}%")
    print(f"   Топ страниц: {len(top_pages)}")
    print(f"   Поисковых запросов: {len(search_queries)}")


def main():
    """CLI для тестирования и экспорта."""
    if len(sys.argv) < 2:
        print("Использование:")
        print("  python metrika_seo.py test YYYY-MM-DD YYYY-MM-DD")
        print("  python metrika_seo.py export YYYY-MM-DD YYYY-MM-DD output.json")
        print("\nПример:")
        print("  python metrika_seo.py test 2026-06-01 2026-06-07")
        print("  python metrika_seo.py export 2026-05-04 2026-06-07 seo_data.json")
        return 1
    
    command = sys.argv[1]
    
    if command == "test" and len(sys.argv) == 4:
        date_from, date_to = sys.argv[2], sys.argv[3]
        
        print(f"\n📊 Тест Яндекс.Метрика SEO: {date_from} — {date_to}")
        print("=" * 60)
        
        # SEO статистика
        stats = get_seo_visits(date_from, date_to)
        print(f"\n🔍 SEO Статистика:")
        print(f"   Визиты: {stats['visits']}")
        print(f"   Пользователи: {stats['users']}")
        print(f"   Показатель отказов: {stats['bounce_rate']}%")
        print(f"   Глубина просмотра: {stats['page_depth']} страниц")
        print(f"   Среднее время: {stats['avg_duration']} сек")
        
        # Топ страниц
        pages = get_top_landing_pages(date_from, date_to, limit=5)
        print(f"\n📄 Топ-5 посадочных страниц:")
        print(f"{'URL':<50} {'Визиты':>10} {'Отказы':>10}")
        print("-" * 72)
        for page in pages:
            url = page['url'][:47] + "..." if len(page['url']) > 50 else page['url']
            print(f"{url:<50} {page['visits']:>10} {page['bounce_rate']:>9.1f}%")
        
        # Поисковые запросы
        queries = get_search_queries(date_from, date_to, limit=5)
        print(f"\n🔎 Топ-5 поисковых запросов:")
        print(f"{'Запрос':<50} {'Визиты':>10}")
        print("-" * 62)
        for query in queries:
            q = query['query'][:47] + "..." if len(query['query']) > 50 else query['query']
            print(f"{q:<50} {query['visits']:>10}")
    
    elif command == "export" and len(sys.argv) == 5:
        date_from, date_to, output_file = sys.argv[2], sys.argv[3], sys.argv[4]
        export_seo_data(date_from, date_to, output_file)
    
    else:
        print("❌ Неверная команда")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
