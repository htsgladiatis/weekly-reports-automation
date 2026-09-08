"""Weekly report for 31.08-06.09.2026 — Week 18.
Data extracted from CSV exports dated 08.09.2026.

Direct: 20,255 impressions / 282 clicks / 22,734.25 ₽ (5 cabinets, porg-l2oigjze active).
  - porg-l2oigjze (713690254 Товарная remont): 19,848 / 270 / 22,734.25
  - porg-3uieikjn: 407 / 12 / 0.00 (СРА Ф/Ф+ТГ)
  - e-20010227, e-17228851, dune-group: пустые выгрузки → 0
CRM: 35 records → all 35 counted as leads (per W13-W15 convention); 3 target.
  - Директ 11 (9 по UTM 713690254 + 2 целевых по ручной атрибуции РК porg-l2oigjze: 24776 Роман ЖК Эстет 38м2 вайт бокс 1200, 24774 Андрей Левобережная 54м2 типовой 1700)
  - SEO 1 (Ждут сдачу дома, Запросы по СЕО) → 0 целей
  - Другие 23 (0 целей)
SEO Webmaster (31.08-05.09): 56 visits (Clicks по страницам), топ /prices 21, / 10.
"""

import sys
sys.stdout.reconfigure(encoding="utf-8")

from google.oauth2 import service_account
from googleapiclient.discovery import build

SPREADSHEET_ID = "1TMa7NMknshntaQE-Dgmr-Trjk3pQxvY_K1IyAYfjZ4A"
CREDENTIALS_FILE = "credentials.json"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
TAB_NAME = "31.08-06.09"

DIRECT_E20010227 = {"imp": 0, "clicks": 0, "spend": 0.00, "leads": 0, "target": 0}
DIRECT_E17228851 = {"imp": 0, "clicks": 0, "spend": 0.00, "leads": 0, "target": 0}
DIRECT_DUNE = {"imp": 0, "clicks": 0, "spend": 0.00, "leads": 0, "target": 0}
DIRECT_PORG = {"imp": 407, "clicks": 12, "spend": 0.00, "leads": 0, "target": 0}
DIRECT_L2OIGJZE = {"imp": 19848, "clicks": 270, "spend": 22734.25, "leads": 11, "target": 3}  # 9 по UTM 713690254 + 24776 (Роман Эстет 38/1200) + 24774 (Андрей Левобережная 54/1700)
DIRECT_ACCOUNTS = [DIRECT_E20010227, DIRECT_E17228851, DIRECT_DUNE, DIRECT_PORG, DIRECT_L2OIGJZE]
DIRECT_TOTALS = {key: sum(account[key] for account in DIRECT_ACCOUNTS) for key in ("imp", "clicks", "spend", "leads", "target")}

ALL_LEADS, ALL_TARGETS = 35, 3
SEO_LEADS, SEO_TARGETS, SEO_VISITS = 1, 0, 56
OTHER_LEADS, OTHER_TARGETS = 23, 0


def fmt_money(value):
    if value is None or value == 0 or value == "—":
        return "—"
    return f"р.{int(round(value)):,}".replace(",", " ")


def fmt_pct(value):
    if value is None or value == 0 or value == "—":
        return "—"
    return f"{value:.2f}%".replace(".", ",")


def safe_div(a, b):
    return 0 if not b else a / b


def metric_row(label, data):
    imp, clicks, spend, leads, target = (data[key] for key in ("imp", "clicks", "spend", "leads", "target"))
    return [label, imp, clicks, fmt_pct(safe_div(clicks, imp) * 100), fmt_money(safe_div(spend, clicks)), leads,
            fmt_pct(safe_div(leads, clicks) * 100), fmt_money(safe_div(spend, leads)), target,
            fmt_pct(safe_div(target, leads) * 100), fmt_money(safe_div(spend, target)), fmt_money(spend)]


def campaign_row(label, imp, clicks, spend, leads=0, target=0):
    return metric_row(label, {"imp": imp, "clicks": clicks, "spend": spend, "leads": leads, "target": target})


