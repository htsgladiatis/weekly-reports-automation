import csv
from datetime import datetime

with open('001.csv', 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f, delimiter=';')
    leads = list(reader)

# Get date range
dates = []
for lead in leads:
    date_str = lead.get('Дата создания', '').split(' ')[0]
    try:
        date = datetime.strptime(date_str, '%d.%m.%Y')
        dates.append(date)
    except:
        pass

if dates:
    min_date = min(dates)
    max_date = max(dates)
    print(f'Период данных: {min_date.strftime("%d.%m.%Y")} - {max_date.strftime("%d.%m.%Y")}')
    print(f'Всего лидов с датами: {len(dates)}')
    print()

# Analyze by week
print('НЕДЕЛЯ 8 (22.06-29.06):')
week8_leads = [l for l, d in zip(leads, dates) if datetime(2026, 6, 22) <= d <= datetime(2026, 6, 29)]
print(f'Всего лидов: {len(week8_leads)}')

target = [l for l in week8_leads if l.get('Стадия','').strip() == 'Целевой лид']
print(f'Целевых лидов: {len(target)}')

direct = [l for l in target if 'Яндекс.Директ' in l.get('Источник','')]
direct_marquiz = [l for l in direct if 'marquiz' in l.get('Дополнительно об источнике','').lower()]
seo = [l for l in target if 'СЕО' in l.get('Источник','')]
other_sources = len(target) - len(direct) - len(seo)

print(f'  Директ: {len(direct)} (marquiz: {len(direct_marquiz)})')
print(f'  SEO: {len(seo)}')
print(f'  Другие: {other_sources}')
print()

# Show target leads
print('Целевые лиды:')
for l in target:
    name = l.get('Название лида', '')[:50]
    source = l.get('Источник', '')
    extra = l.get('Дополнительно об источнике', '')[:20]
    print(f'  - {name} | {source} | {extra}')
