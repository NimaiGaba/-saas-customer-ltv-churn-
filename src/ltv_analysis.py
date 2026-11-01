"""
Customer Lifetime Value (LTV) Analysis Module
==============================================
Calculates HISTORICAL customer lifetime value metrics.

IMPORTANT: LTV in this module is the actual total revenue received from a
customer during their lifetime (TotalCharges). This is NOT a predictive model.

Methodology:
- Historical LTV = TotalCharges (all payments received)
- Average LTV = Mean of TotalCharges across a segment
- LTV can also be expressed as: AvgMonthlyCharges × AvgTenure
"""

import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)


def calculate_overall_ltv(df: pd.DataFrame) -> dict:
    """Calculate overall LTV statistics across all customers."""
    stats = {
        'avg_ltv': round(df['TotalCharges'].mean(), 2),
        'median_ltv': round(df['TotalCharges'].median(), 2),
        'min_ltv': round(df['TotalCharges'].min(), 2),
        'max_ltv': round(df['TotalCharges'].max(), 2),
        'std_ltv': round(df['TotalCharges'].std(), 2),
        'total_lifetime_revenue': round(df['TotalCharges'].sum(), 2),
        'avg_tenure_months': round(df['Tenure'].mean(), 1),
        'avg_monthly_charge': round(df['MonthlyCharges'].mean(), 2),
        # Cross-check: AvgMonthly × AvgTenure ≈ AvgLTV
        'ltv_cross_check': round(df['MonthlyCharges'].mean() * df['Tenure'].mean(), 2),
    }
    logger.info(f"Overall LTV — Avg: ${stats['avg_ltv']:,.2f}, Median: ${stats['median_ltv']:,.2f}")
    return stats


def ltv_by_subscription(df: pd.DataFrame) -> pd.DataFrame:
    """LTV breakdown by subscription type."""
    ltv = df.groupby('SubscriptionType').agg(
        CustomerCount=('CustomerID', 'count'),
        AvgLTV=('TotalCharges', 'mean'),
        MedianLTV=('TotalCharges', 'median'),
        TotalRevenue=('TotalCharges', 'sum'),
        AvgTenure=('Tenure', 'mean'),
        AvgMonthlyCharge=('MonthlyCharges', 'mean'),
    ).round(2)
    ltv['LTV_CrossCheck'] = (ltv['AvgMonthlyCharge'] * ltv['AvgTenure']).round(2)
    ltv = ltv.reindex(['Basic', 'Standard', 'Premium'])
    logger.info(f"LTV by subscription:\n{ltv}")
    return ltv


def ltv_by_segment(df: pd.DataFrame) -> pd.DataFrame:
    """LTV breakdown by customer segment."""
    ltv = df.groupby('CustomerSegment').agg(
        CustomerCount=('CustomerID', 'count'),
        AvgLTV=('TotalCharges', 'mean'),
        MedianLTV=('TotalCharges', 'median'),
        TotalRevenue=('TotalCharges', 'sum'),
        AvgTenure=('Tenure', 'mean'),
        AvgMonthlyCharge=('MonthlyCharges', 'mean'),
        ChurnRate=('ChurnFlag', 'mean'),
    ).round(2)
    ltv['ChurnRate'] = (ltv['ChurnRate'] * 100).round(2)
    ltv['RevenueShare'] = (ltv['TotalRevenue'] / ltv['TotalRevenue'].sum() * 100).round(2)
    ltv = ltv.sort_values('AvgLTV', ascending=False)
    logger.info(f"LTV by segment:\n{ltv}")
    return ltv


def ltv_by_churn_status(df: pd.DataFrame) -> pd.DataFrame:
    """Compare LTV between active and churned customers."""
    ltv = df.groupby('Churn').agg(
        CustomerCount=('CustomerID', 'count'),
        AvgLTV=('TotalCharges', 'mean'),
        MedianLTV=('TotalCharges', 'median'),
        TotalRevenue=('TotalCharges', 'sum'),
        AvgTenure=('Tenure', 'mean'),
        AvgMonthlyCharge=('MonthlyCharges', 'mean'),
        AvgSupportTickets=('SupportTickets', 'mean'),
    ).round(2)
    logger.info(f"LTV by churn status:\n{ltv}")
    return ltv


def ltv_quartile_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """Group customers into LTV quartiles and analyze characteristics."""
    df = df.copy()
    df['LTV_Quartile'] = pd.qcut(df['TotalCharges'], q=4,
                                   labels=['Q1 (Bottom 25%)', 'Q2 (25-50%)',
                                           'Q3 (50-75%)', 'Q4 (Top 25%)'])

    quartiles = df.groupby('LTV_Quartile', observed=False).agg(
        CustomerCount=('CustomerID', 'count'),
        AvgLTV=('TotalCharges', 'mean'),
        MinLTV=('TotalCharges', 'min'),
        MaxLTV=('TotalCharges', 'max'),
        AvgTenure=('Tenure', 'mean'),
        AvgMonthlyCharge=('MonthlyCharges', 'mean'),
        ChurnRate=('ChurnFlag', 'mean'),
        AvgSupportTickets=('SupportTickets', 'mean'),
    ).round(2)
    quartiles['ChurnRate'] = (quartiles['ChurnRate'] * 100).round(2)
    logger.info(f"LTV quartile analysis:\n{quartiles}")
    return quartiles


def identify_high_value_customers(df: pd.DataFrame, top_n: int = 50) -> pd.DataFrame:
    """Identify the top N customers by lifetime value."""
    cols = ['CustomerID', 'CustomerSegment', 'SubscriptionType', 'ContractDuration',
            'Tenure', 'MonthlyCharges', 'TotalCharges', 'Churn', 'SupportTickets']
    top = df.nlargest(top_n, 'TotalCharges')[cols].copy()
    total_revenue = df['TotalCharges'].sum()
    top['RevenueContribution'] = (top['TotalCharges'] / total_revenue * 100).round(4)
    logger.info(f"Top {top_n} customers account for {top['RevenueContribution'].sum():.2f}% of revenue")
    return top


def ltv_by_contract(df: pd.DataFrame) -> pd.DataFrame:
    """LTV analysis by contract duration."""
    ltv = df.groupby('ContractDuration').agg(
        CustomerCount=('CustomerID', 'count'),
        AvgLTV=('TotalCharges', 'mean'),
        MedianLTV=('TotalCharges', 'median'),
        AvgTenure=('Tenure', 'mean'),
        AvgMonthlyCharge=('MonthlyCharges', 'mean'),
        ChurnRate=('ChurnFlag', 'mean'),
    ).round(2)
    ltv['ChurnRate'] = (ltv['ChurnRate'] * 100).round(2)
    ltv = ltv.reindex(['Month-to-Month', 'One Year', 'Two Year'])
    logger.info(f"LTV by contract:\n{ltv}")
    return ltv


def run_ltv_analysis(df: pd.DataFrame) -> dict:
    """Execute all LTV analysis functions."""
    logger.info("=" * 60)
    logger.info("STARTING CUSTOMER LIFETIME VALUE ANALYSIS")
    logger.info("=" * 60)

    results = {
        'overall': calculate_overall_ltv(df),
        'by_subscription': ltv_by_subscription(df),
        'by_segment': ltv_by_segment(df),
        'by_churn_status': ltv_by_churn_status(df),
        'quartiles': ltv_quartile_analysis(df),
        'high_value': identify_high_value_customers(df),
        'by_contract': ltv_by_contract(df),
    }

    logger.info("LTV analysis complete")
    return results
