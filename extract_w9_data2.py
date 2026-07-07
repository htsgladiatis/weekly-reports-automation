"""Extract W9 leads data with better HTML parser"""
import re
from pathlib import Path

with open("05.07/LEAD_20260706_6454f36c_6a4bdebd6ed11.xls", "r", encoding="utf-8") as f:
    html_content = f.read()

print(f"Total HTML length: {len(html_content)} chars")
print(f"\nHas tbody tag: {'<tbody>' in html_content}")
print(f"Has table tag: {'<table' in html_content}")
print(f"Number of <tr> tags: {len(re.findall(r'<tr', html_content))}")

# Try BeautifulSoup first - more reliable
try:
    from bs4 import BeautifulSoup
    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False

if HAS_BS4:
    soup = BeautifulSoup(html_content, "html.parser")
    table = soup.find("table")
    if not table:
        print("BS4: no table found")
    else:
        # Headers
        thead = table.find("thead")
        headers = []
        if thead:
            for th in thead.find_all("th"):
                headers.append(th.get_text(strip=True))
        print(f"\nBS4 Headers: {headers}")

        # Body rows
        rows = []
        tbody = table.find("tbody")
        if tbody:
            for tr in tbody.find_all("tr"):
                row = []
                for cell in tr.find_all("td"):
                    row.append(cell.get_text(strip=True))
                rows.append(row)

        print(f"\nBS4 Total rows: {len(rows)}")
        print(f"\n=== FIRST 50 LEADS (BS4) ===")
        for i, row in enumerate(rows[:50]):
            print(f"  {i:3d}: {row}")

        print(f"\n=== LAST 5 LEADS (BS4) ===")
        for i, row in enumerate(rows[-5:]):
            print(f"  {len(rows)-5+i:3d}: {row}")

        # === CLASSIFICATION ===
        print("\n" + "=" * 70)
        print("LEAD CLASSIFICATION BY SOURCE & STAGE")
        print("=" * 70)

        # Find column indexes
        col_idx = {}
        if headers:
            for i, h in enumerate(headers):
                col_idx[h] = i

        print(f"Column indexes: {col_idx}")

        # Count by source
        src_count = {}
        stage_count = {}
        src_stage = {}
        for row in rows:
            if len(row) < len(headers):
                continue
            src = row[col_idx.get("Источник", 3)] if "Источник" in col_idx else (
                row[col_idx.get("Source", 3)] if "Source" in col_idx else ""
            )
            stage = row[col_idx.get("Стадия", 1)] if "Стадия" in col_idx else (
                row[col_idx.get("Stage", 1)] if "Stage" in col_idx else ""
            )
            src_count[src] = src_count.get(src, 0) + 1
            stage_count[stage] = stage_count.get(stage, 0) + 1
            key = f"{src} | {stage}"
            src_stage[key] = src_stage.get(key, 0) + 1

        print(f"\nTotal leads: {len(rows)}")
        print(f"\nBy Source:")
        for k, v in sorted(src_count.items(), key=lambda x: -x[1]):
            print(f"  {k}: {v}")
        print(f"\nBy Stage:")
        for k, v in sorted(stage_count.items(), key=lambda x: -x[1]):
            print(f"  {k}: {v}")
        print(f"\nBy Source × Stage:")
        for k, v in sorted(src_stage.items(), key=lambda x: -x[1]):
            print(f"  {k}: {v}")

        # Target leads
        target_word = "Целевой лид"
        is_target = lambda stage: target_word.lower() in stage.lower() if stage else False

        # Direct leads (Yandex Direct) - marquiz attribution = e-20010227
        targets_per_source = {}
        for row in rows:
            if len(row) < len(headers):
                continue
            src = row[col_idx.get("Источник", 3)] if "Источник" in col_idx else ""
            stage = row[col_idx.get("Стадия", 1)] if "Стадия" in col_idx else ""
            if is_target(stage):
                targets_per_source[src] = targets_per_source.get(src, 0) + 1

        print(f"\n=== TARGET LEADS BY SOURCE ===")
        for k, v in sorted(targets_per_source.items(), key=lambda x: -x[1]):
            print(f"  {k}: {v}")

        # Detail attribution for Direct leads
        print(f"\n=== ATTRIBUTION DETAILS (Direct) ===")
        for i, row in enumerate(rows):
            if len(row) < len(headers):
                continue
            src = row[col_idx.get("Источник", 3)] if "Источник" in col_idx else ""
            stage = row[col_idx.get("Стадия", 1)] if "Стадия" in col_idx else ""
            name_val = row[col_idx.get("Название лида", 0)] if "Название лида" in col_idx else ""
            date_val = row[col_idx.get("Дата создания", 2)] if "Дата создания" in col_idx else ""

            if "Директ" in src or "директ" in src:
                marker = "[ЦЕЛЕВОЙ]" if is_target(stage) else f"[{stage[:15] if stage else 'обычный'}]"
                print(f"  {marker} {date_val} | {src[:30]:30s} | {name_val[:50]}")

else:
    # Regex fallback
    print("\nBS4 not available, using regex")
    # Find all <tr>...</tr> blocks
    row_pattern = re.compile(r"<tr[^>]*>(.*?)</tr>", re.DOTALL)
    cell_pattern = re.compile(r"<t[dh][^>]*>(.*?)</t[dh]>", re.DOTALL)
    rows = []
    for m in row_pattern.finditer(html_content):
        cells = [cell_pattern.search(c).group(1).strip() if cell_pattern.search(c) else ""
                 for c in re.findall(r"<t[dh][^>]*>.*?</t[dh]>", m.group(1), re.DOTALL)]
        rows.append(cells)
    print(f"Found {len(rows)} rows (regex)")
    for i, row in enumerate(rows[:50]):
        print(f"  {i:3d}: {row}")
