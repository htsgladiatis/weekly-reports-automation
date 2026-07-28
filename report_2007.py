"""
Weekly report for 20.07-26.07.2026 — Week 12.
Data manually extracted from CSV exports (28.07.2026).

Sources:
  Direct (0. reports/20-26/*.csv):
    e-20010227:     1 503 imp /   35 clicks /  3 089.07 ₽ (1 campaign)
    e-17228851:    72 271 imp / 5 231 clicks / 26 828.19 ₽ (2 campaigns)
    dune-group:         0 imp /    0 clicks /      0.00 ₽
    porg-3uieikjn:    209 imp /   11 clicks /      0.00 ₽ (2 campaigns)
    TOTAL:         73 983 imp / 5 277 clicks / 29 917.26 ₽

  CRM (LEAD_20260728_*.csv):
    Total: 36 leads, 0 target
    Яндекс.Директ: 4 leads / 0 target
    Звонки/Другие: 32 leads / 0 target
    SEO: 0 leads / 0 target

  SEO (dune-group.ru_* landing pages): 47 visits
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')

from google.oauth2 import service_account
from googleapiclient.discovery import build

SPREADSHEET_ID = "1TMa7NMknshntaQE-Dgmr-Trjk3pQxvY_K1IyAYfjZ4A"
CREDENTIALS_FILE = "credentials.json"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

TAB_NAME = "20.07-26.07"

# === DIRECT TOTALS ===
DIRECT_E20010227 = {"imp": 1503, "clicks": 35, "spend": 3089.07, "leads": 4, "target": 0}
DIRECT_E17228851 = {"imp": 72271, "clicks": 5231, "spend": 26828.19, "leads": 0, "target": 0}
DIRECT_DUNE      = {"imp": 0,     "clicks": 0,   "spend": 0.00,     "leads": 0, "target": 0}
DIRECT_PORG      = {"imp": 209,   "clicks": 11,  "spend": 0.00,     "leads": 0, "target": 0}

DIRECT_TOTALS = {
    "imp":    DIRECT_E20010227["imp"]    + DIRECT_E17228851["imp"]    + DIRECT_DUNE["imp"]    + DIRECT_PORG["imp"],
    "clicks": DIRECT_E20010227["clicks"] + DIRECT_E17228851["clicks"] + DIRECT_DUNE["clicks"] + DIRECT_PORG["clicks"],
    "spend":  DIRECT_E20010227["spend"]  + DIRECT_E17228851["spend"]  + DIRECT_DUNE["spend"]  + DIRECT_PORG["spend"],
    "leads":  DIRECT_E20010227["leads"]  + DIRECT_E17228851["leads"]  + DIRECT_DUNE["leads"]  + DIRECT_PORG["leads"],
    "target": DIRECT_E20010227["target"] + DIRECT_E17228851["target"] + DIRECT_DUNE["target"] + DIRECT_PORG["target"],
}

# === CRM (Bitrix24) ===
ALL_LEADS = 36
ALL_TARGETS = 0
SEO_LEADS = 0
SEO_TARGETS = 0
OTHER_LEADS = 32
OTHER_TARGETS = 0

# === SEO ===
SEO_VISITS = 47

# === Helpers ===
def fmt_money(n):
    if n is None or n == 0 or n == "—":
        return "—"
    return f"р.{int(round(n)):,}".replace(",", " ")

def fmt_pct(n):
    if n is None or n == 0 or n == "—":
        return "—"
    return f"{n:.2f}%".replace(".", ",")

def safe_div(a, b):
    if b is None or b == 0:
        return 0
    return a / b

def row_direct_totals():
    imp = DIRECT_TOTALS["imp"]
    cl  = DIRECT_TOTALS["clicks"]
    sp  = DIRECT_TOTALS["spend"]
    ld  = DIRECT_TOTALS["leads"]
    tg  = DIRECT_TOTALS["target"]
    return [
        "Яндекс Директ",
        imp, cl,
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

def row_account(acc, label):
    imp = acc["imp"]
    cl  = acc["clicks"]
    sp  = acc["spend"]
    ld  = acc["leads"]
    tg  = acc["target"]
    return [
        f"  {label}",
        imp, cl,
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

# === Build table ===
ROWS = [
    ["20.07.2026–26.07.2026"],
    [],
    ["Канал", "Показы", "Визиты", "CTR", "CPC", "Лиды", "Конверсия в Лид", "CPA", "Ц. Лиды", "Конверсия в Ц. Лид", "CPL", "Расход"],

    # ── ИТОГО ─────────────────────────────────────
    [
        "",
        DIRECT_TOTALS["imp"], DIRECT_TOTALS["clicks"],
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

    # ── Яндекс Директ total ──────────────────────
    row_direct_totals(),

    # ── e-20010227 (1 campaign) ───────────────────
    row_account(DIRECT_E20010227, "e-20010227"),
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

    # ── e-17228851 (2 campaigns) ──────────────────
    row_account(DIRECT_E17228851, "e-17228851"),
    ["    МК // Строительство // СРА->в платку", 63260, 5193,
     fmt_pct(safe_div(5193, 63260) * 100),
     fmt_money(safe_div(24100.97, 5193)),
     0, "—", "—", 0, "—", "—", fmt_money(24100.97)],
    ["    МК // Ремонт Денис Бренд//", 9011, 38,
     fmt_pct(safe_div(38, 9011) * 100),
     fmt_money(safe_div(2727.22, 38)),
     0, "—", "—", 0, "—", "—", fmt_money(2727.22)],

    # ── dune-group (empty) ────────────────────────
    row_account(DIRECT_DUNE, "dune-group"),

    # ── porg-3uieikjn (2 campaigns) ───────────────
    row_account(DIRECT_PORG, "porg-3uieikjn"),
    ["    МК // Строительство // СРА (Ф+ТГ)", 181, 10,
     fmt_pct(safe_div(10, 181) * 100), "—",
     0, "—", "—", 0, "—", "—", "—"],
    ["    МК // Строительство // СРА (Ф)", 28, 1,
     fmt_pct(safe_div(1, 28) * 100), "—",
     0, "—", "—", 0, "—", "—", "—"],

    [],
    [],
    # ── SEO ───────────────────────────────────────
    [
        "SEO", "—", SEO_VISITS, "—", "—",
        SEO_LEADS,
        fmt_pct(safe_div(SEO_LEADS, SEO_VISITS) * 100),
        "—", SEO_TARGETS,
        fmt_pct(safe_div(SEO_TARGETS, SEO_LEADS) * 100) if SEO_LEADS > 0 else "—",
        "—", "—",
    ],

    # ── Рекомендации ──────────────────────────────
    [
        "Рекомендации", "—", "—", "—", "—",
        OTHER_LEADS, "—", "—",
        OTHER_TARGETS, "—", "—", "—",
    ],
]

BOLD_ROWS = [0, 2, 3, 4, 5, 7, 10, 11, 16, 17]

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
    # Highlight total row
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
