"""
Weekly report for 25.05-31.05.2026
"""

from google.oauth2 import service_account
from googleapiclient.discovery import build

SPREADSHEET_ID = "1TMa7NMknshntaQE-Dgmr-Trjk3pQxvY_K1IyAYfjZ4A"
CREDENTIALS_FILE = "credentials.json"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

TAB_NAME = "25.05-31.05"

# Данные Директ из скриншотов:
# e-20010227: 67151 imp, 2654 clicks, 23022 spend, 2 conversions
# e-17228851: 72942 imp, 1463 clicks, 5735 spend, 1 conversion
# dune-group: 4350 imp, 234 clicks, 0 spend, 0 conversions
# porg-3uieikjn: 5703 imp, 114 clicks, 0 spend, 0 conversions

# Totals Директ:
# impressions: 67151+72942+4350+5703 = 150146
# clicks: 2654+1463+234+114 = 4465
# spend: 23022+5735+0+0 = 28757
# leads from Директ: 5 (все e-20010227)
# target from Директ: 2 (Владимир, Анна)
# CTR: 4465/150146=2.97%, CPC: 28757/4465=6, conv: 5/4465=0.11%, CPA: 28757/5=5751
# conv_target: 2/5=40.00%, CPL: 28757/2=14379

# Total all channels:
# leads: 5(Директ)+0(SEO)+0(Рек) = 5
# target: 2(Директ)+0(SEO)+0(Рек) = 2
# CPA total: 28757/5=5751, CPL total: 28757/2=14379

ROWS = [
    ["25.05.2026–31.05.2026"],
    [],
    [],
    ["Канал","Показы","Визиты","CTR","CPC","Лиды","Конверсия в Лид","CPA","Ц. Лиды","Конверсия в Ц. Лид","CPL","Расход"],
    # summary: total leads=5, target=2
    # CPA=28757/5=5751, CPL=28757/2=14379
    ["","","","","",5,"","р.5 751",2,"","р.14 379","р.28 757"],
    # Яндекс Директ total
    # leads=5, target=2
    # CTR=4465/150146=2.97%, CPC=28757/4465=6, conv=5/4465=0.11%, CPA=28757/5=5751, conv_t=2/5=40%, CPL=28757/2=14379
    ["Яндекс Директ",150146,4465,"2,97%","р.6",5,"0,11%","р.5 751",2,"40,00%","р.14 379","р.28 757"],
    # e-20010227: 67151 imp, 2654 clicks, 23022 spend, 5 leads, 2 target
    # CTR=2654/67151=3.95%, CPC=23022/2654=9, conv=5/2654=0.19%, CPA=23022/5=4604, conv_t=2/5=40%, CPL=23022/2=11511
    ["e-20010227",67151,2654,"3,95%","р.9",5,"0,19%","р.4 604",2,"40,00%","р.11 511","р.23 022"],
    # campaigns e-20010227 - все лиды идут на основную кампанию
    ["МК ТК // Ремонт // remont.dune-group.ru",62073,2213,"3,56%","р.10",5,"0,23%","р.4 604",2,"40,00%","р.11 511","р.23 022"],
    ["Поиск/РСЯ Главная // Март // CPA ЦЕЛЬ",2058,146,"7,09%","р.0",0,"0,00%","-",0,"-","-","р.0"],
    ["Поиск/РСЯ доп.домен // Март // CPA ЦЕЛЬ",1921,53,"2,76%","р.0",0,"0,00%","-",0,"-","-","р.0"],
    ["РСЯ // типовой ремонт // Синяя кухня",188,14,"7,45%","р.0",0,"0,00%","-",0,"-","-","р.0"],
    ["Поиск/РСЯ Главная // Март // CPA ЦЕЛЬ (копия)",911,28,"3,07%","р.0",0,"0,00%","-",0,"-","-","р.0"],
    ["Поиск // строительство (конкуренты)",0,0,"0,00%","р.0",0,"-","-",0,"-","-","р.0"],
    # e-17228851: 72942 imp, 1463 clicks, 5735 spend, 0 leads from Директ, 0 target
    # CTR=1463/72942=2.01%, CPC=5735/1463=4, conv=0
    ["Яндекс Директ e-17228851",72942,1463,"2,01%","р.4",0,"0,00%","р.0",0,"-","р.0","р.5 735"],
    # campaigns e-17228851
    ["МК // Строительство // CPA->в платку",34878,1346,"3,86%","р.4",0,"0,00%","р.0",0,"-","р.0","р.5 735"],
    ["ЕПК // Ремонт // ФЦ remont.dune-group.ru",25241,13,"0,05%","р.0",0,"0,00%","р.0",0,"-","р.0","р.0"],
    # dune-group: 4350 imp, 234 clicks, 0 spend, 0 leads, 0 target
    ["dune-group",4350,234,"5,38%","р.0",0,"0,00%","р.0",0,"-","р.0","р.0"],
    # campaigns dune-group
    ["ЕПК РСЯ Риелторы (сегмент+)",2674,182,"6,81%","р.0",0,"0,00%","р.0",0,"-","р.0","р.0"],
    ["ЕПК РСЯ Риелторы (сегмент)",1686,52,"3,08%","р.0",0,"0,00%","р.0",0,"-","р.0","р.0"],
    # porg-3uieikjn: 5703 imp, 114 clicks, 0 spend, 0 leads, 0 target
    ["porg-3uieikjn",5703,114,"2,00%","р.0",0,"0,00%","-",0,"-","-","р.0"],
    # campaigns porg
    ["МК // Строительство // CPA (Ф)",4347,64,"1,47%","р.0",0,"0,00%","-",0,"-","-","р.0"],
    ["МК // Строительство // CPA (Ф+ТГ)",1436,50,"3,48%","р.0",0,"0,00%","-",0,"-","-","р.0"],
    # empty
    [],
    [],
    # SEO: 44 visits (из Метрики), 0 target leads
    ["SEO","",44,"","",0,"","",0,"","",""],
    # Рекомендации: 0
    ["Рекомендации","","","","",0,"","",0,"","",""],
]

BOLD_ROWS = [0, 3, 4, 5, 6, 13, 16, 19, 22, 25, 26]


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
    print(f"Done! https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}")


if __name__ == "__main__":
    main()
