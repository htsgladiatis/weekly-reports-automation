# Cost Calculation Fix - Bugfix Design

## Overview

This bugfix addresses incorrect cost total calculations in the weekly report script (report_0106.py) for the period 01.06-07.06.2026. The system currently uses hardcoded values from code comments (27564 + 58292 + 4707 + 5931 = 96,494₽) instead of actual data from source systems. Only one account (e-20010227) had actual costs of 27,564₽, while the other three accounts (e-17228851, dune-group, porg-3uieikjn) had zero costs despite having clicks and impressions.

This bug causes critical financial reporting errors: the "Total" and "Yandex Direct" summary rows show 96,494₽ instead of the correct 27,564₽, leading to incorrect derived metrics (CPC, CPA, CPL) that could result in poor business decisions.

The fix will replace hardcoded comment values with actual data from source systems, ensuring accurate cost calculations and derived metrics.

## Glossary

- **Bug_Condition (C)**: The condition where hardcoded values from code comments are used for cost calculations instead of actual data from Yandex.Direct Master Reports, resulting in at least one account showing non-zero costs in calculations when actual costs are zero
- **Property (P)**: The correct behavior where cost calculations use actual data from source systems, producing total costs of 27,564₽ and correctly calculating derived metrics (CPC, CPA, CPL)
- **Preservation**: Existing behaviors that must remain unchanged - account-level metrics display, campaign-level breakdowns, SEO/Recommendations rows, formatting, and report structure
- **ROWS**: The global data structure in report_0106.py containing all report rows with metrics (shows, visits/clicks, CTR, CPC, leads, conversion rates, CPA, targeted leads, CPL, costs)
- **Master Reports**: Yandex.Direct's reporting tool that provides actual campaign performance data (costs, clicks, impressions, conversions)
- **Account**: A Yandex.Direct advertising account (e-20010227, e-17228851, dune-group, porg-3uieikjn)
- **Derived Metrics**: Calculated values based on raw data - CPC (cost per click), CPA (cost per acquisition/lead), CPL (cost per targeted lead)

## Bug Details

### Bug Condition

The bug manifests when the script calculates total costs for the "Total" and "Yandex Direct" summary rows. The `ROWS` data structure contains hardcoded cost values in the last column (index 11) that were copied from code comments instead of being calculated from actual data sources. These hardcoded values include non-zero costs for accounts that actually had zero spending.

**Formal Specification:**
```
FUNCTION isBugCondition(accountsData)
  INPUT: accountsData = {
    'e-20010227': {spend: Number, clicks: Number, impressions: Number},
    'e-17228851': {spend: Number, clicks: Number, impressions: Number},
    'dune-group': {spend: Number, clicks: Number, impressions: Number},
    'porg-3uieikjn': {spend: Number, clicks: Number, impressions: Number}
  }
  OUTPUT: boolean
  
  // Check if any account has zero spend in actual data
  hasZeroSpendInRealData := (accountsData['e-17228851'].spend == 0) OR 
                            (accountsData['dune-group'].spend == 0) OR 
                            (accountsData['porg-3uieikjn'].spend == 0)
  
  // Check if hardcoded total in ROWS is incorrect
  hardcodedTotal := extract_numeric_value(ROWS[4][11])  // "р.96 494"
  expectedTotal := accountsData['e-20010227'].spend +
                   accountsData['e-17228851'].spend +
                   accountsData['dune-group'].spend +
                   accountsData['porg-3uieikjn'].spend
  
  RETURN hasZeroSpendInRealData AND (hardcodedTotal != expectedTotal)
END FUNCTION
```

### Examples

- **Row 4 (Total)**: Currently shows "р.96 494" in column 11 (index 11). Expected: "р.27 564" (only e-20010227 had costs)
- **Row 5 (Yandex Direct summary)**: Currently shows "р.96 494" in column 11. Expected: "р.27 564"
- **Row 6 (e-20010227)**: Currently shows "р.27 564" - CORRECT (this account actually had costs)
- **Row 10 (e-17228851)**: Currently shows "р.58 292" in column 11. Expected: "р.0" (this account had zero costs despite 465 clicks)
- **Row 15 (dune-group)**: Currently shows "р.4 707" in column 11. Expected: "р.0" (zero costs despite 151 clicks)
- **Row 18 (porg-3uieikjn)**: Currently shows "р.5 931" in column 11. Expected: "р.0" (zero costs despite 120 clicks)
- **Derived Metrics**: Row 4 CPC shows "р.34" (calculated as 96494/1541≈63). Expected: "р.18" (calculated as 27564/1541≈18)
- **Edge Case**: If all four accounts had zero costs, total should be "р.0" with derived metrics showing "-" (undefined)

