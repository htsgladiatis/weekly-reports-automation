"""
Менеджер кампаний Яндекс.Директ — Level 99 директолог.

Управление кампаниями, ключевыми словами, ставками, объявлениями
через Яндекс.Директ API v5.

Использование:
    python direct_manager.py list [--account LOGIN] [--state active|paused|archived]
    python direct_manager.py pause CAMPAIGN_ID [CAMPAIGN_ID ...]
    python direct_manager.py resume CAMPAIGN_ID [CAMPAIGN_ID ...]
    python direct_manager.py keywords CAMPAIGN_ID [--adgroup-id ID]
    python direct_manager.py ads CAMPAIGN_ID [--adgroup-id ID]
    python direct_manager.py set-bid KEYWORD_ID BID [--network-bid BID]
    python direct_manager.py budget CAMPAIGN_ID DAILY_BUDGET
    python direct_manager.py info CAMPAIGN_ID
"""

import json
import sys
import os
import time
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

# Windows: UTF-8 для вывода в консоль
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

try:
    import requests
except ImportError:
    print("❌ Требуется requests: pip install requests")
    sys.exit(1)

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


# ─── API endpoints ───────────────────────────────────────────────────────────

API_URL = "https://api.direct.yandex.com/json/v5"


# ─── Менеджер кампаний ──────────────────────────────────────────────────────

