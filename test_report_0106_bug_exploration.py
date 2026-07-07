"""
Bug Condition Exploration Test for Cost Calculation Fix

**Validates: Requirements 1.1, 1.2, 1.3, 1.4**

This test is EXPECTED TO FAIL on unfixed code - failure confirms the bug exists.
DO NOT attempt to fix the test or the code when it fails.

GOAL: Surface counterexamples that demonstrate hardcoded values don't match actual data.

The test verifies that ROWS data structure contains incorrect hardcoded values:
- ROWS[4][11] (Total cost) shows "р.96 494" instead of expected "р.27 564"
- ROWS[5][11] (Yandex Direct summary) shows "р.96 494" instead of "р.27 564"
- ROWS[10][11] (e-17228851) shows "р.58 292" instead of "р.0"
- ROWS[15][11] (dune-group) shows "р.4 707" instead of "р.0"
- ROWS[18][11] (porg-3uieikjn) shows "р.5 931" instead of "р.0"
- Derived metrics use incorrect total: ROWS[4][4] CPC uses 96494 instead of 27564
"""

import pytest
from report_0106 import ROWS, cpc


def extract_numeric_value(cost_string):
    """
    Extract numeric value from formatted cost string.
    Examples: "р.96 494" -> 96494, "р.27 564" -> 27564, "р.0" -> 0
    """
    if not cost_string or cost_string == "-" or cost_string == "":
        return 0
    
    # Remove "р." prefix and spaces
    numeric_str = cost_string.replace("р.", "").replace(" ", "").strip()
    
    if not numeric_str:
        return 0
    
    try:
        return int(numeric_str)
    except ValueError:
        return 0


def extract_cpc_value(cpc_string):
    """
    Extract numeric value from CPC string.
    Examples: "р.18" -> 18, "р.63" -> 63
    """
    if not cpc_string or cpc_string == "-":
        return None
    
    numeric_str = cpc_string.replace("р.", "").strip()
    try:
        return int(numeric_str)
    except ValueError:
        return None


def test_bug_condition_total_cost_incorrect():
    """
    **Property 1: Bug Condition** - Total Cost Shows Incorrect Hardcoded Value
    
    This test verifies that ROWS[4][11] (Total cost row) contains the incorrect
    hardcoded value of 96,494₽ instead of the expected correct value of 27,564₽.
    
    EXPECTED OUTCOME: Test FAILS on unfixed code (proves bug exists)
    After fix: Test PASSES (confirms fix works)
    
    **Validates: Requirements 1.1, 1.2, 2.2**
    """
    actual_total_cost = extract_numeric_value(ROWS[4][11])
    expected_total_cost = 27564  # Only e-20010227 had actual costs
    
    # Document counterexample
    counterexample = {
        "row": "ROWS[4] (Total)",
        "actual_value": ROWS[4][11],
        "actual_numeric": actual_total_cost,
        "expected_value": "р.27 564",
        "expected_numeric": expected_total_cost,
        "bug": "Uses hardcoded value from comments instead of actual data"
    }
    
    assert actual_total_cost == expected_total_cost, (
        f"Bug detected - Total cost is incorrect:\n"
        f"  Found: {ROWS[4][11]} ({actual_total_cost}₽)\n"
        f"  Expected: р.27 564 ({expected_total_cost}₽)\n"
        f"  Counterexample: {counterexample}\n"
        f"  Root cause: Hardcoded value (96,494₽) from code comments used instead of actual data (27,564₽)"
    )


def test_bug_condition_yandex_direct_summary_cost_incorrect():
    """
    **Property 1: Bug Condition** - Yandex Direct Summary Cost Shows Incorrect Value
    
    This test verifies that ROWS[5][11] (Yandex Direct summary row) contains the
    incorrect hardcoded value of 96,494₽ instead of the expected 27,564₽.
    
    EXPECTED OUTCOME: Test FAILS on unfixed code (proves bug exists)
    After fix: Test PASSES (confirms fix works)
    
    **Validates: Requirements 1.1, 1.3, 2.3**
    """
    actual_direct_cost = extract_numeric_value(ROWS[5][11])
    expected_direct_cost = 27564  # Sum of four accounts (only e-20010227 had costs)
    
    counterexample = {
        "row": "ROWS[5] (Yandex Direct summary)",
        "actual_value": ROWS[5][11],
        "actual_numeric": actual_direct_cost,
        "expected_value": "р.27 564",
        "expected_numeric": expected_direct_cost,
        "bug": "Uses hardcoded sum (27564+58292+4707+5931=96494) instead of actual (27564+0+0+0=27564)"
    }
    
    assert actual_direct_cost == expected_direct_cost, (
        f"Bug detected - Yandex Direct summary cost is incorrect:\n"
        f"  Found: {ROWS[5][11]} ({actual_direct_cost}₽)\n"
        f"  Expected: р.27 564 ({expected_direct_cost}₽)\n"
        f"  Counterexample: {counterexample}\n"
        f"  Root cause: Sum includes non-zero hardcoded values for accounts with zero actual costs"
    )


