import csv
import collections

acc = collections.defaultdict(lambda: {"impressions": 0, "clicks": 0, "spend": 0.0})

with open("direct_2906.csv", "r", encoding="utf-8-sig", newline="") as f:
    r = csv.DictReader(f)
    for row in r:
        a = (row.get("Account") or "").strip()
        if not a:
            continue

        def to_int(x):
            s = str(x or "0").replace(" ", "")
            try:
                return int(float(s))
            except Exception:
                return 0

        def to_float(x):
            s = str(x or "0").replace(" ", "").replace(",", ".")
            try:
                return float(s)
            except Exception:
                return 0.0

        acc[a]["impressions"] += to_int(row.get("Impressions"))
        acc[a]["clicks"] += to_int(row.get("Clicks"))
        acc[a]["spend"] += to_float(row.get("Spend"))

print("accounts", len(acc))
for k, v in acc.items():
    print(k, v)

total_spend = sum(v["spend"] for v in acc.values())
total_clicks = sum(v["clicks"] for v in acc.values())
total_impressions = sum(v["impressions"] for v in acc.values())

print("totals", total_spend, total_clicks, total_impressions)