class DirectManager:
    """Управление кампаниями Яндекс.Директ через API v5."""

    def __init__(self, token: str = None, login: str = None):
        self.token = token or os.getenv("YANDEX_DIRECT_TOKEN", "")
        self.login = login or os.getenv("YANDEX_DIRECT_LOGIN", "")

        if not self.token:
            raise ValueError("Токен не найден. Проверьте .env файл (YANDEX_DIRECT_TOKEN)")

    # ─── Базовый запрос ──────────────────────────────────────────────────────

    def _headers(self) -> Dict[str, str]:
        h = {
            "Authorization": f"Bearer {self.token}",
            "Accept-Language": "ru",
            "Content-Type": "application/json; charset=utf-8",
        }
        if self.login:
            h["Client-Login"] = self.login
        return h

    def _call(self, service: str, method: str, params: Dict[str, Any],
              retries: int = 3, delay: float = 1.0) -> Dict[str, Any]:
        """
        Универсальный вызов API.

        Args:
            service: Имя сервиса (campaigns, adgroups, ads, keywords, bids)
            method: Имя метода (get, add, update, delete, suspend, resume, set)
            retries: Количество попыток при rate limit
            delay: Задержка между попытками (сек)
        """
        url = f"{API_URL}/{service}"
        body = {"method": method, "params": params}

        for attempt in range(retries):
            try:
                resp = requests.post(url, headers=self._headers(), json=body, timeout=60)

                if resp.status_code == 200:
                    data = resp.json()
                    if "error" in data:
                        err = data["error"]
                        code = err.get("error_code")
                        # Rate limit — ждём и повторяем
                        if code == 53:
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
                    raise Exception("403 Forbidden — нет прав на запись. "
                                    "Проверьте роль аккаунта (нужен Представитель с правами редактирования)")

                elif resp.status_code == 401:
                    raise Exception("401 Unauthorized — токен истёк или невалиден")

                else:
                    raise Exception(f"HTTP {resp.status_code}: {resp.text[:300]}")

            except requests.exceptions.Timeout:
                if attempt < retries - 1:
                    time.sleep(delay * (attempt + 1))
                    continue
                raise Exception("Таймаут запроса к API")

            except requests.exceptions.ConnectionError:
                if attempt < retries - 1:
                    time.sleep(delay * (attempt + 1))
                    continue
                raise Exception("Ошибка подключения к API")

        raise Exception("Превышено количество попыток")

    # ─── Кампании ────────────────────────────────────────────────────────────

    def get_campaigns(self, state: str = None, campaign_ids: List[int] = None) -> List[Dict]:
        """
        Получить список кампаний.

        Args:
            state: Фильтр по состоянию (on|off|suspended|archived)
            campaign_ids: Фильтр по ID кампаний
        """
        criteria = {}
        if state:
            criteria["States"] = [state]
        if campaign_ids:
            criteria["Ids"] = campaign_ids

        params = {
            "SelectionCriteria": criteria,
            "FieldNames": [
                "Id", "Name", "State", "Status", "Type",
                "DailyBudget", "StartDate", "EndDate"
            ]
        }

        result = self._call("campaigns", "get", params)
        return result.get("result", {}).get("Campaigns", [])

    def get_campaign_full(self, campaign_id: int) -> Dict:
        """Получить полную информацию о кампании."""
        campaigns = self.get_campaigns(campaign_ids=[campaign_id])
        if not campaigns:
            raise Exception(f"Кампания {campaign_id} не найдена")
        return campaigns[0]

    def suspend_campaigns(self, campaign_ids: List[int]) -> Dict:
        """Приостановить кампании (pause)."""
        params = {"Ids": campaign_ids}
        result = self._call("campaigns", "suspend", params)
        return result.get("result", {})

    def resume_campaigns(self, campaign_ids: List[int]) -> Dict:
        """Возобновить кампании (resume)."""
        params = {"Ids": campaign_ids}
        result = self._call("campaigns", "resume", params)
        return result.get("result", {})

    def archive_campaigns(self, campaign_ids: List[int]) -> Dict:
        """Архивировать кампании."""
        params = {"Ids": campaign_ids}
        result = self._call("campaigns", "archive", params)
        return result.get("result", {})

    def unarchive_campaigns(self, campaign_ids: List[int]) -> Dict:
        """Разархивировать кампании."""
        params = {"Ids": campaign_ids}
        result = self._call("campaigns", "unarchive", params)
        return result.get("result", {})

    def update_campaign_budget(self, campaign_id: int,
                               daily_budget: float = None,
                               monthly_budget: float = None) -> Dict:
        """
        Изменить бюджет кампании.

        Args:
            campaign_id: ID кампании
            daily_budget: Дневной бюджет в рублях (0 = без ограничений)
            monthly_budget: Месячный бюджет в рублях
        """
        update_data = {"Id": campaign_id}

        if daily_budget is not None:
            update_data["DailyBudget"] = {
                "Amount": str(int(daily_budget * 1_000_000)),  # в микрорублях
                "Mode": "STANDARD"
            }

        if monthly_budget is not None:
            update_data["MonthlyBudget"] = {
                "Amount": str(int(monthly_budget * 1_000_000))
            }

        params = {"Campaigns": [update_data]}
        result = self._call("campaigns", "update", params)
        return result.get("result", {})

    # ─── Группы объявлений ───────────────────────────────────────────────────

    def get_ad_groups(self, campaign_id: int = None,
                      ad_group_ids: List[int] = None) -> List[Dict]:
        """
        Получить группы объявлений.

        Args:
            campaign_id: Фильтр по кампании
            ad_group_ids: Фильтр по ID групп
        """
        criteria = {}
        if campaign_id:
            criteria["CampaignIds"] = [campaign_id]
        if ad_group_ids:
            criteria["Ids"] = ad_group_ids

        params = {
            "SelectionCriteria": criteria,
            "FieldNames": [
                "Id", "Name", "CampaignId", "Type", "Status",
                "NegativeKeywords", "RegionIds"
            ]
        }

        result = self._call("adgroups", "get", params)
        return result.get("result", {}).get("AdGroups", [])

    # ─── Ключевые слова ──────────────────────────────────────────────────────

    def get_keywords(self, campaign_id: int = None,
                     ad_group_ids: List[int] = None,
                     keyword_ids: List[int] = None) -> List[Dict]:
        """
        Получить ключевые слова.

        Args:
            campaign_id: Фильтр по кампании (через группы)
            ad_group_ids: Фильтр по группам
            keyword_ids: Фильтр по ID ключевых слов
        """
        criteria = {}
        if ad_group_ids:
            criteria["AdGroupIds"] = ad_group_ids
        elif campaign_id:
            # Получаем группы кампании, затем ключевые слова
            groups = self.get_ad_groups(campaign_id=campaign_id)
            if not groups:
                return []
            criteria["AdGroupIds"] = [g["Id"] for g in groups]
        if keyword_ids:
            criteria["Ids"] = keyword_ids

        params = {
            "SelectionCriteria": criteria,
            "FieldNames": [
                "Id", "Keyword", "AdGroupId", "CampaignId",
                "State", "Bid", "ContextBid", "AutoBid",
                "MatchType", "StatisticsSearch", "StatisticsNetwork"
            ]
        }

        result = self._call("keywords", "get", params)
        return result.get("result", {}).get("Keywords", [])

    def add_keywords(self, ad_group_id: int, keywords: List[Dict]) -> List[Dict]:
        """
        Добавить ключевые слова в группу.

        Args:
            ad_group_id: ID группы объявлений
            keywords: Список [{"Keyword": "текст", "Bid": 30000000, "MatchType": "EXACT"}]
                      Bid в микрорублях (30000000 = 30 руб)
        """
        kw_list = []
        for kw in keywords:
            item = {"AdGroupId": ad_group_id, "Keyword": kw["Keyword"]}
            if "Bid" in kw:
                item["Bid"] = kw["Bid"]
            if "MatchType" in kw:
                item["MatchType"] = kw["MatchType"]
            kw_list.append(item)

        params = {"Keywords": kw_list}
        result = self._call("keywords", "add", params)
        return result.get("result", {}).get("AddResults", [])

    def update_keywords(self, keyword_updates: List[Dict]) -> List[Dict]:
        """
        Обновить ключевые слова.

        Args:
            keyword_updates: Список [{"Id": 123, "Keyword": "новый текст", "Bid": 50000000}]
        """
        params = {"Keywords": keyword_updates}
        result = self._call("keywords", "update", params)
        return result.get("result", {}).get("UpdateResults", [])

    def delete_keywords(self, keyword_ids: List[int]) -> Dict:
        """Удалить ключевые слова по ID."""
        params = {"SelectionCriteria": {"Ids": keyword_ids}}
        result = self._call("keywords", "delete", params)
        return result.get("result", {})

    # ─── Ставки ──────────────────────────────────────────────────────────────

    def get_bids(self, keyword_ids: List[int] = None,
                 ad_group_ids: List[int] = None) -> List[Dict]:
        """
        Получить текущие ставки.

        Args:
            keyword_ids: ID ключевых слов
            ad_group_ids: ID групп объявлений
        """
        criteria = {}
        if keyword_ids:
            criteria["KeywordIds"] = keyword_ids
        if ad_group_ids:
            criteria["AdGroupIds"] = ad_group_ids

        params = {
            "SelectionCriteria": criteria,
            "FieldNames": ["KeywordId", "AdGroupId", "Bid", "ContextBid", "AutoBid"]
        }

        result = self._call("bids", "get", params)
        return result.get("result", {}).get("Bids", [])

    def set_bids(self, bids: List[Dict]) -> List[Dict]:
        """
        Установить ставки вручную.

        Args:
            bids: Список [{"KeywordId": 123, "Bid": 50000000, "ContextBid": 20000000}]
                  Bid/ContextBid в микрорублях (50000000 = 50 руб)
        """
        params = {"Bids": bids}
        result = self._call("bids", "set", params)
        return result.get("result", {}).get("SetResults", [])

    # ─── Объявления ──────────────────────────────────────────────────────────

    def get_ads(self, campaign_id: int = None,
                ad_group_ids: List[int] = None,
                ad_ids: List[int] = None) -> List[Dict]:
        """
        Получить объявления.

        Args:
            campaign_id: Фильтр по кампании
            ad_group_ids: Фильтр по группам
            ad_ids: Фильтр по ID объявлений
        """
        criteria = {}
        if ad_ids:
            criteria["Ids"] = ad_ids
        if ad_group_ids:
            criteria["AdGroupIds"] = ad_group_ids
        elif campaign_id:
            groups = self.get_ad_groups(campaign_id=campaign_id)
            if not groups:
                return []
            criteria["AdGroupIds"] = [g["Id"] for g in groups]

        params = {
            "SelectionCriteria": criteria,
            "FieldNames": [
                "Id", "AdGroupId", "CampaignId", "State", "Status",
                "Type", "Title", "Text", "DisplayUrl",
                "Sitelinks", "Callout"
            ],
            "TextAdFieldNames": ["Title", "Title2", "Text", "Href", "DisplayUrl"],
            "TextAdImageAdFieldNames": ["ImageHash"],
        }

        result = self._call("ads", "get", params)
        return result.get("result", {}).get("Ads", [])

    def update_ads(self, ad_updates: List[Dict]) -> List[Dict]:
        """
        Обновить объявления.

        Args:
            ad_updates: Список словарей с полями для обновления:
                [{"Id": 123, "TextAd": {"Title": "Новый заголовок", "Text": "Новый текст"}}]
        """
        params = {"Ads": ad_updates}
        result = self._call("ads", "update", params)
        return result.get("result", {}).get("UpdateResults", [])

    # ─── Минус-слова ─────────────────────────────────────────────────────────

    def get_negative_keywords(self, campaign_ids: List[int] = None,
                               ad_group_ids: List[int] = None) -> List[Dict]:
        """Получить минус-слова кампаний и групп."""
        # Минус-слова возвращаются в составе кампаний/групп
        if campaign_ids:
            campaigns = self.get_campaigns(campaign_ids=campaign_ids)
            result = []
            for c in campaigns:
                result.append({
                    "CampaignId": c["Id"],
                    "CampaignName": c["Name"],
                    "NegativeKeywords": c.get("NegativeKeywords", [])
                })
            return result
        elif ad_group_ids:
            groups = self.get_ad_groups(ad_group_ids=ad_group_ids)
            return [{
                "AdGroupId": g["Id"],
                "AdGroupName": g["Name"],
                "NegativeKeywords": g.get("NegativeKeywords", [])
            } for g in groups]
        return []

    def update_campaign_negative_keywords(self, campaign_id: int,
                                           negative_keywords: List[str]) -> Dict:
        """
        Обновить минус-слова кампании.

        Args:
            campaign_id: ID кампании
            negative_keywords: Список минус-слов ["-слово1", "-слово2"]
        """
        params = {
            "Campaigns": [{
                "Id": campaign_id,
                "NegativeKeywords": {"Items": negative_keywords}
            }]
        }
        result = self._call("campaigns", "update", params)
        return result.get("result", {})

    # ─── Вспомогательные методы ──────────────────────────────────────────────

    def rubles_to_micros(self, rubles: float) -> int:
        """Конвертировать рубли в микрорубли."""
        return int(rubles * 1_000_000)

    def micros_to_rubles(self, micros: int) -> float:
        """Конвертировать микрорубли в рубли."""
        return micros / 1_000_000


