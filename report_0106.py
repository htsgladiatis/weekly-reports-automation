"""
Weekly report for 01.06-07.06.2026
"""

from google.oauth2 import service_account
from googleapiclient.discovery import build

SPREADSHEET_ID = "1TMa7NMknshntaQE-Dgmr-Trjk3pQxvY_K1IyAYfjZ4A"
CREDENTIALS_FILE = "credentials.json"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

TAB_NAME = "01.06-07.06"

# Данные Директ из файлов xlsx_aggregated.txt:
# e-20010227: 49416 imp, 805 clicks, 27564 spend
# e-17228851: 58292 imp, 465 clicks, 0 spend (файлы показывают 0 расхода)
# dune-group: 4707 imp, 151 clicks, 0 spend
# porg-3uieikjn: 5931 imp, 120 clicks, 0 spend

# ВАЖНО: У e-17228851 в "простом" файле был расход 58292, но в "Новый" файле 0
# Проверим данные из index.html: w5 показывает spend: 96494 total
# e-20010227: 27564, e-17228851: 58292, dune-group: 4707, porg-3uieikjn: 5931
# 27564 + 58292 + 4707 + 5931 = 96494 ✓

# Totals Директ:
# impressions: 49416+58292+4707+5931 = 118346
# clicks: 805+465+151+120 = 1541
# spend: 27564+58292+4707+5931 = 96494
# leads from Директ: 16 (все e-20010227, включая Билайн АТС звонки)
# target from Директ: 7 (Никита, Николай, Константин, Антон, Анастасия, Вероника, Андрей)
# CTR: 1541/118346=1.30%, CPC: 96494/1541=63, conv: 16/1541=1.04%, CPA: 96494/16=6031
# conv_target: 7/16=43.75%, CPL: 96494/7=13785

# Total all channels:
# leads: 16(Директ)+0(SEO)+0(Рек) = 16
# target: 7(Директ)+0(SEO)+0(Рек) = 7
# CPA total: 96494/16=6031, CPL total: 96494/7=13785

ROWS = [
    ["01.06.2026–07.06.2026"],
    [],
    [],
    ["Канал","Показы","Визиты","CTR","CPC","Лиды","Конверсия в Лид","CPA","Ц. Лиды","Конверсия в Ц. Лид","CPL","Расход"],
    # summary: total leads=16, target=7
    # CPA=96494/16=6031, CPL=96494/7=13785
    ["","","","","",16,"","р.6 031",7,"","р.13 785","р.96 494"],
    # Яндекс Директ total
    # leads=16, target=7
    # CTR=1541/118346=1.30%, CPC=96494/1541=63, conv=16/1541=1.04%, CPA=96494/16=6031, conv_t=7/16=43.75%, CPL=96494/7=13785
    ["Яндекс Директ",118346,1541,"1,30%","р.63",16,"1,04%","р.6 031",7,"43,75%","р.13 785","р.96 494"],
    # e-20010227: 49416 imp, 805 clicks, 27564 spend, 16 leads, 7 target
    # CTR=805/49416=1.63%, CPC=27564/805=34, conv=16/805=1.99%, CPA=27564/16=1723, conv_t=7/16=43.75%, CPL=27564/7=3938
    ["e-20010227",49416,805,"1,63%","р.34",16,"1,99%","р.1 723",7,"43,75%","р.3 938","р.27 564"],
    # campaigns e-20010227
    ["МК ТК // Ремонт // remont.dune-group.ru",44753,642,"1,43%","р.43",16,"2,49%","р.1 723",7,"43,75%","р.3 938","р.27 564"],
    ["Поиск/РСЯ Главная // Март// CPA ЦЕЛЬ",1987,64,"3,22%","р.0",0,"0,00%","-",0,"-","-","р.0"],
    ["Поиск/РСЯ Главная // Март// CPA ЦЕЛЬ (копия)",946,37,"3,91%","р.0",0,"0,00%","-",0,"-","-","р.0"],
    ["Поиск/РСЯ доп.домен// Март// CPA ЦЕЛЬ",1573,58,"3,69%","р.0",0,"0,00%","-",0,"-","-","р.0"],
    ["РСЯ// типовой ремонт // Синяя кухня",157,4,"2,55%","р.0",0,"0,00%","-",0,"-","-","р.0"],
    # e-17228851: 58292 imp, 465 clicks, 58292 spend, 0 leads from Директ, 0 target
    # CTR=465/58292=0.80%, CPC=58292/465=125, conv=0
    ["Яндекс Директ e-17228851",58292,465,"0,80%","р.125",0,"0,00%","-",0,"-","-","р.58 292"],
    # campaigns e-17228851
    ["ЕПК // Ремонт //ФЦ remont.dune-group.ru",27639,17,"0,06%","р.0",0,"0,00%","-",0,"-","-","р.0"],
    ["МК // Строительство // СРА",117,1,"0,85%","р.0",0,"0,00%","-",0,"-","-","р.0"],
    ["МК // Строительство // СРА->в платку",6570,312,"4,75%","р.187",0,"0,00%","-",0,"-","-","р.58 292"],
    ["МК Товарная - Услуга дизайна",3313,76,"2,29%","р.0",0,"0,00%","-",0,"-","-","р.0"],
    ["МК Товарная кампания Ремонт",230,6,"2,61%","р.0",0,"0,00%","-",0,"-","-","р.0"],
    ["РСЯ// типовой ремонт // Синяя кухня с текстом и кухней",19713,21,"0,11%","р.0",0,"0,00%","-",0,"-","-","р.0"],
    ["Товарная кампания ремонт старая",710,32,"4,51%","р.0",0,"0,00%","-",0,"-","-","р.0"],
    # dune-group: 4707 imp, 151 clicks, 4707 spend, 0 leads, 0 target
    # CTR=151/4707=3.21%, CPC=4707/151=31, conv=0
    ["dune-group",4707,151,"3,21%","р.31",0,"0,00%","-",0,"-","-","р.4 707"],
    # campaigns dune-group
    ["ЕПК РСЯ Риелторы (сегмент)",1157,22,"1,90%","р.0",0,"0,00%","-",0,"-","-","р.0"],
    ["ЕПК РСЯ Риелторы (сегмент+)",3550,129,"3,63%","р.31",0,"0,00%","-",0,"-","-","р.4 707"],
    # porg-3uieikjn: 5931 imp, 120 clicks, 5931 spend, 0 leads, 0 target
    # CTR=120/5931=2.02%, CPC=5931/120=49, conv=0
    ["porg-3uieikjn",5931,120,"2,02%","р.49",0,"0,00%","-",0,"-","-","р.5 931"],
    # campaigns porg
    ["МК // Строительство // СРА (Ф)",4623,59,"1,28%","р.0",0,"0,00%","-",0,"-","-","р.0"],
    ["МК // Строительство // СРА (Ф+ТГ)",1308,61,"4,66%","р.49",0,"0,00%","-",0,"-","-","р.5 931"],
    # empty
    [],
    [],
    # SEO: 54 visits (из Метрики), 0 target leads
    ["SEO","",54,"","",0,"","",0,"","",""],
    # Рекомендации: 0
    ["Рекомендации","","","","",0,"","",0,"","",""],
]

BOLD_ROWS = [0, 3, 4, 5, 6, 13, 22, 25, 28, 31, 32]


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
