import report_2707 as report


def test_week_13_counts_all_crm_records_with_ids():
    assert report.ALL_LEADS == 47
    assert report.OTHER_LEADS == 42
    assert report.DIRECT_TOTALS["leads"] == 5