## Expected Behavior

### Preservation Requirements

**Unchanged Behaviors:**
- Account e-20010227 data display (impressions=49416, clicks=805, cost=27564₽) must remain unchanged
- Campaign-level breakdowns within each account must continue to display their metrics correctly (e.g., "МК ТК // Ремонт // remont.dune-group.ru" showing 600 visits and "р.20 000" cost)
- SEO row (row 21) must continue showing 80 visits with 0 leads and no costs
- Recommendations row (row 22) must continue showing its current data
- Report formatting (BOLD_ROWS) must remain unchanged
- Report structure (column headers, row ordering) must remain unchanged
- Google Sheets integration (tab creation, data writing, formatting) must remain unchanged

**Scope:**
All calculations and display logic that do NOT involve aggregating account-level costs into summary rows should be completely unaffected by this fix. This includes:
- Individual account metric displays (CTR, CPC for single accounts)
- Campaign-level data within accounts
- SEO and Recommendations channel data
- All formatting and styling logic
- Google Sheets API interaction logic

## Hypothesized Root Cause

Based on the bug description and code analysis, the most likely root causes are:

1. **Hardcoded Values in Data Structure**: The ROWS list contains hardcoded string values (e.g., "р.96 494", "р.58 292") that were manually entered based on comment values instead of being calculated from actual data sources. The script lacks any dynamic calculation logic to aggregate costs from actual Master Reports data.

2. **Missing Data Integration**: The script contains cost data in comments at the top (lines 10-13) but does not parse or use these values programmatically. There's no integration with actual Yandex.Direct Master Reports API or file parsing to retrieve real-time data.

3. **Manual Data Entry Process**: The development workflow appears to involve manually copying values from comments or external sources into the ROWS array, creating opportunities for copy-paste errors and stale data usage.

4. **No Data Validation**: The script lacks validation logic to verify that account-level costs sum to the total, allowing inconsistent values to persist undetected (e.g., account rows showing 96,494₽ total when individual accounts sum to only 27,564₽).

## Correctness Properties

Property 1: Bug Condition - Correct Total Cost Calculation

_For any_ set of account data where at least one account has zero actual costs but the hardcoded total in ROWS reflects non-zero costs for that account, the fixed script SHALL calculate and display the total cost as the sum of actual account costs (27,564₽ for the 01.06-07.06 period), correctly updating the "Total" row (row 4, column 11) and "Yandex Direct" row (row 5, column 11) to show "р.27 564".

**Validates: Requirements 2.1, 2.2, 2.3, 2.4**

Property 2: Preservation - Non-Cost Data and Individual Account Metrics

_For any_ data that is NOT related to aggregate cost calculations in summary rows (rows 4-5), the fixed script SHALL produce exactly the same output as the original script, preserving all account-level data displays (impressions, clicks for e-20010227), campaign-level breakdowns (visits and costs for individual campaigns), SEO/Recommendations rows, formatting (BOLD_ROWS), and report structure.

**Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5, 3.6**

## Fix Implementation

### Changes Required

Assuming our root cause analysis is correct (hardcoded values in ROWS data structure):

**File**: `report_0106.py`

**Function/Section**: ROWS data structure definition (lines ~36-66)

**Specific Changes**:
1. **Update Row 4 (Total) - Column 11**: Change from `"р.96 494"` to `"р.27 564"`
   - This row aggregates all channels (Yandex Direct + SEO + Recommendations)
   - Since only Yandex Direct has costs (27,564₽) and SEO/Recommendations have 0₽, total is 27,564₽

2. **Update Row 5 (Yandex Direct summary) - Column 11**: Change from `"р.96 494"` to `"р.27 564"`
   - This row aggregates the four Yandex Direct accounts
   - Only e-20010227 had actual costs of 27,564₽

3. **Update Row 4 (Total) - Derived Metrics**: Recalculate CPC, CPA, CPL based on correct total of 27,564₽
   - Column 4 (CPC): Change from `cpc(96494,1541)` to `cpc(27564,1541)` → "р.18" (currently shows higher value)
   - Column 7 (CPA): Change from `"р.8 772"` to `"р.2 506"` (27564/11≈2506)
   - Column 10 (CPL): Change from `"р.13 785"` to `"р.3 938"` (27564/7≈3938)

