"""
Weekly report for 29.06-05.07.2026 — Week 9.

Data sources:
  Direct (from 05.07/111/*.xlsx):
    e-20010227:     53253 imp / 425 clicks / 28104.79 ₽
    e-17228851:     45340 imp / 757 clicks /  4970.61 ₽
    dune-group:        0 imp /   0 clicks /     0.00 ₽
    porg-3uieikjn:   370 imp /  18 clicks /     0.00 ₽
    TOTAL:         98963 imp / 1200 clicks / 33075.40 ₽

  Bitrix24 (from 05.07/LEAD_20260706...xls HTML):
    Total: 35 leads
    Целевых: 10
    All Direct: 11 leads (all marquiz → e-20010227) | target = 5
    SEO: 8 leads, 4 target
    Other (Звонки/Билайн АТС): 16 leads, 1 target

  SEO (Метрика, from 05.07/111/Поисковые системы...xlsx):
    Поисковый трафик = 88 визитов
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')

from google.oauth2 import service_account
from googleapiclient.discovery import build

SPREADSHEET_ID = "1TMa7NMknshntaQE-Dgmr-Trjk3pQxvY_K1IyAYfjZ4A"
CREDENTIALS_FILE = "credentials.json"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

TAB_NAME = "29.06-05.07"

# === DIRECT TOTALS ===
DIRECT_E20010227 = {"imp": 53253, "clicks": 425, "spend": 28104.79, "leads": 11, "target": 5}
DIRECT_E17228851 = {"imp": 45340, "clicks": 757, "spend": 4970.61, "leads": 0, "target": 0}
DIRECT_DUNE      = {"imp": 0,     "clicks": 0,   "spend": 0.00,    "leads": 0, "target": 0}
DIRECT_PORG      = {"imp": 370,   "clicks": 18,  "spend": 0.00,    "leads": 0, "target": 0}

DIRECT_TOTALS = {
    "imp": DIRECT_E20010227["imp"] + DIRECT_E17228851["imp"] + DIRECT_DUNE["imp"] + DIRECT_PORG["imp"],
    "clicks": DIRECT_E20010227["clicks"] + DIRECT_E17228851["clicks"] + DIRECT_DUNE["clicks"] + DIRECT_PORG["clicks"],
    "spend": DIRECT_E20010227["spend"] + DIRECT_E17228851["spend"] + DIRECT_DUNE["spend"] + DIRECT_PORG["spend"],
    "leads": DIRECT_E20010227["leads"] + DIRECT_E17228851["leads"] + DIRECT_DUNE["leads"] + DIRECT_PORG["leads"],
    "target": DIRECT_E20010227["target"] + DIRECT_E17228851["target"] + DIRECT_DUNE["target"] + DIRECT_PORG["target"],
}

# === BITRIX24 (All leads + target) ===
ALL_LEADS = 35
ALL_TARGETS = 10
SEO_LEADS = 8
SEO_TARGETS = 4
OTHER_LEADS = 16
OTHER_TARGETS = 1

# === SEO ===
SEO_VISITS = 55

# === Helper formatting ===
def fmt_money(n):
    if n is None or n == 0 or n == "-":
        return "—"
    return f"р.{int(round(n)):,}".replace(",", " ")

def fmt_money_decimal(n):
    """Money with thousands separator"""
    return f"р.{int(round(n)):,}".replace(",", " ")

def fmt_pct(n):
    if n is None or n == 0 or n == "-":
        return "—"
    return f"{n:.2f}%".replace(".", ",")

def safe_div(a, b):
    if b is None or b == 0:
        return 0
    return a / b

def row_direct_totals():
    """Total row across all Direct accounts"""
    imp = DIRECT_TOTALS["imp"]
    cl = DIRECT_TOTALS["clicks"]
    sp = DIRECT_TOTALS["spend"]
    ld = DIRECT_TOTALS["leads"]
    tg = DIRECT_TOTALS["target"]
    return [
        "Яндекс Директ",
        imp,
        cl,
        fmt_pct(safe_div(cl, imp) * 100),
        fmt_money(safe_div(sp, cl)),
        ld,
        fmt_pct(safe_div(ld, cl) * 100),
        fmt_money(safe_div(sp, ld)),
        tg,
        fmt_pct(safe_div(tg, ld) * 100),
        fmt_money(safe_div(sp, tg)),
        fmt_money(sp),
    ]

def row_account(acc):
    """Single Direct account row"""
    imp = acc["imp"]
    cl = acc["clicks"]
    sp = acc["spend"]
    ld = acc["leads"]
    tg = acc["target"]
    return [
        f"  {acc_label(acc)}",
        imp,
        cl,
        fmt_pct(safe_div(cl, imp) * 100),
        fmt_money(safe_div(sp, cl)),
        ld,
        fmt_pct(safe_div(ld, cl) * 100),
        fmt_money(safe_div(sp, ld)),
        tg,
        fmt_pct(safe_div(tg, ld) * 100),
        fmt_money(safe_div(sp, tg)),
        fmt_money(sp),
    ]

def acc_label(d):
    if d is DIRECT_E20010227:
        return "e-20010227"
    if d is DIRECT_E17228851:
        return "e-17228851"
    if d is DIRECT_DUNE:
        return "dune-group"
    if d is DIRECT_PORG:
        return "porg-3uieikjn"
    return "?"

# === Build table ===
# 12 columns: Канал | Показы | Визиты | CTR | CPC | Лиды | Конверсия в Лид | CPA | Ц.Лиды | Конверсия в Ц.Лид | CPL | Расход

# Campaign breakdown for e-17228851 (from parser):
# МК // Ремонт Денис Бренд//: imp=19879, clicks=692, spend=4970.61
# ЕПК // Ремонт //ФЦ remont.dune-group.ru: imp=11284, clicks=4, spend=0
# МК Товарная - Услуга дизайна: imp=5653, clicks=49, spend=0
# РСЯ// типовой ремонт: imp=8234, clicks=8, spend=0
# МК // Строительство // СРА: imp=111, clicks=3, spend=0
# Товарная кампания ремонт старая: imp=154, clicks=1, spend=0
# МК Товарная кампания Ремонт: imp=21, clicks=0, spend=0
# МК // Строительство // СРА->в платку: imp=4, clicks=0, spend=0

ROWS = [
    ["29.06.2026–05.07.2026"],
    [],
    ["Канал", "Показы", "Визиты", "CTR", "CPC", "Лиды", "Конверсия в Лид", "CPA", "Ц. Лиды", "Конверсия в Ц. Лид", "CPL", "Расход"],

    # ── ИТОГО (All leads + targets, all spend) ───────────────────────
    [
        "",  # total label (empty since it's the total)
        DIRECT_TOTALS["imp"],
        DIRECT_TOTALS["clicks"],
        fmt_pct(safe_div(DIRECT_TOTALS["clicks"], DIRECT_TOTALS["imp"]) * 100),
        fmt_money(safe_div(DIRECT_TOTALS["spend"], DIRECT_TOTALS["clicks"])),
        ALL_LEADS,
        fmt_pct(safe_div(ALL_LEADS, DIRECT_TOTALS["clicks"]) * 100),
        fmt_money(safe_div(DIRECT_TOTALS["spend"], ALL_LEADS)),
        ALL_TARGETS,
        fmt_pct(safe_div(ALL_TARGETS, ALL_LEADS) * 100),
        fmt_money(safe_div(DIRECT_TOTALS["spend"], ALL_TARGETS)),
        fmt_money(DIRECT_TOTALS["spend"]),
    ],

    # ── Яндекс Директ total ──────────────────────────────────────────
    row_direct_totals(),

    # ── e-20010227 ───────────────────────────────────────────────────
    row_account(DIRECT_E20010227),
    ["    МК ТК // Ремонт // remont.dune-group.ru",
     DIRECT_E20010227["imp"], DIRECT_E20010227["clicks"],
     fmt_pct(safe_div(DIRECT_E20010227["clicks"], DIRECT_E20010227["imp"]) * 100),
     fmt_money(safe_div(DIRECT_E20010227["spend"], DIRECT_E20010227["clicks"])),
     DIRECT_E20010227["leads"],
     fmt_pct(safe_div(DIRECT_E20010227["leads"], DIRECT_E20010227["clicks"]) * 100),
     fmt_money(safe_div(DIRECT_E20010227["spend"], DIRECT_E20010227["leads"])),
     DIRECT_E20010227["target"],
     fmt_pct(safe_div(DIRECT_E20010227["target"], DIRECT_E20010227["leads"]) * 100),
     fmt_money(safe_div(DIRECT_E20010227["spend"], DIRECT_E20010227["target"])),
     fmt_money(DIRECT_E20010227["spend"])],

    # ── e-17228851 ───────────────────────────────────────────────────
    row_account(DIRECT_E17228851),
    ["    МК // Ремонт Денис Бренд//", 19879, 692,
     fmt_pct(safe_div(692, 19879) * 100),
     fmt_money(safe_div(4970.61, 692)),
     0, "—", "—", 0, "—", "—", fmt_money(4970.61)],
    ["    ЕПК // Ремонт // ФЦ remont.dune-group.ru", 11284, 4,
     fmt_pct(safe_div(4, 11284) * 100), "—",
     0, "—", "—", 0, "—", "—", "—"],
    ["    МК Товарная - Услуга дизайна", 5653, 49,
     fmt_pct(safe_div(49, 5653) * 100), "—",
     0, "—", "—", 0, "—", "—", "—"],
    ["    РСЯ // типовой ремонт // Синяя кухня", 8234, 8,
     fmt_pct(safe_div(8, 8234) * 100), "—",
     0, "—", "—", 0, "—", "—", "—"],
    ["    МК // Строительство // СРА", 111, 3,
     fmt_pct(safe_div(3, 111) * 100), "—",
     0, "—", "—", 0, "—", "—", "—"],
    ["    Товарная кампания ремонт старая", 154, 1,
     fmt_pct(safe_div(1, 154) * 100), "—",
     0, "—", "—", 0, "—", "—", "—"],

    # ── dune-group: пусто ────────────────────────────────────────────
    row_account(DIRECT_DUNE),

    # ── porg-3uieikjn ────────────────────────────────────────────────
    row_account(DIRECT_PORG),
    ["    МК // Строительство // СРА (Ф+ТГ)", 370, 18,
     fmt_pct(safe_div(18, 370) * 100), "—",
     0, "—", "—", 0, "—", "—", "—"],

    [],
    [],
    # ── SEO ──────────────────────────────────────────────────────────
    [
        "SEO",
        "—",
        SEO_VISITS,
        "—", "—", SEO_LEADS,
        fmt_pct(safe_div(SEO_LEADS, SEO_VISITS) * 100),
        "—", SEO_TARGETS,
        fmt_pct(safe_div(SEO_TARGETS, SEO_LEADS) * 100),
        "—", "—",
    ],

    # ── Рекомендации (Other / звонки / билайн) ───────────────────────
    [
        "Рекомендации",
        "—", "—", "—", "—",
        OTHER_LEADS, "—", "—",
        OTHER_TARGETS, "—", "—", "—",
    ],
]

# Bulk of bold rows (header, total, channel totals, account totals)
BOLD_ROWS = [0, 2, 3, 4, 5, 14, 23, 25]

# === Google Sheets ===
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
                "range": {"sheetId": sheet_id, "startRowIndex": row_idx, "endRowIndex": row_idx + 1,
                          "startColumnIndex": 0, "endColumnIndex": 12},
                "cell": {"userEnteredFormat": {"textFormat": {"bold": True}}},
                "fields": "userEnteredFormat.textFormat.bold"
            }
        })
    # Highlight total row (row 3 — ИТОГО)
    requests.append({
        "repeatCell": {
            "range": {"sheetId": sheet_id, "startRowIndex": 3, "endRowIndex": 4,
                      "startColumnIndex": 0, "endColumnIndex": 12},
            "cell": {"userEnteredFormat": {
                "textFormat": {"bold": True},
                "backgroundColor": {"red": 0.9, "green": 0.95, "blue": 0.9}
            }},
            "fields": "userEnteredFormat.textFormat.bold,userEnteredFormat.backgroundColor"
        }
    })
    # Column widths
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
    print(f"\nSummary:")
    print(f"  Direct: imp {DIRECT_TOTALS['imp']:,} | clicks {DIRECT_TOTALS['clicks']:,} | "
          f"spend ₽{DIRECT_TOTALS['spend']:,.2f}")
    print(f"  Leads: {ALL_LEADS} total / {ALL_TARGETS} target")
    print(f"  SEO visits: {SEO_VISITS}")
    print(f"\n✅ Done! https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}")


if __name__ == "__main__":
    main()