# ─── CLI ─────────────────────────────────────────────────────────────────────

def format_campaign(c: Dict) -> str:
    """Форматировать кампанию для вывода."""
    state = c.get("State", "?")
    status_icon = {"on": "🟢", "off": "🔴", "suspended": "⏸️", "archived": "📦"}.get(state, "❓")

    daily = c.get("DailyBudget")
    if daily and daily.get("Amount"):
        budget = f"{int(daily['Amount'])/1_000_000:,.0f} ₽/день"
    else:
        budget = "без лимита"

    return (f"{status_icon} [{c['Id']}] {c['Name']}\n"
            f"   Статус: {state} | Тип: {c.get('Type', '?')} | Бюджет: {budget}")


def cmd_list(manager: DirectManager, args: List[str]) -> None:
    """Показать список кампаний."""
    state_filter = None
    account_filter = None

    i = 0
    while i < len(args):
        if args[i] == "--state" and i + 1 < len(args):
            state_filter = args[i + 1]
            i += 2
        elif args[i] == "--account" and i + 1 < len(args):
            account_filter = args[i + 1]
            i += 2
        else:
            i += 1

    if account_filter:
        manager.login = account_filter

    campaigns = manager.get_campaigns(state=state_filter)

    if not campaigns:
        print("Кампании не найдены")
        return

    print(f"\n📋 Кампании ({len(campaigns)} шт.)")
    print("=" * 70)

    for c in campaigns:
        print(format_campaign(c))
        print()

    # Статистика по статусам
    states = {}
    for c in campaigns:
        s = c.get("State", "unknown")
        states[s] = states.get(s, 0) + 1

    print("─" * 40)
    for s, count in sorted(states.items()):
        icon = {"on": "🟢", "off": "🔴", "suspended": "⏸️", "archived": "📦"}.get(s, "❓")
        print(f"  {icon} {s}: {count}")


