"""
Анализ CSV файлов с лидами для актуализации дашборда
"""
import csv
from collections import defaultdict

def analyze_csv_leads(csv_path):
    """Анализирует CSV файл с лидами"""
    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f, delimiter=';')
        leads = list(reader)
    
    total = len(leads)
    target = len([l for l in leads if l.get('Стадия', '').strip() == 'Целевой лид'])
    
    # Классификация по источникам
    direct = 0
    direct_target = 0
    seo = 0
    seo_target = 0
    other = 0
    other_target = 0
    
    e_20010227 = 0
    e_20010227_target = 0
    
    for lead in leads:
        source = lead.get('Источник', '').strip()
        extra = lead.get('Дополнительно об источнике', '').strip()
        is_target = lead.get('Стадия', '').strip() == 'Целевой лид'
        
        if 'Яндекс.Директ' in source:
            direct += 1
            if is_target:
                direct_target += 1
            
            # marquiz = e-20010227
            if 'marquiz' in extra.lower():
                e_20010227 += 1
                if is_target:
                    e_20010227_target += 1
        elif 'SEO' in source or 'Запросы по СЕО' in source:
            seo += 1
            if is_target:
                seo_target += 1
        else:
            other += 1
            if is_target:
                other_target += 1
    
    return {
        'total': total,
        'target': target,
        'direct': direct,
        'direct_target': direct_target,
        'seo': seo,
        'seo_target': seo_target,
        'other': other,
        'other_target': other_target,
        'e_20010227': e_20010227,
        'e_20010227_target': e_20010227_target,
        'leads': leads
    }

if __name__ == "__main__":
    periods = [
        ('01.06-07.06', 'new/1-7.csv'),
        ('08.06-14.06', None),  # Нет CSV
        ('15.06-21.06', 'new/15-21.csv')
    ]
    
    print("=" * 80)
    print("АНАЛИЗ ЛИДОВ ПО НЕДЕЛЯМ (из CSV файлов)")
    print("=" * 80)
    
    for period, csv_path in periods:
        print(f"\n📅 {period}")
        print("-" * 80)
        
        if csv_path is None:
            print("  ⚠️  CSV файл отсутствует")
            continue
        
        try:
            stats = analyze_csv_leads(csv_path)
            
            print(f"  Всего лидов: {stats['total']}")
            print(f"  Целевых лидов: {stats['target']}")
            print(f"\n  По каналам:")
            print(f"    Яндекс.Директ: {stats['direct']} ({stats['direct_target']} целевых)")
            print(f"      - e-20010227 (marquiz): {stats['e_20010227']} ({stats['e_20010227_target']} целевых)")
            print(f"    SEO: {stats['seo']} ({stats['seo_target']} целевых)")
            print(f"    Другие/Звонки: {stats['other']} ({stats['other_target']} целевых)")
            
        except Exception as e:
            print(f"  ❌ Ошибка: {e}")
