# Requirements Document

## Introduction

This document specifies requirements for the Automated Weekly Report feature for generating marketing analytics reports for the period 29.06–05.07.2026. The system automates data collection from multiple sources (Yandex.Direct, Bitrix24 CRM, Yandex.Metrika) and generates comprehensive weekly reports published to Google Sheets.

## Glossary

- **Report_System**: The automated weekly reporting system
- **Yandex_Direct**: Yandex advertising platform providing campaign performance data
- **Bitrix24_CRM**: Customer relationship management system storing lead information
- **Yandex_Metrika**: Web analytics platform tracking SEO performance
- **CSV_File**: Comma-separated values file containing Yandex.Direct export data
- **Google_Sheets**: Cloud spreadsheet service for report output
- **Lead**: A potential customer contact record in CRM
- **Target_Lead**: A qualified lead marked with status "S" in CRM
- **Advertising_Account**: Yandex.Direct account identifier (e-20010227, e-17228851, dune-group, porg-3uieikjn)
- **Campaign**: Individual advertising campaign within an account
- **Traffic_Channel**: Source of website traffic (direct, seo, recommendations)
- **Week_Period**: Seven-day reporting period from Sunday to Saturday
- **Report_Tab**: Individual worksheet within Google Sheets spreadsheet
- **Metrics_Calculator**: Component computing derived metrics (CTR, CPC, CPA, CPL)

## Requirements

### Requirement 1

**User Story:** As a marketing analyst, I want the system to automatically collect Yandex.Direct data from CSV files, so that I can generate reports without manual data entry

#### Acceptance Criteria

1. WHEN a CSV_File is provided with Yandex.Direct data, THE Report_System SHALL parse the file and extract campaign statistics
2. THE CSV_File SHALL contain columns: Account, Campaign, Impressions, Clicks, Spend
3. THE Report_System SHALL support UTF-8 encoding for CSV_File reading
4. THE Report_System SHALL aggregate impressions, clicks, and spend by Advertising_Account
5. THE Report_System SHALL preserve individual Campaign data within each Advertising_Account
6. IF the CSV_File is missing or unreadable, THEN THE Report_System SHALL display an error message and halt execution
7. THE Report_System SHALL recognize four Advertising_Account identifiers: e-20010227, e-17228851, dune-group, porg-3uieikjn

### Requirement 2

**User Story:** As a marketing analyst, I want the system to retrieve lead data from Bitrix24 CRM, so that I can analyze conversion metrics

#### Acceptance Criteria

1. WHEN the Week_Period is specified, THE Report_System SHALL fetch all leads created within that period from Bitrix24_CRM
2. THE Report_System SHALL use the Bitrix24 REST API with webhook authentication
3. THE Report_System SHALL extract lead fields: ID, TITLE, STATUS_ID, SOURCE_ID, DATE_CREATE, UTM_SOURCE, UTM_MEDIUM, UTM_CAMPAIGN
4. THE Report_System SHALL classify each Lead by Advertising_Account based on UTM_CAMPAIGN parameter
5. THE Report_System SHALL identify Target_Lead records by STATUS_ID equal to "S"
6. THE Report_System SHALL exclude leads with STATUS_ID in ["F", "JUNK", "SPAM"] from statistics
7. THE Report_System SHALL classify leads by Traffic_Channel using UTM_SOURCE and SOURCE_ID
8. IF the Bitrix24_CRM API fails, THEN THE Report_System SHALL use zero values for lead metrics and display a warning

### Requirement 3

**User Story:** As a marketing analyst, I want the system to collect SEO data from Yandex.Metrika, so that I can measure organic traffic performance

#### Acceptance Criteria

1. WHEN the Week_Period is specified, THE Report_System SHALL fetch organic traffic statistics from Yandex_Metrika
2. THE Report_System SHALL use counter ID 90747520 for dune-group.ru
3. THE Report_System SHALL filter data by traffic source equal to "organic"
4. THE Report_System SHALL retrieve metrics: visits, users, bounce_rate, page_depth, avg_duration
5. THE Report_System SHALL fetch top 5 landing pages with visits and bounce rates
6. THE Report_System SHALL retrieve top 5 search queries with visit counts
7. IF the Yandex_Metrika API fails, THEN THE Report_System SHALL use zero values for SEO metrics and display a warning

### Requirement 4

**User Story:** As a marketing analyst, I want the system to calculate marketing performance metrics, so that I can evaluate campaign effectiveness

#### Acceptance Criteria

1. THE Metrics_Calculator SHALL compute CTR as (clicks / impressions) × 100 for each Advertising_Account
2. THE Metrics_Calculator SHALL compute CPC as (spend / clicks) for each Advertising_Account
3. THE Metrics_Calculator SHALL compute conversion rate as (leads / clicks) × 100 for each Advertising_Account
4. THE Metrics_Calculator SHALL compute CPA as (spend / total_leads) for each Advertising_Account
5. THE Metrics_Calculator SHALL compute target conversion rate as (target_leads / total_leads) × 100 for each Advertising_Account
6. THE Metrics_Calculator SHALL compute CPL as (spend / target_leads) for each Advertising_Account
7. THE Metrics_Calculator SHALL compute SEO conversion as (seo_leads / seo_visits) × 100
8. IF clicks equal zero, THEN THE Metrics_Calculator SHALL display CPC as "р.0"
9. IF total_leads equal zero, THEN THE Metrics_Calculator SHALL display CPA as "-"
10. IF target_leads equal zero, THEN THE Metrics_Calculator SHALL display CPL as "-"