def cmd_pause(manager: DirectManager, args: List[str]) -> None:
    """Приостановить кампании."""
    if not args:
        print("❌ Укажите ID кампаний: pause ID1 ID2 ...")
        return

    ids = [int(a) for a in args]
    print(f"\n⏸️  Приостановка кампаний: {ids}")

    result = manager.suspend_campaigns(ids)
    print(f"✅ Результат: {json.dumps(result, ensure_ascii=False, indent=2)}")


def cmd_resume(manager: DirectManager, args: List[str]) -> None:
    """Возобновить кампании."""
    if not args:
        print("❌ Укажите ID кампаний: resume ID1 ID2 ...")
        return

    ids = [int(a) for a in args]
    print(f"\n▶️  Возобновление кампаний: {ids}")

    result = manager.resume_campaigns(ids)
    print(f"✅ Результат: {json.dumps(result, ensure_ascii=False, indent=2)}")


def cmd_keywords(manager: DirectManager, args: List[str]) -> None:
    """Показать ключевые слова кампании."""
    if not args:
        print("❌ Укажите ID кампании: keywords CAMPAIGN_ID")
        return

    campaign_id = int(args[0])
    ad_group_id = None

    i = 1
    while i < len(args):
        if args[i] == "--adgroup-id" and i + 1 < len(args):
            ad_group_id = int(args[i + 1])
            i += 2
        else:
            i += 1

    ad_group_ids = [ad_group_id] if ad_group_id else None
    keywords = manager.get_keywords(campaign_id=campaign_id, ad_group_ids=ad_group_ids)

    if not keywords:
        print("Ключевые слова не найдены")
        return

    print(f"\n🔑 Ключевые слова кампании {campaign_id} ({len(keywords)} шт.)")
    print("=" * 80)

    for kw in keywords:
        bid = kw.get("Bid")
        bid_r = f"{int(bid)/1_000_000:.0f} ₽" if bid else "—"
        ctx_bid = kw.get("ContextBid")
        ctx_r = f"{int(ctx_bid)/1_000_000:.0f} ₽" if ctx_bid else "—"
        state_icon = {"on": "🟢", "off": "🔴"}.get(kw.get("State", ""), "❓")

        print(f"{state_icon} [{kw['Id']}] {kw['Keyword']}")
        print(f"   Группа: {kw.get('AdGroupId', '?')} | "
              f"Ставка: {bid_r} | Контекст: {ctx_r} | "
              f"Тип: {kw.get('MatchType', '?')}")


