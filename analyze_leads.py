import csv
from datetime import datetime

with open('LEAD_20260602_62fb5d42_6a1ecef6ed0f7.csv', 'r', encoding='utf-8-sig') as f:
    reader = csv.reader(f, delimiter=';')
    rows = list(reader)

excluded_stages = {'Дубль', 'Подрядчики реклама', 'Ошиблись номером', 'Вакансии'}

weeks = {
    'w1': {'start': datetime(2026, 5, 4), 'end': datetime(2026, 5, 10, 23, 59, 59), 'label': '04.05-10.05'},
    'w2': {'start': datetime(2026, 5, 11), 'end': datetime(2026, 5, 17, 23, 59, 59), 'label': '11.05-17.05'},
    'w3': {'start': datetime(2026, 5, 18), 'end': datetime(2026, 5, 24, 23, 59, 59), 'label': '18.05-24.05'},
    'w4': {'start': datetime(2026, 5, 25), 'end': datetime(2026, 5, 31, 23, 59, 59), 'label': '25.05-31.05'},
}

results = {k: {'leads': 0, 'target': 0, 'accounts': {}} for k in weeks}

for row in rows[1:]:
    stage = row[1].strip()
    date_str = row[8].strip().split()[0]
    source = row[9].strip()
    add_source = row[41].strip().lower()
    utm_campaign = row[66].strip().lower()
    
    if stage in excluded_stages:
        continue
    
    dt = datetime.strptime(date_str, '%d.%m.%Y')
    
    # Determine account
    account = 'unknown'
    if 'marquiz' in add_source:
        account = 'e-20010227'
    elif 'cabinet-17228851' in utm_campaign:
        account = 'e-17228851'
    elif 'cabinet-20010227' in utm_campaign:
        account = 'e-20010227'
    elif source == 'Яндекс.Директ':
        account = 'e-20010227'
    elif 'звонок' in add_source.lower() or source == 'Звонок (входящий)':
        account = 'recommendations'
    elif 'риелтор' in source.lower():
        account = 'recommendations'
    elif source == 'По рекомендации':
        account = 'recommendations'
    elif source == 'Запросы по СЕО':
        account = 'seo'
    
    is_target = (stage == 'Целевой лид')
    
    for wk, wv in weeks.items():
        if wv['start'] <= dt <= wv['end']:
            results[wk]['leads'] += 1
            if is_target:
                results[wk]['target'] += 1
            if account not in results[wk]['accounts']:
                results[wk]['accounts'][account] = {'leads': 0, 'target': 0}
            results[wk]['accounts'][account]['leads'] += 1
            if is_target:
                results[wk]['accounts'][account]['target'] += 1
            break
    
    print(f"Date: {date_str}, Stage: {stage:15}, Source: {source:25}, Account: {account:20}, Target: {is_target}")

print()
for wk, wv in weeks.items():
    print(f"{wv['label']}: leads={results[wk]['leads']}, target={results[wk]['target']}, accounts={results[wk]['accounts']}")
