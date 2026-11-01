"""
SaaS Customer LTV & Churn Analytics — Main Pipeline
====================================================
Orchestrates the complete end-to-end analytics pipeline:
1. Generate/load raw data
2. Clean and validate data
3. Perform feature engineering
4. Generate EDA visualizations
5. Load data into SQLite database
6. Execute SQL business analysis
7. Perform LTV analysis
8. Perform cohort and retention analysis
9. Generate dashboard-ready CSV exports
10. Generate business insights report

Usage:
    python main.py
"""

import os
import sys
import logging
import sqlite3
import json
from datetime import datetime

import pandas as pd
import numpy as np

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

from src.data_generation import generate_dataset
from src.data_cleaning import run_cleaning_pipeline
from src.eda import run_eda
from src.customer_analysis import run_customer_analysis
from src.revenue_analysis import run_revenue_analysis
from src.ltv_analysis import run_ltv_analysis
from src.cohort_analysis import run_cohort_analysis

# ── Logging Configuration ─────────────────────────────────────────────────
LOG_FORMAT = '%(asctime)s — %(levelname)s — %(name)s — %(message)s'
LOG_FILE = os.path.join(PROJECT_ROOT, 'pipeline.log')

logging.basicConfig(
    level=logging.INFO,
    format=LOG_FORMAT,
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(LOG_FILE, mode='w', encoding='utf-8'),
    ]
)
logger = logging.getLogger('main')

# ── Path Configuration ─────────────────────────────────────────────────────
RAW_DATA_PATH = os.path.join(PROJECT_ROOT, 'data', 'raw', 'saas_customer_data.csv')
CLEANED_DATA_PATH = os.path.join(PROJECT_ROOT, 'data', 'processed', 'saas_customer_cleaned.csv')
DB_PATH = os.path.join(PROJECT_ROOT, 'saas_analytics.db')
CHARTS_DIR = os.path.join(PROJECT_ROOT, 'dashboard', 'charts')
EXPORTS_DIR = os.path.join(PROJECT_ROOT, 'dashboard', 'exports')
REPORTS_DIR = os.path.join(PROJECT_ROOT, 'reports')
SQL_DIR = os.path.join(PROJECT_ROOT, 'sql')


def create_directories():
    """Create all required output directories."""
    dirs = [
        os.path.join(PROJECT_ROOT, 'data', 'raw'),
        os.path.join(PROJECT_ROOT, 'data', 'processed'),
        CHARTS_DIR,
        EXPORTS_DIR,
        REPORTS_DIR,
        os.path.join(PROJECT_ROOT, 'tests'),
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)
    logger.info("Output directories created")


def step_1_generate_data() -> pd.DataFrame:
    """Step 1: Generate or load raw dataset."""
    logger.info("=" * 70)
    logger.info("STEP 1: DATA GENERATION")
    logger.info("=" * 70)

    if os.path.exists(RAW_DATA_PATH):
        logger.info(f"Raw data already exists at {RAW_DATA_PATH}")
        df = pd.read_csv(RAW_DATA_PATH)
        logger.info(f"Loaded existing raw data: {df.shape}")
    else:
        df = generate_dataset(RAW_DATA_PATH)
        logger.info(f"Generated new dataset: {df.shape}")

    return df


def step_2_clean_data() -> pd.DataFrame:
    """Step 2: Clean, validate, and engineer features."""
    logger.info("=" * 70)
    logger.info("STEP 2: DATA CLEANING & FEATURE ENGINEERING")
    logger.info("=" * 70)

    df = run_cleaning_pipeline(RAW_DATA_PATH, CLEANED_DATA_PATH)
    logger.info(f"Cleaned data: {df.shape}")
    return df


def step_3_eda(df: pd.DataFrame) -> dict:
    """Step 3: Generate all EDA visualizations."""
    logger.info("=" * 70)
    logger.info("STEP 3: EXPLORATORY DATA ANALYSIS")
    logger.info("=" * 70)

    insights = run_eda(df, CHARTS_DIR)
    logger.info(f"Generated {len(insights)} EDA charts")
    return insights


def step_4_load_to_sql(df: pd.DataFrame):
    """Step 4: Load cleaned data into SQLite database."""
    logger.info("=" * 70)
    logger.info("STEP 4: LOADING DATA INTO SQLITE DATABASE")
    logger.info("=" * 70)

    conn = sqlite3.connect(DB_PATH)
    df.to_sql('customers', conn, if_exists='replace', index=False)

    # Verify
    count = pd.read_sql('SELECT COUNT(*) AS cnt FROM customers', conn).iloc[0, 0]
    logger.info(f"Loaded {count} rows into SQLite database: {DB_PATH}")
    conn.close()


