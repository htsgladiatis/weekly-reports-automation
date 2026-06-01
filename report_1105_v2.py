"""
Weekly report for 11.05-17.05.2026 (updated e-17228851 data)
"""

from google.oauth2 import service_account
from googleapiclient.discovery import build

SPREADSHEET_ID = "1TMa7NMknshntaQE-Dgmr-Trjk3pQxvY_K1IyAYfjZ4A"
CREDENTIALS_FILE = "credentials.json"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

TAB_NAME = "11.05-17.05"

# Totals:
# impressions: 68900+84570+2933+4583 = 160986
# clicks: 1230+120+73+108 = 1531
# spend: 20204
# leads: 10 (9 e-20010227 + 1 e-17228851)
# target: 6 (5 e-20010227 + 1 e-17228851)
# CTR: 1531/160986*100 = 0.95%
# CPC: 20204/1531 = 13
# conv lead: 10/1531*100 = 0.65%
# CPA: 20204/10 = 2020
# conv target: 6/10*100 = 60.00%
# CPL: 20204/6 = 3367

ROWS = [
    ["11.05.2026–17.05.2026"],
    [],
    [],
    ["Канал","Показы","Визиты","CTR","CPC","Лиды","Конверсия в Лид","CPA","Ц. Лиды","Конверсия в Ц. Лид","CPL","Расход"],
    # summary
    ["","","","","",10,"","р.2 020",6,"","р.3 367","р.20 204"],
    # Яндекс Директ total
    ["Яндекс Директ",160986,1531,"0,95%","р.13",10,"0,65%","р.2 020",6,"60,00%","р.3 367","р.20 204"],
    # e-20010227: 68900 impressions, 1230 clicks, 20204 spend, 9 leads, 5 target
    # CTR=1230/68900=1.79%, CPC=20204/1230=16, conv=9/1230=0.73%, CPA=20204/9=2245, conv_t=5/9=55.56%, CPL=20204/5=4041
    ["e-20010227",68900,1230,"1,79%","р.16",9,"0,73%","р.2 245",5,"55,56%","р.4 041","р.20 204"],
    # campaigns e-20010227
    ["МК ТК // Ремонт // remont.dune-group.ru",63832,1057,"1,66%","р.19",9,"0,85%","р.2 245",5,"55,56%","р.4 041","р.20 204"],
    ["Поиск // строительство (конкуренты)",100,0,"0,00%","р.0",0,"-","-",0,"-","-","р.0"],
    ["РСЯ // типовой ремонт // Синяя кухня",760,28,"3,68%","р.0",0,"0,00%","-",0,"-","-","р.0"],
    ["Поиск/РСЯ Главная // Март // CPA ЦЕЛЬ",1057,51,"4,82%","р.0",0,"0,00%","-",0,"-","-","р.0"],
    ["Поиск/РСЯ доп.домен // Март // CPA ЦЕЛЬ",1618,54,"3,34%","р.0",0,"0,00%","-",0,"-","-","р.0"],
    ["Поиск/РСЯ Главная // Март // CPA ЦЕЛЬ (копия)",1533,40,"2,61%","р.0",0,"0,00%","-",0,"-","-","р.0"],
    # e-17228851: 84570 impressions, 120 clicks, 0 spend, 1 lead, 1 target
    # CTR=120/84570=0.14%, CPC=0, conv=1/120=0.83%, CPA=0, conv_t=1/1=100%, CPL=0
    ["Яндекс Директ e-17228851",84570,120,"0,14%","р.0",1,"0,83%","р.0",1,"100,00%","р.0","р.0"],
    # campaigns e-17228851
    ["ЕПК // Ремонт // ФЦ remont.dune-group.ru",80476,62,"0,08%","р.0",0,"0,00%","р.0",0,"-","р.0","р.0"],
    ["МК // Строительство // CPA->в платку",434,30,"6,91%","р.0",0,"0,00%","-",0,"-","-","р.0"],
    ["МК // Строительство // CPA",706,24,"3,40%","р.0",0,"0,00%","-",0,"-","-","р.0"],
    ["РСЯ // типовой ремонт // Синяя кухня с текстом и кухней",2954,4,"0,14%","р.0",0,"0,00%","р.0",0,"-","р.0","р.0"],
    # dune-group: 2933 impressions, 73 clicks, 0 spend, 0 leads, 0 target
    ["dune-group",2933,73,"2,49%","р.0",0,"0,00%","р.0",0,"-","р.0","р.0"],
    # campaigns dune-group
    ["ЕПК РСЯ Риелторы (сегмент)",415,26,"6,27%","р.0",0,"0,00%","р.0",0,"-","р.0","р.0"],
    ["ЕПК РСЯ Риелторы (сегмент+)",2518,47,"1,87%","р.0",0,"0,00%","р.0",0,"-","р.0","р.0"],
    # porg-3uieikjn: 4583 impressions, 108 clicks, 0 spend, 0 leads, 0 target
    ["porg-3uieikjn",4583,108,"2,36%","р.0",0,"0,00%","-",0,"-","-","р.0"],
    # campaigns porg
    ["МК // Строительство // CPA (Ф+ТГ)",1566,57,"3,64%","р.0",0,"0,00%","-",0,"-","-","р.0"],
    ["МК // Строительство // CPA (Ф)",3017,51,"1,69%","р.0",0,"0,00%","-",0,"-","-","р.0"],
    # empty
    [],
    [],
    # SEO: 35 visits from search
    ["SEO","",35,"","",0,"0,00%","",0,"","",""],
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
