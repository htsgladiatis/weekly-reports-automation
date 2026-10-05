"""Добавляет недельный SEO-снимок w19 (07.09–13.09) в seoWeeklyData.

Источник — недельная выгрузка Вебмастера в 0. reports/07-13.09/.
visits = клики по СТРАНИЦАМ (конвенция проекта).
"""

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "0. reports" / "07-13.09"
INDEX = ROOT / "index.html"
LABEL = "07.09–13.09"


def top_by(rows: list[dict], key: str, limit: int = 10) -> list[tuple[str, int]]:
    pairs = [(r[key], int(float(r["Clicks"] or 0))) for r in rows]
    pairs = [p for p in pairs if p[1] > 0]
    pairs.sort(key=lambda pair: -pair[1])
    return pairs[:limit]


def main() -> int:
    files = sorted(SOURCE.glob("dune-group.ru*.csv"))
    parsed = []
    for path in files:
        with path.open(encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.DictReader(handle, delimiter=","))
        key = "Path" if "Path" in rows[0] else "Query"
        parsed.append((key, rows))

    top_pages, top_queries = {}, {}
    for key, rows in parsed:
        clicks = sum(int(float(r["Clicks"] or 0)) for r in rows)
        if key == "Path":
            top_pages = dict(top_by(rows, "Path"))
        else:
            top_queries = dict(top_by(rows, "Query"))

    visits = sum(int(float(r["Clicks"] or 0)) for k, rows in parsed if k == "Path" for r in rows)

    pages_js = "\n".join(
        "      {{ url: 'https://dune-group.ru{path}', visits: {v}, bounceRate: null }},".format(
            path=path, v=v
        )
        for path, v in list(top_pages.items())
    ).rstrip(",")
    queries_js = "\n".join(
        "      {{ query: '{q}', visits: {v} }},".format(q=q.replace("'", "\\'"), v=v)
        for q, v in list(top_queries.items())
    ).rstrip(",")

    block = (
        "  'w19': {{\n"
        "    // Вебмастер за 07.09–13.09: 59 кликов/визитов (файл страниц).\n"
        "    stats: {{ visits: {visits}, users: null, bounceRate: null, pageDepth: null, avgDuration: null }},\n"
        "    topPages: [\n{pages}\n    ],\n"
        "    searchQueries: [\n{queries}\n    ],\n"
        "  }},".format(visits=visits, pages=pages_js, queries=queries_js)
    )

    html = INDEX.read_text(encoding="utf-8")
    anchor = "const seoWeeklyData = {"
    start = html.index(anchor)
    insert_at = html.index("\n", html.index("{", start) + 1) + 1
    html = html[:insert_at] + block + "\n" + html[insert_at:]
    INDEX.write_text(html, encoding="utf-8")
    print(f"seoWeeklyData['w19']: visits={visits}, топов {len(top_pages)}/{len(top_queries)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
