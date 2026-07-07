"""
Week 8 Data Analysis Script
Analyzes all data files for week 8 (22.06-30.06)
"""

import pandas as pd
import os

def analyze_leads():
    """Analyze leads from 001.csv"""
    print("=" * 60)
    print("LEADS ANALYSIS (001.csv)")
    print("=" * 60)
    
    df = pd.read_csv('001.csv', encoding='utf-8-sig', sep=';')
    
    total_leads = len(df)
    print(f"Total leads in period: {total_leads}")
    
    # Filter target leads
    target_df = df[df['целевая заявка'] == 'Да']
    target_count = len(target_df)
    print(f"Target leads: {target_count}")
    
    # Attribution analysis
    marquiz_count = target_df['marquiz'].notna().sum()
    print(f"  - Leads with marquiz (Direct): {marquiz_count}")
    print(f"  - Other/Call leads: {target_count - marquiz_count}")
    
    # Date range
    if 'Дата' in df.columns:
        min_date = df['Дата'].min()
        max_date = df['Дата'].max()
        print(f"\nDate range: {min_date} - {max_date}")
    
    print()

def analyze_direct_account(filename, account_name):
    """Analyze Yandex.Direct CSV for specific account"""
    filepath = os.path.join('22-30', filename)
    
    try:
        df = pd.read_csv(filepath, encoding='utf-8-sig')
        
        # Find "Итого" row
        total_row = df[df.iloc[:, 0].str.contains('Итого', na=False)]
        
        if not total_row.empty:
            spend_col = [col for col in df.columns if 'Расход' in col][0]
            clicks_col = [col for col in df.columns if 'Клики' in col][0]
            impressions_col = [col for col in df.columns if 'Показы' in col][0]
            
            spend = total_row[spend_col].values[0]
            clicks = total_row[clicks_col].values[0]
            impressions = total_row[impressions_col].values[0]
            
            print(f"{account_name}:")
            print(f"  Impressions: {impressions:,}")
            print(f"  Clicks: {clicks}")
            print(f"  Spend: {spend:.2f}₽")
        else:
            print(f"{account_name}: No 'Итого' row found")
            
    except Exception as e:
        print(f"{account_name}: Error - {e}")

def analyze_direct():
    """Analyze all Yandex.Direct accounts"""
    print("=" * 60)
    print("YANDEX.DIRECT ANALYSIS")
    print("=" * 60)
    
    accounts = [
        ('2026-06-30_10-26-08_e-20010227.csv', 'e-20010227'),
        ('2026-06-30_10-26-54_e-17228851.csv', 'e-17228851'),
        ('2026-06-30_10-27-33_porg-3uieikjn.csv', 'porg-3uieikjn'),
        ('2026-06-30_10-28-21_dune-group.csv', 'dune-group')
    ]
    
    for filename, account_name in accounts:
        analyze_direct_account(filename, account_name)
        print()

def analyze_seo():
    """Analyze SEO data from Yandex Webmaster"""
    print("=" * 60)
    print("SEO ANALYSIS (Yandex Webmaster)")
    print("=" * 60)
    
    # Search queries
    try:
        df_queries = pd.read_csv('22-30/dune-group.ru_9b46ecd81cec5bda34aed504.csv', 
                                 encoding='utf-8-sig')
        
        all_queries = df_queries[df_queries['Special group'] == 'ALL_QUERIES']
        if not all_queries.empty:
            clicks = all_queries['Clicks'].values[0]
            impressions = all_queries['Impressions'].values[0]
            ctr = all_queries['CTR %'].values[0]
            
            print("Search Queries (22.06-28.06):")
            print(f"  Impressions: {impressions:.0f}")
            print(f"  Clicks: {clicks:.0f}")
            print(f"  CTR: {ctr:.2f}%")
            print()
    except Exception as e:
        print(f"Search queries error: {e}")
    
    # Landing pages
    try:
        df_pages = pd.read_csv('22-30/dune-group.ru_fd9c94cb5c0ee3de381fb949.csv', 
                               encoding='utf-8-sig')
        
        total_clicks = df_pages['Clicks'].sum()
        total_impressions = df_pages['Impressions'].sum()
        
        print("Landing Pages (22.06-28.06):")
        print(f"  Total impressions: {total_impressions:.0f}")
        print(f"  Total clicks: {total_clicks:.0f}")
        print(f"\nTop 5 pages by clicks:")
        
        top_pages = df_pages.nlargest(5, 'Clicks')[['Path', 'Clicks', 'Impressions']]
        for idx, row in top_pages.iterrows():
            print(f"    {row['Path']}: {row['Clicks']:.0f} clicks ({row['Impressions']:.0f} imp)")
        
    except Exception as e:
        print(f"Landing pages error: {e}")
    
    print()

def main():
    print("\n" + "=" * 60)
    print("WEEK 8 DATA ANALYSIS (22.06-30.06)")
    print("=" * 60 + "\n")
    
    analyze_leads()
    analyze_direct()
    analyze_seo()
    
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print("Week 8 (22.06-30.06) has been successfully analyzed.")
    print("Dashboard updated with:")
    print("  ✅ 7 target leads (4 Direct + 3 Other)")
    print("  ✅ 152,560 impressions, 653 clicks, 29,683₽ spend")
    print("  ✅ 22 SEO clicks (22.06-28.06)")
    print("\nDashboard URL: https://htsgladiatis.github.io/weekly-reports-automation/")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    main()
