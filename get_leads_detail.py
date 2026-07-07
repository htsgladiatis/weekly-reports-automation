"""
Получение детальных данных лидов из Bitrix24 для анализа
"""
import json
import urllib.request
from datetime import datetime

WEBHOOK_URL = "https://dunegroup.bitrix24.ru/rest/396/vk0fdm6r1qrtt81w/"

def fetch_leads_raw(date_from: str, date_to: str):
    """Получает сырые данные лидов"""
    date_from_iso = f"{date_from}T00:00:00"
    date_to_iso = f"{date_to}T23:59:59"
    
    # Получаем все поля
    url = f"{WEBHOOK_URL}crm.lead.list"
    url += f"?filter[>=DATE_CREATE]={date_from_iso}"
    url += f"&filter[<=DATE_CREATE]={date_to_iso}"
    url += "&select[]=*"
    
    req = urllib.request.Request(url, method="GET")
    req.add_header("User-Agent", "Mozilla/5.0")
    
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            return result.get("result", [])
    except Exception as e:
        print(f"Ошибка: {e}")
        return []

def analyze_leads(leads):
    """Анализирует статусы и источники лидов"""
    print(f"\nВсего лидов: {len(leads)}\n")
    
    # Группируем по статусам
    by_status = {}
    for lead in leads:
        status = lead.get("STATUS_ID", "UNKNOWN")
        if status not in by_status:
            by_status[status] = []
        by_status[status].append(lead)
    
    print("=" * 80)
    print("РАСПРЕДЕЛЕНИЕ ПО СТАТУСАМ:")
    print("=" * 80)
    
    for status, leads_list in sorted(by_status.items()):
        print(f"\nСтатус: {status} ({len(leads_list)} лидов)")
        
        # Показываем примеры
        for lead in leads_list[:3]:
            title = lead.get("TITLE", "")[:60]
            source = lead.get("SOURCE_ID", "")
            utm_source = lead.get("UTM_SOURCE", "")
            utm_campaign = lead.get("UTM_CAMPAIGN", "")
            print(f"  - {title}")
            print(f"    SOURCE_ID: {source}, UTM_SOURCE: {utm_source}, UTM_CAMPAIGN: {utm_campaign}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 3:
        print("Использование: python get_leads_detail.py YYYY-MM-DD YYYY-MM-DD")
        sys.exit(1)
    
    date_from, date_to = sys.argv[1], sys.argv[2]
    
    print(f"Получение лидов: {date_from} — {date_to}")
    leads = fetch_leads_raw(date_from, date_to)
    analyze_leads(leads)
    
    # Сохраняем в файл
    output_file = f"leads_raw_{date_from.replace('-', '')}_{date_to.replace('-', '')}.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(leads, f, ensure_ascii=False, indent=2)
    print(f"\n✅ Сохранено в {output_file}")