ROWS = [
    ["31.08.2026–06.09.2026"],
    [],
    ["Канал", "Показы", "Визиты", "CTR", "CPC", "Лиды", "Конверсия в Лид", "CPA", "Ц. Лиды", "Конверсия в Ц. Лид", "CPL", "Расход"],
    metric_row("", {**DIRECT_TOTALS, "leads": ALL_LEADS, "target": ALL_TARGETS}),
    metric_row("Яндекс Директ", DIRECT_TOTALS),
    metric_row("  e-20010227", DIRECT_E20010227),
    metric_row("  e-17228851", DIRECT_E17228851),
    metric_row("  dune-group", DIRECT_DUNE),
    metric_row("  porg-3uieikjn", DIRECT_PORG),
    campaign_row("    МК // Строительство // СРА (Ф)", 302, 5, 0),
    campaign_row("    МК // Строительство // СРА (Ф+ТГ)", 105, 7, 0),
    metric_row("  porg-l2oigjze", DIRECT_L2OIGJZE),
    campaign_row("    Товарная кампания remont.dune-group.ru (713690254)", 19848, 270, 22734.25, 11, 3),
    [],
    [],
    ["SEO", "—", SEO_VISITS, "—", "—", SEO_LEADS, "—", "—", SEO_TARGETS, "—", "—", "—"],
    ["Рекомендации", "—", "—", "—", "—", OTHER_LEADS, "—", "—", OTHER_TARGETS, "—", "—", "—"],
]

BOLD_ROWS = [0, 2, 3, 4, 5, 6, 8, 9, 12, 16, 17]


def get_service():
    creds = service_account.Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
    return build("sheets", "v4", credentials=creds)


def get_or_create_sheet(service, tab_name):
    spreadsheet = service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
    requests = [{"deleteSheet": {"sheetId": sheet["properties"]["sheetId"]}}
                for sheet in spreadsheet.get("sheets", [])
                if sheet["properties"]["title"] == tab_name]
    requests.append({"addSheet": {"properties": {"title": tab_name, "index": 0}}})
    response = service.spreadsheets().batchUpdate(spreadsheetId=SPREADSHEET_ID, body={"requests": requests}).execute()
    for reply in response.get("replies", []):
        if "addSheet" in reply:
            return reply["addSheet"]["properties"]["sheetId"]
    raise RuntimeError("Failed to create sheet")


def write_data(service, tab_name):
    values = [[str(cell) if cell != "" else "" for cell in row] for row in ROWS]
    service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID, range=f"'{tab_name}'!A1",
        valueInputOption="USER_ENTERED", body={"values": values}
    ).execute()


def apply_formatting(service, sheet_id):
    requests = []
    for row_idx in BOLD_ROWS:
        requests.append({"repeatCell": {
            "range": {"sheetId": sheet_id, "startRowIndex": row_idx, "endRowIndex": row_idx + 1, "startColumnIndex": 0, "endColumnIndex": 12},
            "cell": {"userEnteredFormat": {"textFormat": {"bold": True}}},
            "fields": "userEnteredFormat.textFormat.bold"
        }})
    requests.append({"repeatCell": {
        "range": {"sheetId": sheet_id, "startRowIndex": 3, "endRowIndex": 4, "startColumnIndex": 0, "endColumnIndex": 12},
        "cell": {"userEnteredFormat": {"textFormat": {"bold": True}, "backgroundColor": {"red": 0.9, "green": 0.95, "blue": 0.9}}},
        "fields": "userEnteredFormat.textFormat.bold,userEnteredFormat.backgroundColor"
    }})
    requests.append({"updateDimensionProperties": {
        "range": {"sheetId": sheet_id, "dimension": "COLUMNS", "startIndex": 0, "endIndex": 1},
        "properties": {"pixelSize": 380}, "fields": "pixelSize"
    }})
    service.spreadsheets().batchUpdate(spreadsheetId=SPREADSHEET_ID, body={"requests": requests}).execute()


def main():
    service = get_service()
    sheet_id = get_or_create_sheet(service, TAB_NAME)
    write_data(service, TAB_NAME)
    apply_formatting(service, sheet_id)
    print(f"Done: {TAB_NAME}; Direct {DIRECT_TOTALS['imp']:,} imp / {DIRECT_TOTALS['clicks']:,} clicks / ₽{DIRECT_TOTALS['spend']:,.2f}; leads {ALL_LEADS}; SEO {SEO_VISITS}")


if __name__ == "__main__":
    main()
