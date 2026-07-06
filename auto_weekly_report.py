"""
Автоматическое создание еженедельного отчета.

Собирает данные из:
1. Яндекс.Директ (из Excel/CSV выгрузки)
2. Bitrix24 CRM (через API)
3. Яндекс.Метрика (через API)

Создает:
- report_DDMM.py скрипт
- Обновляет Google Sheets
- Обновляет дашборд (index.html)
- Коммитит изменения в GitHub
"""

import json
import os
import sys
import re
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Импорты локальных модулей
try:
    from bitrix_api import get_lead_stats
    from metrika_seo import get_seo_visits, get_top_landing_pages, get_search_queries
except ImportError as e:
    print(f"⚠️  Внимание: {e}")
    print("   Убедитесь, что bitrix_api.py и metrika_seo.py находятся в той же папке")


class WeeklyReportBuilder:
    """Построитель еженедельного отчета."""
    
    def __init__(self, week_start: str, week_end: str):
        """
        Args:
            week_start: Дата начала недели (YYYY-MM-DD)
            week_end: Дата конца недели (YYYY-MM-DD)
        """
        self.week_start = week_start
        self.week_end = week_end
        self.week_label = self._format_week_label()
        self.tab_name = self._format_tab_name()
        self.script_filename = self._format_script_filename()
        
        # Данные для отчета
        self.direct_data = {}  # Данные Яндекс.Директ
        self.crm_data = {}     # Данные из Bitrix24
        self.seo_data = {}     # Данные из Метрики
        
    def _format_week_label(self) -> str:
        """Форматирует метку недели: 08.06–14.06"""
        start = datetime.strptime(self.week_start, "%Y-%m-%d")
        end = datetime.strptime(self.week_end, "%Y-%m-%d")
        return f"{start.strftime('%d.%m')}–{end.strftime('%d.%m')}"
    
    def _format_tab_name(self) -> str:
        """Форматирует имя вкладки: 08.06-14.06"""
        start = datetime.strptime(self.week_start, "%Y-%m-%d")
        end = datetime.strptime(self.week_end, "%Y-%m-%d")
        return f"{start.strftime('%d.%m')}-{end.strftime('%d.%m')}"
    
    def _format_script_filename(self) -> str:
        """Форматирует имя скрипта: report_0806.py"""
        start = datetime.strptime(self.week_start, "%Y-%m-%d")
        return f"report_{start.strftime('%d%m')}.py"
    
    def load_direct_from_csv(self, csv_path: str) -> bool:
        """
        Загружает данные Яндекс.Директ из CSV файла.
        
        CSV должен содержать:
        - Account (e-20010227, e-17228851, dune-group, porg-3uieikjn)
        - Campaign
        - Impressions
        - Clicks
        - Spend
        
        Args:
            csv_path: Путь к CSV файлу
            
        Returns:
            True если успешно загружено
        """
        import csv
        
        if not os.path.exists(csv_path):
            print(f"❌ Файл не найден: {csv_path}")
            return False
        
        print(f"📊 Загрузка данных Директа из {csv_path}...")
        
        # Инициализация структуры
        accounts = {}
        
        try:
            with open(csv_path, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    account = row.get('Account', '').strip()
                    campaign = row.get('Campaign', '').strip()
                    
                    if not account:
                        continue
                    
                    # Парсим числовые значения
                    impressions = int(row.get('Impressions', '0').replace(' ', ''))
                    clicks = int(row.get('Clicks', '0').replace(' ', ''))
                    spend = float(row.get('Spend', '0').replace(' ', '').replace(',', '.'))
                    
                    # Добавляем аккаунт если не существует
                    if account not in accounts:
                        accounts[account] = {
                            'impressions': 0,
                            'clicks': 0,
                            'spend': 0,
                            'campaigns': []
                        }
                    
                    # Агрегируем по аккаунту
                    accounts[account]['impressions'] += impressions
                    accounts[account]['clicks'] += clicks
                    accounts[account]['spend'] += spend
                    
                    # Сохраняем кампанию
                    accounts[account]['campaigns'].append({
                        'name': campaign,
                        'impressions': impressions,
                        'clicks': clicks,
                        'spend': spend
                    })
            
            self.direct_data = accounts
            
            # Выводим summary
            total_spend = sum(a['spend'] for a in accounts.values())
            total_clicks = sum(a['clicks'] for a in accounts.values())
            
            print(f"✅ Загружено:")
            print(f"   Аккаунтов: {len(accounts)}")
            print(f"   Расход: {total_spend:,.0f} руб")
            print(f"   Кликов: {total_clicks:,}")
            
            return True
            
        except Exception as e:
            print(f"❌ Ошибка при чтении CSV: {e}")
            return False
    
    def load_crm_data(self) -> bool:
        """Загружает данные лидов из Bitrix24 CRM."""
        print(f"👥 Загрузка лидов из Bitrix24: {self.week_start} — {self.week_end}...")
        
        try:
            self.crm_data = get_lead_stats(self.week_start, self.week_end)
            
            total_leads = self.crm_data['total']['leads']
            total_target = self.crm_data['total']['target']
            
            print(f"✅ Загружено:")
            print(f"   Лидов: {total_leads}")
            print(f"   Целевых: {total_target}")
            
            return True
            
        except Exception as e:
            print(f"❌ Ошибка загрузки из Bitrix24: {e}")
            print("   Будет использовано значение 0")
            
            # Фоллбек - пустые данные
            self.crm_data = {
                'accounts': {
                    'e-20010227': {'leads': 0, 'target': 0},
                    'e-17228851': {'leads': 0, 'target': 0},
                    'dune-group': {'leads': 0, 'target': 0},
                    'porg-3uieikjn': {'leads': 0, 'target': 0}
                },
                'channels': {
                    'direct': {'leads': 0, 'target': 0},
                    'seo': {'leads': 0, 'target': 0},
                    'recommendations': {'leads': 0, 'target': 0}
                },
                'total': {'leads': 0, 'target': 0}
            }
            return False
    
    def load_seo_data(self) -> bool:
        """Загружает SEO данные из Яндекс.Метрики."""
        print(f"🔍 Загрузка SEO из Метрики: {self.week_start} — {self.week_end}...")
        
        try:
            # Базовая статистика
            seo_stats = get_seo_visits(self.week_start, self.week_end)
            
            # Топ страниц и запросы
            top_pages = get_top_landing_pages(self.week_start, self.week_end, limit=5)
            queries = get_search_queries(self.week_start, self.week_end, limit=5)
            
            self.seo_data = {
                'visits': seo_stats['visits'],
                'users': seo_stats['users'],
                'bounce_rate': seo_stats['bounce_rate'],
                'page_depth': seo_stats['page_depth'],
                'avg_duration': seo_stats['avg_duration'],
                'top_pages': top_pages,
                'search_queries': queries
            }
            
            print(f"✅ Загружено:")
            print(f"   SEO визитов: {seo_stats['visits']}")
            print(f"   Показатель отказов: {seo_stats['bounce_rate']:.1f}%")
            
            return True
            
        except Exception as e:
            print(f"❌ Ошибка загрузки из Метрики: {e}")
            print("   Будет использовано значение 0")
            
            self.seo_data = {
                'visits': 0,
                'users': 0,
                'bounce_rate': 0,
                'page_depth': 0,
                'avg_duration': 0,
                'top_pages': [],
                'search_queries': []
            }
            return False
    
    def generate_report_script(self) -> str:
        """
        Генерирует Python скрипт отчета (report_DDMM.py).
        
        Returns:
            Содержимое скрипта
        """
        # TODO: Реализовать генерацию скрипта на основе данных
        # Пока возвращаем заглушку
        return f'''"""
Weekly report for {self.week_label}
Auto-generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""

# TODO: Implement report generation
'''
    
    def save_report_script(self, output_dir: str = ".") -> bool:
        """Сохраняет скрипт отчета в файл."""
        script_content = self.generate_report_script()
        filepath = os.path.join(output_dir, self.script_filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(script_content)
            print(f"✅ Скрипт сохранен: {filepath}")
            return True
        except Exception as e:
            print(f"❌ Ошибка сохранения скрипта: {e}")
            return False
    
    def print_summary(self):
        """Выводит сводку по собранным данным."""
        print("\n" + "=" * 70)
        print(f"📊 СВОДКА ПО ОТЧЕТУ: {self.week_label}")
        print("=" * 70)
        
        # Яндекс.Директ
        if self.direct_data:
            total_spend = sum(a['spend'] for a in self.direct_data.values())
            total_clicks = sum(a['clicks'] for a in self.direct_data.values())
            total_impressions = sum(a['impressions'] for a in self.direct_data.values())
            
            print(f"\n💰 Яндекс.Директ:")
            print(f"   Расход: {total_spend:,.0f} руб")
            print(f"   Показы: {total_impressions:,}")
            print(f"   Клики: {total_clicks:,}")
            print(f"   CTR: {(total_clicks / total_impressions * 100):.2f}%")
            print(f"   CPC: {(total_spend / total_clicks):.0f} руб")
        
        # CRM Лиды
        if self.crm_data:
            print(f"\n👥 Лиды (CRM):")
            print(f"   Всего: {self.crm_data['total']['leads']}")
            print(f"   Целевые: {self.crm_data['total']['target']}")
            
            if self.crm_data['total']['leads'] > 0 and total_spend > 0:
                cpa = total_spend / self.crm_data['total']['leads']
                print(f"   CPA: {cpa:,.0f} руб")
            
            if self.crm_data['total']['target'] > 0 and total_spend > 0:
                cpl = total_spend / self.crm_data['total']['target']
                print(f"   CPL: {cpl:,.0f} руб")
        
        # SEO
        if self.seo_data:
            print(f"\n🔍 SEO:")
            print(f"   Визиты: {self.seo_data['visits']}")
            print(f"   Показатель отказов: {self.seo_data['bounce_rate']:.1f}%")
            print(f"   Лиды: {self.crm_data['channels']['seo']['leads']}")
        
        print("\n" + "=" * 70)


def main():
    """Главная функция CLI."""
    print("🤖 Автоматический генератор еженедельного отчета")
    print("=" * 70)
    
    if len(sys.argv) < 4:
        print("\nИспользование:")
        print("  python auto_weekly_report.py YYYY-MM-DD YYYY-MM-DD direct.csv")
        print("\nПример:")
        print("  python auto_weekly_report.py 2026-06-08 2026-06-14 direct_w6.csv")
        print("\nФормат CSV файла:")
        print("  Account,Campaign,Impressions,Clicks,Spend")
        print("  e-20010227,МК ТК // Ремонт,50382,470,27820")
        print("  ...")
        return 1
    
    week_start = sys.argv[1]
    week_end = sys.argv[2]
    direct_csv = sys.argv[3]
    
    # Создаем билдер
    builder = WeeklyReportBuilder(week_start, week_end)
    
    print(f"\n📅 Период: {builder.week_label}")
    print(f"📄 Вкладка: {builder.tab_name}")
    print(f"🐍 Скрипт: {builder.script_filename}")
    print()
    
    # Загружаем данные
    success = True
    
    # 1. Яндекс.Директ из CSV
    if not builder.load_direct_from_csv(direct_csv):
        success = False
    
    # 2. CRM данные
    if not builder.load_crm_data():
        print("⚠️  Продолжаем без данных CRM")
    
    # 3. SEO данные
    if not builder.load_seo_data():
        print("⚠️  Продолжаем без данных SEO")
    
    if not success:
        print("\n❌ Ошибка: не удалось загрузить данные Директа")
        return 1
    
    # Выводим сводку
    builder.print_summary()
    
    # Генерируем скрипт
    # builder.save_report_script()
    
    print("\n✅ Готово!")
    print("\nСледующие шаги:")
    print("  1. Проверьте данные выше")
    print("  2. Запустите скрипт для создания отчета в Google Sheets")
    print("  3. Обновите дашборд (index.html)")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
