"""
SaaS Customer Churn & LTV Exploratory Data Analysis Pipeline
============================================================
Interactive/standalone exploratory data analysis script demonstrating
data analysis, metric calculation, cohort breakdown, and visualization.

NOTE: This is a pure Data Analytics & Business Intelligence pipeline.
No machine learning algorithms or predictive modeling are used.
"""

import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Path configuration
NOTEBOOK_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(NOTEBOOK_DIR)
RAW_DATA_PATH = os.path.join(PROJECT_ROOT, "data", "raw", "saas_customer_data.csv")
PROCESSED_DATA_PATH = os.path.join(PROJECT_ROOT, "data", "processed", "saas_customer_cleaned.csv")
CHARTS_DIR = os.path.join(PROJECT_ROOT, "dashboard", "charts")

# Styling
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['font.size'] = 10


def load_dataset(use_processed: bool = True) -> pd.DataFrame:
    """Load processed or raw SaaS customer subscription data."""
    target_path = PROCESSED_DATA_PATH if use_processed and os.path.exists(PROCESSED_DATA_PATH) else RAW_DATA_PATH
    if not os.path.exists(target_path):
        raise FileNotFoundError(f"Dataset not found at {target_path}. Please run main.py first.")
    
    print(f"[1/4] Loading customer dataset from: {target_path}")
    df = pd.read_csv(target_path)
    print(f"      Loaded {len(df):,} customer records across {df.shape[1]} columns.")
    return df


def inspect_key_metrics(df: pd.DataFrame) -> dict:
    """Calculate and display core SaaS customer and revenue metrics."""
    print("\n[2/4] Key SaaS Business Metrics Overview:")
    print("=" * 60)
    
    total_customers = len(df)
    churn_count = (df['Churn'] == 'Yes').sum() if 'Churn' in df.columns else (df['ChurnFlag'] == 1).sum()
    churn_rate = (churn_count / total_customers) * 100
    retention_rate = 100.0 - churn_rate
    
    mrr = df[df['Churn'] == 'No']['MonthlyCharges'].sum() if 'Churn' in df.columns else df['MonthlyCharges'].sum()
    arr = mrr * 12
    arpu = df['MonthlyCharges'].mean()
    avg_tenure = df['Tenure'].mean()
    avg_ltv = df['TotalCharges'].mean()
    
    metrics = {
        "Total Customers": f"{total_customers:,}",
        "Active Customers": f"{(total_customers - churn_count):,}",
        "Churned Customers": f"{churn_count:,}",
        "Overall Churn Rate": f"{churn_rate:.2f}%",
        "Overall Retention Rate": f"{retention_rate:.2f}%",
        "Monthly Recurring Revenue (MRR)": f"${mrr:,.2f}",
        "Annual Recurring Revenue (ARR)": f"${arr:,.2f}",
        "Average Revenue Per User (ARPU)": f"${arpu:.2f}",
        "Average Tenure (Months)": f"{avg_tenure:.1f} months",
        "Average Lifetime Value (LTV)": f"${avg_ltv:,.2f}",
    }
    
    for k, v in metrics.items():
        print(f"  {k:<35}: {v}")
    print("=" * 60)
    return metrics


def analyze_churn_drivers(df: pd.DataFrame) -> None:
    """Break down churn across subscription tier, contract type, and support tickets."""
    print("\n[3/4] Customer Churn Drivers & Segment Breakdown:")
    print("-" * 60)
    
    # 1. By Contract Duration
    print("\n-- Churn by Contract Duration --")
    contract_churn = df.groupby('ContractDuration').agg(
        TotalCustomers=('CustomerID', 'count'),
        Churned=('Churn', lambda x: (x == 'Yes').sum()),
        AvgMonthlyCharge=('MonthlyCharges', 'mean')
    )
    contract_churn['ChurnRate'] = (contract_churn['Churned'] / contract_churn['TotalCustomers'] * 100).round(2)
    print(contract_churn.to_string())
    
    # 2. By Subscription Tier
    print("\n-- Churn by Subscription Type --")
    sub_churn = df.groupby('SubscriptionType').agg(
        TotalCustomers=('CustomerID', 'count'),
        Churned=('Churn', lambda x: (x == 'Yes').sum()),
        AvgLTV=('TotalCharges', 'mean')
    )
    sub_churn['ChurnRate'] = (sub_churn['Churned'] / sub_churn['TotalCustomers'] * 100).round(2)
    print(sub_churn.to_string())
    
    # 3. By Support Tickets
    if 'SupportTickets' in df.columns:
        print("\n-- Churn by Support Tickets --")
        ticket_churn = df.groupby('SupportTickets').agg(
            CustomerCount=('CustomerID', 'count'),
            Churned=('Churn', lambda x: (x == 'Yes').sum())
        )
        ticket_churn['ChurnRate'] = (ticket_churn['Churned'] / ticket_churn['CustomerCount'] * 100).round(2)
        print(ticket_churn.head(8).to_string())


def generate_summary_plots(df: pd.DataFrame, output_dir: str = CHARTS_DIR) -> None:
    """Generate and display summary exploratory analysis charts."""
    print(f"\n[4/4] Generating exploratory visualizations in: {output_dir}")
    os.makedirs(output_dir, exist_ok=True)
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Plot A: Contract Duration vs Churn Rate
    contract_summary = df.groupby('ContractDuration', as_index=False).apply(
        lambda g: pd.Series({'ChurnRate': (g['Churn'] == 'Yes').mean() * 100})
    )
    sns.barplot(data=contract_summary, x='ContractDuration', y='ChurnRate', ax=axes[0], hue='ContractDuration', palette='Blues_r', legend=False)
    axes[0].set_title('Churn Rate by Contract Duration (%)', fontweight='bold')
    axes[0].set_ylabel('Churn Rate (%)')
    axes[0].set_xlabel('Contract Type')
    for p in axes[0].patches:
        val = p.get_height()
        if not np.isnan(val) and val > 0:
            axes[0].annotate(f"{val:.1f}%", (p.get_x() + p.get_width() / 2., val / 2),
                             ha='center', va='center', color='white', fontweight='bold')
    
    # Plot B: Support Tickets vs Churn
    ticket_summary = df.groupby('SupportTickets', as_index=False).apply(
        lambda g: pd.Series({'ChurnRate': (g['Churn'] == 'Yes').mean() * 100})
    )
    sns.lineplot(data=ticket_summary, x='SupportTickets', y='ChurnRate', ax=axes[1], marker='o', color='#E63946', linewidth=2)
    axes[1].set_title('Churn Rate vs Support Ticket Frequency', fontweight='bold')
    axes[1].set_ylabel('Churn Rate (%)')
    axes[1].set_xlabel('Number of Support Tickets')
    
    plt.tight_layout()
    chart_path = os.path.join(output_dir, 'notebook_eda_summary.png')
    plt.savefig(chart_path, dpi=200)
    plt.close()
    print(f"      Saved summary figure: {chart_path}")
    print("\nEDA Pipeline completed successfully without predictive ML modeling.")


if __name__ == "__main__":
    df = load_dataset()
    inspect_key_metrics(df)
    analyze_churn_drivers(df)
    generate_summary_plots(df)
