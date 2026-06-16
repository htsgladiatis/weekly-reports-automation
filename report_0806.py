"""
Weekly report for 08.06-14.06.2026
"""

from google.oauth2 import service_account
from googleapiclient.discovery import build

SPREADSHEET_ID = "1TMa7NMknshntaQE-Dgmr-Trjk3pQxvY_K1IyAYfjZ4A"
CREDENTIALS_FILE = "credentials.json"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

TAB_NAME = "08.06-14.06"

# Данные Директ из скриншотов:
# e-20010227: 53240 imp, 542 clicks, 27820 spend, 7 conversions
# e-17228851: 67615 imp, 81 clicks, 2074 spend, 1 conversion
# dune-group: 0 imp, 0 clicks, 0 spend, 0 conversions
# porg-3uieikjn: 185 imp, 7 clicks, 0 spend, 0 conversions

# Totals Директ:
# impressions: 53240+67615+0+185 = 121040
# clicks: 542+81+0+7 = 630
# spend: 27820+2074+0+0 = 29894
# leads from Директ: 11 (все e-20010227)
# target from Директ: 2 (Альбина, Владимир)
# CTR: 630/121040=0.52%, CPC: 29894/630=47, conv: 11/630=1.75%, CPA: 29894/11=2718
# conv_target: 2/11=18.18%, CPL: 29894/2=14947

# SEO:
# visits: 72 (из Метрики - переходы из поисковых систем)
# leads: 2 (Лейсан + 1 необработанная заявка)
# target: 1 (Лейсан)

# Total all channels:
# leads: 11(Директ)+2(SEO)+15(Другие) = 28
# target: 2(Директ)+1(SEO)+0(Другие) = 3
# CPA total: 29894/28=1068, CPL total: 29894/3=9965

ROWS = [
    ["08.06.2026–14.06.2026"],
    [],
    [],
    ["Канал","Показы","Визиты","CTR","CPC","Лиды","Конверсия в Лид","CPA","Ц. Лиды","Конверсия в Ц. Лид","CPL","Расход"],
    # summary: total leads=28, target=3
    # CPA=29894/28=1068, CPL=29894/3=9965
    ["","","","","",28,"","р.1 068",3,"","р.9 965","р.29 894"],
    # Яндекс Директ total
    # leads=11, target=2
    # CTR=630/121040=0.52%, CPC=29894/630=47, conv=11/630=1.75%, CPA=29894/11=2718, conv_t=2/11=18.18%, CPL=29894/2=14947
    ["Яндекс Директ",121040,630,"0,52%","р.47",11,"1,75%","р.2 718",2,"18,18%","р.14 947","р.29 894"],
    # e-20010227: 53240 imp, 542 clicks, 27820 spend, 11 leads, 2 target
    # CTR=542/53240=1.02%, CPC=27820/542=51, conv=11/542=2.03%, CPA=27820/11=2529, conv_t=2/11=18.18%, CPL=27820/2=13910
    ["e-20010227",53240,542,"1,02%","р.51",11,"2,03%","р.2 529",2,"18,18%","р.13 910","р.27 820"],
    # campaigns e-20010227 - все лиды идут на основную кампанию
    ["МК ТК // Ремонт // remont.dune-group.ru",50382,470,"0,93%","р.59",11,"2,34%","р.2 529",2,"18,18%","р.13 910","р.27 820"],
    ["РСЯ// типовой ремонт // Синяя кухня",15,1,"6,67%","р.0",0,"0,00%","-",0,"-","-","р.0"],
    ["Поиск/РСЯ Главная // Март// CPA ЦЕЛЬ",387,12,"3,10%","р.0",0,"0,00%","-",0,"-","-","р.0"],
    ["Поиск/РСЯ доп.домен// Март// CPA ЦЕЛЬ",563,5,"0,89%","р.0",0,"0,00%","-",0,"-","-","р.0"],
    ["Поиск/РСЯ Главная // Март// CPA ЦЕЛЬ (копия)",1893,54,"2,85%","р.0",0,"0,00%","-",0,"-","-","р.0"],
    # e-17228851: 67615 imp, 81 clicks, 2074 spend, 0 leads from Директ, 0 target
    # CTR=81/67615=0.12%, CPC=2074/81=26, conv=0
    ["Яндекс Директ e-17228851",67615,81,"0,12%","р.26",0,"0,00%","р.0",0,"-","р.0","р.2 074"],
    # campaigns e-17228851
    ["МК Товарная - Мутуа дизайна",1051,15,"1,43%","р.138",0,"0,00%","р.0",0,"-","р.0","р.2 074"],
    ["МК Товарная кампания ремонт",3202,27,"2,25%","р.0",0,"0,00%","р.0",0,"-","р.0","р.0"],
    ["Товарная кампания ремонт старая",544,9,"1,65%","р.0",0,"0,00%","р.0",0,"-","р.0","р.0"],
    ["МК // Строительство // СРА",295,1,"1,67%","р.0",0,"0,00%","р.0",0,"-","р.0","р.0"],
    ["МК // Строительство // СРА -за платку",7,1,"14,29%","р.0",0,"0,00%","р.0",0,"-","р.0","р.0"],
    ["РСЯ// типовой ремонт // Синяя кухня с тапсом и кухой",33030,5,"0,02%","р.0",0,"0,00%","р.0",0,"-","р.0","р.0"],
    ["ЕПК // Ремонт //ФЦ remont.dune-group.ru",31726,20,"0,06%","р.0",0,"0,00%","р.0",0,"-","р.0","р.0"],
    # dune-group: 0 imp, 0 clicks, 0 spend, 0 leads, 0 target
    ["dune-group",0,0,"0,00%","р.0",0,"-","р.0",0,"-","р.0","р.0"],
    # campaigns dune-group - все с нулями
    ["ЕПК РСЯ Риелторы - Яндекс.Услуги",0,0,"0,00%","р.0",0,"-","р.0",0,"-","р.0","р.0"],
    ["ЕПК РСЯ Риелторы (сегмент)",0,0,"0,00%","р.0",0,"-","р.0",0,"-","р.0","р.0"],
    ["ЕПК РСЯ Риелторы (сегмент+)",0,0,"0,00%","р.0",0,"-","р.0",0,"-","р.0","р.0"],
    ["ЕПК Retra-set",0,0,"0,00%","р.0",0,"-","р.0",0,"-","р.0","р.0"],
    # porg-3uieikjn: 185 imp, 7 clicks, 0 spend, 0 leads, 0 target
    ["porg-3uieikjn",185,7,"3,78%","р.0",0,"0,00%","-",0,"-","-","р.0"],
    # campaigns porg
    ["МК // Строительство // СРА (Ф+ТГ)",156,7,"4,43%","р.0",0,"0,00%","-",0,"-","-","р.0"],
    ["МК // Строительство // СРА (Ф)",29,0,"0,00%","р.0",0,"-","-",0,"-","-","р.0"],
    # empty
    [],
    [],
    # SEO: 72 visits (из Метрики - переходы из поисковых систем), 2 leads, 1 target
    # conv=2/72=2.78%, conv_target=1/2=50%
    ["SEO","",72,"","",2,"2,78%","",1,"50,00%","",""],
    # Рекомендации: 0
    ["Рекомендации","","","","",0,"","",0,"","",""],
]

BOLD_ROWS = [0, 3, 4, 5, 6, 13, 21, 26, 29, 32, 33]


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
