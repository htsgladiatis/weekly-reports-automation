"""Добавляет SEO-снимок сентября в seoMonthlyData['m5'] и пересчитывает seoWeeklyData['all'].

visits = клики Вебмастера по СТРАНИЦАМ (конвенция проекта).
'all' = сумма недельных SEO-визитов; топ-10 объединяются и переранжировываются.
"""

import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPORTS = ROOT / "0. reports" / "01-30.09"
INDEX = ROOT / "index.html"


def read_rows(name: str) -> list[dict]:
    with (REPORTS / name).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter=","))


def top_by(rows: list[dict], key: str, limit: int = 10) -> list[tuple[str, int]]:
    pairs = [(r[key], int(float(r["Clicks"] or 0))) for r in rows]
    pairs = [p for p in pairs if p[1] > 0]
    pairs.sort(key=lambda pair: -pair[1])
    return pairs[:limit]


def js_pages(pairs: list[tuple[str, int]]) -> str:
    lines = [
        "      {{ url: 'https://dune-group.ru{path}', visits: {visits}, bounceRate: null }},".format(
            path=path, visits=visits
        )
        for path, visits in pairs
    ]
    return "\n".join(lines).rstrip(",")


def js_queries(pairs: list[tuple[str, int]]) -> str:
    lines = [
        "      {{ query: '{query}', visits: {visits} }},".format(
            query=query.replace("'", "\\'"), visits=visits
        )
        for query, visits in pairs
    ]
    return "\n".join(lines).rstrip(",")


def main() -> int:
    pages = read_rows("dune-group.ru_4ebbc4434b9e8d3c2218c441.csv")
    queries = read_rows("dune-group.ru_fb689607d9f34661c8827b4f.csv")
    top_pages = top_by(pages, "Path")
    top_queries = top_by(queries, "Query")
    visits = sum(v for _, v in top_by(pages, "Path", limit=10_000))

    html = INDEX.read_text(encoding="utf-8")

    # --- seoMonthlyData['m5'] ---
    block = (
        "  // Exact September export from Yandex Webmaster (01.09-30.09.2026): "
        "клики Вебмастера по страницам/запросам.\n"
        "  'm5': {{\n"
        "    stats: {{ visits: {visits}, users: null, bounceRate: null, pageDepth: null, avgDuration: null }},\n"
        "    topPages: [\n{pages}\n    ],\n"
        "    searchQueries: [\n{queries}\n    ]\n"
        "  }}\n".format(
            visits=visits,
            pages=js_pages(top_pages),
            queries=js_queries(top_queries),
        )
    )
    anchor = "const seoMonthlyData = {"
    start = html.index(anchor)
    end = html.index("\n};", start)
    head = html[:end].rstrip().rstrip(",")
    html = head + ",\n" + block.rstrip().rstrip(",") + "\n" + html[end:]

    # --- пересчёт seoWeeklyData['all'] ---
    weekly_start = html.index("const seoWeeklyData = {")
    weekly_end = html.index("\n};", weekly_start)
    weekly = html[weekly_start:weekly_end]

    # Итог SEO берём из weeks[].seo — именно эти значения показывают KPI, таблицы
    # и графики. seoWeeklyData содержит подробные топы только для части недель,
    # поэтому суммировать stats.visits оттуда нельзя.
    weeks_start = html.index("const weeks = [")
    weeks_end = html.index("const months", weeks_start)
    weeks_block = html[weeks_start:weeks_end]
    per_week = {}
    for match in re.finditer(
        r"\{ id: '(w\d+)', label: '[^']*', short: '[^']*',([\s\S]*?)\n  \}", weeks_block
    ):
        found = re.search(r"seo: (\d+)", match.group(2))
        if found:
            per_week[match.group(1)] = int(found.group(1))
    total = sum(per_week.values())

    # Из выгрузки топов исключаем сам агрегат 'all', иначе каждая страница
    # и каждый запрос будут учтены дважды.
    all_at = weekly.find("\n  'all': {")
    if all_at != -1:
        weekly = weekly[:all_at]

    # Добавляем месячные топы сентября (m5) — их нет в недельных блоках.
    pages_map_m5: dict[str, int] = dict(top_pages)
    queries_map_m5: dict[str, int] = dict(top_queries)

    pages_map: dict[str, int] = {}
    for url, visits_ in re.findall(r"url: 'https://dune-group\.ru([^']*)', visits: (\d+)", weekly):
        pages_map[url or "/"] = pages_map.get(url or "/", 0) + int(visits_)
    queries_map: dict[str, int] = {}
    for query, visits_ in re.findall(r"query: '((?:[^'\\]|\\.)*)', visits: (\d+)", weekly):
        queries_map[query] = queries_map.get(query, 0) + int(visits_)
    for url, clicks in pages_map_m5.items():
        pages_map[url] = pages_map.get(url, 0) + clicks
    for query, clicks in queries_map_m5.items():
        queries_map[query] = queries_map.get(query, 0) + clicks

    def top_map(mapping: dict[str, int], limit: int = 10) -> list[tuple[str, int]]:
        return sorted(mapping.items(), key=lambda pair: (-pair[1], pair[0]))[:limit]

    all_pages = top_map(pages_map)
    all_queries = top_map(queries_map)

    old_all = re.search(
        r"  'all': \{[\s\S]*?\n  \},\n\};",
        html[weekly_start:weekly_end + 3],
    )
    new_all = (
        "  'all': {{\n"
        "    stats: {{ visits: {visits}, users: 542, bounceRate: 6.93, pageDepth: 3.29, avgDuration: 159 }},\n"
        "    topPages: [\n{pages}\n    ],\n"
        "    searchQueries: [\n{queries}\n    ],\n"
        "  }}".format(
            visits=total,
            pages="\n".join(
                "      {{ url: 'https://dune-group.ru{path}', visits: {visits}, bounceRate: null }},".format(
                    path=path, visits=visits_
                )
                for path, visits_ in all_pages
            ).rstrip(","),
            queries="\n".join(
                "      {{ query: '{query}', visits: {visits} }},".format(
                    query=query.replace("'", "\\'"), visits=visits_
                )
                for query, visits_ in all_queries
            ).rstrip(","),
        )
    )

    segment = html[weekly_start:weekly_end + 3]
    assert old_all, "блок 'all' не найден"
    segment = segment[: old_all.start()] + new_all + "\n};" + segment[old_all.end():]
    html = html[:weekly_start] + segment + html[weekly_end + 3:]

    INDEX.write_text(html, encoding="utf-8")
    print(f"seoMonthlyData['m5']: visits={visits}, топов {len(top_pages)}/{len(top_queries)}")
    print(f"seoWeeklyData['all']: visits={total} (сумма {len(per_week)} недель)")
    print("ТОП-5 страниц месяца:", top_pages[:5])
    print("ТОП-5 запросов месяца:", top_queries[:5])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
