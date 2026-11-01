"""
Exploratory Data Analysis (EDA) Module
=======================================
Generates 12 publication-quality visualizations with business interpretations.
Each visualization includes statistical annotations and is saved to disk.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import os
import logging

logger = logging.getLogger(__name__)

# ── Style configuration ───────────────────────────────────────────────────
COLORS = {
    'primary': '#2E86AB',
    'secondary': '#A23B72',
    'accent': '#F18F01',
    'success': '#2ECC71',
    'danger': '#E74C3C',
    'dark': '#2C3E50',
    'light': '#ECF0F1',
    'palette': ['#2E86AB', '#A23B72', '#F18F01', '#2ECC71', '#E74C3C', '#9B59B6'],
}

sns.set_theme(style='whitegrid', font_scale=1.1)
plt.rcParams.update({
    'figure.dpi': 150,
    'savefig.dpi': 150,
    'figure.facecolor': 'white',
    'axes.facecolor': 'white',
    'font.family': 'sans-serif',
})


def _save_chart(fig, name: str, output_dir: str):
    """Save chart and close figure."""
    path = os.path.join(output_dir, f'{name}.png')
    fig.savefig(path, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    logger.info(f"Saved: {path}")


def chart_01_churn_distribution(df: pd.DataFrame, output_dir: str) -> dict:
    """
    Chart 1: Overall Customer Churn Distribution
    Shows the proportion of churned vs active customers.
    """
    churn_counts = df['Churn'].value_counts()
    churn_pct = (churn_counts / len(df) * 100).round(1)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Pie chart
    colors = [COLORS['success'], COLORS['danger']]
    wedges, texts, autotexts = ax1.pie(
        churn_counts.values, labels=churn_counts.index,
        autopct='%1.1f%%', colors=colors, startangle=90,
        explode=(0.02, 0.05), shadow=False,
        textprops={'fontsize': 13, 'fontweight': 'bold'}
    )
    ax1.set_title('Customer Churn Distribution', fontsize=14, fontweight='bold', pad=15)

    # Bar chart with counts
    bars = ax2.bar(churn_counts.index, churn_counts.values, color=colors, width=0.5,
                   edgecolor='white', linewidth=1.5)
    for bar, count, pct in zip(bars, churn_counts.values, churn_pct.values):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 30,
                f'{count:,}\n({pct}%)', ha='center', va='bottom',
                fontsize=12, fontweight='bold')
    ax2.set_title('Customer Count by Churn Status', fontsize=14, fontweight='bold', pad=15)
    ax2.set_ylabel('Number of Customers', fontsize=12)
    ax2.set_xlabel('')

    fig.suptitle('1. Overall Customer Churn Distribution', fontsize=16, fontweight='bold', y=1.02)
    fig.tight_layout()
    _save_chart(fig, '01_churn_distribution', output_dir)

    return {
        'churned': int(churn_counts.get('Yes', 0)),
        'active': int(churn_counts.get('No', 0)),
        'churn_rate': float(churn_pct.get('Yes', 0)),
    }


def chart_02_churn_by_subscription(df: pd.DataFrame, output_dir: str) -> dict:
    """
    Chart 2: Churn Rate by Subscription Type
    Reveals which plans lose the most customers.
    """
    ct = pd.crosstab(df['SubscriptionType'], df['Churn'])
    ct_pct = ct.div(ct.sum(axis=1), axis=0) * 100
    order = ['Basic', 'Standard', 'Premium']
    ct_pct = ct_pct.reindex(order)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Stacked bar
    ct_pct.plot(kind='bar', stacked=True, ax=ax1,
                color=[COLORS['success'], COLORS['danger']], edgecolor='white')
    ax1.set_title('Churn Rate by Subscription Type (%)', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Percentage (%)', fontsize=12)
    ax1.set_xlabel('Subscription Type', fontsize=12)
    ax1.legend(title='Churn', fontsize=10)
    ax1.set_xticklabels(order, rotation=0)
    for container in ax1.containers:
        ax1.bar_label(container, fmt='%.1f%%', label_type='center', fontsize=10, fontweight='bold')

    # Count by subscription
    sub_churn = df[df['Churn'] == 'Yes'].groupby('SubscriptionType').size().reindex(order, fill_value=0)
    sub_total = df.groupby('SubscriptionType').size().reindex(order, fill_value=0)
    bars = ax2.bar(order, sub_churn.values, color=COLORS['danger'], alpha=0.7, label='Churned')
    ax2.bar(order, sub_total.values - sub_churn.values, bottom=sub_churn.values,
            color=COLORS['success'], alpha=0.7, label='Active')
    ax2.set_title('Customer Count by Subscription & Churn', fontsize=14, fontweight='bold')
    ax2.set_ylabel('Number of Customers', fontsize=12)
    ax2.legend(fontsize=10)

    fig.suptitle('2. Churn Analysis by Subscription Type', fontsize=16, fontweight='bold', y=1.02)
    fig.tight_layout()
    _save_chart(fig, '02_churn_by_subscription', output_dir)

    rates = {}
    for sub in order:
        if sub in ct_pct.index and 'Yes' in ct_pct.columns:
            rates[sub] = round(ct_pct.loc[sub, 'Yes'], 1)
    return rates


def chart_03_churn_by_contract(df: pd.DataFrame, output_dir: str) -> dict:
    """
    Chart 3: Churn Rate by Contract Duration
    Shows how contract commitment affects retention.
    """
    ct = pd.crosstab(df['ContractDuration'], df['Churn'])
    ct_pct = ct.div(ct.sum(axis=1), axis=0) * 100
    order = ['Month-to-Month', 'One Year', 'Two Year']
    ct_pct = ct_pct.reindex(order)

    fig, ax = plt.subplots(figsize=(10, 6))
    churn_rates = ct_pct['Yes'].values if 'Yes' in ct_pct.columns else [0] * len(order)
    bars = ax.bar(order, churn_rates, color=[COLORS['danger'], COLORS['accent'], COLORS['success']],
                  width=0.5, edgecolor='white', linewidth=2)
    for bar, rate in zip(bars, churn_rates):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
               f'{rate:.1f}%', ha='center', va='bottom', fontsize=13, fontweight='bold')

    ax.set_title('3. Churn Rate by Contract Duration', fontsize=16, fontweight='bold')
    ax.set_ylabel('Churn Rate (%)', fontsize=13)
    ax.set_xlabel('Contract Duration', fontsize=13)
    ax.set_ylim(0, max(churn_rates) * 1.3 if max(churn_rates) > 0 else 10)

    fig.tight_layout()
    _save_chart(fig, '03_churn_by_contract', output_dir)

    rates = {order[i]: round(churn_rates[i], 1) for i in range(len(order))}
    return rates


def chart_04_churn_by_charges(df: pd.DataFrame, output_dir: str) -> dict:
    """
    Chart 4: Churn by Monthly Charges
    Explores whether higher-paying customers churn more.
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Box plot
    sns.boxplot(data=df, x='Churn', y='MonthlyCharges', ax=ax1,
                palette=[COLORS['success'], COLORS['danger']], width=0.4)
    ax1.set_title('Monthly Charges Distribution by Churn', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Monthly Charges ($)', fontsize=12)

    # Means annotation
    for i, churn_val in enumerate(['No', 'Yes']):
        mean_val = df[df['Churn'] == churn_val]['MonthlyCharges'].mean()
        median_val = df[df['Churn'] == churn_val]['MonthlyCharges'].median()
        ax1.text(i, mean_val, f'Mean: ${mean_val:.0f}\nMedian: ${median_val:.0f}',
                ha='center', va='bottom', fontsize=9, fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7))

    # Histogram
    df[df['Churn'] == 'No']['MonthlyCharges'].hist(ax=ax2, bins=30, alpha=0.6,
        color=COLORS['success'], label='Active', edgecolor='white')
    df[df['Churn'] == 'Yes']['MonthlyCharges'].hist(ax=ax2, bins=30, alpha=0.6,
        color=COLORS['danger'], label='Churned', edgecolor='white')
    ax2.set_title('Monthly Charges Distribution', fontsize=14, fontweight='bold')
    ax2.set_xlabel('Monthly Charges ($)', fontsize=12)
    ax2.set_ylabel('Frequency', fontsize=12)
    ax2.legend(fontsize=11)

    fig.suptitle('4. Churn Analysis by Monthly Charges', fontsize=16, fontweight='bold', y=1.02)
    fig.tight_layout()
    _save_chart(fig, '04_churn_by_charges', output_dir)

    return {
        'active_mean': round(df[df['Churn'] == 'No']['MonthlyCharges'].mean(), 2),
        'churned_mean': round(df[df['Churn'] == 'Yes']['MonthlyCharges'].mean(), 2),
    }


