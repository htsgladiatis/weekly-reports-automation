"""
Яндекс.Директ API Client для автоматической выгрузки статистики.

Документация API: https://yandex.ru/dev/direct/doc/
Reports API: https://yandex.ru/dev/direct/doc/reports/reports.html
"""

import json
import time
import sys
import os
from typing import Dict, List, Any, Optional
from datetime import datetime

try:
    import requests
except ImportError:
    print("❌ Требуется библиотека requests")
    print("   Установите: pip install requests")
    sys.exit(1)

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️  Библиотека python-dotenv не установлена (необязательна)")
    print("   Установите: pip install python-dotenv")


# Яндекс.Директ API endpoints
API_URL = "https://api.direct.yandex.com/json/v5"
REPORTS_URL = "https://api.direct.yandex.com/json/v5/reports"

# Токен из переменной окружения
YANDEX_DIRECT_TOKEN = os.getenv("YANDEX_DIRECT_TOKEN", "")
YANDEX_DIRECT_LOGIN = os.getenv("YANDEX_DIRECT_LOGIN", "")


class YandexDirectAPI:
    """API клиент для Яндекс.Директ."""
    
    def __init__(self, token: str = None, login: str = None):
        """
        Args:
            token: OAuth токен для API
            login: Логин аккаунта (опционально)
        """
        self.token = token or YANDEX_DIRECT_TOKEN
        self.login = login or YANDEX_DIRECT_LOGIN
        
        if not self.token:
            raise ValueError(
                "Токен не найден! Создайте .env файл с YANDEX_DIRECT_TOKEN="
            )
    
    def _make_request(self, url: str, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Выполняет запрос к API Яндекс.Директ.
        
        Args:
            url: URL endpoint'а
            method: Название метода API
            params: Параметры запроса
            
        Returns:
            Ответ API
        """
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept-Language": "ru",
            "Content-Type": "application/json; charset=utf-8"
        }
        
        if self.login:
            headers["Client-Login"] = self.login
        
        body = {
            "method": method,
            "params": params
        }
        
        try:
            response = requests.post(url, headers=headers, json=body, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            
            if "error" in result:
                error = result["error"]
                raise Exception(
                    f"API Error [{error.get('error_code')}]: "
                    f"{error.get('error_string')} - {error.get('error_detail')}"
                )
            
            return result
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Ошибка запроса к API: {e}")
    
    def get_campaigns(self) -> List[Dict[str, Any]]:
        """
        Получает список всех кампаний.
        
        Returns:
            Список кампаний с ID, именем и статусом
        """
        params = {
            "SelectionCriteria": {},
            "FieldNames": ["Id", "Name", "State", "Status", "Type"]
        }
        
        result = self._make_request(API_URL + "/campaigns", "get", params)
        
        return result.get("result", {}).get("Campaigns", [])
    
    def get_campaign_stats(
        self,
        date_from: str,
        date_to: str,
        campaign_ids: Optional[List[int]] = None
    ) -> List[Dict[str, Any]]:
        """
        Получает статистику по кампаниям за период.
        
        Args:
            date_from: Дата начала (YYYY-MM-DD)
            date_to: Дата конца (YYYY-MM-DD)
            campaign_ids: Список ID кампаний (None = все)
            
        Returns:
            Статистика по кампаниям
        """
        params = {
            "SelectionCriteria": {
                "DateFrom": date_from,
                "DateTo": date_to
            },
            "FieldNames": [
                "CampaignId",
                "CampaignName",
                "Date",
                "Impressions",
                "Clicks",
                "Cost"
            ],
            "ReportName": f"Campaign Stats {date_from} - {date_to}",
            "ReportType": "CAMPAIGN_PERFORMANCE_REPORT",
            "DateRangeType": "CUSTOM_DATE",
            "Format": "TSV",
            "IncludeVAT": "YES",
            "IncludeDiscount": "YES"
        }
        
        if campaign_ids:
            params["SelectionCriteria"]["CampaignIds"] = campaign_ids
        
        return self._get_report(params)
    
    def _get_report(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Получает отчет из Reports API.
        
        Reports API работает асинхронно:
        1. Отправляем запрос
        2. Ждем готовности (статус 200)
        3. Скачиваем результат
        
        Args:
            params: Параметры отчета
            
        Returns:
            Данные отчета
        """
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept-Language": "ru",
            "Content-Type": "application/json; charset=utf-8",
            "processingMode": "auto",
            "returnMoneyInMicros": "false",
            "skipReportHeader": "true",
            "skipReportSummary": "true"
        }
        
        if self.login:
            headers["Client-Login"] = self.login
        
        body = {"params": params}
        
        print(f"📊 Запрос отчета: {params['ReportName']}")
        
        # Отправляем запрос
        response = requests.post(REPORTS_URL, headers=headers, json=body)
        
        # Проверяем статус
        retry_in = 0
        while response.status_code == 201 or response.status_code == 202:
            # Отчет еще формируется
            retry_in = int(response.headers.get("retryIn", 5))
            print(f"   ⏳ Ожидание готовности отчета ({retry_in} сек)...")
            time.sleep(retry_in)
            
            # Повторный запрос
            response = requests.post(REPORTS_URL, headers=headers, json=body)
        
        if response.status_code == 200:
            # Отчет готов
            print(f"   ✅ Отчет готов")
            
            # Парсим TSV ответ
            return self._parse_tsv_report(response.text)
        else:
            # Ошибка
            error_data = response.json()
            error = error_data.get("error", {})
            raise Exception(
                f"Ошибка получения отчета [{error.get('error_code')}]: "
                f"{error.get('error_string')} - {error.get('error_detail')}"
            )
    
    def _parse_tsv_report(self, tsv_text: str) -> List[Dict[str, Any]]:
        """
        Парсит TSV ответ от Reports API.
        
        Args:
            tsv_text: Текст отчета в формате TSV
            
        Returns:
            Список строк отчета как словарей
        """
        lines = tsv_text.strip().split("\n")
        
        if not lines:
            return []
        
        # Первая строка - заголовки
        headers = lines[0].split("\t")
        
        # Остальные строки - данные
        result = []
        for line in lines[1:]:
            values = line.split("\t")
            
            if len(values) != len(headers):
                continue
            
            row = {}
            for i, header in enumerate(headers):
                value = values[i]
                
                # Преобразуем числовые значения
                if header in ["Impressions", "Clicks"]:
                    row[header] = int(value) if value != "--" else 0
                elif header in ["Cost"]:
                    # Cost возвращается в микрорублях или рублях
                    # Если returnMoneyInMicros=false, то в рублях
                    row[header] = float(value) if value != "--" else 0.0
                else:
                    row[header] = value
            
            result.append(row)
        
        return result
    
    def get_stats_by_account(
        self,
        date_from: str,
        date_to: str,
        accounts: Dict[str, List[int]]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Получает статистику по аккаунтам (группам кампаний).

        Args:
            date_from: Дата начала (YYYY-MM-DD)
            date_to: Дата конца (YYYY-MM-DD)
            accounts: Словарь {account_name: [campaign_ids]}

        Returns:
            Статистика по аккаунтам
        """
        result = {}

        for account_name, campaign_ids in accounts.items():
            print(f"\n📊 Аккаунт: {account_name}")

            stats = self.get_campaign_stats(date_from, date_to, campaign_ids)

            # Агрегируем данные
            total_impressions = sum(row.get("Impressions", 0) for row in stats)
            total_clicks = sum(row.get("Clicks", 0) for row in stats)
            total_cost = sum(row.get("Cost", 0) for row in stats)

            result[account_name] = {
                "impressions": total_impressions,
                "clicks": total_clicks,
                "spend": total_cost,
                "campaigns": stats
            }

            print(f"   Показы: {total_impressions:,}")
            print(f"   Клики: {total_clicks:,}")
            print(f"   Расход: {total_cost:,.2f} руб")

        return result

    # ─── Управление кампаниями (write operations) ─────────────────────────

    def _call(self, service: str, method: str, params: Dict[str, Any],
              retries: int = 3, delay: float = 1.0) -> Dict[str, Any]:
        """Универсальный вызов API с поддержкой записи."""
        url = f"{API_URL}/{service}"
        body = {"method": method, "params": params}

        for attempt in range(retries):
            try:
                resp = requests.post(
                    url, headers={
                        "Authorization": f"Bearer {self.token}",
                        "Accept-Language": "ru",
                        "Content-Type": "application/json; charset=utf-8",
                        **({"Client-Login": self.login} if self.login else {})
                    },
                    json=body, timeout=60
                )

                if resp.status_code == 200:
                    data = resp.json()
                    if "error" in data:
                        err = data["error"]
                        code = err.get("error_code")
                        if code == 53:  # Rate limit
                            wait = int(resp.headers.get("retryIn", 5))
                            print(f"   ⏳ Rate limit, ожидание {wait} сек...")
                            time.sleep(wait)
                            continue
                        raise Exception(
                            f"API Error [{code}]: {err.get('error_string')} — "
                            f"{err.get('error_detail')}"
                        )
                    return data

                elif resp.status_code == 403:
                    raise Exception("403 Forbidden — нет прав на запись")
                elif resp.status_code == 401:
                    raise Exception("401 Unauthorized — токен истёк")
                else:
                    raise Exception(f"HTTP {resp.status_code}: {resp.text[:300]}")

            except requests.exceptions.Timeout:
                if attempt < retries - 1:
                    time.sleep(delay * (attempt + 1))
                    continue
                raise

            except requests.exceptions.ConnectionError:
                if attempt < retries - 1:
                    time.sleep(delay * (attempt + 1))
                    continue
                raise

        raise Exception("Превышено количество попыток")

    def suspend_campaigns(self, campaign_ids: List[int]) -> Dict:
        """Приостановить кампании (pause)."""
        return self._call("campaigns", "suspend", {"Ids": campaign_ids}).get("result", {})

    def resume_campaigns(self, campaign_ids: List[int]) -> Dict:
        """Возобновить кампании (resume)."""
        return self._call("campaigns", "resume", {"Ids": campaign_ids}).get("result", {})

    def update_campaign_budget(self, campaign_id: int,
                               daily_budget: float = None) -> Dict:
        """Изменить дневной бюджет кампании (в рублях)."""
        update_data = {"Id": campaign_id}
        if daily_budget is not None:
            update_data["DailyBudget"] = {
                "Amount": str(int(daily_budget * 1_000_000)),
                "Mode": "STANDARD"
            }
        return self._call("campaigns", "update", {"Campaigns": [update_data]}).get("result", {})

    def get_ad_groups(self, campaign_id: int = None,
                      ad_group_ids: List[int] = None) -> List[Dict]:
        """Получить группы объявлений."""
        criteria = {}
        if campaign_id:
            criteria["CampaignIds"] = [campaign_id]
        if ad_group_ids:
            criteria["Ids"] = ad_group_ids
        params = {
            "SelectionCriteria": criteria,
            "FieldNames": ["Id", "Name", "CampaignId", "Type", "Status", "NegativeKeywords"]
        }
        return self._call("adgroups", "get", params).get("result", {}).get("AdGroups", [])

    def get_keywords(self, campaign_id: int = None,
                     ad_group_ids: List[int] = None) -> List[Dict]:
        """Получить ключевые слова кампании."""
        criteria = {}
        if ad_group_ids:
            criteria["AdGroupIds"] = ad_group_ids
        elif campaign_id:
            groups = self.get_ad_groups(campaign_id=campaign_id)
            if not groups:
                return []
            criteria["AdGroupIds"] = [g["Id"] for g in groups]
        params = {
            "SelectionCriteria": criteria,
            "FieldNames": ["Id", "Keyword", "AdGroupId", "CampaignId", "State",
                           "Bid", "ContextBid", "MatchType"]
        }
        return self._call("keywords", "get", params).get("result", {}).get("Keywords", [])

    def add_keywords(self, ad_group_id: int, keywords: List[Dict]) -> List[Dict]:
        """Добавить ключевые слова. keywords: [{"Keyword": "текст", "Bid": 30000000}]"""
        kw_list = [{"AdGroupId": ad_group_id, **kw} for kw in keywords]
        return self._call("keywords", "add", {"Keywords": kw_list}).get("result", {}).get("AddResults", [])

    def update_keywords(self, keyword_updates: List[Dict]) -> List[Dict]:
        """Обновить ключевые слова. [{"Id": 123, "Bid": 50000000}]"""
        return self._call("keywords", "update", {"Keywords": keyword_updates}).get("result", {}).get("UpdateResults", [])

    def delete_keywords(self, keyword_ids: List[int]) -> Dict:
        """Удалить ключевые слова по ID."""
        return self._call("keywords", "delete", {"SelectionCriteria": {"Ids": keyword_ids}}).get("result", {})

    def get_bids(self, keyword_ids: List[int] = None,
                 ad_group_ids: List[int] = None) -> List[Dict]:
        """Получить текущие ставки."""
        criteria = {}
        if keyword_ids:
            criteria["KeywordIds"] = keyword_ids
        if ad_group_ids:
            criteria["AdGroupIds"] = ad_group_ids
        params = {
            "SelectionCriteria": criteria,
            "FieldNames": ["KeywordId", "AdGroupId", "Bid", "ContextBid", "AutoBid"]
        }
        return self._call("bids", "get", params).get("result", {}).get("Bids", [])

    def set_bids(self, bids: List[Dict]) -> List[Dict]:
        """Установить ставки. [{"KeywordId": 123, "Bid": 50000000}]"""
        return self._call("bids", "set", {"Bids": bids}).get("result", {}).get("SetResults", [])

    def get_ads(self, campaign_id: int = None,
                ad_group_ids: List[int] = None) -> List[Dict]:
        """Получить объявления кампании."""
        criteria = {}
        if ad_group_ids:
            criteria["AdGroupIds"] = ad_group_ids
        elif campaign_id:
            groups = self.get_ad_groups(campaign_id=campaign_id)
            if not groups:
                return []
            criteria["AdGroupIds"] = [g["Id"] for g in groups]
        params = {
            "SelectionCriteria": criteria,
            "FieldNames": ["Id", "AdGroupId", "CampaignId", "State", "Status", "Type", "Title", "Text"],
            "TextAdFieldNames": ["Title", "Title2", "Text", "Href", "DisplayUrl"]
        }
        return self._call("ads", "get", params).get("result", {}).get("Ads", [])

    def update_ads(self, ad_updates: List[Dict]) -> List[Dict]:
        """Обновить объявления. [{"Id": 123, "TextAd": {"Title": "...", "Text": "..."}}]"""
        return self._call("ads", "update", {"Ads": ad_updates}).get("result", {}).get("UpdateResults", [])

    def get_negative_keywords(self, campaign_ids: List[int]) -> List[Dict]:
        """Получить минус-слова кампаний."""
        campaigns = self.get_campaigns(campaign_ids=campaign_ids)
        return [{
            "CampaignId": c["Id"],
            "CampaignName": c["Name"],
            "NegativeKeywords": c.get("NegativeKeywords", [])
        } for c in campaigns]

    def update_campaign_negative_keywords(self, campaign_id: int,
                                           negative_keywords: List[str]) -> Dict:
        """Обновить минус-слова кампании."""
        return self._call("campaigns", "update", {
            "Campaigns": [{
                "Id": campaign_id,
                "NegativeKeywords": {"Items": negative_keywords}
            }]
        }).get("result", {})

    @staticmethod
    def rubles_to_micros(rubles: float) -> int:
        return int(rubles * 1_000_000)

    @staticmethod
    def micros_to_rubles(micros: int) -> float:
        return micros / 1_000_000


def main():
    """CLI для тестирования API."""
    if len(sys.argv) < 2:
        print("Использование:")
        print("  python yandex_direct_api.py test                    # Проверка подключения")
        print("  python yandex_direct_api.py campaigns               # Список кампаний")
        print("  python yandex_direct_api.py stats YYYY-MM-DD YYYY-MM-DD  # Статистика")
        print("\nПример:")
        print("  python yandex_direct_api.py test")
        print("  python yandex_direct_api.py campaigns")
        print("  python yandex_direct_api.py stats 2026-06-08 2026-06-14")
        return 1
    
    command = sys.argv[1]
    
    try:
        api = YandexDirectAPI()
        
        if command == "test":
            print("\n🔑 Проверка подключения к Яндекс.Директ API")
            print("=" * 70)
            
            campaigns = api.get_campaigns()
            
            print(f"\n✅ Подключение успешно!")
            print(f"   Найдено кампаний: {len(campaigns)}")
            
            if campaigns:
                print(f"\n📋 Первые 5 кампаний:")
                for i, campaign in enumerate(campaigns[:5], 1):
                    print(f"   {i}. [{campaign['Id']}] {campaign['Name']} "
                          f"({campaign['State']}, {campaign['Status']})")
        
        elif command == "campaigns":
            print("\n📋 Список всех кампаний")
            print("=" * 70)
            
            campaigns = api.get_campaigns()
            
            print(f"\n{'ID':<15} {'Название':<50} {'Статус':<15}")
            print("-" * 80)
            
            for campaign in campaigns:
                print(f"{campaign['Id']:<15} {campaign['Name'][:47]:<50} "
                      f"{campaign['State']:<15}")
            
            print(f"\nВсего: {len(campaigns)} кампаний")
        
        elif command == "stats" and len(sys.argv) == 4:
            date_from, date_to = sys.argv[2], sys.argv[3]
            
            print(f"\n📊 Статистика: {date_from} — {date_to}")
            print("=" * 70)
            
            stats = api.get_campaign_stats(date_from, date_to)
            
            print(f"\n{'Кампания':<50} {'Показы':>12} {'Клики':>10} {'Расход':>12}")
            print("-" * 86)
            
            total_impressions = 0
            total_clicks = 0
            total_cost = 0
            
            for row in stats:
                campaign_name = row["CampaignName"][:47]
                impressions = row.get("Impressions", 0)
                clicks = row.get("Clicks", 0)
                cost = row.get("Cost", 0)
                
                total_impressions += impressions
                total_clicks += clicks
                total_cost += cost
                
                print(f"{campaign_name:<50} {impressions:>12,} {clicks:>10,} "
                      f"{cost:>11,.2f}₽")
            
            print("-" * 86)
            print(f"{'ИТОГО':<50} {total_impressions:>12,} {total_clicks:>10,} "
                  f"{total_cost:>11,.2f}₽")
            
            if total_impressions > 0:
                ctr = (total_clicks / total_impressions * 100)
                print(f"\nCTR: {ctr:.2f}%")
            
            if total_clicks > 0:
                cpc = total_cost / total_clicks
                print(f"CPC: {cpc:.2f} руб")
        
        else:
            print("❌ Неверная команда")
            return 1
    
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
