"""
Preservation Property Tests for Cost Calculation Fix

**Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5, 3.6**

These tests capture baseline behavior on UNFIXED code that must be preserved after the fix.
Tests should PASS on unfixed code and continue to PASS after the fix.

GOAL: Verify that non-buggy data (account metrics, campaign details, SEO/Recommendations, 
formatting, structure) remains unchanged when the cost calculation bug is fixed.

The tests verify preservation of:
- Account e-20010227 data (row 6): impressions=49416, clicks=805, cost="р.27 564"
- Campaign-level rows (7-9, 11-14, 16-17, 19-20): individual visits and costs
- SEO row (21): 80 visits, 0 leads, no costs
- Recommendations row (22): data unchanged
- BOLD_ROWS formatting list
- Report structure: total rows, column count, headers
"""

import pytest
from report_0106 import ROWS, BOLD_ROWS


# Baseline snapshots of unfixed code behavior that must be preserved
# These represent the CORRECT behavior that should NOT change

# Row 6: e-20010227 account (this data is CORRECT and should not change)
EXPECTED_E20010227_ROW = [
    "e-20010227",  # Account name
    49416,  # Impressions
    805,  # Clicks
    "1.63%",  # CTR (805/49416*100)
    "р.34",  # CPC (27564/805)
    11,  # Leads
    "1.37%",  # Conversion to Lead
    "р.2 506",  # CPA (27564/11)
    7,  # Targeted Leads
    "63.64%",  # Conversion to Targeted Lead
    "р.3 938",  # CPL (27564/7)
    "р.27 564"  # Cost
]

# Campaign rows under e-20010227 (rows 7-9) - these are CORRECT
EXPECTED_E20010227_CAMPAIGNS = [
    ["МК ТК // Ремонт // remont.dune-group.ru", "", 600, "", "", 11, "", "", 7, "", "", "р.20 000"],
    ["Поиск/РСЯ Главная // Март // CPA ЦЕЛЬ", "", 100, "", "", 0, "", "", 0, "", "", "р.5 000"],
    ["Поиск/РСЯ доп.домен // Март // CPA ЦЕЛЬ", "", 105, "", "", 0, "", "", 0, "", "", "р.2 564"],
]

# Campaign rows under e-17228851 (rows 11-14)
EXPECTED_E17228851_CAMPAIGNS = [
    ["РСЯ// типовой ремонт // Синяя кухня", "", 21, "", "", 0, "", "", 0, "", "", ""],
    ["Товарная кампания ремонт старая", "", 32, "", "", 0, "", "", 0, "", "", ""],
    ["ЕПК // Ремонт //ФЦ", "", 17, "", "", 0, "", "", 0, "", "", ""],
    ["МК // Строительство // СРА", "", 312, "", "", 0, "", "", 0, "", "", ""],
]

# Campaign rows under dune-group (rows 16-17)
EXPECTED_DUNE_GROUP_CAMPAIGNS = [
    ["Кампания dune-group 1", "", 80, "", "", 0, "", "", 0, "", "", ""],
    ["Кампания dune-group 2", "", 71, "", "", 0, "", "", 0, "", "", ""],
]

# Campaign rows under porg-3uieikjn (rows 19-20)
EXPECTED_PORG_CAMPAIGNS = [
    ["Кампания porg-1", "", 60, "", "", 0, "", "", 0, "", "", ""],
    ["Кампания porg-2", "", 60, "", "", 0, "", "", 0, "", "", ""],
]

# Empty row (row 21)
EXPECTED_EMPTY_ROW_21 = []

# SEO row (row 22)
EXPECTED_SEO_ROW = ["SEO", "", 80, "", "", 0, "", "", 0, "", "", ""]

# Recommendations row (row 23)
EXPECTED_RECOMMENDATIONS_ROW = ["Рекомендации", "", "", "", "", 0, "", "", 0, "", "", ""]

# Headers row (row 3)
EXPECTED_HEADERS_ROW = [
    "Канал", "Показы", "Визиты", "CTR", "CPC", "Лиды", 
    "Конверсия в Лид", "CPA", "Ц. Лиды", "Конверсия в Ц. Лид", "CPL", "Расход"
]

# Expected BOLD_ROWS formatting
EXPECTED_BOLD_ROWS = [0, 3, 4, 5, 6, 20, 25, 26]