def chart_05_churn_by_tenure(df: pd.DataFrame, output_dir: str) -> dict:
    """
    Chart 5: Churn by Customer Tenure
    Shows whether newer customers are more likely to churn.
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Tenure distribution by churn
    sns.kdeplot(data=df, x='Tenure', hue='Churn', ax=ax1, fill=True,
                palette=[COLORS['success'], COLORS['danger']], alpha=0.5, linewidth=2)
    ax1.set_title('Tenure Distribution by Churn Status', fontsize=14, fontweight='bold')
    ax1.set_xlabel('Tenure (Months)', fontsize=12)

    # Churn rate by tenure group
    if 'TenureGroup' in df.columns:
        tenure_churn = df.groupby('TenureGroup', observed=False)['ChurnFlag'].mean() * 100
        bars = ax2.bar(range(len(tenure_churn)), tenure_churn.values,
                      color=COLORS['palette'][:len(tenure_churn)], width=0.6, edgecolor='white')
        ax2.set_xticks(range(len(tenure_churn)))
        ax2.set_xticklabels(tenure_churn.index, rotation=25, ha='right', fontsize=10)
        for bar, rate in zip(bars, tenure_churn.values):
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
                    f'{rate:.1f}%', ha='center', va='bottom', fontsize=11, fontweight='bold')
        ax2.set_title('Churn Rate by Tenure Group', fontsize=14, fontweight='bold')
        ax2.set_ylabel('Churn Rate (%)', fontsize=12)

    fig.suptitle('5. Churn Analysis by Customer Tenure', fontsize=16, fontweight='bold', y=1.02)
    fig.tight_layout()
    _save_chart(fig, '05_churn_by_tenure', output_dir)

    return {
        'active_avg_tenure': round(df[df['Churn'] == 'No']['Tenure'].mean(), 1),
        'churned_avg_tenure': round(df[df['Churn'] == 'Yes']['Tenure'].mean(), 1),
    }


def chart_06_churn_by_payment(df: pd.DataFrame, output_dir: str) -> dict:
    """
    Chart 6: Churn Rate by Payment Method
    Identifies if payment method correlates with churn.
    """
    ct = pd.crosstab(df['PaymentMethod'], df['Churn'])
    ct_pct = ct.div(ct.sum(axis=1), axis=0) * 100
    ct_pct = ct_pct.sort_values('Yes', ascending=False) if 'Yes' in ct_pct.columns else ct_pct

    fig, ax = plt.subplots(figsize=(10, 6))
    churn_rates = ct_pct['Yes'].values if 'Yes' in ct_pct.columns else []
    methods = ct_pct.index.tolist()
    colors = [COLORS['palette'][i % len(COLORS['palette'])] for i in range(len(methods))]

    bars = ax.barh(methods, churn_rates, color=colors, height=0.5, edgecolor='white')
    for bar, rate in zip(bars, churn_rates):
        ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height()/2,
               f'{rate:.1f}%', ha='left', va='center', fontsize=12, fontweight='bold')

    ax.set_title('6. Churn Rate by Payment Method', fontsize=16, fontweight='bold')
    ax.set_xlabel('Churn Rate (%)', fontsize=13)
    ax.invert_yaxis()

    fig.tight_layout()
    _save_chart(fig, '06_churn_by_payment', output_dir)

    return {m: round(r, 1) for m, r in zip(methods, churn_rates)}


def chart_07_churn_by_support_tickets(df: pd.DataFrame, output_dir: str) -> dict:
    """
    Chart 7: Churn by Customer Support Tickets
    Explores the relationship between support interactions and churn.
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Box plot
    sns.boxplot(data=df, x='Churn', y='SupportTickets', ax=ax1,
                palette=[COLORS['success'], COLORS['danger']], width=0.4)
    ax1.set_title('Support Tickets by Churn Status', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Number of Support Tickets', fontsize=12)

    # Churn rate by ticket category
    if 'TicketCategory' in df.columns:
        ticket_churn = df.groupby('TicketCategory', observed=False)['ChurnFlag'].mean() * 100
        bars = ax2.bar(range(len(ticket_churn)), ticket_churn.values,
                      color=COLORS['palette'][:len(ticket_churn)], width=0.6, edgecolor='white')
        ax2.set_xticks(range(len(ticket_churn)))
        ax2.set_xticklabels(ticket_churn.index, rotation=15, fontsize=10)
        for bar, rate in zip(bars, ticket_churn.values):
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
                    f'{rate:.1f}%', ha='center', va='bottom', fontsize=11, fontweight='bold')
        ax2.set_title('Churn Rate by Support Ticket Volume', fontsize=14, fontweight='bold')
        ax2.set_ylabel('Churn Rate (%)', fontsize=12)

    fig.suptitle('7. Churn Analysis by Support Tickets', fontsize=16, fontweight='bold', y=1.02)
    fig.tight_layout()
    _save_chart(fig, '07_churn_by_support_tickets', output_dir)

    return {
        'active_avg_tickets': round(df[df['Churn'] == 'No']['SupportTickets'].mean(), 1),
        'churned_avg_tickets': round(df[df['Churn'] == 'Yes']['SupportTickets'].mean(), 1),
    }


