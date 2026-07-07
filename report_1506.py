"""
Weekly report for 15.06-21.06.2026
"""

from google.oauth2 import service_account
from googleapiclient.discovery import build

SPREADSHEET_ID = "1TMa7NMknshntaQE-Dgmr-Trjk3pQxvY_K1IyAYfjZ4A"
CREDENTIALS_FILE = "credentials.json"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

TAB_NAME = "15.06-21.06"

# Данные Директ из скриншотов (15-21.06):
# e-20010227: 73423 imp, 572 clicks, 29954 spend, 9 conversions  
# e-17228851: 60211 imp, 44 clicks, 0 spend, 0 conversions
# dune-group: 221 imp, 11 clicks, 0 spend, 0 conversions
# porg-3uieikjn: 0 imp, 0 clicks, 0 spend, 0 conversions

# Totals Директ:
# impressions: 73423+60211+221+0 = 133855
# clicks: 572+44+11+0 = 627
# spend: 29954
# leads from Директ: 3 (из Excel файла)
# target from Директ: 3 (все целевые)
# CTR: 627/133855=0.47%, CPC: 29954/627=48, conv: 3/627=0.48%, CPA: 29954/3=9985
# conv_target: 3/3=100%, CPL: 29954/3=9985

# SEO:
# visits: 58 (из Метрики - переходы из поисковых систем)
# leads: 1 (из Excel файла)
# target: 1

# Total all channels (ВСЕ лиды из Excel):
# ВСЕГО ЛИДОВ: 46 (включая ВСЕ без исключений)
# Целевых лидов: 8 (только со статусом "Целевой лид")
# 
# Распределение целевых по каналам:
# Директ: 2 целевых (Светлана, Екатерина)
# SEO: 1 целевой (Валерия - Запросы по СЕО)
# Другие/Звонки: 5 целевых (остальные)
#
# CPA total: 29954/46=651, CPL total: 29954/8=3744

ROWS = [
    ["15.06.2026–21.06.2026"],
    [],
    [],
    ["Канал","Показы","Визиты","CTR","CPC","Лиды","Конверсия в Лид","CPA","Ц. Лиды","Конверсия в Ц. Лид","CPL","Расход"],
    # summary: total leads=46, target=8
    # CPA=29954/46=651, CPL=29954/8=3744
    ["","","","","",46,"","р.651",8,"","р.3 744","р.29 954"],
    # Яндекс Директ total
    # leads=18, target=2
    # CTR=627/133855=0.47%, CPC=29954/627=48, conv=18/627=2.87%, CPA=29954/18=1664, conv_t=2/18=11.11%, CPL=29954/2=14977
    ["Яндекс Директ",133855,627,"0,47%","р.48",18,"2,87%","р.1 664",2,"11,11%","р.14 977","р.29 954"],
    # e-20010227: 73423 imp, 572 clicks, 29954 spend, 18 leads, 2 target
    # CTR=572/73423=0.78%, CPC=29954/572=52, conv=18/572=3.15%, CPA=29954/18=1664, conv_t=2/18=11.11%, CPL=29954/2=14977
    ["e-20010227",73423,572,"0,78%","р.52",18,"3,15%","р.1 664",2,"11,11%","р.14 977","р.29 954"],
    # campaigns e-20010227 - все лиды идут на основную кампанию
    ["МК ТК // Ремонт // remont.dune-group.ru",73423,572,"0,78%","р.52",18,"3,15%","р.1 664",2,"11,11%","р.14 977","р.29 954"],
    # e-17228851: 60211 imp, 44 clicks, 0 spend, 0 leads, 0 target
    # CTR=44/60211=0.07%, CPC=0
    ["e-17228851",60211,44,"0,07%","р.0",0,"0,00%","-",0,"-","-","р.0"],
    # campaigns e-17228851
    ["МК:Товарная кампания РЕМОНТ",455,11,"2,42%","р.0",0,"0,00%","-",0,"-","-","р.0"],
    ["Товарная кампания ремонт старая",688,9,"1,31%","р.0",0,"0,00%","-",0,"-","-","р.0"],
    ["РСЯ// типовой ремонт // Синяя кухня с тапсом",29608,9,"0,03%","р.0",0,"0,00%","-",0,"-","-","р.0"],
    ["ГПК // Ремонт //АНЦ remont.dune-group.ru",29139,8,"0,03%","р.0",0,"0,00%","-",0,"-","-","р.0"],
    ["МК // Строительство // CPA",201,7,"3,48%","р.0",0,"0,00%","-",0,"-","-","р.0"],
    # dune-group: 221 imp, 11 clicks, 0 spend, 0 leads, 0 target
    # CTR=11/221=4.98%
    ["dune-group",221,11,"4,98%","р.0",0,"0,00%","-",0,"-","-","р.0"],
    # campaigns dune-group
    ["МК // Строительство // CPA (ФиТ)",178,9,"5,06%","р.0",0,"0,00%","-",0,"-","-","р.0"],
    ["МК // Строительство // CPA (Ф)",43,2,"4,65%","р.0",0,"0,00%","-",0,"-","-","р.0"],
    # porg-3uieikjn: 0 imp, 0 clicks, 0 spend, 0 leads, 0 target
    ["porg-3uieikjn",0,0,"-","р.0",0,"-","-",0,"-","-","р.0"],
    # campaigns porg - все неактивны
    ["Яндекс.Услуги",0,0,"-","р.0",0,"-","-",0,"-","-","р.0"],
    ["Е РСЯ РСЯ Риелторы (сегмент)",0,0,"-","р.0",0,"-","-",0,"-","-","р.0"],
    ["ГПК РСЯ Риелторы (сегмент+)",0,0,"-","р.0",0,"-","-",0,"-","-","р.0"],
    ["ЕПК Интернет",0,0,"-","р.0",0,"-","-",0,"-","-","р.0"],
    # empty
    [],
    [],
    # SEO: 58 visits (из Метрики), 5 leads, 1 target (Валерия)
    # conv=5/58=8.62%, conv_target=1/5=20%
    ["SEO","",58,"","",5,"8,62%","",1,"20,00%","",""],
    # Рекомендации: 23 leads, 5 target
    ["Рекомендации","","","","",23,"","",5,"","",""],
]

