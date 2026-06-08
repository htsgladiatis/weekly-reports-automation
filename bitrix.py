"""
Интеграция с Битрикс24 CRM через REST API (входящий вебхук).

Тянет лиды за период напрямую из Битрикса и считает лиды / целевые лиды
по тем же правилам атрибуции, что использовались при ручной выгрузке CSV:

  - Лид        = директовый (источник "Яндекс.Директ", либо UTM medium=direct,
                  либо source_description=marquiz) и не в браке (семантика стадии ≠ F).
                  Это автоматически исключает Дубль, Подрядчики реклама,
                  Ошиблись номером, Вакансии, Нецелевой лид и прочий брак.
  - Целевой лид = стадия с семантикой "успех" (S) — в dunegroup это CONVERTED / "Целевой лид".
  - Атрибуция по аккаунтам: по utm_campaign (см. ACCOUNT_BY_UTM_CAMPAIGN),
                  иначе по умолчанию в e-20010227 (marquiz).

Настройка:
  1. В Битрикс24: Разработчикам → Другое → Входящий вебхук.
     Выдать права на CRM (crm) и сохранить. Скопировать URL вида
     https://ВАШ-ПОРТАЛ.bitrix24.ru/rest/1/КОД/
  2. Положить URL в переменную окружения BITRIX_WEBHOOK_URL
     (или вписать в константу WEBHOOK_URL ниже).

Использование:
  python bitrix.py 2026-06-01 2026-06-07     # печатает разбивку по аккаунтам

Импорт в скрипт отчёта:
  from bitrix import get_lead_stats
  stats = get_lead_stats("2026-06-01", "2026-06-07")
  # stats["total"]["leads"], stats["accounts"]["e-20010227"]["target"] и т.д.
"""

import json
import os
import sys
import urllib.parse
import urllib.request

# --- Настройки -------------------------------------------------------------

# URL входящего вебхука. Лучше держать в переменной окружения, а не в коде.
# WEBHOOK_URL = os.environ.get("BITRIX_WEBHOOK_URL", "")
WEBHOOK_URL = "https://dunegroup.bitrix24.ru/rest/396/vk0fdm6r1qrtt81w/"

# Семантика стадии в Битриксе: 'S' — успех (целевой), 'F' — провал (брак),
# None — в работе. Целевые лиды = S; брак (F) исключается из подсчёта лидов.
SEMANTIC_SUCCESS = "S"
SEMANTIC_FAILURE = "F"

# Источники, которые считаются рекламой Яндекс.Директ.
DIRECT_SOURCE_NAMES = {"Яндекс.Директ", "Билайн АТС 9094091176"}

# Аккаунт по умолчанию для лидов Директа без явной привязки по UTM.
DEFAULT_ACCOUNT = "e-20010227"

# Все аккаунты отчёта (для инициализации нулями).
ACCOUNTS = ["e-20010227", "e-17228851", "dune-group", "porg-3uieikjn"]

# Привязка лида к аккаунту по utm_campaign.
# Ключ — подстрока в нижнем регистре, значение — код аккаунта.
# Заполняется по мере появления utm_campaign=cabinet-XXXXX в данных.
ACCOUNT_BY_UTM_CAMPAIGN = {
    # "cabinet-17228851": "e-17228851",
    # "cabinet-dune": "dune-group",
}

# Поля, которые запрашиваем у Битрикса.
LEAD_FIELDS = [
    "ID",
    "TITLE",
    "STATUS_ID",
    "SOURCE_ID",
    "SOURCE_DESCRIPTION",
    "UTM_SOURCE",
    "UTM_MEDIUM",
    "UTM_CAMPAIGN",
    "DATE_CREATE",
]


# --- Низкоуровневый вызов API ---------------------------------------------


def _webhook():
    if not WEBHOOK_URL:
        raise RuntimeError(
            "Не задан URL вебхука Битрикс24. Установите переменную окружения "
            "BITRIX_WEBHOOK_URL или впишите WEBHOOK_URL в bitrix.py"
        )
    return WEBHOOK_URL.rstrip("/") + "/"


def call(method, params=None):
    """Один вызов REST-метода. Возвращает разобранный JSON-ответ целиком."""
    url = _webhook() + method + ".json"
    data = urllib.parse.urlencode(_flatten(params or {}), doseq=True).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST")
    with urllib.request.urlopen(req, timeout=60) as resp:
        payload = json.loads(resp.read().decode("utf-8"))
    if "error" in payload:
        raise RuntimeError(
            f"Битрикс API ошибка [{payload.get('error')}]: "
            f"{payload.get('error_description', '')}"
        )
    return payload


def call_list(method, params=None):
    """Вызов list-метода с автоматической постраничной загрузкой (по 50)."""
    params = dict(params or {})
    start = 0
    items = []
    while True:
        params["start"] = start
        payload = call(method, params)
        result = payload.get("result", [])
        items.extend(result)
        total = payload.get("total", 0)
        next_start = payload.get("next")
        if next_start is None or len(items) >= total:
            break
        start = next_start
    return items


def _flatten(params, parent_key=""):
    """Битрикс принимает вложенные структуры как filter[KEY]=value в form-data."""
    pairs = []
    if isinstance(params, dict):
        for key, value in params.items():
            new_key = f"{parent_key}[{key}]" if parent_key else str(key)
            pairs.extend(_flatten(value, new_key))
    elif isinstance(params, (list, tuple)):
        for i, value in enumerate(params):
            new_key = f"{parent_key}[{i}]" if parent_key else str(i)
            pairs.extend(_flatten(value, new_key))
    else:
        pairs.append((parent_key, params))
    return pairs


# --- Справочники (коды стадий и источников → имена) ------------------------


