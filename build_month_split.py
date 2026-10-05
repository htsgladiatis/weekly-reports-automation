"""Разбор месячной выгрузки Яндекс.Директ/CRM/Вебмастера на недельные срезы.

Использование:
    python build_month_split.py <папка> [--weeks 03.08-09.08,10.08-16.08] [--out split.json]

Что умеет:
  * Direct CSVs (5 кабинетов) — агрегация по колонке «День» с разбивкой по неделям.
  * LEAD_*.csv (CRM Bitrix) — разбивка по «Дата создания», целевые = стадия «Целевой лид».
  * Вебмастер (Path/Query) и Метрика — только общий итог за период (в выгрузке нет дат).

Правила, унаследованные из проекта:
  * Лиды недели = ВСЕ записи CRM за период (стадии НЕ исключаются).
  * Атрибуция лидов: UTM 713690254 -> porg-l2oigjze, иначе активный платный кабинет.
  * SEO-визиты = клики из файла Вебмастера по СТРАНИЦАМ (Path).
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import defaultdict
from datetime import date, datetime
from pathlib import Path

ACCOUNTS = ["e-20010227", "e-17228851", "dune-group", "porg-3uieikjn", "porg-l2oigjze"]
TARGET_STAGE = "Целевой лид"
# 713690254 — товарная кампания remont.dune-group.ru (porg-l2oigjze)
# 714208144 — remont-denis.ru (e-17228851); {campaign_id} — сломанная метка той же посадочной
UTM_TO_ACCOUNT = {
    "713690254": "porg-l2oigjze",
    "714208144": "e-17228851",
    "{campaign_id}": "e-17228851",
}


def to_num(value: str) -> float:
    """Русская/английская десятичная дробь -> float."""
    text = (value or "").replace("\xa0", "").replace(" ", "").replace(",", ".")
    if text in {"", "-", "—", "null", "None"}:
        return 0.0
    try:
        return float(text)
    except ValueError:
        return 0.0


def parse_day(value: str) -> date | None:
    text = (value or "").strip()
    if not text:
        return None
    for fmt in ("%d.%m.%Y", "%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    return None


def detect_delimiter(path: Path) -> str:
    """CRM-выгрузки используют «;», выгрузки Директа/Вебмастера — «,»."""
    with path.open(encoding="utf-8-sig", newline="") as handle:
        first_line = handle.readline()
    for candidate in (";", ",", "\t"):
        if first_line.count(candidate) > first_line.count(";" if candidate != ";" else ","):
            return candidate
    return ";"


def read_csv(path: Path, delimiter: str | None = None) -> list[dict]:
    delimiter = delimiter or detect_delimiter(path)
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return [
            {(k or "").strip(): (v or "").strip() for k, v in row.items()}
            for row in csv.DictReader(handle, delimiter=delimiter)
        ]


def classify(path: Path, rows: list[dict]) -> str:
    keys = set(rows[0]) if rows else set()
    if {"Стадия", "Дата создания"} & keys:
        return "crm"
    if "Path" in keys:
        return "seo_pages"
    if "Query" in keys:
        return "seo_queries"
    if "Источник трафика" in keys:
        return "metrika"
    if {"День", "Показы", "Клики"} <= keys:
        return "direct"
    return "unknown"


def account_from_name(path: Path) -> str | None:
    for acc in ACCOUNTS:
        if acc in path.name:
            return acc
    return None


def new_bucket() -> dict:
    return {"impressions": 0, "clicks": 0, "spend": 0.0, "conversions": 0}


def parse_direct(rows: list[dict]) -> dict:
    """Возвращает {день: {impressions, clicks, spend}} — строка «Итого» отбрасывается."""
    daily: dict[date, dict] = defaultdict(new_bucket)
    totals = new_bucket()
    for row in rows:
        day = parse_day(row.get("День", ""))
        if day is None:  # строка «Итого» или разделитель
            continue
        impressions = int(to_num(row.get("Показы")))
        clicks = int(to_num(row.get("Клики")))
        spend = to_num(row.get("Расход, ₽"))
        conversions = int(to_num(row.get("Конверсии")))

        bucket = daily[day]
        bucket["impressions"] += impressions
        bucket["clicks"] += clicks
        bucket["spend"] += spend
        bucket["conversions"] += conversions

        totals["impressions"] += impressions
        totals["clicks"] += clicks
        totals["spend"] += spend
        totals["conversions"] += conversions
    return {
        "daily": {d.isoformat(): v for d, v in sorted(daily.items())},
        "total": totals,
    }


def parse_crm(rows: list[dict]) -> list[dict]:
    leads = []
    for row in rows:
        raw = row.get("Дата создания", "")
        stamp = None
        for fmt in ("%d.%m.%Y %H:%M:%S", "%d.%m.%Y %H:%M", "%Y-%m-%d %H:%M:%S"):
            try:
                stamp = datetime.strptime(raw, fmt)
                break
            except ValueError:
                continue
        if stamp is None:
            continue
        leads.append(
            {
                "date": stamp.date(),
                "stage": row.get("Стадия", ""),
                "source": row.get("Источник", ""),
                "utm_source": row.get("UTM Source", ""),
                "utm_campaign": row.get("UTM Campaign", ""),
                "title": row.get("Название лида", "")[:60],
            }
        )
    return leads


def attribute_account(lead: dict, fallback: str) -> str:
    """Возвращает id аккаунта Директа либо 'seo' / 'instagram' / 'other'."""
    source = f"{lead['source']} {lead['utm_source']}".lower()
    # По конвенции проекта: «Запросы по СЕО» -> SEO.
    if "сео" in source or "seo" in source:
        return "seo"
    # Instagram — отдельная строка в детализации дашборда.
    if "instagram" in source or "инстаграм" in source:
        return "instagram"
    campaign = (lead["utm_campaign"] or "").strip()
    if campaign in UTM_TO_ACCOUNT:
        return UTM_TO_ACCOUNT[campaign]
    if "директ" in source or "yandex" in source:
        # Без UTM -> активный платный кабинет недели (конвенция w17/w19).
        return fallback
    return "other"


def parse_weeks(spec: str) -> list[tuple[str, str]]:
    weeks = []
    for chunk in spec.split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        left, _, right = chunk.partition("-")
        start = parse_day(f"{left.strip()}.2026")
        end = parse_day(f"{right.strip()}.2026")
        if start and end:
            weeks.append((start.isoformat(), end.isoformat()))
    return weeks


def empty_week(start: str, end: str) -> dict:
    return {
        "range": f"{start}..{end}",
        "accounts": {acc: {**new_bucket(), "leads": 0, "target": 0} for acc in ACCOUNTS},
        "leads": 0,
        "target": 0,
        "seo_leads": 0,
        "seo_target": 0,
        "instagram_leads": 0,
        "instagram_target": 0,
        "other_leads": 0,
        "other_target": 0,
        "_leads_by_account": defaultdict(int),
        "_target_by_account": defaultdict(int),
    }


def finalize(week: dict) -> dict:
    for acc, data in week["accounts"].items():
        data["spend"] = round(data["spend"], 2)
    for key in ("_leads_by_account", "_target_by_account"):
        week.pop(key)
    return week


def main() -> int:
    parser = argparse.ArgumentParser(description="Разбор месячной выгрузки на недели")
    parser.add_argument("folder", type=Path)
    parser.add_argument("--weeks", required=True, help="например 03.08-09.08,10.08-16.08")
    parser.add_argument("--out", type=Path)
    parser.add_argument(
        "--direct-fallback-account",
        default="e-17228851",
        help="куда относить Директ-лиды без UTM-кампании",
    )
    args = parser.parse_args()

    weeks = parse_weeks(args.weeks)
    if not weeks:
        print("Не удалось разобрать --weeks", file=sys.stderr)
        return 2

    buckets = {w[0]: empty_week(*w) for w in weeks}
    unassigned = {"direct_days": 0, "leads": 0}
    direct_month = {acc: new_bucket() for acc in ACCOUNTS}
    seo = {"pages": 0, "queries": 0, "impressions": 0, "top_pages": [], "top_queries": []}
    crm_total = {"leads": 0, "target": 0}
    metrika = {}

    for path in sorted(args.folder.glob("*.csv")):
        rows = read_csv(path)
        kind = classify(path, rows) if rows else "empty"
        label = f"{path.name} -> {kind}"

        if kind == "empty":
            print(f"[пусто] {label}")
            continue

        if kind == "direct":
            acc = account_from_name(path)
            parsed = parse_direct(rows)
            if acc is None:
                print(f"[!!] не определён кабинет: {label}")
                continue
            for key, value in parsed["total"].items():
                direct_month[acc][key] += value
            for day_str, values in parsed["daily"].items():
                day = date.fromisoformat(day_str)
                target_bucket = None
                for start, end in weeks:
                    if date.fromisoformat(start) <= day <= date.fromisoformat(end):
                        target_bucket = buckets[start]
                        break
                if target_bucket is None:
                    unassigned["direct_days"] += 1
                    continue
                acc_bucket = target_bucket["accounts"][acc]
                for key in ("impressions", "clicks", "spend", "conversions"):
                    acc_bucket[key] += values[key]
            print(f"[direct] {label}: {parsed['total']}")
            continue

        if kind == "crm":
            leads = parse_crm(rows)
            crm_total["leads"] += len(leads)
            crm_total["target"] += sum(1 for lead in leads if lead["stage"] == TARGET_STAGE)
            for lead in leads:
                target_bucket = None
                for start, end in weeks:
                    if date.fromisoformat(start) <= lead["date"] <= date.fromisoformat(end):
                        target_bucket = buckets[start]
                        break
                if target_bucket is None:
                    unassigned["leads"] += 1
                    continue
                is_target = lead["stage"] == TARGET_STAGE
                target_bucket["leads"] += 1
                target_bucket["target"] += int(is_target)
                acc = attribute_account(lead, args.direct_fallback_account)
                if acc == "seo":
                    target_bucket["seo_leads"] += 1
                    target_bucket["seo_target"] += int(is_target)
                elif acc == "instagram":
                    target_bucket["instagram_leads"] += 1
                    target_bucket["instagram_target"] += int(is_target)
                elif acc == "other":
                    target_bucket["other_leads"] += 1
                    target_bucket["other_target"] += int(is_target)
                else:
                    target_bucket["accounts"][acc]["leads"] += 1
                    target_bucket["accounts"][acc]["target"] += int(is_target)
                    target_bucket["_leads_by_account"][acc] += 1
                    target_bucket["_target_by_account"][acc] += int(is_target)
            print(f"[crm] {label}: {len(leads)} лидов, "
                  f"{sum(1 for x in leads if x['stage'] == TARGET_STAGE)} целевых")
            continue

        if kind in ("seo_pages", "seo_queries"):
            clicks = sum(int(to_num(r.get("Clicks"))) for r in rows)
            impressions = sum(int(to_num(r.get("Impressions"))) for r in rows)
            key_name = "Path" if kind == "seo_pages" else "Query"
            top = sorted(
                ((r.get(key_name, ""), int(to_num(r.get("Clicks")))) for r in rows),
                key=lambda pair: -pair[1],
            )[:10]
            if kind == "seo_pages":
                seo["pages"] = clicks
                seo["top_pages"] = top
            else:
                seo["queries"] = clicks
                seo["top_queries"] = top
            seo["impressions"] += impressions
            print(f"[{kind}] {label}: клики={clicks}, показы={impressions}")
            continue

        if kind == "metrika":
            for row in rows:
                metrika[row.get("Источник трафика", "")] = int(to_num(row.get("Визиты")))
            print(f"[metrika] {label}: {len(rows)} строк")
            continue

        print(f"[??] {label}")

    result = {
        "folder": str(args.folder),
        "weeks": [finalize(buckets[start]) for start, _ in weeks],
        "month": {
            "accounts": {
                acc: {**data, "spend": round(data["spend"], 2)} for acc, data in direct_month.items()
            },
            "crm": crm_total,
        },
        "seo": seo,
        "metrika": metrika,
        "unassigned": unassigned,
    }

    payload = json.dumps(result, ensure_ascii=False, indent=2)
    if args.out:
        args.out.write_text(payload, encoding="utf-8")
        print(f"\nЗаписано: {args.out}")
    else:
        print(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
