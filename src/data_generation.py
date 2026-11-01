"""
SaaS Customer Subscription Dataset Generator
=============================================
Generates a realistic synthetic SaaS subscription dataset for analytics.

Dataset Design Rationale:
- 5,000 customers to provide sufficient volume for cohort and segmentation analysis
- Realistic distributions modeled on publicly available SaaS industry benchmarks
- Churn rates vary by contract type (monthly ~30%, annual ~10%, 2-year ~5%)
- Revenue correlates with subscription tier and contract commitment
- Support ticket volume correlates with churn probability
- Tenure and signup dates span 36 months for meaningful cohort analysis

This dataset is SYNTHETIC and documented as such. No real customer data is used.
"""

import pandas as pd
import numpy as np
import os
import logging

logger = logging.getLogger(__name__)

# ── Configuration ──────────────────────────────────────────────────────────

SEED = 42
N_CUSTOMERS = 5000

SUBSCRIPTION_TYPES = ['Basic', 'Standard', 'Premium']
SUBSCRIPTION_WEIGHTS = [0.40, 0.35, 0.25]

CONTRACT_DURATIONS = ['Month-to-Month', 'One Year', 'Two Year']
CONTRACT_WEIGHTS = [0.50, 0.30, 0.20]

PAYMENT_METHODS = ['Credit Card', 'Bank Transfer', 'PayPal', 'Check']
PAYMENT_WEIGHTS = [0.40, 0.25, 0.25, 0.10]

CUSTOMER_SEGMENTS = ['SMB', 'Mid-Market', 'Enterprise']
SEGMENT_WEIGHTS = [0.50, 0.30, 0.20]

# Monthly charge ranges by subscription type
CHARGE_RANGES = {
    'Basic':    (15, 45),
    'Standard': (45, 95),
    'Premium':  (95, 200),
}

# Churn probabilities by contract type (base rates)
CHURN_BASE_RATES = {
    'Month-to-Month': 0.30,
    'One Year':       0.10,
    'Two Year':       0.05,
}


