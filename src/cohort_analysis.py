"""
Cohort Analysis Module
======================
Performs acquisition cohort analysis to track customer retention and revenue
patterns over time.

Methodology:
- Cohorts defined by signup month (first month of customer subscription)
- Retention = Customers still active (Churn = 'No') / Total cohort size
- Snapshot-based retention (not event-level tracking)
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import logging

logger = logging.getLogger(__name__)


def build_cohort_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Build monthly acquisition cohort summary."""
    cohorts = df.groupby('SignupMonth').agg(
        CohortSize=('CustomerID', 'count'),
        StillActive=('Churn', lambda x: (x == 'No').sum()),
        Churned=('ChurnFlag', 'sum'),
        AvgTenure=('Tenure', 'mean'),
        AvgMonthlyCharge=('MonthlyCharges', 'mean'),
        TotalRevenue=('TotalCharges', 'sum'),
        AvgLTV=('TotalCharges', 'mean'),
    ).round(2).sort_index()

    cohorts['RetentionRate'] = (cohorts['StillActive'] / cohorts['CohortSize'] * 100).round(2)
    cohorts['ChurnRate'] = (cohorts['Churned'] / cohorts['CohortSize'] * 100).round(2)

    logger.info(f"Built {len(cohorts)} monthly cohorts")
    return cohorts


def build_quarterly_cohorts(df: pd.DataFrame) -> pd.DataFrame:
    """Build quarterly acquisition cohort summary."""
    cohorts = df.groupby('SignupQuarter').agg(
        CohortSize=('CustomerID', 'count'),
        StillActive=('Churn', lambda x: (x == 'No').sum()),
        Churned=('ChurnFlag', 'sum'),
        AvgTenure=('Tenure', 'mean'),
        TotalRevenue=('TotalCharges', 'sum'),
        AvgLTV=('TotalCharges', 'mean'),
    ).round(2).sort_index()

    cohorts['RetentionRate'] = (cohorts['StillActive'] / cohorts['CohortSize'] * 100).round(2)
    logger.info(f"Built {len(cohorts)} quarterly cohorts")
    return cohorts


def build_retention_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """
    Build a cohort retention matrix.
    Rows: signup month cohorts
    Columns: tenure milestones (3, 6, 9, 12, 18, 24 months)
    Values: % of cohort that reached that tenure milestone
    """
    milestones = [3, 6, 9, 12, 18, 24]
    cohorts = df.groupby('SignupMonth').agg(CohortSize=('CustomerID', 'count')).sort_index()

    for m in milestones:
        reached = df[df['Tenure'] >= m].groupby('SignupMonth').size()
        cohorts[f'{m}mo'] = (reached / cohorts['CohortSize'] * 100).round(1)

    # Fill NaN with 0 for cohorts that haven't existed long enough
    cohorts = cohorts.fillna(0)
    logger.info(f"Retention matrix: {cohorts.shape}")
    return cohorts


def plot_retention_heatmap(matrix: pd.DataFrame, output_dir: str):
    """Generate a cohort retention heatmap visualization."""
    # Select only retention columns
    ret_cols = [c for c in matrix.columns if c.endswith('mo')]
    if not ret_cols:
        logger.warning("No retention columns found for heatmap")
        return

    plot_data = matrix[ret_cols].copy()
    # Only show every 3rd cohort for readability if too many
    if len(plot_data) > 18:
        plot_data = plot_data.iloc[::3]

    fig, ax = plt.subplots(figsize=(12, max(8, len(plot_data) * 0.4)))
    sns.heatmap(
        plot_data, annot=True, fmt='.0f', cmap='YlGnBu',
        linewidths=0.5, ax=ax, vmin=0, vmax=100,
        cbar_kws={'label': 'Retention %'}
    )
    ax.set_title('Cohort Retention Matrix (%)', fontsize=16, fontweight='bold', pad=15)
    ax.set_ylabel('Signup Month Cohort', fontsize=12)
    ax.set_xlabel('Tenure Milestone', fontsize=12)

    path = os.path.join(output_dir, 'cohort_retention_heatmap.png')
    fig.savefig(path, bbox_inches='tight', facecolor='white', dpi=150)
    plt.close(fig)
    logger.info(f"Saved cohort retention heatmap: {path}")


def analyze_early_churn(df: pd.DataFrame) -> pd.DataFrame:
    """Analyze customers who churned within the first 6 months."""
    early_churners = df[(df['Churn'] == 'Yes') & (df['Tenure'] <= 6)]
    all_churners = df[df['Churn'] == 'Yes']

    by_quarter = df.groupby('SignupQuarter').agg(
        CohortSize=('CustomerID', 'count'),
        EarlyChurners=('CustomerID', lambda x: len(
            df.loc[x.index][(df.loc[x.index, 'Churn'] == 'Yes') & (df.loc[x.index, 'Tenure'] <= 6)]
        )),
    )
    by_quarter['EarlyChurnRate'] = (by_quarter['EarlyChurners'] / by_quarter['CohortSize'] * 100).round(2)

    summary = {
        'total_early_churners': len(early_churners),
        'pct_of_all_churners': round(len(early_churners) / len(all_churners) * 100, 1) if len(all_churners) > 0 else 0,
        'avg_monthly_charge': round(early_churners['MonthlyCharges'].mean(), 2) if len(early_churners) > 0 else 0,
        'avg_support_tickets': round(early_churners['SupportTickets'].mean(), 1) if len(early_churners) > 0 else 0,
    }
    logger.info(f"Early churn analysis: {summary}")
    return by_quarter


def cohort_retention_by_subscription(df: pd.DataFrame) -> pd.DataFrame:
    """Retention analysis by quarterly cohort and subscription type."""
    result = df.groupby(['SignupQuarter', 'SubscriptionType']).agg(
        CohortSize=('CustomerID', 'count'),
        StillActive=('Churn', lambda x: (x == 'No').sum()),
        AvgLTV=('TotalCharges', 'mean'),
    ).round(2)
    result['RetentionRate'] = (result['StillActive'] / result['CohortSize'] * 100).round(2)
    result = result.sort_index()
    logger.info(f"Cohort × subscription retention: {len(result)} groups")
    return result


def run_cohort_analysis(df: pd.DataFrame, output_dir: str = 'dashboard/charts') -> dict:
    """Execute all cohort analysis functions."""
    logger.info("=" * 60)
    logger.info("STARTING COHORT ANALYSIS")
    logger.info("=" * 60)

    os.makedirs(output_dir, exist_ok=True)

    monthly = build_cohort_summary(df)
    quarterly = build_quarterly_cohorts(df)
    matrix = build_retention_matrix(df)
    plot_retention_heatmap(matrix, output_dir)
    early = analyze_early_churn(df)
    by_sub = cohort_retention_by_subscription(df)

    results = {
        'monthly_cohorts': monthly,
        'quarterly_cohorts': quarterly,
        'retention_matrix': matrix,
        'early_churn': early,
        'by_subscription': by_sub,
    }

    logger.info("Cohort analysis complete")
    return results