def cmd_ads(manager: DirectManager, args: List[str]) -> None:
    """Показать объявления кампании."""
    if not args:
        print("❌ Укажите ID кампании: ads CAMPAIGN_ID")
        return

    campaign_id = int(args[0])
    ads = manager.get_ads(campaign_id=campaign_id)

    if not ads:
        print("Объявления не найдены")
        return

    print(f"\n📢 Объявления кампании {campaign_id} ({len(ads)} шт.)")
    print("=" * 80)

    for ad in ads:
        state_icon = {"on": "🟢", "off": "🔴", "archived": "📦"}.get(
            ad.get("State", ""), "❓"
        )

        print(f"\n{state_icon} [{ad['Id']}] Группа: {ad.get('AdGroupId', '?')}")

        # Текст объявления
        if "TextAd" in ad:
            ta = ad["TextAd"]
            print(f"   Заголовок: {ta.get('Title', '?')} {ta.get('Title2', '')}")
            print(f"   Текст: {ta.get('Text', '?')}")
            if ta.get("Href"):
                print(f"   URL: {ta['Href']}")

        print(f"   Статус: {ad.get('Status', '?')} | Тип: {ad.get('Type', '?')}")


def cmd_set_bid(manager: DirectManager, args: List[str]) -> None:
    """Установить ставку для ключевого слова."""
    if len(args) < 2:
        print("❌ Использование: set-bid KEYWORD_ID BID_RUB [--network-bid BID_RUB]")
        return

    keyword_id = int(args[0])
    bid_rub = float(args[1])
    network_bid_rub = None

    i = 2
    while i < len(args):
        if args[i] == "--network-bid" and i + 1 < len(args):
            network_bid_rub = float(args[i + 1])
            i += 2
        else:
            i += 1

    bid_data = {
        "KeywordId": keyword_id,
        "Bid": manager.rubles_to_micros(bid_rub)
    }
    if network_bid_rub is not None:
        bid_data["ContextBid"] = manager.rubles_to_micros(network_bid_rub)

    print(f"\n💰 Установка ставки для ключевого слова {keyword_id}")
    print(f"   Поиск: {bid_rub:.0f} ₽")
    if network_bid_rub is not None:
        print(f"   Сеть: {network_bid_rub:.0f} ₽")

    result = manager.set_bids([bid_data])
    print(f"✅ Результат: {json.dumps(result, ensure_ascii=False, indent=2)}")


