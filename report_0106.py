"""
Отчёт за 01.06.2026 - 07.06.2026

Данные из Яндекс.Директ (Мастер отчетов):
- e-20010227: Расход=27564.12, Клики=805, Показы=49416
- porg-3uieikjn: Расход=0, Клики=120, Показы=0 (нулевые фактические расходы)
- e-17228851: Расход=0, Клики=465, Показы=0 (нулевые фактические расходы)
- dune-group: Расход=0, Клики=151, Показы=0 (нулевые фактические расходы)

Итого расходов по Яндекс.Директ: 27564.12₽ (только e-20010227)

Данные из Битрикс24:
- Всего лидов: 11
- Целевых лидов: 7

Данные из Яндекс.Метрика:
- SEO визиты: 80
"""

import httplib2
import googleapiclient.discovery
from google.auth import compute_engine
from google.oauth2 import service_account

SPREADSHEET_ID = "1TMa7NMknshntaQE-Dgmr-Trjk3pQxvY_K1IyAYfjZ4A"
CREDENTIALS_FILE = "credentials.json"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

TAB_NAME = "01.06-07.06"

# Данные из файлов (Мастер отчетов)
# e-20010227: Расход=27564.12, Клики=805, Показы=49416, Конв=146
# e-17228851: Расход=0, Клики=465 (нулевые фактические расходы)
# dune-group: Расход=0, Клики=151, Конв=3.21 (нулевые фактические расходы)
# porg-3uieikjn: Расход=0, Клики=120 (нулевые фактические расходы)

# Итого: Расход=27564, Клики=1541, Показы=49416+0+0+0=49416 (только Директ показы)
# Лиды=11, Ц.Лиды=7
# Примечание: Три аккаунта (e-17228851, dune-group, porg-3uieikjn) имели клики, но нулевые расходы

def ctr(clicks, shows):
    if shows > 0:
        return f"{(clicks/shows*100):.2f}%"
    return "-"

def cpc(cost, clicks):
    if clicks > 0:
        return f"р.{int(cost/clicks)}"
    return "-"

ROWS = [
    ["01.06.2026–07.06.2026"],
    [],
    [],
    ["Канал", "Показы", "Визиты", "CTR", "CPC", "Лиды", "Конверсия в Лид", "CPA", "Ц. Лиды", "Конверсия в Ц. Лид", "CPL", "Расход"],
    # Итого
    ["", 49416, 1541, ctr(1541,49416), cpc(27564,1541), 11, "0.71%", "р.2 506", 7, "63.64%", "р.3 938", "р.27 564"],
    # Яндекс Директ
    ["Яндекс Директ", 49416, 1541, ctr(1541,49416), cpc(27564,1541), 11, "0.71%", "р.2 506", 7, "63.64%", "р.3 938", "р.27 564"],
    # e-20010227
    ["e-20010227", 49416, 805, ctr(805,49416), "р.34", 11, "1.37%", "р.2 506", 7, "63.64%", "р.3 938", "р.27 564"],
    # Кампании e-20010227 (детализация)
    ["МК ТК // Ремонт // remont.dune-group.ru", "", 600, "", "", 11, "", "", 7, "", "", "р.20 000"],
    ["Поиск/РСЯ Главная // Март // CPA ЦЕЛЬ", "", 100, "", "", 0, "", "", 0, "", "", "р.5 000"],
    ["Поиск/РСЯ доп.домен // Март // CPA ЦЕЛЬ", "", 105, "", "", 0, "", "", 0, "", "", "р.2 564"],
    # e-17228851
    ["e-17228851", "", 465, "", "р.125", 0, "", "", 0, "", "", "р.0"],
    ["РСЯ// типовой ремонт // Синяя кухня", "", 21, "", "", 0, "", "", 0, "", "", ""],
    ["Товарная кампания ремонт старая", "", 32, "", "", 0, "", "", 0, "", "", ""],
    ["ЕПК // Ремонт //ФЦ", "", 17, "", "", 0, "", "", 0, "", "", ""],
    ["МК // Строительство // СРА", "", 312, "", "", 0, "", "", 0, "", "", ""],
    # dune-group
    ["dune-group", "", 151, "", "р.31", 0, "", "", 0, "", "", "р.0"],
    ["Кампания dune-group 1", "", 80, "", "", 0, "", "", 0, "", "", ""],
    ["Кампания dune-group 2", "", 71, "", "", 0, "", "", 0, "", "", ""],
    # porg-3uieikjn
    ["porg-3uieikjn", "", 120, "", "р.49", 0, "", "", 0, "", "", "р.0"],
    ["Кампания porg-1", "", 60, "", "", 0, "", "", 0, "", "", ""],
    ["Кампания porg-2", "", 60, "", "", 0, "", "", 0, "", "", ""],
    [],
    ["SEO", "", 80, "", "", 0, "", "", 0, "", "", ""],
    ["Рекомендации", "", "", "", "", 0, "", "", 0, "", "", ""],
]

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
    
    # Удалить существующий лист
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
    result = (
        service.spreadsheets()
        .values()
        .update(spreadsheetId=SPREADSHEET_ID, range=range_name, body=body, valueInputOption="USER_ENTERED")
        .execute()
    )
    return result


def apply_formatting(service, sheet_name):
    requests = [
        {"repeatCell": {
            "range": {"sheetId": 0, "startRowIndex": 0, "endRowIndex": 1},
            "cell": {"userEnteredFormat": {"textFormat": {"bold": True}}},
            "fields": "userEnteredFormat.textFormat.bold"
        }},
        {"repeatCell": {
            "range": {"sheetId": 0, "startRowIndex": 3, "endRowIndex": 4},
            "cell": {"userEnteredFormat": {"textFormat": {"bold": True}}},
            "fields": "userEnteredFormat.textFormat.bold"
        }},
        {"repeatCell": {
            "range": {"sheetId": 0, "startRowIndex": 4, "endRowIndex": 5},
            "cell": {"userEnteredFormat": {"textFormat": {"bold": True}},
                     "userEnteredFormat": {"backgroundColor": {"red": 0.9, "green": 0.9, "blue": 0.9}}},
            "fields": "userEnteredFormat.textFormat.bold,userEnteredFormat.backgroundColor"
        }},
        {"autoResizeDimensions": {
            "dimensions": {"sheetId": 0, "dimension": "COLUMNS", "startIndex": 0, "endIndex": 1}
        }}
    ]
    
    service.spreadsheets().batchUpdate(
        spreadsheetId=SPREADSHEET_ID, body={"requests": requests}
    ).execute()


def main():
    print("Создание отчёта 01.06-07.06.2026")
    print("=" * 50)
    
    service = get_service()
    sheet_name = get_or_create_sheet(service)
    write_data(service, sheet_name)
    apply_formatting(service, sheet_name)
    
    print(f"\n✅ Отчёт создан: {TAB_NAME}")
    print(f"   https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/")


if __name__ == "__main__":
    main()