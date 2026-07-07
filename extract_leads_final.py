"""Clean W9 leads extractor - fixed"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import re
from pathlib import Path
from bs4 import BeautifulSoup

with open("05.07/LEAD_20260706_6454f36c_6a4bdebd6ed11.xls", "r", encoding="utf-8") as f:
    html_content = f.read()

soup = BeautifulSoup(html_content, "html.parser")
table = soup.find("table")

# Headers
headers = []
thead = table.find("thead")
if thead:
    for th in thead.find_all("th"):
        headers.append(th.get_text(strip=True))

# Rows
rows = []
tbody = table.find("tbody")
if tbody:
    for tr in tbody.find_all("tr"):
        row = []
        for cell in tr.find_all("td"):
            row.append(cell.get_text(strip=True))
        rows.append(row)

print(f"Headers: {headers}")
print(f"Total rows: {len(rows)}")

# Show ALL leads
print("\n=== ALL LEADS ===")
for i, row in enumerate(rows):
    print(f"{i:3d}: {row}")

# Build column dict
col_idx = {h: i for i, h in enumerate(headers)}
print(f"\nCol indexes: {col_idx}")

# Stats by source
print("\n=== STATS BY SOURCE ===")
src_count = {}
stage_count = {}
src_stage = {}
for row in rows:
    src = row[col_idx.get("Источник", -1)] if "Источник" in col_idx else ""
    extra = row[col_idx.get("Дополнительно об источнике", -1)] if "Дополнительно об источнике" in col_idx else ""
    combined_src = f"{src} | {extra}" if extra else src
    stage = row[col_idx.get("Стадия", -1)] if "Стадия" in col_idx else ""
    src_count[combined_src] = src_count.get(combined_src, 0) + 1
    stage_count[stage] = stage_count.get(stage, 0) + 1
    key = f"{combined_src} | {stage}"
    src_stage[key] = src_stage.get(key, 0) + 1

print("\nBy Source:")
for k, v in sorted(src_count.items(), key=lambda x: -x[1]):
    print(f"  '{k}': {v}")
print("\nBy Stage:")
for k, v in sorted(stage_count.items(), key=lambda x: -x[1]):
    print(f"  '{k}': {v}")

print("\nBy Source x Stage:")
for k, v in sorted(src_stage.items(), key=lambda x: -x[1]):
    print(f"  '{k}': {v}")

# Target leads only
target_count = 0
target_per_channel = {}
print("\n=== TARGET LEADS (Целевой лид) ===")
for i, row in enumerate(rows):
    stage = row[col_idx.get("Стадия", -1)] if "Стадия" in col_idx else ""
    src = row[col_idx.get("Источник", -1)] if "Источник" in col_idx else ""
    extra = row[col_idx.get("Дополнительно об источнике", -1)] if "Дополнительно об источнике" in col_idx else ""
    name = row[col_idx.get("Название лида", -1)] if "Название лида" in col_idx else ""
    date = row[col_idx.get("Дата создания", -1)] if "Дата создания" in col_idx else ""
    if "Целевой лид" == stage:
        target_count += 1
        print(f"  [TARGET] {date} | {src} | {extra} | {name}")
        # attribute to channel
        if "Директ" in src:
            target_per_channel["Direct"] = target_per_channel.get("Direct", 0) + 1
            if "marquiz" in extra.lower():
                target_per_channel["Direct-e-20010227"] = target_per_channel.get("Direct-e-20010227", 0) + 1
        elif "СЕО" in src or "SEO" in src:
            target_per_channel["SEO"] = target_per_channel.get("SEO", 0) + 1
        else:
            target_per_channel["Other"] = target_per_channel.get("Other", 0) + 1

print(f"\n=== TARGET TOTAL: {target_count} ===")
for k, v in target_per_channel.items():
    print(f"  {k}: {v}")

# ALL leads attribution (include all, not just target)
print("\n=== ALL LEADS ATTRIBUTION ===")
all_per_channel = {}
for i, row in enumerate(rows):
    src = row[col_idx.get("Источник", -1)] if "Источник" in col_idx else ""
    extra = row[col_idx.get("Дополнительно об источнике", -1)] if "Дополнительно об источнике" in col_idx else ""
    if "Директ" in src:
        all_per_channel["Direct"] = all_per_channel.get("Direct", 0) + 1
        if "marquiz" in extra.lower():
            all_per_channel["Direct-e-20010227"] = all_per_channel.get("Direct-e-20010227", 0) + 1
    elif "СЕО" in src or "SEO" in src:
        all_per_channel["SEO"] = all_per_channel.get("SEO", 0) + 1
    else:
        all_per_channel["Other"] = all_per_channel.get("Other", 0) + 1

for k, v in all_per_channel.items():
    print(f"  {k}: {v}")