def test_preservation_e20010227_account_data():
    """
    **Property 2: Preservation** - Account e-20010227 Data Remains Unchanged
    
    Verify that row 6 (e-20010227 account) displays its metrics correctly:
    - Impressions: 49416
    - Clicks: 805
    - Cost: "р.27 564"
    - CTR, CPC, leads, conversions, CPA, CPL all remain unchanged
    
    This account has CORRECT data and should not be affected by the fix.
    
    EXPECTED OUTCOME: Test PASSES on unfixed code
    After fix: Test continues to PASS (no regression)
    
    **Validates: Requirements 3.1**
    """
    actual_row = ROWS[6]
    
    assert actual_row == EXPECTED_E20010227_ROW, (
        f"Account e-20010227 data changed unexpectedly:\n"
        f"  Expected: {EXPECTED_E20010227_ROW}\n"
        f"  Found: {actual_row}\n"
        f"  This data should remain unchanged - it was correct in the original code"
    )


def test_preservation_e20010227_campaign_breakdown():
    """
    **Property 2: Preservation** - Campaign Breakdown for e-20010227 Remains Unchanged
    
    Verify that rows 7-9 (campaign-level breakdown under e-20010227) display
    their individual visits and costs correctly. These campaigns had actual costs:
    - МК ТК // Ремонт: 600 visits, "р.20 000"
    - Поиск/РСЯ Главная: 100 visits, "р.5 000"
    - Поиск/РСЯ доп.домен: 105 visits, "р.2 564"
    
    EXPECTED OUTCOME: Test PASSES on unfixed code
    After fix: Test continues to PASS (no regression)
    
    **Validates: Requirements 3.2**
    """
    actual_campaigns = [ROWS[7], ROWS[8], ROWS[9]]
    
    for i, (actual, expected) in enumerate(zip(actual_campaigns, EXPECTED_E20010227_CAMPAIGNS)):
        assert actual == expected, (
            f"Campaign {i+1} under e-20010227 changed unexpectedly:\n"
            f"  Expected: {expected}\n"
            f"  Found: {actual}\n"
            f"  Campaign-level data should remain unchanged"
        )


def test_preservation_e17228851_campaigns():
    """
    **Property 2: Preservation** - Campaign Breakdown for e-17228851 Remains Unchanged
    
    Verify that rows 11-14 (campaign-level breakdown under e-17228851) remain unchanged.
    These campaigns show their individual visit counts and metrics.
    
    EXPECTED OUTCOME: Test PASSES on unfixed code
    After fix: Test continues to PASS (no regression)
    
    **Validates: Requirements 3.2**
    """
    actual_campaigns = [ROWS[11], ROWS[12], ROWS[13], ROWS[14]]
    
    for i, (actual, expected) in enumerate(zip(actual_campaigns, EXPECTED_E17228851_CAMPAIGNS)):
        assert actual == expected, (
            f"Campaign {i+1} under e-17228851 changed unexpectedly:\n"
            f"  Expected: {expected}\n"
            f"  Found: {actual}\n"
            f"  Campaign-level data should remain unchanged"
        )


def test_preservation_dune_group_campaigns():
    """
    **Property 2: Preservation** - Campaign Breakdown for dune-group Remains Unchanged
    
    Verify that rows 16-17 (campaign-level breakdown under dune-group) remain unchanged.
    
    EXPECTED OUTCOME: Test PASSES on unfixed code
    After fix: Test continues to PASS (no regression)
    
    **Validates: Requirements 3.2**
    """
    actual_campaigns = [ROWS[16], ROWS[17]]
    
    for i, (actual, expected) in enumerate(zip(actual_campaigns, EXPECTED_DUNE_GROUP_CAMPAIGNS)):
        assert actual == expected, (
            f"Campaign {i+1} under dune-group changed unexpectedly:\n"
            f"  Expected: {expected}\n"
            f"  Found: {actual}\n"
            f"  Campaign-level data should remain unchanged"
        )


def test_preservation_porg_campaigns():
    """
    **Property 2: Preservation** - Campaign Breakdown for porg-3uieikjn Remains Unchanged
    
    Verify that rows 19-20 (campaign-level breakdown under porg-3uieikjn) remain unchanged.
    
    EXPECTED OUTCOME: Test PASSES on unfixed code
    After fix: Test continues to PASS (no regression)
    
    **Validates: Requirements 3.2**
    """
    actual_campaigns = [ROWS[19], ROWS[20]]
    
    for i, (actual, expected) in enumerate(zip(actual_campaigns, EXPECTED_PORG_CAMPAIGNS)):
        assert actual == expected, (
            f"Campaign {i+1} under porg-3uieikjn changed unexpectedly:\n"
            f"  Expected: {expected}\n"
            f"  Found: {actual}\n"
            f"  Campaign-level data should remain unchanged"
        )


