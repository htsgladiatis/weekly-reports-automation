"""Добавляет точный месячный снимок сентября (01.09–30.09) в monthDataOverrides['m5'].

Данные берутся из split_full5.json (разбор 5 CSV Директа + CRM + Вебмастера).
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "0. reports" / "01-30.09" / "split_full5.json"
INDEX = ROOT / "index.html"
ACCOUNTS = ["e-20010227", "e-17228851", "dune-group", "porg-3uieikjn", "porg-l2oigjze"]


def main() -> int:
    data = json.loads(DATA.read_text(encoding="utf-8"))
    weeks = data["weeks"]
    month = data["month"]
    accounts = month["accounts"]
    crm = month["crm"]

    impressions = sum(a["impressions"] for a in accounts.values())
    clicks = sum(a["clicks"] for a in accounts.values())
    spend = round(sum(a["spend"] for a in accounts.values()), 2)

    direct_leads = sum(sum(a["leads"] for a in w["accounts"].values()) for w in weeks)
    direct_target = sum(sum(a["target"] for a in w["accounts"].values()) for w in weeks)
    seo_leads = sum(w["seo_leads"] for w in weeks)
    seo_target = sum(w["seo_target"] for w in weeks)
    insta_leads = sum(w["instagram_leads"] for w in weeks)
    insta_target = sum(w["instagram_target"] for w in weeks)
    other_leads = sum(w["other_leads"] for w in weeks)
    other_target = sum(w["other_target"] for w in weeks)

    assert direct_leads + seo_leads + insta_leads + other_leads == crm["leads"], "лиды не сходятся"
    assert direct_target + seo_target + insta_target + other_target == crm["target"], "целевые не сходятся"

    # Лиды и целевые по аккаунтам — суммируем недельную разбивку.
    per_account = {acc: {"leads": 0, "target": 0} for acc in ACCOUNTS}
    for week in weeks:
        for acc, values in week["accounts"].items():
            per_account[acc]["leads"] += values["leads"]
            per_account[acc]["target"] += values["target"]

    assert sum(v["leads"] for v in per_account.values()) == direct_leads

    acc_lines = []
    for acc in ACCOUNTS:
        values = accounts[acc]
        leads = per_account[acc]["leads"]
        target = per_account[acc]["target"]
        acc_lines.append(
            "      '{acc}': {{ imp: {imp}, clicks: {clicks}, spend: {spend}, "
            "leads: {leads}, target: {target} }},".format(
                acc=acc,
                imp=values["impressions"],
                clicks=values["clicks"],
                spend=round(values["spend"], 2),
                leads=leads,
                target=target,
            )
        )
    acc_lines[-1] = acc_lines[-1].rstrip(",")

    block = (
        "  // Exact September export from Yandex Direct + CRM + Webmaster (01.09-30.09.2026).\n"
        "  // 5 кабинетов (e-20010227 и dune-group без расхода) · лиды = все записи CRM · SEO = клики Вебмастера.\n"
        "  'm5': {{\n"
        "    id: 'm5', label: 'Сентябрь 2026', short: 'Сентябрь',\n"
        "    impressions: {impressions}, clicks: {clicks}, spend: {spend},\n"
        "    leads: {leads}, target: {target},\n"
        "    ctr: {ctr}, cpc: {cpc}, cpa: {cpa}, cpl: {cpl},\n"
        "    convLead: {convLead}, convTarget: {convTarget},\n"
        "    seo: {seo}, seoLeads: {seoLeads}, seoTarget: {seoTarget},\n"
        "    otherLeads: {otherLeads}, otherTarget: {otherTarget}, "
        "instagramLeads: {instaLeads}, instagramTarget: {instaTarget},\n"
        "    accounts: {{\n{accounts}\n    }}\n"
        "  }}".format(
            impressions=impressions,
            clicks=clicks,
            spend=spend,
            leads=crm["leads"],
            target=crm["target"],
            ctr=round(clicks / impressions * 100, 2),
            cpc=round(spend / clicks, 2),
            cpa=round(spend / crm["leads"], 2),
            cpl=round(spend / crm["target"], 2),
            convLead=round(crm["leads"] / clicks * 100, 2),
            convTarget=round(crm["target"] / crm["leads"] * 100, 2),
            seo=data["seo"]["pages"],
            seoLeads=seo_leads,
            seoTarget=seo_target,
            otherLeads=other_leads,
            otherTarget=other_target,
            instaLeads=insta_leads,
            instaTarget=insta_target,
            accounts="\n".join(acc_lines),
        )
    )

    html = INDEX.read_text(encoding="utf-8")
    anchor = "const monthDataOverrides = {"
    start = html.index(anchor)
    end = html.index("\n};", start)
    head = html[:end].rstrip().rstrip(",")
    html = head + ",\n" + block + "\n" + html[end:]
    INDEX.write_text(html, encoding="utf-8")
    print(
        "monthDataOverrides['m5']: {imp} imp / {clk} clicks / {spd} RUB / "
        "{leads} leads / {target} target / SEO {seo}".format(
            imp=impressions, clk=clicks, spd=spend,
            leads=crm["leads"], target=crm["target"], seo=data["seo"]["pages"],
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