def _status_names(entity_id):
    """Карта STATUS_ID -> NAME для заданной сущности (STATUS, SOURCE)."""
    items = call_list("crm.status.list", {"filter": {"ENTITY_ID": entity_id}})
    return {row["STATUS_ID"]: row["NAME"] for row in items}


def _stage_semantics():
    """Карта STATUS_ID -> SEMANTICS для стадий лида (S/F/None)."""
    items = call_list("crm.status.list", {"filter": {"ENTITY_ID": "STATUS"}})
    return {row["STATUS_ID"]: row.get("SEMANTICS") for row in items}


# --- Загрузка и разбор лидов ----------------------------------------------


def fetch_leads(date_from, date_to):
    """
    Возвращает список лидов за период [date_from, date_to] включительно.
    Даты в формате YYYY-MM-DD. Фильтр по дате создания (DATE_CREATE).
    """
    filter_params = {
        ">=DATE_CREATE": f"{date_from} 00:00:00",
        "<=DATE_CREATE": f"{date_to} 23:59:59",
    }
    return call_list(
        "crm.lead.list",
        {
            "filter": filter_params,
            "select": LEAD_FIELDS,
            "order": {"DATE_CREATE": "ASC"},
        },
    )


def _resolve_account(lead):
    """Определяет аккаунт лида по utm_campaign, иначе аккаунт по умолчанию."""
    utm_campaign = (lead.get("UTM_CAMPAIGN") or "").lower()
    for needle, account in ACCOUNT_BY_UTM_CAMPAIGN.items():
        if needle in utm_campaign:
            return account
    return DEFAULT_ACCOUNT


def _is_direct(lead, source_names):
    """Лид директовый по источнику, UTM medium=direct или marquiz."""
    source_name = source_names.get(lead.get("SOURCE_ID"), "")
    if source_name in DIRECT_SOURCE_NAMES:
        return True
    if (lead.get("UTM_MEDIUM") or "").lower() == "direct":
        return True
    if (lead.get("SOURCE_DESCRIPTION") or "").strip().lower() == "marquiz":
        return True
    return False


def get_lead_stats(date_from, date_to):
    """
    Возвращает агрегированную статистику лидов за период:

      {
        "total":    {"leads": int, "target": int},
        "accounts": {"e-20010227": {"leads": int, "target": int}, ...},
        "details":  [ {ID, TITLE, stage, source, account, is_target}, ... ],
      }

    Учитываются только директовые лиды; стадии из EXCLUDED_STAGES отбрасываются.
    """
    status_names = _status_names("STATUS")
    source_names = _status_names("SOURCE")
    semantics = _stage_semantics()
    leads = fetch_leads(date_from, date_to)

    accounts = {acc: {"leads": 0, "target": 0} for acc in ACCOUNTS}
    total = {"leads": 0, "target": 0}
    details = []

    for lead in leads:
        status_id = lead.get("STATUS_ID")
        stage = status_names.get(status_id, status_id or "")
        sem = semantics.get(status_id)
        if not _is_direct(lead, source_names):
            continue
        # брак (Дубль, Подрядчики, Ошиблись номером, Вакансии, Нецелевой лид...)
        if sem == SEMANTIC_FAILURE:
            continue

        account = _resolve_account(lead)
        is_target = sem == SEMANTIC_SUCCESS

        accounts.setdefault(account, {"leads": 0, "target": 0})
        accounts[account]["leads"] += 1
        total["leads"] += 1
        if is_target:
            accounts[account]["target"] += 1
            total["target"] += 1

        details.append(
            {
                "ID": lead.get("ID"),
                "TITLE": lead.get("TITLE"),
                "stage": stage,
                "source": source_names.get(lead.get("SOURCE_ID"), ""),
                "source_description": lead.get("SOURCE_DESCRIPTION", ""),
                "utm_campaign": lead.get("UTM_CAMPAIGN", ""),
                "account": account,
                "date": lead.get("DATE_CREATE"),
                "is_target": is_target,
            }
        )

    return {"total": total, "accounts": accounts, "details": details}


# --- CLI -------------------------------------------------------------------


def _print_report(stats, date_from, date_to):
    print(f"\nЛиды из Битрикс24 за {date_from} — {date_to}\n" + "=" * 60)
    print(f"{'Аккаунт':<20}{'Лиды':>8}{'Ц. Лиды':>10}")
    print("-" * 60)
    for acc in ACCOUNTS:
        a = stats["accounts"].get(acc, {"leads": 0, "target": 0})
        print(f"{acc:<20}{a['leads']:>8}{a['target']:>10}")
    # аккаунты, появившиеся динамически и не входящие в ACCOUNTS
    for acc, a in stats["accounts"].items():
        if acc not in ACCOUNTS:
            print(f"{acc + ' (новый)':<20}{a['leads']:>8}{a['target']:>10}")
    print("-" * 60)
    print(f"{'ИТОГО':<20}{stats['total']['leads']:>8}{stats['total']['target']:>10}")

    print("\nДетализация:")
    for d in stats["details"]:
        flag = "★" if d["is_target"] else " "
        print(
            f"  {flag} [{d['ID']}] {d['date']}  {d['account']:<12} "
            f"{d['stage']:<14} src={d['source']}/{d['source_description']} "
            f"utm_campaign={d['utm_campaign']}  {d['TITLE']}"
        )


def main(argv):
    if len(argv) != 3:
        print("Использование: python bitrix.py YYYY-MM-DD YYYY-MM-DD")
        return 1
    date_from, date_to = argv[1], argv[2]
    stats = get_lead_stats(date_from, date_to)
    _print_report(stats, date_from, date_to)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

