"""Weekly report for 27.07-02.08.2026 — Week 13.
Data manually extracted from CSV exports dated 03.08.2026.

Direct: 27,851 impressions / 2,585 clicks / 9,898.92 ₽.
CRM: 47 records with IDs / 0 target; 5 Direct, 2 SEO, 40 other.
SEO exports: 44 organic clicks/visits, coverage 27.07-01.08 (incomplete week).
"""

import sys
sys.stdout.reconfigure(encoding="utf-8")

from google.oauth2 import service_account
from googleapiclient.discovery import build

SPREADSHEET_ID = "1TMa7NMknshntaQE-Dgmr-Trjk3pQxvY_K1IyAYfjZ4A"
CREDENTIALS_FILE = "credentials.json"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
TAB_NAME = "27.07-02.08"

DIRECT_E20010227 = {"imp": 3449, "clicks": 51, "spend": 1220.00, "leads": 4, "target": 0}
DIRECT_E17228851 = {"imp": 22320, "clicks": 2481, "spend": 8678.92, "leads": 1, "target": 0}
DIRECT_DUNE = {"imp": 0, "clicks": 0, "spend": 0.00, "leads": 0, "target": 0}
DIRECT_PORG = {"imp": 2082, "clicks": 53, "spend": 0.00, "leads": 0, "target": 0}
DIRECT_ACCOUNTS = [DIRECT_E20010227, DIRECT_E17228851, DIRECT_DUNE, DIRECT_PORG]
DIRECT_TOTALS = {key: sum(account[key] for account in DIRECT_ACCOUNTS) for key in ("imp", "clicks", "spend", "leads", "target")}

ALL_LEADS, ALL_TARGETS = 47, 0
# Manual CRM attribution confirmed from Bitrix24 lead cards.
MANUAL_CRM_ATTRIBUTION = {
    "24390": "e-17228851",
    "24424": "seo",
    "24410": "seo",
}
SEO_LEADS, SEO_TARGETS, SEO_VISITS = 2, 0, 44
OTHER_LEADS, OTHER_TARGETS = 40, 0

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
    ["27.07.2026–02.08.2026"],
    [],
    ["Канал", "Показы", "Визиты", "CTR", "CPC", "Лиды", "Конверсия в Лид", "CPA", "Ц. Лиды", "Конверсия в Ц. Лид", "CPL", "Расход"],
    metric_row("", {**DIRECT_TOTALS, "leads": ALL_LEADS, "target": ALL_TARGETS}),
    metric_row("Яндекс Директ", DIRECT_TOTALS),
    metric_row("  e-20010227", DIRECT_E20010227),
    campaign_row("    МК ТК // Ремонт // remont.dune-group.ru", 3449, 51, 1220, 5),
    metric_row("  e-17228851", DIRECT_E17228851),
    # CRM ID 24390 confirms the account e-17228851, but not a specific campaign.
    campaign_row("    МК // Строительство // СРА->в платку", 20393, 2416, 6596.49),
    campaign_row("    МК // Ремонт Денис Бренд//", 1443, 18, 1455.44),
    campaign_row("    Стройка / Поиск / Ростов", 484, 47, 626.99),
    metric_row("  dune-group", DIRECT_DUNE),
    metric_row("  porg-3uieikjn", DIRECT_PORG),
    campaign_row("    МК // Строительство // СРА (Ф)", 1418, 38, 0),
    campaign_row("    МК // Строительство // СРА (Ф+ТГ)", 664, 15, 0),
    [],
    [],
    ["SEO", "—", SEO_VISITS, "—", "—", SEO_LEADS, "—", "—", SEO_TARGETS, "—", "—", "—"],
    ["Рекомендации", "—", "—", "—", "—", OTHER_LEADS, "—", "—", OTHER_TARGETS, "—", "—", "—"],
]

BOLD_ROWS = [0, 2, 3, 4, 5, 7, 11, 12, 17, 18]

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