def chart_08_revenue_by_subscription(df: pd.DataFrame, output_dir: str) -> dict:
    """
    Chart 8: Revenue by Subscription Type
    Shows total and average revenue contribution per subscription tier.
    """
    order = ['Basic', 'Standard', 'Premium']
    total_rev = df.groupby('SubscriptionType')['TotalCharges'].sum().reindex(order, fill_value=0)
    avg_rev = df.groupby('SubscriptionType')['MonthlyCharges'].mean().reindex(order, fill_value=0)
    count = df.groupby('SubscriptionType').size().reindex(order, fill_value=0)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Total revenue
    bars = ax1.bar(order, total_rev.values, color=COLORS['palette'][:3],
                   width=0.5, edgecolor='white', linewidth=2)
    for bar, rev in zip(bars, total_rev.values):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 500,
                f'${rev:,.0f}', ha='center', va='bottom', fontsize=11, fontweight='bold')
    ax1.set_title('Total Revenue by Subscription', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Total Revenue ($)', fontsize=12)
    ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:,.0f}'))

    # Average monthly charge
    bars2 = ax2.bar(order, avg_rev.values, color=COLORS['palette'][:3],
                    width=0.5, edgecolor='white', linewidth=2)
    for bar, rev in zip(bars2, avg_rev.values):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                f'${rev:.2f}', ha='center', va='bottom', fontsize=11, fontweight='bold')
    ax2.set_title('Avg Monthly Charge by Subscription', fontsize=14, fontweight='bold')
    ax2.set_ylabel('Average Monthly Charges ($)', fontsize=12)

    fig.suptitle('8. Revenue Analysis by Subscription Type', fontsize=16, fontweight='bold', y=1.02)
    fig.tight_layout()
    _save_chart(fig, '08_revenue_by_subscription', output_dir)

    return {sub: round(rev, 2) for sub, rev in zip(order, total_rev.values)}