def test_preservation_empty_row_21():
    """
    **Property 2: Preservation** - Empty Row 21 Remains Unchanged
    
    Verify that row 21 is an empty row (separator).
    
    EXPECTED OUTCOME: Test PASSES on unfixed code
    After fix: Test continues to PASS (no regression)
    
    **Validates: Requirements 3.6**
    """
    actual_empty_row = ROWS[21]
    
    assert actual_empty_row == EXPECTED_EMPTY_ROW_21, (
        f"Empty row 21 changed unexpectedly:\n"
        f"  Expected: {EXPECTED_EMPTY_ROW_21}\n"
        f"  Found: {actual_empty_row}\n"
        f"  Empty row should remain unchanged"
    )


def test_preservation_seo_row():
    """
    **Property 2: Preservation** - SEO Row Data Remains Unchanged
    
    Verify that row 22 (SEO channel) displays:
    - 80 visits
    - 0 leads
    - No costs
    
    EXPECTED OUTCOME: Test PASSES on unfixed code
    After fix: Test continues to PASS (no regression)
    
    **Validates: Requirements 3.4**
    """
    actual_seo_row = ROWS[22]
    
    assert actual_seo_row == EXPECTED_SEO_ROW, (
        f"SEO row changed unexpectedly:\n"
        f"  Expected: {EXPECTED_SEO_ROW}\n"
        f"  Found: {actual_seo_row}\n"
        f"  SEO data should remain unchanged"
    )


def test_preservation_recommendations_row():
    """
    **Property 2: Preservation** - Recommendations Row Data Remains Unchanged
    
    Verify that row 23 (Recommendations channel) displays its data unchanged.
    
    EXPECTED OUTCOME: Test PASSES on unfixed code
    After fix: Test continues to PASS (no regression)
    
    **Validates: Requirements 3.5**
    """
    actual_recommendations_row = ROWS[23]
    
    assert actual_recommendations_row == EXPECTED_RECOMMENDATIONS_ROW, (
        f"Recommendations row changed unexpectedly:\n"
        f"  Expected: {EXPECTED_RECOMMENDATIONS_ROW}\n"
        f"  Found: {actual_recommendations_row}\n"
        f"  Recommendations data should remain unchanged"
    )


def test_preservation_headers_row():
    """
    **Property 2: Preservation** - Headers Row Remains Unchanged
    
    Verify that row 3 (column headers) contains the expected header labels.
    
    EXPECTED OUTCOME: Test PASSES on unfixed code
    After fix: Test continues to PASS (no regression)
    
    **Validates: Requirements 3.6**
    """
    actual_headers = ROWS[3]
    
    assert actual_headers == EXPECTED_HEADERS_ROW, (
        f"Headers row changed unexpectedly:\n"
        f"  Expected: {EXPECTED_HEADERS_ROW}\n"
        f"  Found: {actual_headers}\n"
        f"  Header structure should remain unchanged"
    )


def test_preservation_bold_rows_formatting():
    """
    **Property 2: Preservation** - BOLD_ROWS Formatting List Remains Unchanged
    
    Verify that the BOLD_ROWS list (which controls bold formatting in Google Sheets)
    remains unchanged: [0, 3, 4, 5, 6, 20, 25, 26]
    
    Note: This assumes row indices don't change. If rows are added/removed, this
    would need adjustment, but for this fix we're only changing values, not structure.
    
    EXPECTED OUTCOME: Test PASSES on unfixed code
    After fix: Test continues to PASS (no regression)
    
    **Validates: Requirements 3.6**
    """
    assert BOLD_ROWS == EXPECTED_BOLD_ROWS, (
        f"BOLD_ROWS formatting changed unexpectedly:\n"
        f"  Expected: {EXPECTED_BOLD_ROWS}\n"
        f"  Found: {BOLD_ROWS}\n"
        f"  Formatting list should remain unchanged"
    )