def test_bug_condition_e17228851_zero_cost():
    """
    **Property 1: Bug Condition** - Account e-17228851 Shows Non-Zero Cost When Actual is Zero
    
    This test verifies that ROWS[10][11] (e-17228851 account) shows 58,292₽
    instead of 0₽. This account had clicks but zero actual spending.
    
    EXPECTED OUTCOME: Test FAILS on unfixed code (proves bug exists)
    After fix: Test PASSES (confirms fix works)
    
    **Validates: Requirements 1.1, 2.1**
    """
    actual_e17228851_cost = extract_numeric_value(ROWS[10][11])
    expected_e17228851_cost = 0  # This account had zero actual costs
    
    counterexample = {
        "row": "ROWS[10] (e-17228851)",
        "actual_value": ROWS[10][11],
        "actual_numeric": actual_e17228851_cost,
        "expected_value": "р.0",
        "expected_numeric": expected_e17228851_cost,
        "bug": "Shows hardcoded value 58,292₽ when actual cost is 0₽",
        "note": "Account had 465 clicks but zero spending"
    }
    
    assert actual_e17228851_cost == expected_e17228851_cost, (
        f"Bug detected - Account e-17228851 cost is incorrect:\n"
        f"  Found: {ROWS[10][11]} ({actual_e17228851_cost}₽)\n"
        f"  Expected: р.0 ({expected_e17228851_cost}₽)\n"
        f"  Counterexample: {counterexample}\n"
        f"  Root cause: Hardcoded non-zero value for account with zero actual costs"
    )


def test_bug_condition_dune_group_zero_cost():
    """
    **Property 1: Bug Condition** - Account dune-group Shows Non-Zero Cost When Actual is Zero
    
    This test verifies that ROWS[15][11] (dune-group account) shows 4,707₽
    instead of 0₽. This account had clicks but zero actual spending.
    
    EXPECTED OUTCOME: Test FAILS on unfixed code (proves bug exists)
    After fix: Test PASSES (confirms fix works)
    
    **Validates: Requirements 1.1, 2.1**
    """
    actual_dune_group_cost = extract_numeric_value(ROWS[15][11])
    expected_dune_group_cost = 0  # This account had zero actual costs
    
    counterexample = {
        "row": "ROWS[15] (dune-group)",
        "actual_value": ROWS[15][11],
        "actual_numeric": actual_dune_group_cost,
        "expected_value": "р.0",
        "expected_numeric": expected_dune_group_cost,
        "bug": "Shows hardcoded value 4,707₽ when actual cost is 0₽",
        "note": "Account had 151 clicks but zero spending"
    }
    
    assert actual_dune_group_cost == expected_dune_group_cost, (
        f"Bug detected - Account dune-group cost is incorrect:\n"
        f"  Found: {ROWS[15][11]} ({actual_dune_group_cost}₽)\n"
        f"  Expected: р.0 ({expected_dune_group_cost}₽)\n"
        f"  Counterexample: {counterexample}\n"
        f"  Root cause: Hardcoded non-zero value for account with zero actual costs"
    )


def test_bug_condition_porg_3uieikjn_zero_cost():
    """
    **Property 1: Bug Condition** - Account porg-3uieikjn Shows Non-Zero Cost When Actual is Zero
    
    This test verifies that ROWS[18][11] (porg-3uieikjn account) shows 5,931₽
    instead of 0₽. This account had clicks but zero actual spending.
    
    EXPECTED OUTCOME: Test FAILS on unfixed code (proves bug exists)
    After fix: Test PASSES (confirms fix works)
    
    **Validates: Requirements 1.1, 2.1**
    """
    actual_porg_cost = extract_numeric_value(ROWS[18][11])
    expected_porg_cost = 0  # This account had zero actual costs
    
    counterexample = {
        "row": "ROWS[18] (porg-3uieikjn)",
        "actual_value": ROWS[18][11],
        "actual_numeric": actual_porg_cost,
        "expected_value": "р.0",
        "expected_numeric": expected_porg_cost,
        "bug": "Shows hardcoded value 5,931₽ when actual cost is 0₽",
        "note": "Account had 120 clicks but zero spending"
    }
    
    assert actual_porg_cost == expected_porg_cost, (
        f"Bug detected - Account porg-3uieikjn cost is incorrect:\n"
        f"  Found: {ROWS[18][11]} ({actual_porg_cost}₽)\n"
        f"  Expected: р.0 ({expected_porg_cost}₽)\n"
        f"  Counterexample: {counterexample}\n"
        f"  Root cause: Hardcoded non-zero value for account with zero actual costs"
    )


