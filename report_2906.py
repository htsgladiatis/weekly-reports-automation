"""
Weekly report for 29.06-05.07.2026
"""

import httplib2
import googleapiclient.discovery
from google.auth import compute_engine
from google.oauth2 import service_account

SPREADSHEET_ID = "1TMa7NMknshntaQE-Dgmr-Trjk3pQxvY_K1IyAYfjZ4A"
CREDENTIALS_FILE = "credentials.json"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

TAB_NAME = "29.06-05.07"

# Direct (из direct_2906.csv):
# e-20010227: impressions=53253, clicks=425, spend=28104.79
# e-17228851: impressions=45340, clicks=757, spend=4970.61
# porg-3uieikjn: impressions=370, clicks=18, spend=0
#
# Totals Direct:
# impressions=98963, clicks=1200, spend=33075.40

# CRM (Bitrix24):
# leads=23, target=0

# SEO (Яндекс.Метрика):
# visits=53, bounce_rate=9.4%
# leads=0 (из сводки auto_weekly_report.py)

def ctr(clicks, shows):
    if shows and shows > 0:
        return f"{(clicks / shows * 100):.2f}%"
    return "-"

def cpc(cost, clicks):
    if clicks and clicks > 0:
        return f"р.{int(cost / clicks)}"
    return "-"

# Примерное форматирование cost/clicks:
# total CPC = int(33075/1200)=27
total_impressions = 98963
total_clicks = 1200
total_spend = 33075.40

total_leads = 23
total_target = 0

seo_visits = 53
seo_bounce_rate = 9.4
seo_leads = 0

# Расчёты для Direct totals:
# CTR = 1200/98963=1.21%
# CPC = 33075/1200=27.56 -> 27
ROWS = [
    ["29.06.2026–05.07.2026"],
    [],
    [],
    ["Канал", "Показы", "Визиты", "CTR", "CPC", "Лиды", "Конверсия в Лид", "CPA", "Ц. Лиды", "Конверсия в Ц. Лид", "CPL", "Расход"],
    # Итого
    ["", total_impressions, total_clicks, ctr(total_clicks, total_impressions), cpc(total_spend, total_clicks), total_leads, "0.00%", "-", total_target, "-", "-", f"р.{int(round(total_spend))}"],
    # Яндекс Директ
    ["Яндекс Директ", total_impressions, total_clicks, ctr(total_clicks, total_impressions), cpc(total_spend, total_clicks), total_leads, "0.00%", "-", total_target, "-", "-", f"р.{int(round(total_spend))}"],

    # e-20010227
    ["e-20010227", 53253, 425, ctr(425, 53253), cpc(28104.79, 425), 0, "", "", 0, "", "", f"р.{int(round(28104.79))}"],

    # e-17228851
    ["e-17228851", 45340, 757, ctr(757, 45340), cpc(4970.61, 757), 0, "", "", 0, "", "", f"р.{int(round(4970.61))}"],

    # porg-3uieikjn
    ["porg-3uieikjn", 370, 18, ctr(18, 370), cpc(0.0, 18), 0, "", "", 0, "", "", "р.0"],

    [],
    # SEO
    ["SEO", "", seo_visits, "", "", seo_leads, "", "", 0, "", "", ""],

    # Рекомендации (если по структуре фронта нужно существование строки)
    ["Рекомендации", "", "", "", "", 0, "", "", 0, "", "", ""],
]

# Жирные строки (индексация как в report_0106.py)
# 0: дата (жирн.)
# 3: заголовок таблицы
# 4: итог
# 5: Яндекс Директ
BOLD_ROWS = [0, 3, 4, 5, 6, 20, 25, 26]

def get_service():
    credentials = service_account.Credentials.from_service_account_file(
        CREDENTIALS_FILE, scopes=SCOPES
    )
    service = googleapiclient.discovery.build("sheets", "v4", credentials=credentials)
    return service

def get_or_create_sheet(service):
    spreadsheet = service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
    sheets = spreadsheet.get("sheets", [])

    # Удалить существующий лист, если есть
    for sheet in sheets:
        if sheet["properties"]["title"] == TAB_NAME:
            requests = [{"deleteSheet": {"sheetId": sheet["properties"]["sheetId"]}}]
            service.spreadsheets().batchUpdate(
                spreadsheetId=SPREADSHEET_ID, body={"requests": requests}
            ).execute()
            break

    # Создать новый лист
    requests = [{"addSheet": {"properties": {"title": TAB_NAME, "index": 0}}}]
    service.spreadsheets().batchUpdate(
        spreadsheetId=SPREADSHEET_ID, body={"requests": requests}
    ).execute()

    return TAB_NAME

def write_data(service, sheet_name):
    range_name = f"{sheet_name}!A1:L{len(ROWS)}"
    body = {"values": ROWS}
    return (
        service.spreadsheets()
        .values()
        .update(
            spreadsheetId=SPREADSHEET_ID,
            range=range_name,
            body=body,
            valueInputOption="USER_ENTERED",
        )
        .execute()
    )

def apply_formatting(service, sheet_name):
    # В report_0106.py везде sheetId==0, поэтому повторяем подход.
    requests = [
        {
            "repeatCell": {
                "range": {"sheetId": 0, "startRowIndex": 0, "endRowIndex": 1},
                "cell": {"userEnteredFormat": {"textFormat": {"bold": True}}},
                "fields": "userEnteredFormat.textFormat.bold",
            }
        },
        {
            "repeatCell": {
                "range": {"sheetId": 0, "startRowIndex": 3, "endRowIndex": 4},
                "cell": {"userEnteredFormat": {"textFormat": {"bold": True}}},
                "fields": "userEnteredFormat.textFormat.bold",
            }
        },
        {
            "repeatCell": {
                "range": {"sheetId": 0, "startRowIndex": 4, "endRowIndex": 5},
                "cell": {
                    "userEnteredFormat": {
                        "textFormat": {"bold": True},
                        "backgroundColor": {"red": 0.9, "green": 0.9, "blue": 0.9},
                    }
                },
                "fields": "userEnteredFormat.textFormat.bold,userEnteredFormat.backgroundColor",
            }
        },
        {
            "autoResizeDimensions": {
                "dimensions": {"sheetId": 0, "dimension": "COLUMNS", "startIndex": 0, "endIndex": 1}
            }
        },
    ]

    service.spreadsheets().batchUpdate(
        spreadsheetId=SPREADSHEET_ID, body={"requests": requests}
    ).execute()

def main():
    print("Создание отчёта 29.06-05.07.2026")
    print("=" * 50)

    service = get_service()
    sheet_name = get_or_create_sheet(service)
    write_data(service, sheet_name)
    apply_formatting(service, sheet_name)

    print(f"\n✅ Отчёт создан: {TAB_NAME}")
    print(f"   https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/")

if __name__ == "__main__":
    main()