def step_5_run_sql_analysis() -> dict:
    """Step 5: Execute all SQL business analysis queries."""
    logger.info("=" * 70)
    logger.info("STEP 5: SQL BUSINESS ANALYSIS")
    logger.info("=" * 70)

    conn = sqlite3.connect(DB_PATH)
    sql_results = {}

    sql_files = [
        'customer_analysis.sql',
        'revenue_analysis.sql',
        'churn_analysis.sql',
        'ltv_analysis.sql',
        'cohort_analysis.sql',
    ]

    for sql_file in sql_files:
        filepath = os.path.join(SQL_DIR, sql_file)
        if not os.path.exists(filepath):
            logger.warning(f"SQL file not found: {filepath}")
            continue

        logger.info(f"Executing: {sql_file}")
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Split into individual queries (separated by --)
        queries = []
        current_query = []
        current_comment = ""

        for line in content.split('\n'):
            stripped = line.strip()
            if stripped.startswith('-- ') and not stripped.startswith('-- ==='):
                if current_query:
                    # Save previous query
                    query_text = '\n'.join(current_query).strip()
                    if query_text:
                        queries.append((current_comment, query_text))
                    current_query = []
                current_comment = stripped.lstrip('- ').strip()
            elif stripped and not stripped.startswith('--'):
                current_query.append(line)

        # Don't forget last query
        if current_query:
            query_text = '\n'.join(current_query).strip()
            if query_text:
                queries.append((current_comment, query_text))

        file_results = {}
        for comment, query in queries:
            try:
                result = pd.read_sql(query, conn)
                file_results[comment] = result
                logger.info(f"  ✓ {comment}: {len(result)} rows")
            except Exception as e:
                logger.error(f"  ✗ {comment}: {e}")
                file_results[comment] = f"ERROR: {e}"

        sql_results[sql_file] = file_results

    conn.close()
    logger.info(f"SQL analysis complete — {sum(len(v) for v in sql_results.values())} queries executed")
    return sql_results


def step_6_python_analysis(df: pd.DataFrame) -> dict:
    """Step 6: Run all Python analysis modules."""
    logger.info("=" * 70)
    logger.info("STEP 6: PYTHON BUSINESS ANALYSIS")
    logger.info("=" * 70)

    results = {
        'customer': run_customer_analysis(df),
        'revenue': run_revenue_analysis(df),
        'ltv': run_ltv_analysis(df),
        'cohort': run_cohort_analysis(df, CHARTS_DIR),
    }

    logger.info("Python business analysis complete")
    return results


