"""
Получение данных из Битрикс24 и Яндекс.Метрика для отчёта 01.06-07.06.
Вывод в файл result_data.txt (UTF-8).
"""
import json, sys, os
sys.path.insert(0, os.path.dirname(__file__))

out = open("result_data.txt", "w", encoding="utf-8")

def p(*args, **kwargs):
    print(*args, **kwargs)
    kwargs2 = {k: v for k, v in kwargs.items() if k != "file"}
    print(*args, file=out, **kwargs2)

# --- Битрикс ---------------------------------------------------------------
from bitrix import get_lead_stats

DATE_FROM = "2026-06-01"
DATE_TO   = "2026-06-07"

p("=" * 60)
p(f"БИТРИКС: лиды {DATE_FROM} — {DATE_TO}")
p("=" * 60)

stats = get_lead_stats(DATE_FROM, DATE_TO)

p(f"\n{'Аккаунт':<20} {'Лиды':>6} {'Ц.Лиды':>8}")
p("-" * 40)
for acc in ["e-20010227", "e-17228851", "dune-group", "porg-3uieikjn"]:
    a = stats["accounts"].get(acc, {"leads": 0, "target": 0})
    p(f"{acc:<20} {a['leads']:>6} {a['target']:>8}")
p("-" * 40)
p(f"{'ИТОГО':<20} {stats['total']['leads']:>6} {stats['total']['target']:>8}")

p("\nДетализация:")
for d in stats["details"]:
    flag = "[ЦЕЛЕВОЙ]" if d["is_target"] else "[обычный]"
    p(f"  {flag}  [{d['ID']}] {d['date'][:10]}  {d['account']:<14} "
      f"stage={d['stage']:<14} src={d['source']}/{d['source_description']}  {d['TITLE']}")

# --- Яндекс.Метрика --------------------------------------------------------
import urllib.request, urllib.parse

ACCESS_TOKEN = "y0__wgBEM-PhesCGM73QSCayNHIFx4hTUWtppv9M4CUxW2X8SfIBsnW"
COUNTER_ID   = "90747520"

p("\n" + "=" * 60)
p(f"МЕТРИКА: визиты {DATE_FROM} — {DATE_TO}")
p("=" * 60)

# Запрос 1: по источникам трафика
params = {
    "id": COUNTER_ID,
    "date1": DATE_FROM,
    "date2": DATE_TO,
    "metrics": "ym:s:visits",
    "dimensions": "ym:s:trafficSource",
    "limit": 100,
}
url = "https://api-metrika.yandex.net/stat/v1/data?" + urllib.parse.urlencode(params)
req = urllib.request.Request(url, headers={"Authorization": f"Bearer {ACCESS_TOKEN}"})
with urllib.request.urlopen(req, timeout=30) as resp:
    r1 = json.loads(resp.read().decode("utf-8"))

total_visits = int(r1.get("totals", [0])[0])
p(f"\nВсего визитов: {total_visits}")
p(f"\n{'Источник трафика':<40} {'Визиты':>8}")
p("-" * 50)
for row in r1.get("data", []):
    name   = row["dimensions"][0].get("name", "—")
    visits = int(row["metrics"][0])
    p(f"{name:<40} {visits:>8}")

# Запрос 2: SEO по поисковым системам
params2 = {
    "id": COUNTER_ID,
    "date1": DATE_FROM,
    "date2": DATE_TO,
    "metrics": "ym:s:visits",
    "dimensions": "ym:s:SearchEngine",
    "limit": 50,
}
url2 = "https://api-metrika.yandex.net/stat/v1/data?" + urllib.parse.urlencode(params2)
req2 = urllib.request.Request(url2, headers={"Authorization": f"Bearer {ACCESS_TOKEN}"})
with urllib.request.urlopen(req2, timeout=30) as resp2:
    r2 = json.loads(resp2.read().decode("utf-8"))

seo_total = int(r2.get("totals", [0])[0])
p(f"\nSEO (поисковые системы) — итого: {seo_total}")
p(f"{'Поисковик':<40} {'Визиты':>8}")
p("-" * 50)
for row in r2.get("data", []):
    name   = row["dimensions"][0].get("name", "—")
    visits = int(row["metrics"][0])
    p(f"{name:<40} {visits:>8}")

p(f"\n=== ИТОГ ===")
p(f"SEO визиты (из поисковиков): {seo_total}")
p(f"Всего визитов Метрика:       {total_visits}")

out.close()
print("Done — see result_data.txt")