def chart_09_customer_segments(df: pd.DataFrame, output_dir: str) -> dict:
    """
    Chart 9: Customer Distribution by Segment
    Shows how customers are distributed across business segments.
    """
    segments = df['CustomerSegment'].value_counts()
    seg_pct = (segments / len(df) * 100).round(1)

    # Revenue by segment
    seg_rev = df.groupby('CustomerSegment')['TotalCharges'].sum()

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Customer count
    colors = [COLORS['primary'], COLORS['secondary'], COLORS['accent']]
    wedges, texts, autotexts = ax1.pie(
        segments.values, labels=segments.index, autopct='%1.1f%%',
        colors=colors, startangle=90, textprops={'fontsize': 12, 'fontweight': 'bold'}
    )
    ax1.set_title('Customer Distribution', fontsize=14, fontweight='bold')

    # Revenue by segment
    bars = ax2.bar(seg_rev.index, seg_rev.values, color=colors[:len(seg_rev)],
                   width=0.5, edgecolor='white')
    for bar, rev in zip(bars, seg_rev.values):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 500,
                f'${rev:,.0f}', ha='center', va='bottom', fontsize=11, fontweight='bold')
    ax2.set_title('Total Revenue by Segment', fontsize=14, fontweight='bold')
    ax2.set_ylabel('Total Revenue ($)', fontsize=12)
    ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:,.0f}'))

    fig.suptitle('9. Customer Distribution by Segment', fontsize=16, fontweight='bold', y=1.02)
    fig.tight_layout()
    _save_chart(fig, '09_customer_segments', output_dir)

    return {seg: int(cnt) for seg, cnt in segments.items()}


