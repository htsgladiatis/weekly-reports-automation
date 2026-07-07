from bitrix_api import fetch_leads, classify_lead

leads = fetch_leads('2026-06-15', '2026-06-21')
print(f'Всего лидов из API: {len(leads)}\n')

# Show all unique statuses
statuses = set()
for lead in leads:
    statuses.add(lead.get("STATUS_ID", ""))
print(f'Уникальные статусы: {sorted(statuses)}\n')

# Count by status with titles
print('Лиды по статусам:')
status_titles = {}
for lead in leads:
    status = lead.get("STATUS_ID", "")
    title = lead.get("TITLE", "")[:50]
    if status not in status_titles:
        status_titles[status] = []
    status_titles[status].append(title)

for status, titles in sorted(status_titles.items()):
    print(f'\n{status} ({len(titles)} лидов):')
    for t in titles[:3]:
        print(f'  - {t}')
