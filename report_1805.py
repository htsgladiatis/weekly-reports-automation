"""
Weekly report for 18.05-24.05.2026
"""

from google.oauth2 import service_account
from googleapiclient.discovery import build

SPREADSHEET_ID = "1TMa7NMknshntaQE-Dgmr-Trjk3pQxvY_K1IyAYfjZ4A"
CREDENTIALS_FILE = "credentials.json"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

TAB_NAME = "18.05-24.05"

# Totals Директ:
# impressions: 55587+97059+3491+7191 = 163328
# clicks: 1568+4032+168+159 = 5927
# spend: 19179+16665+0+0 = 35844
# leads from Директ: 12 (e-20010227)
# target from Директ: 3 (e-20010227: Ирина, Ксения, Александр)
# CTR: 5927/163328=3.63%, CPC: 35844/5927=6, conv: 12/5927=0.20%, CPA: 35844/12=2987
# conv_target: 3/12=25.00%, CPL: 35844/3=11948

# Total all channels:
# leads: 3(Директ)+1(SEO)+6(Рек/Звонки) = 10
# target: 3(Директ)+1(SEO)+6(Рек/Звонки) = 10 целевых всего
# CPA total: 35844/10=3584, CPL total: 35844/10=3584

ROWS = [
    ["18.05.2026–24.05.2026"],
    [],
    [],
    ["Канал","Показы","Визиты","CTR","CPC","Лиды","Конверсия в Лид","CPA","Ц. Лиды","Конверсия в Ц. Лид","CPL","Расход"],
    # summary: total leads=10, target=10 (3 Директ + 1 SEO + 6 Рек/Звонки)
    # CPA=35844/10=3584, CPL=35844/10=3584
    ["","","","","",10,"","р.3 584",10,"","р.3 584","р.35 844"],
    # Яндекс Директ total
    # leads=3 (Александр49, Ксения, Ирина), target=3
    # CTR=5927/163328=3.63%, CPC=35844/5927=6, conv=3/5927=0.05%, CPA=35844/3=11948, conv_t=3/3=100.00%, CPL=35844/3=11948
    ["Яндекс Директ",163328,5927,"3,63%","р.6",3,"0,05%","р.11 948",3,"100,00%","р.11 948","р.35 844"],
    # e-20010227: 55587 imp, 1568 clicks, 19179 spend, 3 leads, 3 target
    # CTR=1568/55587=2.82%, CPC=19179/1568=12, conv=3/1568=0.19%, CPA=19179/3=6393, conv_t=3/3=100.00%, CPL=19179/3=6393
    ["e-20010227",55587,1568,"2,82%","р.12",3,"0,19%","р.6 393",3,"100,00%","р.6 393","р.19 179"],
    # campaigns e-20010227
    ["МК ТК // Ремонт // remont.dune-group.ru",49731,1251,"2,57%","р.15",6,"0,48%","р.3 197",6,"100,00%","р.3 197","р.19 179"],
    ["Поиск/РСЯ Главная // Март // CPA ЦЕЛЬ",1426,112,"7,85%","р.0",0,"0,00%","-",0,"-","-","р.0"],
    ["Поиск/РСЯ доп.домен // Март // CPA ЦЕЛЬ",3361,96,"2,86%","р.0",0,"0,00%","-",0,"-","-","р.0"],
    ["РСЯ // типовой ремонт // Синяя кухня",927,69,"7,44%","р.0",0,"0,00%","-",0,"-","-","р.0"],
    ["Поиск/РСЯ Главная // Март // CPA ЦЕЛЬ (копия)",1057,40,"3,78%","р.0",0,"0,00%","-",0,"-","-","р.0"],
    ["Поиск // строительство (конкуренты)",85,0,"0,00%","р.0",0,"-","-",0,"-","-","р.0"],
    # e-17228851: 97059 imp, 4032 clicks, 16665 spend, 0 leads from Директ, 0 target
    # CTR=4032/97059=4.15%, CPC=16665/4032=4, conv=0, CPA=0
    ["Яндекс Директ e-17228851",97059,4032,"4,15%","р.4",0,"0,00%","р.0",0,"-","р.0","р.16 665"],
    # campaigns e-17228851
    ["МК // Строительство // CPA->в платку",93677,4027,"4,30%","р.4",0,"0,00%","р.0",0,"-","р.0","р.16 665"],
    ["ЕПК // Ремонт // ФЦ remont.dune-group.ru",3165,5,"0,16%","р.0",0,"0,00%","р.0",0,"-","р.0","р.0"],
    # dune-group: 3491 imp, 168 clicks, 0 spend, 0 leads, 0 target
    ["dune-group",3491,168,"4,81%","р.0",0,"0,00%","р.0",0,"-","р.0","р.0"],
    # campaigns dune-group
    ["ЕПК РСЯ Риелторы (сегмент+)",2862,147,"5,14%","р.0",0,"0,00%","р.0",0,"-","р.0","р.0"],
    ["ЕПК РСЯ Риелторы (сегмент)",629,21,"3,34%","р.0",0,"0,00%","р.0",0,"-","р.0","р.0"],
    # porg-3uieikjn: 7191 imp, 159 clicks, 0 spend, 0 leads, 0 target
    ["porg-3uieikjn",7191,159,"2,21%","р.0",0,"0,00%","-",0,"-","-","р.0"],
    # campaigns porg
    ["МК // Строительство // CPA (Ф)",5501,84,"1,53%","р.0",0,"0,00%","-",0,"-","-","р.0"],
    ["МК // Строительство // CPA (Ф+ТГ)",1690,75,"4,44%","р.0",0,"0,00%","-",0,"-","-","р.0"],
    # empty
    [],
    [],
    # SEO: 50 visits, 1 target lead (Анастасия)
    ["SEO","",50,"","",1,"","",1,"","",""],
    # Рекомендации: 4 target (Дмитрий риелтор, Елена Покидченко, Дмитрий 88м2, Николай 70м2)
    ["Рекомендации","","","","",4,"","",4,"","",""],
]

BOLD_ROWS = [0, 3, 4, 5, 6, 13, 16, 19, 24, 25]


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
