"""
Customer Analysis Module
========================
Performs customer segmentation, distribution analysis, and demographic
profiling using Python and Pandas.
"""

import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)


def analyze_customer_overview(df: pd.DataFrame) -> dict:
    """Generate high-level customer statistics."""
    total = len(df)
    active = len(df[df['Churn'] == 'No'])
    churned = len(df[df['Churn'] == 'Yes'])
    churn_rate = round(churned / total * 100, 2)

    overview = {
        'total_customers': total,
        'active_customers': active,
        'churned_customers': churned,
        'churn_rate_pct': churn_rate,
        'retention_rate_pct': round(100 - churn_rate, 2),
    }
    logger.info(f"Customer overview: {overview}")
    return overview


def analyze_customer_segments(df: pd.DataFrame) -> pd.DataFrame:
    """Analyze churn, revenue, and tenure by customer segment."""
    segments = df.groupby('CustomerSegment').agg(
        CustomerCount=('CustomerID', 'count'),
        ChurnedCount=('ChurnFlag', 'sum'),
        AvgTenure=('Tenure', 'mean'),
        AvgMonthlyCharges=('MonthlyCharges', 'mean'),
        TotalRevenue=('TotalCharges', 'sum'),
        AvgLTV=('TotalCharges', 'mean'),
    ).round(2)
    segments['ChurnRate'] = (segments['ChurnedCount'] / segments['CustomerCount'] * 100).round(2)
    segments['RevenueShare'] = (segments['TotalRevenue'] / segments['TotalRevenue'].sum() * 100).round(2)
    segments = segments.sort_values('TotalRevenue', ascending=False)

    logger.info(f"Customer segment analysis:\n{segments}")
    return segments


def analyze_subscription_distribution(df: pd.DataFrame) -> pd.DataFrame:
    """Analyze customer distribution and churn across subscription types."""
    subs = df.groupby('SubscriptionType').agg(
        CustomerCount=('CustomerID', 'count'),
        ChurnedCount=('ChurnFlag', 'sum'),
        AvgTenure=('Tenure', 'mean'),
        AvgMonthlyCharges=('MonthlyCharges', 'mean'),
        TotalRevenue=('TotalCharges', 'sum'),
    ).round(2)
    subs['ChurnRate'] = (subs['ChurnedCount'] / subs['CustomerCount'] * 100).round(2)
    subs = subs.reindex(['Basic', 'Standard', 'Premium'])

    logger.info(f"Subscription distribution:\n{subs}")
    return subs


def analyze_contract_impact(df: pd.DataFrame) -> pd.DataFrame:
    """Analyze how contract duration affects retention and revenue."""
    contracts = df.groupby('ContractDuration').agg(
        CustomerCount=('CustomerID', 'count'),
        ChurnedCount=('ChurnFlag', 'sum'),
        AvgTenure=('Tenure', 'mean'),
        AvgMonthlyCharges=('MonthlyCharges', 'mean'),
        TotalRevenue=('TotalCharges', 'sum'),
        AvgSupportTickets=('SupportTickets', 'mean'),
    ).round(2)
    contracts['ChurnRate'] = (contracts['ChurnedCount'] / contracts['CustomerCount'] * 100).round(2)
    contracts['RetentionRate'] = (100 - contracts['ChurnRate']).round(2)
    contracts = contracts.reindex(['Month-to-Month', 'One Year', 'Two Year'])

    logger.info(f"Contract impact analysis:\n{contracts}")
    return contracts


def analyze_demographics(df: pd.DataFrame) -> dict:
    """Analyze customer demographics (age, gender)."""
    age_stats = {
        'mean_age': round(df['Age'].mean(), 1),
        'median_age': round(df['Age'].median(), 1),
        'min_age': int(df['Age'].min()),
        'max_age': int(df['Age'].max()),
    }

    gender_dist = df['Gender'].value_counts().to_dict()
    gender_churn = df.groupby('Gender')['ChurnFlag'].mean().round(4).to_dict()

    return {
        'age_stats': age_stats,
        'gender_distribution': gender_dist,
        'gender_churn_rates': gender_churn,
    }


def run_customer_analysis(df: pd.DataFrame) -> dict:
    """Execute all customer analysis functions."""
    logger.info("=" * 60)
    logger.info("STARTING CUSTOMER ANALYSIS")
    logger.info("=" * 60)

    results = {
        'overview': analyze_customer_overview(df),
        'segments': analyze_customer_segments(df),
        'subscriptions': analyze_subscription_distribution(df),
        'contracts': analyze_contract_impact(df),
        'demographics': analyze_demographics(df),
    }

    logger.info("Customer analysis complete")
    return results