def cmd_budget(manager: DirectManager, args: List[str]) -> None:
    """Изменить бюджет кампании."""
    if len(args) < 2:
        print("❌ Использование: budget CAMPAIGN_ID DAILY_BUDGET_RUB")
        return

    campaign_id = int(args[0])
    daily_budget = float(args[1])

    print(f"\n💰 Изменение бюджета кампании {campaign_id}")
    print(f"   Дневной бюджет: {daily_budget:,.0f} ₽")

    result = manager.update_campaign_budget(campaign_id, daily_budget=daily_budget)
    print(f"✅ Результат: {json.dumps(result, ensure_ascii=False, indent=2)}")


def cmd_info(manager: DirectManager, args: List[str]) -> None:
    """Подробная информация о кампании."""
    if not args:
        print("❌ Укажите ID кампании: info CAMPAIGN_ID")
        return

    campaign_id = int(args[0])

    print(f"\n📊 Информация о кампании {campaign_id}")
    print("=" * 60)

    # Кампания
    campaign = manager.get_campaign_full(campaign_id)
    print(format_campaign(campaign))
    print()

    # Группы
    groups = manager.get_ad_groups(campaign_id=campaign_id)
    print(f"📁 Группы объявлений: {len(groups)}")
    for g in groups:
        print(f"   [{g['Id']}] {g['Name']} ({g.get('Status', '?')})")
    print()

    # Ключевые слова
    keywords = manager.get_keywords(campaign_id=campaign_id)
    print(f"🔑 Ключевые слова: {len(keywords)}")
    active = [k for k in keywords if k.get("State") == "on"]
    paused = [k for k in keywords if k.get("State") == "off"]
    print(f"   🟢 Активных: {len(active)}")
    print(f"   🔴 Приостановленных: {len(paused)}")
    print()

    # Объявления
    ads_list = manager.get_ads(campaign_id=campaign_id)
    print(f"📢 Объявления: {len(ads_list)}")
    for ad in ads_list:
        title = ""
        if "TextAd" in ad:
            title = ad["TextAd"].get("Title", "")
        print(f"   [{ad['Id']}] {title} ({ad.get('State', '?')})")