def generate_dataset(output_path: str = 'data/raw/saas_customer_data.csv') -> pd.DataFrame:
    """
    Generate a synthetic SaaS customer subscription dataset.

    Parameters
    ----------
    output_path : str
        File path to save the generated CSV.

    Returns
    -------
    pd.DataFrame
        The generated dataset.
    """
    logger.info(f"Generating synthetic dataset with {N_CUSTOMERS} customers...")
    rng = np.random.default_rng(SEED)

    # ── Core demographics ──────────────────────────────────────────────
    customer_ids = [f'CUST-{str(i).zfill(5)}' for i in range(1, N_CUSTOMERS + 1)]
    genders = rng.choice(['Male', 'Female', 'Non-Binary'], size=N_CUSTOMERS,
                         p=[0.48, 0.48, 0.04])
    ages = rng.integers(22, 68, size=N_CUSTOMERS)

    # ── Subscription attributes ────────────────────────────────────────
    subscription_types = rng.choice(SUBSCRIPTION_TYPES, size=N_CUSTOMERS,
                                    p=SUBSCRIPTION_WEIGHTS)
    contract_durations = rng.choice(CONTRACT_DURATIONS, size=N_CUSTOMERS,
                                    p=CONTRACT_WEIGHTS)
    payment_methods = rng.choice(PAYMENT_METHODS, size=N_CUSTOMERS,
                                 p=PAYMENT_WEIGHTS)
    customer_segments = rng.choice(CUSTOMER_SEGMENTS, size=N_CUSTOMERS,
                                   p=SEGMENT_WEIGHTS)

    # ── Signup dates: spread over 36 months (2022-01 to 2024-12) ──────
    start_date = pd.Timestamp('2022-01-01')
    end_date = pd.Timestamp('2024-12-31')
    date_range_days = (end_date - start_date).days
    random_days = rng.integers(0, date_range_days, size=N_CUSTOMERS)
    signup_dates = [start_date + pd.Timedelta(days=int(d)) for d in random_days]

    # ── Tenure: months since signup (reference date: 2025-01-01) ──────
    reference_date = pd.Timestamp('2025-01-01')
    tenures = np.array([(reference_date - sd).days // 30 for sd in signup_dates])
    tenures = np.clip(tenures, 1, 36)

    # ── Monthly charges: based on subscription type with noise ────────
    monthly_charges = np.zeros(N_CUSTOMERS)
    for i in range(N_CUSTOMERS):
        low, high = CHARGE_RANGES[subscription_types[i]]
        monthly_charges[i] = rng.uniform(low, high)
    monthly_charges = np.round(monthly_charges, 2)

    # ── Total charges: tenure × monthly charge with small variance ────
    total_charges = np.round(tenures * monthly_charges * rng.uniform(0.90, 1.05, N_CUSTOMERS), 2)

    # ── Support tickets: Poisson-distributed, higher for churners ─────
    support_tickets_base = rng.poisson(lam=2, size=N_CUSTOMERS)

    # ── Churn determination ────────────────────────────────────────────
    # Base churn rate from contract type + modifiers
    churn_probs = np.zeros(N_CUSTOMERS)
    for i in range(N_CUSTOMERS):
        base = CHURN_BASE_RATES[contract_durations[i]]

        # Higher charges increase churn slightly
        charge_pct = (monthly_charges[i] - 15) / (200 - 15)
        charge_modifier = charge_pct * 0.08

        # More support tickets increase churn
        ticket_modifier = min(support_tickets_base[i] * 0.04, 0.20)

        # Shorter tenure increases churn
        tenure_modifier = max(0, (12 - tenures[i]) / 12 * 0.10)

        # Enterprise segment churns less
        segment_modifier = {'SMB': 0.05, 'Mid-Market': 0.0, 'Enterprise': -0.05}
        seg_mod = segment_modifier[customer_segments[i]]

        churn_probs[i] = np.clip(base + charge_modifier + ticket_modifier +
                                  tenure_modifier + seg_mod, 0.02, 0.70)

    churn = rng.random(N_CUSTOMERS) < churn_probs
    churn_labels = np.where(churn, 'Yes', 'No')

    # Churners tend to have more support tickets
    for i in range(N_CUSTOMERS):
        if churn[i]:
            support_tickets_base[i] += rng.integers(0, 4)

    # ── Last interaction date ──────────────────────────────────────────
    last_interactions = []
    for i in range(N_CUSTOMERS):
        if churn[i]:
            # Churned customers: last interaction is before reference date
            days_ago = rng.integers(30, 180)
        else:
            # Active customers: recent interaction
            days_ago = rng.integers(0, 30)
        last_interactions.append(reference_date - pd.Timedelta(days=int(days_ago)))

    # ── Assemble dataframe ─────────────────────────────────────────────
    df = pd.DataFrame({
        'CustomerID': customer_ids,
        'Gender': genders,
        'Age': ages,
        'SignupDate': signup_dates,
        'SubscriptionType': subscription_types,
        'ContractDuration': contract_durations,
        'MonthlyCharges': monthly_charges,
        'TotalCharges': total_charges,
        'Tenure': tenures,
        'PaymentMethod': payment_methods,
        'SupportTickets': support_tickets_base,
        'LastInteraction': last_interactions,
        'Churn': churn_labels,
        'CustomerSegment': customer_segments,
    })

    # ── Inject realistic data quality issues ───────────────────────────
    # (So the cleaning pipeline has real work to do)

    # 1. Inject ~2% missing values in MonthlyCharges
    missing_idx = rng.choice(N_CUSTOMERS, size=int(N_CUSTOMERS * 0.02), replace=False)
    df.loc[missing_idx, 'MonthlyCharges'] = np.nan

    # 2. Inject ~1.5% missing values in TotalCharges
    missing_idx2 = rng.choice(N_CUSTOMERS, size=int(N_CUSTOMERS * 0.015), replace=False)
    df.loc[missing_idx2, 'TotalCharges'] = np.nan

    # 3. Inject ~1% missing values in SupportTickets
    missing_idx3 = rng.choice(N_CUSTOMERS, size=int(N_CUSTOMERS * 0.01), replace=False)
    df.loc[missing_idx3, 'SupportTickets'] = np.nan

    # 4. Inject ~20 duplicate rows
    dup_idx = rng.choice(N_CUSTOMERS, size=20, replace=False)
    duplicates = df.iloc[dup_idx].copy()
    df = pd.concat([df, duplicates], ignore_index=True)

    # 5. Inject casing inconsistencies in PaymentMethod
    case_idx = rng.choice(len(df), size=50, replace=False)
    for idx in case_idx:
        val = df.loc[idx, 'PaymentMethod']
        df.loc[idx, 'PaymentMethod'] = val.lower() if rng.random() > 0.5 else val.upper()

    # 6. Inject a few outliers in MonthlyCharges
    outlier_idx = rng.choice(len(df), size=10, replace=False)
    df.loc[outlier_idx, 'MonthlyCharges'] = rng.uniform(300, 500, size=10).round(2)

    # 7. Inject some negative TotalCharges (data entry errors)
    neg_idx = rng.choice(len(df), size=5, replace=False)
    df.loc[neg_idx, 'TotalCharges'] = -abs(df.loc[neg_idx, 'TotalCharges'].fillna(100))

    # ── Save ───────────────────────────────────────────────────────────
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    logger.info(f"Dataset saved to {output_path} — {len(df)} rows, {len(df.columns)} columns")

    return df


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s — %(levelname)s — %(message)s')
    df = generate_dataset()
    print(df.info())
    print(df.head())