def test_preservation_report_structure():
    """
    **Property 2: Preservation** - Report Structure Remains Unchanged
    
    Verify that the overall report structure is preserved:
    - Total number of rows
    - Number of columns in each row
    - Row types (title, empty, headers, data)
    
    EXPECTED OUTCOME: Test PASSES on unfixed code
    After fix: Test continues to PASS (no regression)
    
    **Validates: Requirements 3.6**
    """
    expected_total_rows = 24  # Based on ROWS structure
    actual_total_rows = len(ROWS)
    
    assert actual_total_rows == expected_total_rows, (
        f"Total number of rows changed:\n"
        f"  Expected: {expected_total_rows}\n"
        f"  Found: {actual_total_rows}\n"
        f"  Report structure should remain unchanged"
    )
    
    # Verify row 0 is the title row (single element)
    assert len(ROWS[0]) == 1, "Row 0 should be a title row with single element"
    
    # Verify rows 1-2 are empty
    assert ROWS[1] == [], "Row 1 should be empty"
    assert ROWS[2] == [], "Row 2 should be empty"
    
    # Verify row 3 has 12 columns (headers)
    assert len(ROWS[3]) == 12, "Row 3 (headers) should have 12 columns"
    
    # Verify data rows have 12 columns
    for row_idx in [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 22, 23]:
        actual_cols = len(ROWS[row_idx])
        assert actual_cols == 12, (
            f"Row {row_idx} should have 12 columns, found {actual_cols}\n"
            f"  Row content: {ROWS[row_idx]}"
        )


def test_preservation_non_buggy_rows_unchanged():
    """
    **Property 2: Preservation** - All Non-Buggy Rows Remain Unchanged
    
    This is a comprehensive test that verifies ALL rows except the ones being fixed
    (rows 4, 5, 10, 15, 18) remain exactly the same.
    
    Rows being fixed (excluded from this test):
    - Row 4: Total (cost and derived metrics will change)
    - Row 5: Yandex Direct summary (cost and derived metrics will change)
    - Row 10: e-17228851 account (cost will change to 0)
    - Row 15: dune-group account (cost will change to 0)
    - Row 18: porg-3uieikjn account (cost will change to 0)
    
    All other rows should remain identical.
    
    EXPECTED OUTCOME: Test PASSES on unfixed code
    After fix: Test continues to PASS (no regression)
    
    **Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5, 3.6**
    """
    # Snapshot of all rows that should NOT change
    preserved_rows_snapshot = {
        0: ["01.06.2026–07.06.2026"],
        1: [],
        2: [],
        3: EXPECTED_HEADERS_ROW,
        # 4: excluded (Total - being fixed)
        # 5: excluded (Yandex Direct summary - being fixed)
        6: EXPECTED_E20010227_ROW,
        7: EXPECTED_E20010227_CAMPAIGNS[0],
        8: EXPECTED_E20010227_CAMPAIGNS[1],
        9: EXPECTED_E20010227_CAMPAIGNS[2],
        # 10: excluded (e-17228851 - being fixed)
        11: EXPECTED_E17228851_CAMPAIGNS[0],
        12: EXPECTED_E17228851_CAMPAIGNS[1],
        13: EXPECTED_E17228851_CAMPAIGNS[2],
        14: EXPECTED_E17228851_CAMPAIGNS[3],
        # 15: excluded (dune-group - being fixed)
        16: EXPECTED_DUNE_GROUP_CAMPAIGNS[0],
        17: EXPECTED_DUNE_GROUP_CAMPAIGNS[1],
        # 18: excluded (porg-3uieikjn - being fixed)
        19: EXPECTED_PORG_CAMPAIGNS[0],
        20: EXPECTED_PORG_CAMPAIGNS[1],
        21: EXPECTED_EMPTY_ROW_21,
        22: EXPECTED_SEO_ROW,
        23: EXPECTED_RECOMMENDATIONS_ROW,
    }
    
    changed_rows = []
    for row_idx, expected_row in preserved_rows_snapshot.items():
        actual_row = ROWS[row_idx]
        if actual_row != expected_row:
            changed_rows.append({
                "row_index": row_idx,
                "expected": expected_row,
                "found": actual_row
            })
    
    if changed_rows:
        error_msg = "\nPreservation violation - Non-buggy rows changed unexpectedly:\n\n"
        for change in changed_rows:
            error_msg += f"Row {change['row_index']}:\n"
            error_msg += f"  Expected: {change['expected']}\n"
            error_msg += f"  Found: {change['found']}\n\n"
        
        error_msg += "These rows should remain unchanged - only rows 4, 5, 10, 15, 18 should be modified by the fix."
        pytest.fail(error_msg)


