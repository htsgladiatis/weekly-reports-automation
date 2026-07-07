from bitrix_api import fetch_leads, classify_lead

leads = fetch_leads('2026-06-15', '2026-06-21')
print(f'Всего лидов из API: {len(leads)}\n')

# Group by status and show details
by_status = {}
for lead in leads:
    status = lead.get("STATUS_ID", "unknown")
    if status not in by_status:
        by_status[status] = []
    by_status[status].append(lead)

print('Детализация по статусам:\n')
for status, status_leads in sorted(by_status.items()):
    print(f'Статус "{status}" ({len(status_leads)} лидов):')
    
    # Count by source
    by_source = {}
    for lead in status_leads:
        source = lead.get("SOURCE_ID", "") or ""
        utm_source = (lead.get("UTM_SOURCE") or "").lower()
        additional = (lead.get("UTM_CAMPAIGN") or lead.get("UTM_MEDIUM") or "")
        
        # Classify channel
        if "marquiz" in utm_source or "яндекс" in source.lower() or "yandex" in source.lower():
            channel = "Директ"
        elif "seo" in source.lower() or "органи" in source.lower() or "search" in source.lower() or "запросы" in source.lower():
            channel = "SEO"
        else:
            channel = "Другие/Звонки"
        
        if channel not in by_source:
            by_source[channel] = 0
        by_source[channel] += 1
    
    for channel, count in sorted(by_source.items()):
        print(f'  {channel}: {count}')
    
    # Show 2 examples
    print(f'  Примеры:')
    for lead in status_leads[:2]:
        title = lead.get("TITLE", "")[:50]
        source = lead.get("SOURCE_ID", "")
        print(f'    - {title} | {source}')
    print()

# Summary for report
print('=' * 60)
print('ИТОГО ДЛЯ ОТЧЕТА:')
print('=' * 60)

# Count valid leads (exclude JUNK)
total_valid = 0
total_converted = 0
by_channel = {'direct': 0, 'seo': 0, 'other': 0}
by_channel_converted = {'direct': 0, 'seo': 0, 'other': 0}

for lead in leads:
    status = lead.get("STATUS_ID", "")
    
    # Skip only JUNK
    if status == "JUNK":
        continue
    
    total_valid += 1
    is_converted = status == "CONVERTED"
    if is_converted:
        total_converted += 1
    
    # Classify channel
    source = lead.get("SOURCE_ID", "") or ""
    utm_source = (lead.get("UTM_SOURCE") or "").lower()
    
    if "marquiz" in utm_source or "яндекс" in source.lower():
        channel = 'direct'
    elif "seo" in source.lower() or "запросы" in source.lower():
        channel = 'seo'
    else:
        channel = 'other'
    
    by_channel[channel] += 1
    if is_converted:
        by_channel_converted[channel] += 1

print(f'\nВсего валидных лидов (без JUNK): {total_valid}')
print(f'Из них конвертированных (CONVERTED): {total_converted}')
print()
print(f'По каналам:')
print(f'  Директ: {by_channel["direct"]} лидов ({by_channel_converted["direct"]} конвертированных)')
print(f'  SEO: {by_channel["seo"]} лидов ({by_channel_converted["seo"]} конвертированных)')
print(f'  Другие/Звонки: {by_channel["other"]} лидов ({by_channel_converted["other"]} конвертированных)')