def step_7_generate_exports(df: pd.DataFrame, analysis: dict):
    """Step 7: Generate dashboard-ready CSV exports."""
    logger.info("=" * 70)
    logger.info("STEP 7: GENERATING DASHBOARD EXPORTS")
    logger.info("=" * 70)

    os.makedirs(EXPORTS_DIR, exist_ok=True)

    # Executive overview metrics
    customer = analysis.get('customer', {})
    revenue = analysis.get('revenue', {})
    ltv = analysis.get('ltv', {})

    overview = customer.get('overview', {})
    mrr = revenue.get('mrr_metrics', {})
    ltv_overall = ltv.get('overall', {})

    exec_metrics = pd.DataFrame([{
        'Metric': 'Total Customers', 'Value': overview.get('total_customers', 0),
    }, {
        'Metric': 'Active Customers', 'Value': overview.get('active_customers', 0),
    }, {
        'Metric': 'Churned Customers', 'Value': overview.get('churned_customers', 0),
    }, {
        'Metric': 'Churn Rate (%)', 'Value': overview.get('churn_rate_pct', 0),
    }, {
        'Metric': 'MRR ($)', 'Value': mrr.get('mrr', 0),
    }, {
        'Metric': 'ARPU ($)', 'Value': mrr.get('arpu', 0),
    }, {
        'Metric': 'ARR ($)', 'Value': mrr.get('arr', 0),
    }, {
        'Metric': 'Average LTV ($)', 'Value': ltv_overall.get('avg_ltv', 0),
    }])
    exec_metrics.to_csv(os.path.join(EXPORTS_DIR, 'executive_overview.csv'), index=False)

    # Churn analysis export
    churn_export = df.groupby(['SubscriptionType', 'ContractDuration', 'CustomerSegment']).agg(
        Customers=('CustomerID', 'count'),
        ChurnRate=('ChurnFlag', 'mean'),
        AvgMonthlyCharge=('MonthlyCharges', 'mean'),
        AvgTenure=('Tenure', 'mean'),
    ).round(4).reset_index()
    churn_export['ChurnRate'] = (churn_export['ChurnRate'] * 100).round(2)
    churn_export.to_csv(os.path.join(EXPORTS_DIR, 'churn_analysis.csv'), index=False)

    # Revenue and LTV export
    ltv_export = df.groupby(['SubscriptionType', 'CustomerSegment']).agg(
        Customers=('CustomerID', 'count'),
        TotalRevenue=('TotalCharges', 'sum'),
        AvgLTV=('TotalCharges', 'mean'),
        AvgMonthlyCharge=('MonthlyCharges', 'mean'),
        AvgTenure=('Tenure', 'mean'),
    ).round(2).reset_index()
    ltv_export.to_csv(os.path.join(EXPORTS_DIR, 'revenue_ltv_analysis.csv'), index=False)

    # Cohort retention export
    cohort = analysis.get('cohort', {})
    if 'quarterly_cohorts' in cohort and isinstance(cohort['quarterly_cohorts'], pd.DataFrame):
        cohort['quarterly_cohorts'].to_csv(
            os.path.join(EXPORTS_DIR, 'cohort_retention.csv'))

    # Full cleaned dataset for Power BI
    df.to_csv(os.path.join(EXPORTS_DIR, 'full_dataset_powerbi.csv'), index=False)

    logger.info(f"Dashboard exports saved to {EXPORTS_DIR}")