def cmd_add_keywords(manager: DirectManager, args: List[str]) -> None:
    """Добавить ключевые слова в группу."""
    if len(args) < 2:
        print("❌ Использование: add-keywords ADGROUP_ID 'keyword1' 'keyword2' ...")
        print("   Или: add-keywords ADGROUP_ID --file keywords.txt")
        return

    ad_group_id = int(args[0])
    keywords_text = []

    if args[1] == "--file" and len(args) > 2:
        with open(args[2], "r", encoding="utf-8") as f:
            keywords_text = [line.strip() for line in f if line.strip()]
    else:
        keywords_text = args[1:]

    kw_objects = [{"Keyword": kw} for kw in keywords_text]

    print(f"\n➕ Добавление {len(kw_objects)} ключевых слов в группу {ad_group_id}")

    result = manager.add_keywords(ad_group_id, kw_objects)
    print(f"✅ Добавлено: {len(result)}")

    for r in result:
        if r.get("Id"):
            print(f"   [{r['Id']}] OK")
        else:
            print(f"   ❌ Ошибка: {r.get('Errors', r)}")


def cmd_delete_keywords(manager: DirectManager, args: List[str]) -> None:
    """Удалить ключевые слова."""
    if not args:
        print("❌ Использование: delete-keywords KW_ID1 KW_ID2 ...")
        return

    ids = [int(a) for a in args]
    print(f"\n🗑️  Удаление {len(ids)} ключевых слов")

    result = manager.delete_keywords(ids)
    print(f"✅ Результат: {json.dumps(result, ensure_ascii=False, indent=2)}")


def cmd_update_ad(manager: DirectManager, args: List[str]) -> None:
    """Обновить объявление."""
    if len(args) < 3:
        print("❌ Использование: update-ad AD_ID --title 'Заголовок' --text 'Текст'")
        return

    ad_id = int(args[0])
    title = None
    text = None

    i = 1
    while i < len(args):
        if args[i] == "--title" and i + 1 < len(args):
            title = args[i + 1]
            i += 2
        elif args[i] == "--text" and i + 1 < len(args):
            text = args[i + 1]
            i += 2
        else:
            i += 1

    update = {"Id": ad_id, "TextAd": {}}
    if title:
        update["TextAd"]["Title"] = title
    if text:
        update["TextAd"]["Text"] = text

    print(f"\n✏️  Обновление объявления {ad_id}")
    if title:
        print(f"   Заголовок: {title}")
    if text:
        print(f"   Текст: {text}")

    result = manager.update_ads([update])
    print(f"✅ Результат: {json.dumps(result, ensure_ascii=False, indent=2)}")


def cmd_add_negative(manager: DirectManager, args: List[str]) -> None:
    """Добавить минус-слова к кампании."""
    if len(args) < 2:
        print("❌ Использование: add-negative CAMPAIGN_ID 'слово1' 'слово2' ...")
        return

    campaign_id = int(args[0])
    neg_words = args[1:]

    # Получаем текущие минус-слова
    current = manager.get_negative_keywords(campaign_ids=[campaign_id])
    existing = []
    if current:
        existing = current[0].get("NegativeKeywords", [])
        if isinstance(existing, dict):
            existing = existing.get("Items", [])

    # Объединяем
    all_neg = list(set(existing + neg_words))

    print(f"\n🚫 Минус-слова кампании {campaign_id}")
    print(f"   Было: {len(existing)}, добавляем: {len(neg_words)}, итого: {len(all_neg)}")

    result = manager.update_campaign_negative_keywords(campaign_id, all_neg)
    print(f"✅ Результат: {json.dumps(result, ensure_ascii=False, indent=2)}")


