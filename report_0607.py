"""
Weekly report for 06.07-12.07.2026 (W10)
"""
from google.oauth2 import service_account
from googleapiclient.discovery import build

SPREADSHEET_ID = "1TMa7NMknshntaQE-Dgmr-Trjk3pQxvY_K1IyAYfjZ4A"
CREDENTIALS_FILE = "credentials.json"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

TAB_NAME = "06.07-12.07"

# Direct (from XLSX exports):
# e-20010227: imp=37219, clicks=454, spend=25678.60
# e-17228851: imp=22375, clicks=371, spend=10097.21
# dune-group: imp=0, clicks=0, spend=0
# porg-3uieikjn: imp=288, clicks=14, spend=0
#
# Totals Direct: imp=59882, clicks=839, spend=35775.81

# CRM (Bitrix24): leads=35, target=5
# Direct: 12 leads (5 target) — e-20010227=11, e-17228851=1 (Алена, denis-brend)
# SEO: 1 lead (0 target)
# Other: 22 leads (0 target)

# SEO (Yandex Webmaster): visits=31

# Calculations:
# CTR = 839/59882 = 1.40%
# CPC = 35776/839 = 43
# CPA_total = 35776/35 = 1022
# CPL_total = 35776/5 = 7155
# Conv→Lead = 35/839 = 4.17%
# Conv→Target = 5/35 = 14.29%

ROWS = [
    ["06.07.2026–12.07.2026"],
    [],
    [],
    ["Канал","Показы","Визиты","CTR","CPC","Лиды","Конверсия в Лид","CPA","Ц. Лиды","Конверсия в Ц. Лид","CPL","Расход"],
    # Итого: total leads=35, target=5
    # CPA=35776/35=1022, CPL=35776/5=7155
    ["","","","","",35,"","р.1 022",5,"","р.7 155","р.35 776"],
    # Яндекс Директ: leads=12, target=5
    # CTR=839/59882=1.40%, CPC=35776/839=43,
    # Conv→Lead=12/839=1.43%, CPA=35776/12=2981,
    # Conv→Target=5/12=41.67%, CPL=35776/5=7155
    ["Яндекс Директ",59882,839,"1,40%","р.43",12,"1,43%","р.2 981",5,"41,67%","р.7 155","р.35 776"],
    # e-20010227: imp=37219, clicks=454, spend=25679, leads=11, target=5
    # CTR=454/37219=1.22%, CPC=25679/454=57
    # Conv→Lead=11/454=2.42%, CPA=25679/11=2334
    # Conv→Target=5/11=45.45%, CPL=25679/5=5136
    ["e-20010227",37219,454,"1,22%","р.57",11,"2,42%","р.2 334",5,"45,45%","р.5 136","р.25 679"],
    # Campaigns e-20010227
    ["МК ТК // Ремонт // remont.dune-group.ru",37219,454,"1,22%","р.57",11,"2,42%","р.2 334",5,"45,45%","р.5 136","р.25 679"],
    # e-17228851: imp=22375, clicks=371, spend=10097, leads=1, target=0
    # CTR=371/22375=1.66%, CPC=10097/371=27
    # Conv→Lead=1/371=0.27%, CPA=10097/1=10097
    ["e-17228851",22375,371,"1,66%","р.27",1,"0,27%","р.10 097",0,"-","-","р.10 097"],
    # Campaign e-17228851
    ["МК // Ремонт Денис Бренд//",22375,371,"1,66%","р.27",1,"0,27%","р.10 097",0,"-","-","р.10 097"],
    # dune-group: imp=0, clicks=0, spend=0
    ["dune-group",0,0,"-","р.0",0,"-","-",0,"-","-","р.0"],
    # Campaign dune-group
    ["ЕПК РСЯ Риелторы (сегмент)",0,0,"-","р.0",0,"-","-",0,"-","-","р.0"],
    # porg-3uieikjn: imp=288, clicks=14, spend=0
    ["porg-3uieikjn",288,14,"4,86%","р.0",0,"0,00%","-",0,"-","-","р.0"],
    # Campaigns porg
    ["МК // Строительство // СРА (Ф+ТГ)",287,14,"4,88%","р.0",0,"0,00%","-",0,"-","-","р.0"],
    ["МК // Строительство // СРА (Ф)",1,0,"0,00%","р.0",0,"-","-",0,"-","-","р.0"],
    [],
    [],
    # SEO: 31 visits, 1 lead, 0 target
    # Conv→Lead=1/31=3.23%
    ["SEO","",31,"","",1,"3,23%","",0,"-","",""],
    # Рекомендации/Звонки: 22 leads, 0 target
    ["Рекомендации","","","","",22,"","",0,"","",""],
]

BOLD_ROWS = [0, 3, 4, 5, 6, 10, 12, 13, 15, 16, 17, 22, 23]


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