def test_preservation_summary():
    """
    Summary test documenting all preservation checks.
    
    This test verifies that all non-buggy aspects of the report remain unchanged:
    - Account e-20010227 metrics (correct in original)
    - Campaign-level breakdowns for all accounts
    - SEO and Recommendations channel data
    - Report structure and formatting
    
    **Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5, 3.6**
    """
    preservation_checks = []
    
    # Check account e-20010227
    if ROWS[6] != EXPECTED_E20010227_ROW:
        preservation_checks.append({
            "check": "Account e-20010227 (row 6)",
            "status": "FAILED",
            "impact": "Account metrics changed unexpectedly"
        })
    else:
        preservation_checks.append({
            "check": "Account e-20010227 (row 6)",
            "status": "PASSED",
            "impact": "Account data preserved correctly"
        })
    
    # Check campaign breakdowns
    campaign_checks = [
        (7, "e-20010227 campaign 1"),
        (8, "e-20010227 campaign 2"),
        (9, "e-20010227 campaign 3"),
        (11, "e-17228851 campaign 1"),
        (12, "e-17228851 campaign 2"),
        (13, "e-17228851 campaign 3"),
        (14, "e-17228851 campaign 4"),
        (16, "dune-group campaign 1"),
        (17, "dune-group campaign 2"),
        (19, "porg campaign 1"),
        (20, "porg campaign 2"),
    ]
    
    for row_idx, campaign_name in campaign_checks:
        # We need to map expected values
        expected_map = {
            7: EXPECTED_E20010227_CAMPAIGNS[0],
            8: EXPECTED_E20010227_CAMPAIGNS[1],
            9: EXPECTED_E20010227_CAMPAIGNS[2],
            11: EXPECTED_E17228851_CAMPAIGNS[0],
            12: EXPECTED_E17228851_CAMPAIGNS[1],
            13: EXPECTED_E17228851_CAMPAIGNS[2],
            14: EXPECTED_E17228851_CAMPAIGNS[3],
            16: EXPECTED_DUNE_GROUP_CAMPAIGNS[0],
            17: EXPECTED_DUNE_GROUP_CAMPAIGNS[1],
            19: EXPECTED_PORG_CAMPAIGNS[0],
            20: EXPECTED_PORG_CAMPAIGNS[1],
        }
        
        if ROWS[row_idx] != expected_map[row_idx]:
            preservation_checks.append({
                "check": f"{campaign_name} (row {row_idx})",
                "status": "FAILED",
                "impact": "Campaign data changed unexpectedly"
            })
    
    # Check SEO and Recommendations
    if ROWS[22] != EXPECTED_SEO_ROW:
        preservation_checks.append({
            "check": "SEO row (row 22)",
            "status": "FAILED",
            "impact": "SEO data changed unexpectedly"
        })
    
    if ROWS[23] != EXPECTED_RECOMMENDATIONS_ROW:
        preservation_checks.append({
            "check": "Recommendations row (row 23)",
            "status": "FAILED",
            "impact": "Recommendations data changed unexpectedly"
        })
    
    # Check formatting
    if BOLD_ROWS != EXPECTED_BOLD_ROWS:
        preservation_checks.append({
            "check": "BOLD_ROWS formatting",
            "status": "FAILED",
            "impact": "Formatting list changed unexpectedly"
        })
    
    # Report summary
    failed_checks = [c for c in preservation_checks if c.get("status") == "FAILED"]
    
    if failed_checks:
        error_msg = "\n" + "=" * 80 + "\n"
        error_msg += "PRESERVATION VIOLATION - Non-buggy data changed unexpectedly\n"
        error_msg += "=" * 80 + "\n\n"
        error_msg += "Failed preservation checks:\n\n"
        
        for i, check in enumerate(failed_checks, 1):
            error_msg += f"{i}. {check['check']}\n"
            error_msg += f"   Status: {check['status']}\n"
            error_msg += f"   Impact: {check['impact']}\n\n"
        
        error_msg += "Expected Behavior:\n"
        error_msg += "- Only rows 4, 5, 10, 15, 18 should change (cost corrections)\n"
        error_msg += "- All other data should remain identical to unfixed code\n"
        error_msg += "=" * 80 + "\n"
        
        pytest.fail(error_msg)


if __name__ == "__main__":
    # Run tests and display results
    print("Running Preservation Property Tests")
    print("=" * 80)
    print("IMPORTANT: These tests should PASS on unfixed code")
    print("They capture baseline behavior that must be preserved after the fix")
    print("=" * 80)
    print()
    
    pytest.main([__file__, "-v", "--tb=short"])