def step_8_generate_report(df: pd.DataFrame, eda_insights: dict,
                            analysis: dict, sql_results: dict):
    """Step 8: Generate the business insights report."""
    logger.info("=" * 70)
    logger.info("STEP 8: GENERATING BUSINESS INSIGHTS REPORT")
    logger.info("=" * 70)

    os.makedirs(REPORTS_DIR, exist_ok=True)

    customer = analysis.get('customer', {})
    revenue = analysis.get('revenue', {})
    ltv = analysis.get('ltv', {})
    cohort = analysis.get('cohort', {})

    overview = customer.get('overview', {})
    mrr_metrics = revenue.get('mrr_metrics', {})
    ltv_overall = ltv.get('overall', {})
    at_risk = revenue.get('at_risk', {})

    report_lines = []
    report_lines.append("# SaaS Customer LTV & Churn Analytics — Business Insights Report")
    report_lines.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append("\n---\n")

    # Section 1: Executive Summary
    report_lines.append("## 1. Executive Summary\n")
    report_lines.append(f"| Metric | Value |")
    report_lines.append(f"|--------|-------|")
    report_lines.append(f"| Total Customers | {overview.get('total_customers', 'N/A'):,} |")
    report_lines.append(f"| Active Customers | {overview.get('active_customers', 'N/A'):,} |")
    report_lines.append(f"| Churned Customers | {overview.get('churned_customers', 'N/A'):,} |")
    report_lines.append(f"| Overall Churn Rate | {overview.get('churn_rate_pct', 'N/A')}% |")
    report_lines.append(f"| Monthly Recurring Revenue (MRR) | ${mrr_metrics.get('mrr', 0):,.2f} |")
    report_lines.append(f"| Average Revenue Per User (ARPU) | ${mrr_metrics.get('arpu', 0):.2f} |")
    report_lines.append(f"| Annualized Revenue Run Rate (ARR) | ${mrr_metrics.get('arr', 0):,.2f} |")
    report_lines.append(f"| Average Customer LTV | ${ltv_overall.get('avg_ltv', 0):,.2f} |")
    report_lines.append("")

    # Section 2: Key Findings
    report_lines.append("## 2. Key Findings\n")

    # Finding 1: Subscription revenue
    rev_sub = revenue.get('by_subscription')
    if isinstance(rev_sub, pd.DataFrame):
        top_sub = rev_sub['TotalRevenue'].idxmax()
        top_rev = rev_sub.loc[top_sub, 'TotalRevenue']
        top_share = rev_sub.loc[top_sub, 'RevenueShare']
        report_lines.append(f"### Finding 1: Which subscription plan generates the most revenue?")
        report_lines.append(f"**{top_sub}** generates the most total revenue at **${top_rev:,.2f}** "
                           f"({top_share}% of total revenue).\n")

    # Finding 2: Highest LTV segment
    ltv_seg = ltv.get('by_segment')
    if isinstance(ltv_seg, pd.DataFrame):
        top_seg = ltv_seg['AvgLTV'].idxmax()
        top_ltv = ltv_seg.loc[top_seg, 'AvgLTV']
        report_lines.append(f"### Finding 2: Which customer segment has the highest LTV?")
        report_lines.append(f"**{top_seg}** has the highest average LTV at **${top_ltv:,.2f}**.\n")

    # Finding 3: Highest churn subscription
    cust_subs = customer.get('subscriptions')
    if isinstance(cust_subs, pd.DataFrame):
        high_churn_sub = cust_subs['ChurnRate'].idxmax()
        high_churn_rate = cust_subs.loc[high_churn_sub, 'ChurnRate']
        report_lines.append(f"### Finding 3: Which subscription type experiences the highest churn?")
        report_lines.append(f"**{high_churn_sub}** has the highest churn rate at **{high_churn_rate}%**.\n")

    # Finding 4: Revenue lost to churn
    report_lines.append(f"### Finding 4: How much revenue is lost to churn?")
    report_lines.append(f"Monthly revenue lost: **${at_risk.get('lost_mrr', 0):,.2f}**")
    report_lines.append(f"Annualized revenue lost: **${at_risk.get('lost_arr', 0):,.2f}**")
    report_lines.append(f"Total revenue collected before churn: **${at_risk.get('total_revenue_before_churn', 0):,.2f}**\n")

    # Finding 5: Tenure and churn
    contracts = customer.get('contracts')
    if isinstance(contracts, pd.DataFrame):
        report_lines.append(f"### Finding 5: Does customer tenure influence churn?")
        for idx, row in contracts.iterrows():
            report_lines.append(f"- **{idx}**: Churn rate {row['ChurnRate']}%, "
                              f"Avg tenure {row['AvgTenure']:.1f} months")
        report_lines.append("")

    # Finding 6: Monthly charges and churn
    churn_dist = eda_insights.get('churn_by_charges', {})
    active_mean = churn_dist.get('active_mean', 0)
    churned_mean = churn_dist.get('churned_mean', 0)
    report_lines.append(f"### Finding 6: Are higher-paying customers more likely to leave?")
    report_lines.append(f"- Active customers average monthly charge: **${active_mean:.2f}**")
    report_lines.append(f"- Churned customers average monthly charge: **${churned_mean:.2f}**")
    if churned_mean > active_mean:
        report_lines.append(f"- Higher-paying customers are **slightly more likely** to churn.\n")
    else:
        report_lines.append(f"- No strong evidence that higher charges drive churn.\n")

    # Section 3: Business Recommendations
    report_lines.append("## 3. Business Recommendations\n")

    recommendations = [
        {
            'title': 'Incentivize Annual Contracts',
            'what': 'Month-to-month contracts show significantly higher churn rates.',
            'why': 'Lack of commitment makes it easy for customers to leave at any time.',
            'affected': 'All month-to-month subscribers.',
            'impact': f"Reducing month-to-month churn by 10% could retain "
                      f"${at_risk.get('lost_mrr', 0) * 0.1 * 12:,.0f} in annual revenue.",
            'action': 'Offer discounted annual plans (e.g., 15-20% off) to month-to-month '
                     'customers at the 3-month milestone.',
        },
        {
            'title': 'Proactive Support for High-Ticket Customers',
            'what': 'Customers with 3+ support tickets show elevated churn rates.',
            'why': 'Unresolved issues and poor support experiences drive dissatisfaction.',
            'affected': 'Customers in the Medium and High support ticket categories.',
            'impact': 'These customers represent significant MRR that could be retained.',
            'action': 'Implement a proactive outreach program: when a customer opens their '
                     '3rd ticket, escalate to a Customer Success Manager.',
        },
        {
            'title': 'Focus Retention Efforts on Early Tenure',
            'what': 'Customers in their first 6 months show the highest churn probability.',
            'why': 'New customers haven\'t yet realized the full value of the product.',
            'affected': 'All newly acquired customers.',
            'impact': 'Reducing early churn improves cohort LTV significantly.',
            'action': 'Implement a structured 90-day onboarding program with milestone '
                     'check-ins at days 7, 30, 60, and 90.',
        },
        {
            'title': 'Upsell Premium to Mid-Market Segment',
            'what': 'Premium subscribers generate the highest LTV.',
            'why': 'Higher monthly charges combined with better retention create compounding value.',
            'affected': 'Mid-Market customers on Basic or Standard plans.',
            'impact': 'Upselling 10% of Mid-Market Basic users to Premium could significantly increase MRR.',
            'action': 'Create a targeted upsell campaign highlighting premium features '
                     'most relevant to Mid-Market use cases.',
        },
        {
            'title': 'Enterprise Retention Program',
            'what': 'Enterprise customers have lower churn but highest individual LTV.',
            'why': 'Losing even one Enterprise customer has an outsized revenue impact.',
            'affected': 'All Enterprise segment customers.',
            'impact': 'Enterprise customers contribute disproportionately to total revenue.',
            'action': 'Assign dedicated account managers to all Enterprise accounts '
                     'and implement quarterly business reviews.',
        },
    ]

    for i, rec in enumerate(recommendations, 1):
        report_lines.append(f"### Recommendation {i}: {rec['title']}")
        report_lines.append(f"- **What happened:** {rec['what']}")
        report_lines.append(f"- **Why it may be happening:** {rec['why']}")
        report_lines.append(f"- **Who is affected:** {rec['affected']}")
        report_lines.append(f"- **Financial impact:** {rec['impact']}")
        report_lines.append(f"- **Recommended action:** {rec['action']}")
        report_lines.append("")

    # Section 4: Methodology
    report_lines.append("## 4. Methodology Notes\n")
    report_lines.append("- **Dataset:** Synthetic SaaS subscription data (5,000 customers)")
    report_lines.append("- **LTV Calculation:** Historical LTV = TotalCharges (actual revenue received)")
    report_lines.append("- **Churn Definition:** Binary label (Yes/No) based on customer status")
    report_lines.append("- **MRR:** Sum of MonthlyCharges for active (non-churned) customers")
    report_lines.append("- **ARPU:** MRR / Active customer count")
    report_lines.append("- **Cohorts:** Defined by signup month; retention = still active / cohort size")
    report_lines.append("- **No machine learning models** were used in this analysis")
    report_lines.append("")

    # Write report
    report_path = os.path.join(REPORTS_DIR, 'business_insights_report.md')
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report_lines))

    logger.info(f"Business insights report saved: {report_path}")


