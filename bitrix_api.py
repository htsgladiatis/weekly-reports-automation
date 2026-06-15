"""
Bitrix24 CRM API Integration для Weekly Reports Dashboard.

Модуль для получения лидов из Битрикс24 через REST API (входящий вебхук).
Используется для динамического обновления данных дашборда.

Вебхук: https://dunegroup.bitrix24.ru/rest/396/vk0fdm6r1qrtt81w/
"""

import json
import urllib.request
import urllib.parse
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Dict, List, Any

# Битрикс24 вебхук URL
WEBHOOK_URL = "https://dunegroup.bitrix24.ru/rest/396/vk0fdm6r1qrtt81w/"


def bitrix_call(method: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Вызов API метода Битрикс24 через вебхук.
    
    Args:
        method: Название метода (напр. "crm.lead.list")
        params: Параметры запроса
    
    Returns:
        Результат API запроса
    """
    url = f"{WEBHOOK_URL}{method}"
    
    if params:
        # Кодируем параметры для GET-запроса
        query_params = []
        for key, value in params.items():
            if isinstance(value, list):
                for v in value:
                    query_params.append(f"{key}={urllib.parse.quote(str(v))}")
            else:
                query_params.append(f"{key}={urllib.parse.quote(str(value))}")
        url += "?" + "&".join(query_params)
    
    req = urllib.request.Request(url, method="GET")
    req.add_header("User-Agent", "Mozilla/5.0")
    
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            return result
    except urllib.error.HTTPError as e:
        print(f"❌ HTTP Error {e.code}: {e.reason}")
        return {"error": f"HTTP {e.code}"}
    except urllib.error.URLError as e:
        print(f"❌ URL Error: {e.reason}")
        return {"error": str(e.reason)}
    except Exception as e:
        print(f"❌ Ошибка API Битрикс24: {e}")
        return {"error": str(e)}


def fetch_leads(date_from: str, date_to: str) -> List[Dict[str, Any]]:
    """
    Получает все лиды за период из Битрикс24.
    
    Args:
        date_from: Начало периода (YYYY-MM-DD)
        date_to: Конец периода (YYYY-MM-DD)
    
    Returns:
        Список лидов с полями: ID, TITLE, STATUS_ID, SOURCE_ID, DATE_CREATE, UTM_*
    """
    # Преобразуем даты в ISO формат для Битрикс24
    date_from_iso = f"{date_from}T00:00:00"
    date_to_iso = f"{date_to}T23:59:59"
    
    params = {
        "filter[>=DATE_CREATE]": date_from_iso,
        "filter[<=DATE_CREATE]": date_to_iso,
        "select[]": [
            "ID",
            "TITLE",
            "STATUS_ID",
            "SOURCE_ID",
            "DATE_CREATE",
            "UTM_SOURCE",
            "UTM_MEDIUM",
            "UTM_CAMPAIGN",
            "UTM_CONTENT",
            "UTM_TERM"
        ]
    }
    
    result = bitrix_call("crm.lead.list", params)
    
    if "error" in result:
        return []
    
    return result.get("result", [])


def classify_lead(lead: Dict[str, Any]) -> Dict[str, str]:
    """
    Классифицирует лид по источнику и типу.
    
    Args:
        lead: Данные лида из Битрикс24
    
    Returns:
        {"account": "e-20010227", "is_target": True/False, "channel": "direct"}
    """
    utm_source = lead.get("UTM_SOURCE", "").lower()
    utm_campaign = lead.get("UTM_CAMPAIGN", "").lower()
    source_id = lead.get("SOURCE_ID", "")
    status_id = lead.get("STATUS_ID", "")
    
    # Определяем аккаунт по utm_campaign
    account = "unknown"
    if "cabinet-e-20010227" in utm_campaign or "marquiz" in utm_source:
        account = "e-20010227"
    elif "cabinet-e-17228851" in utm_campaign:
        account = "e-17228851"
    elif "cabinet-dune-group" in utm_campaign:
        account = "dune-group"
    elif "cabinet-porg-3uieikjn" in utm_campaign:
        account = "porg-3uieikjn"
    
    # Определяем канал
    channel = "direct"
    if "yandex" in utm_source or "direct" in utm_source:
        channel = "direct"
    elif "organic" in utm_source or source_id == "SEO":
        channel = "seo"
    elif "referral" in utm_source or source_id == "CALL":
        channel = "recommendations"
    
    # Целевой лид = статус "S" (Целевой лид)
    is_target = status_id == "S"
    
    # Исключаем браковые стадии
    trash_statuses = ["F", "JUNK", "SPAM"]  # F = брак
    is_valid = status_id not in trash_statuses
    
    return {
        "account": account,
        "is_target": is_target,
        "channel": channel,
        "is_valid": is_valid
    }


def get_lead_stats(date_from: str, date_to: str) -> Dict[str, Any]:
    """
    Получает статистику лидов за период.
    
    Args:
        date_from: Начало периода (YYYY-MM-DD)
        date_to: Конец периода (YYYY-MM-DD)
    
    Returns:
        Статистика по аккаунтам и каналам
    """
    leads = fetch_leads(date_from, date_to)
    
    # Инициализация счетчиков
    stats = {
        "accounts": {
            "e-20010227": {"leads": 0, "target": 0},
            "e-17228851": {"leads": 0, "target": 0},
            "dune-group": {"leads": 0, "target": 0},
            "porg-3uieikjn": {"leads": 0, "target": 0}
        },
        "channels": {
            "direct": {"leads": 0, "target": 0},
            "seo": {"leads": 0, "target": 0},
            "recommendations": {"leads": 0, "target": 0}
        },
        "total": {"leads": 0, "target": 0}
    }
    
    # Подсчет лидов
    for lead in leads:
        classification = classify_lead(lead)
        
        if not classification["is_valid"]:
            continue  # Пропускаем бракованные лиды
        
        account = classification["account"]
        channel = classification["channel"]
        is_target = classification["is_target"]
        
        # Статистика по аккаунтам
        if account in stats["accounts"]:
            stats["accounts"][account]["leads"] += 1
            if is_target:
                stats["accounts"][account]["target"] += 1
        
        # Статистика по каналам
        if channel in stats["channels"]:
            stats["channels"][channel]["leads"] += 1
            if is_target:
                stats["channels"][channel]["target"] += 1
        
        # Общая статистика
        stats["total"]["leads"] += 1
        if is_target:
            stats["total"]["target"] += 1
    
    return stats


class BitrixAPIHandler(BaseHTTPRequestHandler):
    """HTTP handler для API endpoint'а получения лидов."""
    
    def do_GET(self):
        """Обработка GET запросов."""
        # Разрешаем CORS
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        
        # Парсим URL параметры
        if "?" in self.path:
            query = urllib.parse.parse_qs(self.path.split("?")[1])
            date_from = query.get("date_from", [None])[0]
            date_to = query.get("date_to", [None])[0]
            
            if date_from and date_to:
                # Получаем статистику
                stats = get_lead_stats(date_from, date_to)
                response = {
                    "success": True,
                    "data": stats,
                    "period": {"from": date_from, "to": date_to}
                }
            else:
                response = {
                    "success": False,
                    "error": "Требуются параметры date_from и date_to"
                }
        else:
            response = {
                "success": False,
                "error": "Требуются параметры date_from и date_to"
            }
        
        self.wfile.write(json.dumps(response, ensure_ascii=False).encode("utf-8"))
    
    def log_message(self, format, *args):
        """Подавляем логи запросов."""
        pass


def start_server(port: int = 8000):
    """
    Запускает HTTP сервер для API endpoint'а.
    
    Args:
        port: Порт сервера (по умолчанию 8000)
    """
    server = HTTPServer(("localhost", port), BitrixAPIHandler)
    print(f"🚀 Bitrix API Server запущен на http://localhost:{port}")
    print(f"   Пример: http://localhost:{port}/?date_from=2026-06-01&date_to=2026-06-07")
    server.serve_forever()


def main():
    """CLI для тестирования и запуска сервера."""
    import sys
    
    if len(sys.argv) < 2:
        print("Использование:")
        print("  python bitrix_api.py server          # Запустить API сервер")
        print("  python bitrix_api.py test YYYY-MM-DD YYYY-MM-DD  # Тест")
        print("  python bitrix_api.py export YYYY-MM-DD YYYY-MM-DD output.json  # Экспорт в JSON")
        return 1
    
    command = sys.argv[1]
    
    if command == "server":
        start_server()
    elif command == "test" and len(sys.argv) == 4:
        date_from, date_to = sys.argv[2], sys.argv[3]
        print(f"\n📊 Тест Bitrix24 API: {date_from} — {date_to}")
        print("=" * 60)
        
        stats = get_lead_stats(date_from, date_to)
        
        print(f"\n{'Аккаунт':<25} {'Лиды':>10} {'Ц. Лиды':>10}")
        print("-" * 60)
        for account, data in stats["accounts"].items():
            print(f"{account:<25} {data['leads']:>10} {data['target']:>10}")
        print("-" * 60)
        print(f"{'ИТОГО':<25} {stats['total']['leads']:>10} {stats['total']['target']:>10}")
        
        print(f"\n{'Канал':<25} {'Лиды':>10} {'Ц. Лиды':>10}")
        print("-" * 60)
        for channel, data in stats["channels"].items():
            print(f"{channel:<25} {data['leads']:>10} {data['target']:>10}")
    elif command == "export" and len(sys.argv) == 5:
        date_from, date_to, output_file = sys.argv[2], sys.argv[3], sys.argv[4]
        print(f"\n📤 Экспорт данных Bitrix24: {date_from} — {date_to}")
        
        stats = get_lead_stats(date_from, date_to)
        
        # Сохраняем в JSON
        output_data = {
            "period": {"from": date_from, "to": date_to},
            "updated": datetime.now().isoformat(),
            "data": stats
        }
        
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Данные сохранены в {output_file}")
        print(f"   Лидов: {stats['total']['leads']}, Целевых: {stats['total']['target']}")
    else:
        print("❌ Неверная команда")
        return 1
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