### Requirement 5

**User Story:** As a marketing analyst, I want the system to generate Python report scripts, so that I can create formatted reports in Google Sheets

#### Acceptance Criteria

1. WHEN data collection is complete, THE Report_System SHALL generate a Python script file named report_DDMM.py
2. THE Report_System SHALL format the script filename using the Week_Period start date (DD = day, MM = month)
3. THE Python script SHALL contain week label in format "DD.MM.2026–DD.MM.2026"
4. THE Python script SHALL define Report_Tab name in format "DD.MM-DD.MM"
5. THE Python script SHALL include aggregated statistics for all Advertising_Account entries
6. THE Python script SHALL include Campaign-level details for each Advertising_Account
7. THE Python script SHALL include SEO statistics row with visits and lead counts
8. THE Python script SHALL define BOLD_ROWS list specifying which rows should have bold formatting
9. THE Python script SHALL use Google Sheets API with service account credentials from credentials.json
10. THE Python script SHALL contain hardcoded spreadsheet ID "1TMa7NMknshntaQE-Dgmr-Trjk3pQxvY_K1IyAYfjZ4A"

### Requirement 6

**User Story:** As a marketing analyst, I want the system to format reports consistently, so that reports are easy to read and compare

#### Acceptance Criteria

1. THE Report_System SHALL format monetary values with "р." prefix and thousand separators
2. THE Report_System SHALL format percentages with two decimal places and "%" suffix
3. THE Report_System SHALL format CTR values with two decimal places
4. THE Report_System SHALL use comma as decimal separator for Russian locale
5. THE Report_System SHALL display dash "-" for undefined metric values
6. THE Report_System SHALL set column A width to 380 pixels for campaign names
7. THE Report_System SHALL apply bold formatting to header rows and summary rows
8. WHEN creating the Report_Tab, THE Report_System SHALL delete any existing tab with the same name
9. THE Report_System SHALL position the new Report_Tab as the first sheet in the spreadsheet

### Requirement 7

**User Story:** As a marketing analyst, I want the system to display data collection progress, so that I can monitor the automation process

#### Acceptance Criteria

1. WHEN the Report_System starts execution, THE Report_System SHALL display the Week_Period being processed
2. THE Report_System SHALL display status messages when loading Yandex_Direct data
3. THE Report_System SHALL display status messages when loading Bitrix24_CRM data
4. THE Report_System SHALL display status messages when loading Yandex_Metrika data
5. WHEN data collection completes, THE Report_System SHALL display a summary table with key metrics
6. THE summary table SHALL include total spend, clicks, impressions, CTR, and CPC from Yandex_Direct
7. THE summary table SHALL include total leads, target leads, CPA, and CPL from all sources
8. THE summary table SHALL include SEO visits and lead counts from Yandex_Metrika
9. IF any data source fails, THEN THE Report_System SHALL display a warning message but continue processing

### Requirement 8

**User Story:** As a marketing analyst, I want the system to validate input data, so that I can trust the generated reports

#### Acceptance Criteria

1. THE Report_System SHALL verify that Week_Period start date is before or equal to end date
2. THE Report_System SHALL verify that CSV_File exists before attempting to parse
3. THE Report_System SHALL verify that CSV_File contains required columns before processing
4. THE Report_System SHALL validate that numeric values in CSV_File are non-negative
5. THE Report_System SHALL verify that Advertising_Account names match expected identifiers
6. IF validation fails, THEN THE Report_System SHALL display a descriptive error message
7. IF validation fails, THEN THE Report_System SHALL terminate execution with non-zero exit code

### Requirement 9

**User Story:** As a marketing analyst, I want the system to handle the specific week 29.06-05.07.2026, so that I can generate the July report

#### Acceptance Criteria

1. THE Report_System SHALL accept Week_Period start date "2026-06-29"
2. THE Report_System SHALL accept Week_Period end date "2026-07-05"
3. THE Report_System SHALL generate script filename "report_2906.py"
4. THE Report_System SHALL create Report_Tab name "29.06-05.07"
5. THE Report_System SHALL format week label as "29.06.2026–05.07.2026"
6. THE Report_System SHALL process data files from folder "05.07"
7. THE Report_System SHALL load Yandex.Direct CSV files from "05.07/111" subdirectory

### Requirement 10

**User Story:** As a marketing analyst, I want the system to use existing API clients, so that I can leverage tested integration code

#### Acceptance Criteria

1. THE Report_System SHALL import get_lead_stats function from bitrix_api module
2. THE Report_System SHALL import get_seo_visits function from metrika_seo module
3. THE Report_System SHALL import get_top_landing_pages function from metrika_seo module
4. THE Report_System SHALL import get_search_queries function from metrika_seo module
5. THE Report_System SHALL use OAuth token from metrika_seo module for Yandex_Metrika authentication
6. THE Report_System SHALL use webhook URL from bitrix_api module for Bitrix24_CRM authentication
7. THE Report_System SHALL handle ImportError exceptions when modules are unavailable