def main():
    """Execute the complete analytics pipeline."""
    start_time = datetime.now()
    logger.info("╔" + "═" * 68 + "╗")
    logger.info("║  SaaS Customer LTV & Churn Analytics Pipeline                     ║")
    logger.info("║  Starting execution...                                            ║")
    logger.info("╚" + "═" * 68 + "╝")

    try:
        # Setup
        create_directories()

        # Step 1: Data Generation
        raw_df = step_1_generate_data()

        # Step 2: Data Cleaning
        df = step_2_clean_data()

        # Step 3: EDA
        eda_insights = step_3_eda(df)

        # Step 4: Load to SQL
        step_4_load_to_sql(df)

        # Step 5: SQL Analysis
        sql_results = step_5_run_sql_analysis()

        # Step 6: Python Analysis
        analysis = step_6_python_analysis(df)

        # Step 7: Dashboard Exports
        step_7_generate_exports(df, analysis)

        # Step 8: Business Report
        step_8_generate_report(df, eda_insights, analysis, sql_results)

        # Summary
        elapsed = (datetime.now() - start_time).total_seconds()
        logger.info("+" + "=" * 68 + "+")
        logger.info("|  PIPELINE COMPLETE                                                |")
        logger.info(f"|  Elapsed time: {elapsed:.1f} seconds" + " " * (52 - len(f"{elapsed:.1f}")) + "|")
        logger.info("+" + "=" * 68 + "+")

        # Print summary
        print("\n" + "=" * 70)
        print("PIPELINE EXECUTION SUMMARY")
        print("=" * 70)
        print(f"  Data:       {len(df):,} customers processed")
        print(f"  Charts:     {len(eda_insights)} visualizations generated")
        print(f"  SQL:        {sum(len(v) for v in sql_results.values())} queries executed")
        print(f"  Exports:    Dashboard CSVs in dashboard/exports/")
        print(f"  Report:     reports/business_insights_report.md")
        print(f"  Database:   {DB_PATH}")
        print(f"  Time:       {elapsed:.1f} seconds")
        print("=" * 70)

    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)
        raise


if __name__ == '__main__':
    main()