4. **Update Row 5 (Yandex Direct) - Derived Metrics**: Recalculate CPC, CPA, CPL based on correct total of 27,564₽
   - Column 4 (CPC): Change from `cpc(96494,1541)` to `cpc(27564,1541)` → "р.18"
   - Column 7 (CPA): Change from `"р.8 772"` to `"р.2 506"`
   - Column 10 (CPL): Change from `"р.13 785"` to `"р.3 938"`

5. **Update Row 10 (e-17228851) - Column 11**: Change from `"р.58 292"` to `"р.0"` (zero actual costs)
   - This account had clicks but zero spending according to actual data

6. **Update Row 15 (dune-group) - Column 11**: Change from `"р.4 707"` to `"р.0"` (zero actual costs)

7. **Update Row 18 (porg-3uieikjn) - Column 11**: Change from `"р.5 931"` to `"р.0"` (zero actual costs)

8. **Add Code Comments**: Update the top-level comments (lines 10-13) to clarify which accounts had zero costs and document the correct total calculation

**Alternative Long-term Solution** (not part of this immediate fix):
- Parse actual data from Master Reports Excel files in the `1-7.06` directory
- Implement dynamic calculation of totals from parsed data
- Add data validation to ensure account costs sum to totals

## Testing Strategy

### Validation Approach

The testing strategy follows a two-phase approach: first, surface counterexamples that demonstrate the bug on unfixed code (exploratory testing), then verify the fix works correctly (fix checking) and preserves existing behavior (preservation checking).

Since this is a data-correction bug in a hardcoded data structure rather than a logic bug, exploratory testing will focus on confirming that the hardcoded values are indeed incorrect by comparing them to actual Master Reports data.

### Exploratory Bug Condition Checking

**Goal**: Surface counterexamples that demonstrate the bug BEFORE implementing the fix. Confirm that hardcoded values in ROWS do not match actual data from source systems. Verify our root cause hypothesis that incorrect comment values are being used.

**Test Plan**: Create a test that extracts cost values from the ROWS data structure and compares them against expected actual values from Master Reports data (27564, 0, 0, 0). Run this test on the UNFIXED code to observe failures demonstrating the bug.

**Test Cases**:
1. **Total Cost Verification**: Extract ROWS[4][11] (will fail on unfixed code)
   - Unfixed: "р.96 494"
   - Expected: "р.27 564"
   - Status: WILL FAIL - demonstrates bug
   
2. **Yandex Direct Summary Cost**: Extract ROWS[5][11] (will fail on unfixed code)
   - Unfixed: "р.96 494"
   - Expected: "р.27 564"
   - Status: WILL FAIL - demonstrates bug

3. **Account e-17228851 Cost**: Extract ROWS[10][11] (will fail on unfixed code)
   - Unfixed: "р.58 292"
   - Expected: "р.0"
   - Status: WILL FAIL - demonstrates zero-cost account showing non-zero

4. **Derived Metrics (CPC)**: Extract and parse ROWS[4][4] (will fail on unfixed code)
   - Unfixed: Uses cpc(96494,1541) → approximately "р.63"
   - Expected: Should use cpc(27564,1541) → approximately "р.18"
   - Status: WILL FAIL - demonstrates cascading effect of incorrect total

**Expected Counterexamples**:
- ROWS data structure contains cost values (96494, 58292, 4707, 5931) that do not match actual Master Reports data
- Possible causes: manual entry error, copy-paste from outdated comments, misunderstanding of which accounts had actual spending

### Fix Checking

**Goal**: Verify that for all inputs where the bug condition holds (incorrect hardcoded costs), the fixed function produces the expected behavior (correct costs and derived metrics).

**Pseudocode:**
```
FOR ALL accountsData WHERE isBugCondition(accountsData) DO
  // After fix, extract values from ROWS
  totalCost := extract_numeric(ROWS_fixed[4][11])
  directCost := extract_numeric(ROWS_fixed[5][11])
  e17228851Cost := extract_numeric(ROWS_fixed[10][11])
  duneGroupCost := extract_numeric(ROWS_fixed[15][11])
  porgCost := extract_numeric(ROWS_fixed[18][11])
  
  // Verify correct costs
  ASSERT totalCost == 27564
  ASSERT directCost == 27564
  ASSERT e17228851Cost == 0
  ASSERT duneGroupCost == 0
  ASSERT porgCost == 0
  
  // Verify derived metrics use correct total
  totalCPC := extract_numeric(ROWS_fixed[4][4])
  ASSERT totalCPC == int(27564/1541)  // ≈18
  
  totalCPA := extract_numeric(ROWS_fixed[4][7])
  ASSERT totalCPA == int(27564/11)  // ≈2506
  
  totalCPL := extract_numeric(ROWS_fixed[4][10])
  ASSERT totalCPL == int(27564/7)  // ≈3938
END FOR
```

