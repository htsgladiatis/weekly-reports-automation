import report_2707 as report


def test_week_13_counts_all_crm_records_with_ids():
    assert report.ALL_LEADS == 47
    assert report.OTHER_LEADS == 40
    assert report.DIRECT_TOTALS["leads"] == 5


def test_week_13_uses_manual_crm_attribution():
    assert report.DIRECT_E20010227["leads"] == 4
    assert report.DIRECT_E17228851["leads"] == 1
    assert report.SEO_LEADS == 2
    assert report.SEO_TARGETS == 0
    assert report.DIRECT_TOTALS["leads"] + report.SEO_LEADS + report.OTHER_LEADS == report.ALL_LEADS


def test_manual_attribution_records_are_auditable():
    assert report.MANUAL_CRM_ATTRIBUTION == {
        "24390": "e-17228851",
        "24424": "seo",
        "24410": "seo",
    }