def cmd_test(manager: DirectManager, args: List[str]) -> None:
    """Проверить подключение к API."""
    print("\n🔑 Проверка подключения к Яндекс.Директ API")
    print("=" * 60)
    print(f"   Токен: {manager.token[:20]}...")
    if manager.login:
        print(f"   Логин: {manager.login}")

    try:
        campaigns = manager.get_campaigns()
        print(f"\n✅ Подключение успешно!")
        print(f"   Кампаний найдено: {len(campaigns)}")

        states = {}
        for c in campaigns:
            s = c.get("State", "unknown")
            states[s] = states.get(s, 0) + 1

        for s, count in sorted(states.items()):
            icon = {"on": "🟢", "off": "🔴", "suspended": "⏸️", "archived": "📦"}.get(s, "❓")
            print(f"   {icon} {s}: {count}")

        # Проверка прав на запись
        print("\n🔐 Проверка прав на запись...")
        try:
            # Пробуем получить группы хотя бы одной кампании
            if campaigns:
                test_id = campaigns[0]["Id"]
                groups = manager.get_ad_groups(campaign_id=test_id)
                print(f"   ✅ Чтение групп: OK ({len(groups)} групп)")
                keywords = manager.get_keywords(campaign_id=test_id)
                print(f"   ✅ Чтение ключевых слов: OK ({len(keywords)} слов)")
        except Exception as e:
            print(f"   ⚠️  Ошибка чтения: {e}")

    except Exception as e:
        print(f"\n❌ Ошибка: {e}")


def main() -> int:
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("""
🎯 Dune Group — Менеджер кампаний Яндекс.Директ (Level 99)

Использование:
    python direct_manager.py <команда> [аргументы]

Команды:
    test                                    Проверить подключение
    list [--state on|off|suspended]         Список кампаний
    info CAMPAIGN_ID                        Подробная информация
    pause CAMPAIGN_ID [...]                 Приостановить кампании
    resume CAMPAIGN_ID [...]                Возобновить кампании
    budget CAMPAIGN_ID DAILY_RUB            Изменить дневной бюджет
    keywords CAMPAIGN_ID                    Ключевые слова кампании
    add-keywords GROUP_ID 'kw1' 'kw2'       Добавить ключевые слова
    delete-keywords KW_ID [...]             Удалить ключевые слова
    set-bid KW_ID BID_RUB                   Установить ставку
    ads CAMPAIGN_ID                         Показать объявления
    update-ad AD_ID --title 'T' --text 'T'  Обновить объявление
    add-negative CAMPA_ID 'word1' 'word2'   Добавить минус-слова

Примеры:
    python direct_manager.py test
    python direct_manager.py list --state on
    python direct_manager.py pause 117666311
    python direct_manager.py keywords 117666311
    python direct_manager.py set-bid 123456789 50
    python direct_manager.py budget 117666311 5000
""")
        return 0

    command = sys.argv[1].lower().replace("-", "_")
    args = sys.argv[2:]

    try:
        manager = DirectManager()
    except ValueError as e:
        print(f"❌ {e}")
        return 1

    commands = {
        "test": cmd_test,
        "list": cmd_list,
        "info": cmd_info,
        "pause": cmd_pause,
        "resume": cmd_resume,
        "budget": cmd_budget,
        "keywords": cmd_keywords,
        "add_keywords": cmd_add_keywords,
        "delete_keywords": cmd_delete_keywords,
        "set_bid": cmd_set_bid,
        "ads": cmd_ads,
        "update_ad": cmd_update_ad,
        "add_negative": cmd_add_negative,
    }

    cmd_func = commands.get(command)
    if not cmd_func:
        print(f"❌ Неизвестная команда: {sys.argv[1]}")
        print(f"   Доступные: {', '.join(commands.keys())}")
        return 1

    try:
        cmd_func(manager, args)
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