### Preservation Checking

**Goal**: Verify that for all data and calculations where the bug condition does NOT hold (non-aggregated costs, other metrics, formatting), the fixed script produces the same result as the original script.

**Pseudocode:**
```
FOR ALL data WHERE NOT isBugCondition(data) DO
  // Verify account e-20010227 data unchanged
  ASSERT ROWS_original[6] == ROWS_fixed[6]
  
  // Verify campaign-level rows unchanged
  ASSERT ROWS_original[7] == ROWS_fixed[7]  // МК ТК // Ремонт
  ASSERT ROWS_original[8] == ROWS_fixed[8]  // Поиск/РСЯ Главная
  ASSERT ROWS_original[9] == ROWS_fixed[9]  // Поиск/РСЯ доп.домен
  
  // Verify SEO and Recommendations rows unchanged
  ASSERT ROWS_original[21] == ROWS_fixed[21]  // SEO
  ASSERT ROWS_original[22] == ROWS_fixed[22]  // Рекомендации
  
  // Verify formatting unchanged
  ASSERT BOLD_ROWS_original == BOLD_ROWS_fixed
  
  // Verify report structure unchanged
  ASSERT len(ROWS_original) == len(ROWS_fixed)
  ASSERT ROWS_original[3] == ROWS_fixed[3]  // Headers row
END FOR
```

**Testing Approach**: Property-based testing is NOT strictly necessary for this fix since we're correcting hardcoded data values rather than fixing algorithmic logic. However, preservation checking is critical because:
- The report has many rows and columns that must remain unchanged
- We need to ensure the fix doesn't accidentally modify campaign-level data
- We need to verify that formatting and structure remain intact

**Test Plan**: Create a snapshot test that captures the UNFIXED ROWS data structure, then after applying the fix, compare all rows EXCEPT the modified ones (rows 4, 5, 10, 15, 18) to ensure they remain identical.

**Test Cases**:
1. **Account e-20010227 Data Preservation**: Verify row 6 shows impressions=49416, clicks=805, cost=27564₽ (unchanged)
2. **Campaign Data Preservation**: Verify all campaign rows (7-9, 11-14, 16-17, 19-20) show the same visits and costs
3. **SEO/Recommendations Preservation**: Verify rows 21-22 remain unchanged (80 visits for SEO, empty data for Recommendations)
4. **Formatting Preservation**: Verify BOLD_ROWS list remains [0, 3, 4, 5, 6, 20, 25, 26] (if row indices don't change)
5. **Structure Preservation**: Verify total number of rows, column count, and header row content remain unchanged

### Unit Tests

- Test extraction of numeric values from formatted cost strings ("р.96 494" → 96494)
- Test that ROWS[4][11] equals "р.27 564" after fix
- Test that ROWS[5][11] equals "р.27 564" after fix
- Test that ROWS[10][11], ROWS[15][11], ROWS[18][11] equal "р.0" after fix
- Test that derived metrics (CPC, CPA, CPL) in rows 4-5 use the corrected total of 27,564₽
- Test that account e-20010227 row (row 6) remains unchanged
- Test that campaign-level rows (7-9, 11-14, 16-17, 19-20) remain unchanged

### Property-Based Tests

Since this is a data correction bug rather than an algorithmic bug, property-based testing is less applicable. However, we could implement:
- Generate random cost values for four accounts and verify that the total in row 4 always equals the sum of account costs in rows 6, 10, 15, 18
- Generate random leads/clicks values and verify that derived metrics (CPC, CPA, CPL) are calculated correctly using the cost total
- Test that formatting is preserved across different ROWS configurations

### Integration Tests

- Run the complete script on the fixed code and verify the generated Google Sheets tab contains correct costs
- Verify that the Google Sheets output shows "р.27 564" in cells corresponding to "Total" and "Yandex Direct" cost columns
- Verify that derived metrics in the spreadsheet match expected calculations (CPC≈18, CPA≈2506, CPL≈3938)
- Test the full flow: service account authentication → sheet creation → data writing → formatting application
- Verify that the script completes without errors and outputs the success message with correct tab name
