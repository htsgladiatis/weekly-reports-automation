"""
Weekly report for 04.05-10.05.2026
"""

from google.oauth2 import service_account
from googleapiclient.discovery import build

SPREADSHEET_ID = "1TMa7NMknshntaQE-Dgmr-Trjk3pQxvY_K1IyAYfjZ4A"
CREDENTIALS_FILE = "credentials.json"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

TAB_NAME = "04.05-10.05"

ROWS = [
    ["04.05.2026–10.05.2026"],
    [],
    [],
    ["Канал","Показы","Визиты","CTR","CPC","Лиды","Конверсия в Лид","CPA","Ц. Лиды","Конверсия в Ц. Лид","CPL","Расход"],
    # summary row: totals
    ["","","","","",5,"","р.2 497",0,"","-","р.12 486"],
    # Яндекс Директ total (all 4 accounts)
    # impressions: 48704+68377+8095+5525=130701, clicks: 475+110+216+121=922, spend: 12242+0+244+0=12486
    # CTR: 922/130701*100=0.71%, CPC: 12486/922=14, leads=5, conv=5/922=0.54%, CPA=12486/5=2497, target=0
    ["Яндекс Директ",130701,922,"0,71%","р.14",5,"0,54%","р.2 497",0,"-","-","р.12 486"],
    # e-20010227: impressions=48704, clicks=475, spend=12242, leads=5, target=0
    # CTR=475/48704=0.98%, CPC=12242/475=26, conv=5/475=1.05%, CPA=12242/5=2448
    ["e-20010227",48704,475,"0,98%","р.26",5,"1,05%","р.2 448",0,"-","-","р.12 242"],
    # campaigns e-20010227
    ["МК ТК // Ремонт // remont.dune-group.ru",46666,387,"0,83%","р.32",5,"1,29%","р.2 448",0,"-","-","р.12 242"],
    ["Поиск // строительство (конкуренты)",71,1,"1,41%","р.0",0,"0,00%","-",0,"-","-","р.0"],
    ["РСЯ // типовой ремонт // Синяя кухня",142,3,"2,11%","р.0",0,"0,00%","-",0,"-","-","р.0"],
    ["Поиск/РСЯ Главная // Март // CPA ЦЕЛЬ",731,35,"4,79%","р.0",0,"0,00%","-",0,"-","-","р.0"],
    ["Поиск/РСЯ доп.домен // Март // CPA ЦЕЛЬ",607,35,"5,77%","р.0",0,"0,00%","-",0,"-","-","р.0"],
    ["Поиск/РСЯ Главная // Март // CPA ЦЕЛЬ (копия)",487,14,"2,87%","р.0",0,"0,00%","-",0,"-","-","р.0"],
    # e-17228851: impressions=68377, clicks=110, spend=0, leads=0, target=0
    ["Яндекс Директ e-17228851",68377,110,"0,16%","р.0",0,"0,00%","р.0",0,"-","р.0","р.0"],
    # campaigns e-17228851
    ["ЕПК // Ремонт // ФЦ remont.dune-group.ru",66010,75,"0,11%","р.0",0,"0,00%","р.0",0,"-","р.0","р.0"],
    ["МК // Строительство // CPA->в платку",283,19,"6,71%","р.0",0,"0,00%","-",0,"-","-","р.0"],
    ["МК // Строительство // CPA",529,12,"2,27%","р.0",0,"0,00%","-",0,"-","-","р.0"],
    ["РСЯ // типовой ремонт // Синяя кухня с текстом и кухней",1555,4,"0,26%","р.0",0,"0,00%","р.0",0,"-","р.0","р.0"],
    # dune-group: impressions=8095, clicks=216, spend=244, leads=0, target=0
    ["dune-group",8095,216,"2,67%","р.1",0,"0,00%","р.0",0,"-","р.0","р.244"],
    # campaigns dune-group
    ["ЕПК РСЯ Риелторы (сегмент)",5945,172,"2,89%","р.1",0,"0,00%","р.0",0,"-","р.0","р.244"],
    ["ЕПК РСЯ Риелторы (сегмент+)",2150,44,"2,05%","р.0",0,"0,00%","р.0",0,"-","р.0","р.0"],
    # porg-3uieikjn: impressions=5525, clicks=121, spend=0, leads=0, target=0
    ["porg-3uieikjn",5525,121,"2,19%","р.0",0,"0,00%","-",0,"-","-","р.0"],
    # campaigns porg
    ["МК // Строительство // CPA (Ф+ТГ)",1149,61,"5,31%","р.0",0,"0,00%","-",0,"-","-","р.0"],
    ["МК // Строительство // CPA (Ф)",4376,60,"1,37%","р.0",0,"0,00%","-",0,"-","-","р.0"],
    # empty
    [],
    [],
    # SEO: search_engine_visits=39
    ["SEO","",39,"","",0,"0,00%","",0,"","",""],
    # Рекомендации
    ["Рекомендации","","","","",0,"","",0,"","",""],
]

BOLD_ROWS = [0, 3, 4, 5, 6, 13, 18, 21, 26, 27]


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
