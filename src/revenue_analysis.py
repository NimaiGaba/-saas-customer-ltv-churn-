"""
Revenue Analysis Module
=======================
Calculates key SaaS revenue metrics: MRR, ARPU, ARR, revenue by segment,
and revenue concentration analysis.
"""

import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)


def calculate_mrr(df: pd.DataFrame) -> dict:
    """
    Calculate Monthly Recurring Revenue (MRR) from active customers.
    MRR = Sum of MonthlyCharges for all active (non-churned) customers.
    """
    active = df[df['Churn'] == 'No']
    mrr = round(active['MonthlyCharges'].sum(), 2)
    active_count = len(active)
    arpu = round(mrr / active_count, 2) if active_count > 0 else 0
    arr = round(mrr * 12, 2)

    metrics = {
        'mrr': mrr,
        'arr': arr,
        'arpu': arpu,
        'active_customers': active_count,
    }
    logger.info(f"MRR: ${mrr:,.2f} | ARPU: ${arpu:.2f} | ARR: ${arr:,.2f}")
    return metrics


def revenue_by_subscription(df: pd.DataFrame) -> pd.DataFrame:
    """Revenue breakdown by subscription type."""
    rev = df.groupby('SubscriptionType').agg(
        CustomerCount=('CustomerID', 'count'),
        TotalRevenue=('TotalCharges', 'sum'),
        AvgRevenue=('TotalCharges', 'mean'),
        MRR=('MonthlyCharges', lambda x: x[df.loc[x.index, 'Churn'] == 'No'].sum()),
        AvgMonthlyCharge=('MonthlyCharges', 'mean'),
    ).round(2)
    rev['RevenueShare'] = (rev['TotalRevenue'] / rev['TotalRevenue'].sum() * 100).round(2)
    rev = rev.reindex(['Basic', 'Standard', 'Premium'])
    logger.info(f"Revenue by subscription:\n{rev}")
    return rev


def revenue_by_segment(df: pd.DataFrame) -> pd.DataFrame:
    """Revenue breakdown by customer segment."""
    rev = df.groupby('CustomerSegment').agg(
        CustomerCount=('CustomerID', 'count'),
        TotalRevenue=('TotalCharges', 'sum'),
        AvgRevenue=('TotalCharges', 'mean'),
        AvgMonthlyCharge=('MonthlyCharges', 'mean'),
    ).round(2)
    rev['RevenueShare'] = (rev['TotalRevenue'] / rev['TotalRevenue'].sum() * 100).round(2)
    rev = rev.sort_values('TotalRevenue', ascending=False)
    logger.info(f"Revenue by segment:\n{rev}")
    return rev


def revenue_at_risk(df: pd.DataFrame) -> dict:
    """
    Calculate revenue lost or at risk due to churn.
    Lost MRR = Sum of MonthlyCharges of churned customers.
    """
    churned = df[df['Churn'] == 'Yes']
    lost_mrr = round(churned['MonthlyCharges'].sum(), 2)
    lost_arr = round(lost_mrr * 12, 2)
    total_revenue_before_churn = round(churned['TotalCharges'].sum(), 2)
    avg_churned_charge = round(churned['MonthlyCharges'].mean(), 2)

    metrics = {
        'lost_mrr': lost_mrr,
        'lost_arr': lost_arr,
        'total_revenue_before_churn': total_revenue_before_churn,
        'avg_churned_monthly_charge': avg_churned_charge,
        'churned_customers': len(churned),
    }
    logger.info(f"Revenue at risk — Lost MRR: ${lost_mrr:,.2f} | Lost ARR: ${lost_arr:,.2f}")
    return metrics


def revenue_concentration(df: pd.DataFrame) -> pd.DataFrame:
    """
    Pareto analysis: what % of customers generate what % of revenue.
    """
    sorted_df = df.sort_values('TotalCharges', ascending=False).reset_index(drop=True)
    sorted_df['CumulativeRevenue'] = sorted_df['TotalCharges'].cumsum()
    total_revenue = sorted_df['TotalCharges'].sum()
    sorted_df['CumulativeRevenuePct'] = (sorted_df['CumulativeRevenue'] / total_revenue * 100).round(2)
    sorted_df['CustomerRank'] = range(1, len(sorted_df) + 1)
    sorted_df['CustomerPctile'] = (sorted_df['CustomerRank'] / len(sorted_df) * 100).round(2)

    # Key milestones
    milestones = []
    for pct in [10, 20, 30, 50, 80]:
        idx = (sorted_df['CustomerPctile'] - pct).abs().idxmin()
        milestones.append({
            'TopPctCustomers': pct,
            'CumulativeRevenuePct': sorted_df.loc[idx, 'CumulativeRevenuePct'],
        })

    pareto = pd.DataFrame(milestones)
    logger.info(f"Revenue concentration (Pareto):\n{pareto}")
    return pareto


def revenue_trends_by_signup(df: pd.DataFrame) -> pd.DataFrame:
    """Monthly revenue acquisition trend based on signup dates."""
    trends = df.groupby('SignupMonth').agg(
        NewCustomers=('CustomerID', 'count'),
        MRR_Acquired=('MonthlyCharges', 'sum'),
        AvgMonthlyCharge=('MonthlyCharges', 'mean'),
        TotalLifetimeRevenue=('TotalCharges', 'sum'),
    ).round(2).sort_index()

    logger.info(f"Revenue trends: {len(trends)} months analyzed")
    return trends


def run_revenue_analysis(df: pd.DataFrame) -> dict:
    """Execute all revenue analysis functions."""
    logger.info("=" * 60)
    logger.info("STARTING REVENUE ANALYSIS")
    logger.info("=" * 60)

    results = {
        'mrr_metrics': calculate_mrr(df),
        'by_subscription': revenue_by_subscription(df),
        'by_segment': revenue_by_segment(df),
        'at_risk': revenue_at_risk(df),
        'concentration': revenue_concentration(df),
        'trends': revenue_trends_by_signup(df),
    }

    logger.info("Revenue analysis complete")
    return results