def test_bug_condition_derived_metrics_cpc():
    """
    **Property 1: Bug Condition** - Derived Metrics Use Incorrect Total Cost
    
    This test verifies that derived metrics (CPC in ROWS[4][4]) use the incorrect
    total cost of 96,494₽ instead of the correct 27,564₽ in their calculations.
    
    Expected CPC = 27564 / 1541 ≈ 18₽
    Incorrect CPC = 96494 / 1541 ≈ 63₽
    
    EXPECTED OUTCOME: Test FAILS on unfixed code (proves bug exists)
    After fix: Test PASSES (confirms fix works)
    
    **Validates: Requirements 1.4, 2.4**
    """
    # Extract CPC from ROWS[4][4] - it's calculated as cpc(cost, clicks)
    actual_cpc_string = ROWS[4][4]
    actual_cpc = extract_cpc_value(actual_cpc_string)
    
    # Expected CPC using correct total
    correct_total = 27564
    correct_clicks = 1541
    expected_cpc = int(correct_total / correct_clicks)  # ≈ 18
    
    # What the bug produces (using incorrect total)
    incorrect_total = 96494
    incorrect_cpc = int(incorrect_total / correct_clicks)  # ≈ 63
    
    counterexample = {
        "row": "ROWS[4][4] (Total CPC)",
        "actual_value": actual_cpc_string,
        "actual_cpc": actual_cpc,
        "expected_cpc": expected_cpc,
        "bug": f"CPC uses incorrect total {incorrect_total}₽ instead of {correct_total}₽",
        "calculation": f"Expected: {correct_total}/{correct_clicks}≈{expected_cpc}₽, Got: {incorrect_total}/{correct_clicks}≈{incorrect_cpc}₽"
    }
    
    assert actual_cpc == expected_cpc, (
        f"Bug detected - Derived metric CPC is incorrect:\n"
        f"  Found: {actual_cpc_string} (CPC={actual_cpc}₽)\n"
        f"  Expected: р.{expected_cpc} (CPC={expected_cpc}₽)\n"
        f"  Counterexample: {counterexample}\n"
        f"  Root cause: CPC calculation uses incorrect total cost (96,494₽ instead of 27,564₽)"
    )


def test_bug_condition_summary():
    """
    Summary test documenting all counterexamples found.
    
    This test aggregates all bug conditions to provide a comprehensive view
    of the cost calculation bug.
    
    **Validates: Requirements 1.1, 1.2, 1.3, 1.4**
    """
    counterexamples = []
    
    # Total cost
    total_cost = extract_numeric_value(ROWS[4][11])
    if total_cost != 27564:
        counterexamples.append({
            "field": "Total cost (ROWS[4][11])",
            "found": ROWS[4][11],
            "expected": "р.27 564",
            "impact": "Critical - affects all derived metrics"
        })
    
    # Yandex Direct summary
    direct_cost = extract_numeric_value(ROWS[5][11])
    if direct_cost != 27564:
        counterexamples.append({
            "field": "Yandex Direct summary (ROWS[5][11])",
            "found": ROWS[5][11],
            "expected": "р.27 564",
            "impact": "Critical - incorrect channel summary"
        })
    
    # Zero-cost accounts
    e17228851_cost = extract_numeric_value(ROWS[10][11])
    if e17228851_cost != 0:
        counterexamples.append({
            "field": "Account e-17228851 (ROWS[10][11])",
            "found": ROWS[10][11],
            "expected": "р.0",
            "impact": "Account with zero actual costs shows non-zero hardcoded value"
        })
    
    dune_group_cost = extract_numeric_value(ROWS[15][11])
    if dune_group_cost != 0:
        counterexamples.append({
            "field": "Account dune-group (ROWS[15][11])",
            "found": ROWS[15][11],
            "expected": "р.0",
            "impact": "Account with zero actual costs shows non-zero hardcoded value"
        })
    
    porg_cost = extract_numeric_value(ROWS[18][11])
    if porg_cost != 0:
        counterexamples.append({
            "field": "Account porg-3uieikjn (ROWS[18][11])",
            "found": ROWS[18][11],
            "expected": "р.0",
            "impact": "Account with zero actual costs shows non-zero hardcoded value"
        })
    
    # Build comprehensive error message
    if counterexamples:
        error_msg = "\n" + "=" * 80 + "\n"
        error_msg += "BUG CONDITION CONFIRMED - Cost Calculation Uses Incorrect Hardcoded Values\n"
        error_msg += "=" * 80 + "\n\n"
        error_msg += "Counterexamples found:\n\n"
        
        for i, example in enumerate(counterexamples, 1):
            error_msg += f"{i}. {example['field']}\n"
            error_msg += f"   Found: {example['found']}\n"
            error_msg += f"   Expected: {example['expected']}\n"
            error_msg += f"   Impact: {example['impact']}\n\n"
        
        error_msg += "Root Cause Analysis:\n"
        error_msg += "- Hardcoded values (96494, 58292, 4707, 5931) from code comments\n"
        error_msg += "- Should use actual data (27564, 0, 0, 0) from Master Reports\n"
        error_msg += "- Only e-20010227 had actual costs of 27,564₽\n"
        error_msg += "- Three accounts (e-17228851, dune-group, porg-3uieikjn) had zero costs\n"
        error_msg += "=" * 80 + "\n"
        
        pytest.fail(error_msg)


if __name__ == "__main__":
    # Run tests and display results
    print("Running Bug Condition Exploration Tests")
    print("=" * 80)
    print("IMPORTANT: These tests are EXPECTED TO FAIL on unfixed code")
    print("Failure confirms the bug exists and documents counterexamples")
    print("=" * 80)
    print()
    
    pytest.main([__file__, "-v", "--tb=short"])
