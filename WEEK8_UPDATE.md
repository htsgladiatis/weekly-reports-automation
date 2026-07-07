# Week 8 Dashboard Update — 30.06.2026

## ✅ Completed Tasks

### Data Analysis
Analyzed new data files for week 8 (22.06–30.06):
- **Leads data**: `001.csv` — 40 total leads, **7 target leads**
- **Yandex.Direct data**: 4 CSV files from `22-30/` folder

### Week 8 Summary (22.06–30.06)

#### Lead Attribution
- **Direct (Marquiz)**: 4 target leads from e-20010227 account
- **SEO**: 0 target leads
- **Other/Calls**: 3 target leads
- **Total Target Leads**: 7 (100% conversion rate)

#### Yandex.Direct Performance by Account

| Account | Impressions | Clicks | Spend (₽) |
|---------|------------|--------|-----------|
| e-20010227 | 91,107 | 593 | 29,682.94 |
| e-17228851 | 61,013 | 40 | 0.00 |
| porg-3uieikjn | 440 | 20 | 0.00 |
| dune-group | 0 | 0 | 0.00 |
| **TOTAL** | **152,560** | **653** | **29,683** |

#### Key Metrics
- **CTR**: 0.43%
- **CPC**: 45₽
- **CPA**: 4,240₽
- **CPL (target)**: 4,240₽
- **Conversion Rate (Lead)**: 1.07%
- **Conversion Rate (Target)**: 100%
- **SEO Visits**: 22 (actual data from Yandex Webmaster for 22.06-28.06)

### Dashboard Changes

1. **Added Week 8** to `weeks` array in `index.html`:
   - Full metrics for w8 (22.06–30.06)
   - Breakdown by all 4 accounts
   - Lead attribution: 4 Direct + 3 Other

2. **Updated June Month** structure:
   - Changed weeks from `['w5', 'w6', 'w7']` to `['w5', 'w6', 'w7', 'w8']`
   - Updated date range from `01.06–21.06` to `01.06–30.06`

### Data Sources

**Leads**: `001.csv`
- Total rows: 40 leads
- Target leads identified: 7
- Attribution logic: marquiz → e-20010227

**Yandex.Direct**:
- `22-30/2026-06-30_10-26-08_e-20010227.csv` — 1.8MB (main campaign with spend)
- `22-30/2026-06-30_10-26-54_e-17228851.csv` — 4.6KB (no spend, 40 clicks)
- `22-30/2026-06-30_10-27-33_porg-3uieikjn.csv` — 1.3KB (no spend, 20 clicks)
- `22-30/2026-06-30_10-28-21_dune-group.csv` — 233 bytes (no activity)

**Yandex Webmaster (SEO)**:
- `22-30/dune-group.ru_9b46ecd81cec5bda34aed504.csv` — Search queries data (22 clicks for 22.06-28.06)
- `22-30/dune-group.ru_fd9c94cb5c0ee3de381fb949.csv` — Landing pages data (21 clicks for 22.06-28.06)

## June 2026 — Complete Month Summary

With week 8 added, June now has **4 weeks** of data:

| Week | Period | Target Leads | Spend (₽) | CPA (₽) |
|------|--------|--------------|-----------|---------|
| w5 | 01.06–07.06 | 8 | 27,564 | 3,446 |
| w6 | 08.06–14.06 | 3 | 29,894 | 9,965 |
| w7 | 15.06–21.06 | 12 | 29,954 | 2,496 |
| w8 | 22.06–30.06 | 7 | 29,683 | 4,240 |
| **Total** | **Jun 2026** | **30** | **117,095** | **3,903** |

## Dashboard Features

✅ **Month/Week Toggle**: Switch between weekly breakdown and monthly aggregates  
✅ **Week Dropdown**: Select "Все недели/месяцы" or specific period  
✅ **KPI Cards**: Auto-update based on selected period  
✅ **Charts**: Show weekly data points when month selected  
✅ **SEO Analytics**: Integrated from weeks structure  
✅ **Detailed Tables**: Account and campaign breakdowns  

## What's Missing? ❓

Week 8 data is complete! All sources have been integrated:
- ✅ Leads data from `001.csv`
- ✅ Yandex.Direct performance from all 4 accounts
- ✅ SEO clicks from Yandex Webmaster (22.06-28.06)

**Note**: SEO data is available for 22.06-28.06 (7 days). If you have Yandex Webmaster data for 29.06-30.06, I can update the SEO clicks count.

---

**Dashboard URL**: https://htsgladiatis.github.io/weekly-reports-automation/  
**Last Updated**: 30.06.2026  
**Status**: ✅ Week 8 data integrated and dashboard actualized