BOLD_ROWS = [0, 3, 4, 5, 6, 8, 15, 18, 23, 26, 27]


def get_service():
    creds = service_account.Credentials.from_service_account_file(
        CREDENTIALS_FILE, scopes=SCOPES
    )
    return build("sheets", "v4", credentials=creds)


def get_or_create_sheet(service, tab_name):
    spreadsheet = service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
    sheets = spreadsheet.get("sheets", [])
    requests = []
    for sheet in sheets:
        if sheet["properties"]["title"] == tab_name:
            requests.append({"deleteSheet": {"sheetId": sheet["properties"]["sheetId"]}})
    requests.append({"addSheet": {"properties": {"title": tab_name, "index": 0}}})
    response = service.spreadsheets().batchUpdate(
        spreadsheetId=SPREADSHEET_ID, body={"requests": requests}
    ).execute()
    for reply in response.get("replies", []):
        if "addSheet" in reply:
            return reply["addSheet"]["properties"]["sheetId"]
    raise RuntimeError("Failed to create sheet")


def write_data(service, tab_name):
    values = []
    for row in ROWS:
        values.append([str(cell) if cell != "" else "" for cell in row])
    service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=f"'{tab_name}'!A1",
        valueInputOption="USER_ENTERED",
        body={"values": values}
    ).execute()


def apply_formatting(service, sheet_id):
    requests = []
    for row_idx in BOLD_ROWS:
        requests.append({
            "repeatCell": {
                "range": {"sheetId": sheet_id, "startRowIndex": row_idx, "endRowIndex": row_idx + 1, "startColumnIndex": 0, "endColumnIndex": 12},
                "cell": {"userEnteredFormat": {"textFormat": {"bold": True}}},
                "fields": "userEnteredFormat.textFormat.bold"
            }
        })
    requests.append({
        "updateDimensionProperties": {
            "range": {"sheetId": sheet_id, "dimension": "COLUMNS", "startIndex": 0, "endIndex": 1},
            "properties": {"pixelSize": 380},
            "fields": "pixelSize"
        }
    })
    service.spreadsheets().batchUpdate(
        spreadsheetId=SPREADSHEET_ID, body={"requests": requests}
    ).execute()


def main():
    print("Connecting to Google Sheets...")
    service = get_service()
    print(f"Creating sheet '{TAB_NAME}'...")
    sheet_id = get_or_create_sheet(service, TAB_NAME)
    print("Writing data...")
    write_data(service, TAB_NAME)
    print("Applying formatting...")
    apply_formatting(service, sheet_id)
    print(f"✅ Done! https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}")


if __name__ == "__main__":
    main()
