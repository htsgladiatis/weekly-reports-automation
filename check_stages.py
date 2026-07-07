"""
Проверка всех стадий лидов за период и их семантики.
"""
import sys
sys.path.insert(0, ".")
from bitrix import call_list, _stage_semantics, _status_names, fetch_leads, _is_direct, _status_names as get_source_names

DATE_FROM = "2026-06-01"
DATE_TO = "2026-06-07"

print(f"=== Проверка стадий лидов {DATE_FROM} — {DATE_TO} ===\n")

# Получить все лиды
leads = fetch_leads(DATE_FROM, DATE_TO)
print(f"Всего лидов за период: {len(leads)}\n")

# Получить названия стадий и семантику
status_names = _status_names("STATUS")
source_names = _status_names("SOURCE")
semantics = _stage_semantics()

print(f"{'ID':<8} {'Дата':<12} {'Стадия':<25} {'Семантика':<12} {'Источник':<20} {'UTM Campaign':<30} {'Имя'}")
print("-" * 150)

direct_count = 0
target_count = 0
all_semantics = set()

for lead in leads:
    lid = lead.get("ID", "")
    date = (lead.get("DATE_CREATE") or "")[:10]
    status_id = lead.get("STATUS_ID")
    stage_name = status_names.get(status_id, status_id or "—")
    sem = semantics.get(status_id) or "None"
    all_semantics.add(sem)
    
    source_id = lead.get("SOURCE_ID")
    source_name = source_names.get(source_id, "—")
    utm_campaign = lead.get("UTM_CAMPAIGN") or "—"
    title = lead.get("TITLE", "")
    
    is_dir = _is_direct(lead, source_names)
    if is_dir:
        direct_count += 1
        marker = ""
        if sem == "S":
            marker = "★ "
            target_count += 1
        elif sem == "F":
            marker = "✗ "
        else:
            marker = "  "
        
        print(f"{marker}{lid:<8} {date:<12} {stage_name:<25} {sem:<12} {source_name:<20} {utm_campaign:<30} {title[:40]}")

print("\n" + "=" * 150)
print(f"Директовых лидов (не брак): {direct_count}")
print(f"Целевых лидов (семантика S): {target_count}")
print(f"Все найденные семантики: {all_semantics}")