def chart_10_mrr_trends(df: pd.DataFrame, output_dir: str) -> dict:
    """
    Chart 10: Monthly Recurring Revenue Trends
    Shows MRR over time based on signup cohorts.
    """
    # Calculate MRR by signup month (using active customers' monthly charges)
    active = df[df['Churn'] == 'No'].copy()
    mrr_by_month = active.groupby('SignupMonth')['MonthlyCharges'].sum().sort_index()

    # Also total customers by signup month
    customers_by_month = df.groupby('SignupMonth').size().sort_index()

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))

    # MRR trend
    ax1.fill_between(range(len(mrr_by_month)), mrr_by_month.values,
                     alpha=0.3, color=COLORS['primary'])
    ax1.plot(range(len(mrr_by_month)), mrr_by_month.values,
             color=COLORS['primary'], linewidth=2.5, marker='o', markersize=4)
    ax1.set_title('Monthly Recurring Revenue (from Active Customers)', fontsize=14, fontweight='bold')
    ax1.set_ylabel('MRR ($)', fontsize=12)
    ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:,.0f}'))
    tick_positions = list(range(0, len(mrr_by_month), max(1, len(mrr_by_month) // 12)))
    ax1.set_xticks(tick_positions)
    ax1.set_xticklabels([mrr_by_month.index[i] for i in tick_positions], rotation=45, ha='right', fontsize=8)

    # Customer acquisition trend
    ax2.bar(range(len(customers_by_month)), customers_by_month.values,
            color=COLORS['secondary'], alpha=0.7, edgecolor='white')
    ax2.set_title('New Customer Acquisitions by Month', fontsize=14, fontweight='bold')
    ax2.set_ylabel('New Customers', fontsize=12)
    ax2.set_xticks(tick_positions)
    ax2.set_xticklabels([customers_by_month.index[i] for i in tick_positions], rotation=45, ha='right', fontsize=8)

    fig.suptitle('10. MRR and Customer Acquisition Trends', fontsize=16, fontweight='bold', y=1.02)
    fig.tight_layout()
    _save_chart(fig, '10_mrr_trends', output_dir)

    return {
        'total_mrr': round(mrr_by_month.sum(), 2),
        'avg_monthly_mrr': round(mrr_by_month.mean(), 2),
    }


def chart_11_retention_trends(df: pd.DataFrame, output_dir: str) -> dict:
    """
    Chart 11: Customer Retention Trends
    Shows retention rate across tenure groups and contract types.
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Retention by tenure group
    if 'TenureGroup' in df.columns:
        retention = df.groupby('TenureGroup', observed=False).apply(
            lambda x: (x['Churn'] == 'No').mean() * 100
        )
        bars = ax1.bar(range(len(retention)), retention.values,
                      color=COLORS['palette'][:len(retention)], width=0.6, edgecolor='white')
        ax1.set_xticks(range(len(retention)))
        ax1.set_xticklabels(retention.index, rotation=25, ha='right', fontsize=10)
        for bar, rate in zip(bars, retention.values):
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
                    f'{rate:.1f}%', ha='center', va='bottom', fontsize=11, fontweight='bold')
        ax1.set_title('Retention Rate by Tenure Group', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Retention Rate (%)', fontsize=12)
        ax1.set_ylim(0, 105)

    # Retention by contract type
    retention_contract = df.groupby('ContractDuration').apply(
        lambda x: (x['Churn'] == 'No').mean() * 100
    )
    order = ['Month-to-Month', 'One Year', 'Two Year']
    retention_contract = retention_contract.reindex(order)
    bars2 = ax2.bar(order, retention_contract.values,
                   color=[COLORS['danger'], COLORS['accent'], COLORS['success']],
                   width=0.5, edgecolor='white')
    for bar, rate in zip(bars2, retention_contract.values):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
                f'{rate:.1f}%', ha='center', va='bottom', fontsize=11, fontweight='bold')
    ax2.set_title('Retention Rate by Contract Duration', fontsize=14, fontweight='bold')
    ax2.set_ylabel('Retention Rate (%)', fontsize=12)
    ax2.set_ylim(0, 105)

    fig.suptitle('11. Customer Retention Trends', fontsize=16, fontweight='bold', y=1.02)
    fig.tight_layout()
    _save_chart(fig, '11_retention_trends', output_dir)

    return {
        'overall_retention': round((df['Churn'] == 'No').mean() * 100, 1),
    }


def chart_12_correlation_heatmap(df: pd.DataFrame, output_dir: str) -> dict:
    """
    Chart 12: Correlation Heatmap
    Shows relationships between numeric variables.
    """
    numeric_cols = ['Age', 'MonthlyCharges', 'TotalCharges', 'Tenure',
                    'SupportTickets', 'ChurnFlag']
    available_cols = [c for c in numeric_cols if c in df.columns]
    corr = df[available_cols].corr()

    fig, ax = plt.subplots(figsize=(10, 8))
    mask = np.triu(np.ones_like(corr, dtype=bool), k=1)
    cmap = sns.diverging_palette(250, 10, as_cmap=True)
    sns.heatmap(corr, mask=mask, cmap=cmap, center=0, annot=True, fmt='.2f',
                square=True, linewidths=1, cbar_kws={'shrink': 0.8},
                ax=ax, vmin=-1, vmax=1)
    ax.set_title('12. Correlation Heatmap of Key Variables', fontsize=16, fontweight='bold', pad=15)

    fig.tight_layout()
    _save_chart(fig, '12_correlation_heatmap', output_dir)

    # Key correlations with churn
    churn_corr = corr['ChurnFlag'].drop('ChurnFlag').sort_values(ascending=False)
    return {col: round(val, 3) for col, val in churn_corr.items()}


def run_eda(df: pd.DataFrame, output_dir: str = 'dashboard/charts') -> dict:
    """
    Execute the full EDA pipeline: generate all 12 visualizations.

    Parameters
    ----------
    df : pd.DataFrame
        Cleaned dataset.
    output_dir : str
        Directory to save chart images.

    Returns
    -------
    dict
        Dictionary of insights from each chart.
    """
    os.makedirs(output_dir, exist_ok=True)
    logger.info("=" * 60)
    logger.info("STARTING EXPLORATORY DATA ANALYSIS")
    logger.info("=" * 60)

    insights = {}

    chart_functions = [
        ('churn_distribution', chart_01_churn_distribution),
        ('churn_by_subscription', chart_02_churn_by_subscription),
        ('churn_by_contract', chart_03_churn_by_contract),
        ('churn_by_charges', chart_04_churn_by_charges),
        ('churn_by_tenure', chart_05_churn_by_tenure),
        ('churn_by_payment', chart_06_churn_by_payment),
        ('churn_by_support_tickets', chart_07_churn_by_support_tickets),
        ('revenue_by_subscription', chart_08_revenue_by_subscription),
        ('customer_segments', chart_09_customer_segments),
        ('mrr_trends', chart_10_mrr_trends),
        ('retention_trends', chart_11_retention_trends),
        ('correlation_heatmap', chart_12_correlation_heatmap),
    ]

    for name, func in chart_functions:
        try:
            logger.info(f"Generating chart: {name}")
            insights[name] = func(df, output_dir)
        except Exception as e:
            logger.error(f"Error generating {name}: {e}")
            insights[name] = {'error': str(e)}

    logger.info(f"EDA complete — {len(insights)} charts generated in {output_dir}")
    return insights


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s — %(levelname)s — %(message)s')
    df = pd.read_csv('data/processed/saas_customer_cleaned.csv')
    insights = run_eda(df)
    for k, v in insights.items():
        print(f"\n{k}: {v}")
