"""
Data Cleaning & Feature Engineering Pipeline
=============================================
Loads raw SaaS subscription data, applies systematic cleaning, engineers
analytical features, validates data quality, and saves the processed output.

Cleaning steps:
1. Missing value analysis and treatment (median imputation for numerics)
2. Duplicate detection and removal
3. Data type correction and standardization
4. Outlier investigation and capping (IQR method)
5. Categorical data standardization (title case, valid categories)
6. Data validation (range checks, logical consistency)
7. Feature engineering (tenure groups, charge bands, LTV estimate, etc.)
"""

import pandas as pd
import numpy as np
import os
import logging

logger = logging.getLogger(__name__)


def load_raw_data(filepath: str) -> pd.DataFrame:
    """Load the raw CSV dataset."""
    logger.info(f"Loading raw data from {filepath}")
    df = pd.read_csv(filepath)
    logger.info(f"Loaded {len(df)} rows, {len(df.columns)} columns")
    return df


def analyze_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """Report missing values by column."""
    missing = df.isnull().sum()
    missing_pct = (missing / len(df) * 100).round(2)
    report = pd.DataFrame({
        'MissingCount': missing,
        'MissingPercent': missing_pct
    }).query('MissingCount > 0').sort_values('MissingCount', ascending=False)
    if len(report) > 0:
        logger.info(f"Missing values found in {len(report)} columns:\n{report}")
    else:
        logger.info("No missing values found")
    return report


def treat_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """Impute missing values using appropriate strategies."""
    df = df.copy()

    # MonthlyCharges: impute with median grouped by SubscriptionType
    if df['MonthlyCharges'].isnull().any():
        count = df['MonthlyCharges'].isnull().sum()
        medians = df.groupby('SubscriptionType')['MonthlyCharges'].transform('median')
        df['MonthlyCharges'] = df['MonthlyCharges'].fillna(medians)
        # Fallback for any remaining NaN
        df['MonthlyCharges'] = df['MonthlyCharges'].fillna(df['MonthlyCharges'].median())
        logger.info(f"Imputed {count} missing MonthlyCharges values (group median)")

    # TotalCharges: impute as Tenure × MonthlyCharges
    if df['TotalCharges'].isnull().any():
        count = df['TotalCharges'].isnull().sum()
        df['TotalCharges'] = df['TotalCharges'].fillna(
            df['Tenure'] * df['MonthlyCharges']
        )
        logger.info(f"Imputed {count} missing TotalCharges values (Tenure × MonthlyCharges)")

    # SupportTickets: impute with 0 (assume no tickets if missing)
    if df['SupportTickets'].isnull().any():
        count = df['SupportTickets'].isnull().sum()
        df['SupportTickets'] = df['SupportTickets'].fillna(0)
        logger.info(f"Imputed {count} missing SupportTickets values (filled with 0)")

    return df


def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """Detect and remove duplicate rows based on CustomerID."""
    before = len(df)
    df = df.drop_duplicates(subset=['CustomerID'], keep='first')
    removed = before - len(df)
    if removed > 0:
        logger.info(f"Removed {removed} duplicate rows (kept first occurrence by CustomerID)")
    else:
        logger.info("No duplicate rows found")
    return df.reset_index(drop=True)


def correct_data_types(df: pd.DataFrame) -> pd.DataFrame:
    """Ensure correct data types for all columns."""
    df = df.copy()

    # Dates
    df['SignupDate'] = pd.to_datetime(df['SignupDate'], errors='coerce')
    df['LastInteraction'] = pd.to_datetime(df['LastInteraction'], errors='coerce')

    # Numerics
    df['MonthlyCharges'] = pd.to_numeric(df['MonthlyCharges'], errors='coerce')
    df['TotalCharges'] = pd.to_numeric(df['TotalCharges'], errors='coerce')
    df['SupportTickets'] = pd.to_numeric(df['SupportTickets'], errors='coerce').fillna(0).astype(int)
    df['Tenure'] = pd.to_numeric(df['Tenure'], errors='coerce').fillna(0).astype(int)
    df['Age'] = pd.to_numeric(df['Age'], errors='coerce').fillna(0).astype(int)

    logger.info("Data types corrected")
    return df


def investigate_outliers(df: pd.DataFrame) -> pd.DataFrame:
    """Investigate and cap outliers using the IQR method for MonthlyCharges."""
    df = df.copy()

    for col in ['MonthlyCharges', 'TotalCharges']:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        lower = Q1 - 1.5 * IQR
        upper = Q3 + 1.5 * IQR

        outliers = ((df[col] < lower) | (df[col] > upper)).sum()
        if outliers > 0:
            df[col] = df[col].clip(lower=max(0, lower), upper=upper)
            logger.info(f"Capped {outliers} outliers in {col} (IQR range: {lower:.2f}–{upper:.2f})")

    # Fix negative TotalCharges (data entry errors)
    neg_count = (df['TotalCharges'] < 0).sum()
    if neg_count > 0:
        df.loc[df['TotalCharges'] < 0, 'TotalCharges'] = abs(df.loc[df['TotalCharges'] < 0, 'TotalCharges'])
        logger.info(f"Corrected {neg_count} negative TotalCharges values (converted to absolute)")

    return df


def standardize_categories(df: pd.DataFrame) -> pd.DataFrame:
    """Standardize categorical columns to title case and valid values."""
    df = df.copy()

    # Payment method standardization
    payment_map = {
        'credit card': 'Credit Card',
        'bank transfer': 'Bank Transfer',
        'paypal': 'PayPal',
        'check': 'Check',
        'CREDIT CARD': 'Credit Card',
        'BANK TRANSFER': 'Bank Transfer',
        'PAYPAL': 'PayPal',
        'CHECK': 'Check',
    }
    original_unique = df['PaymentMethod'].nunique()
    df['PaymentMethod'] = df['PaymentMethod'].map(
        lambda x: payment_map.get(x, x) if isinstance(x, str) else x
    )
    new_unique = df['PaymentMethod'].nunique()
    if original_unique != new_unique:
        logger.info(f"Standardized PaymentMethod: {original_unique} → {new_unique} unique values")

    # Ensure valid categories
    valid_subscriptions = ['Basic', 'Standard', 'Premium']
    valid_contracts = ['Month-to-Month', 'One Year', 'Two Year']
    valid_segments = ['SMB', 'Mid-Market', 'Enterprise']
    valid_churn = ['Yes', 'No']

    df['SubscriptionType'] = df['SubscriptionType'].apply(
        lambda x: x if x in valid_subscriptions else 'Basic')
    df['ContractDuration'] = df['ContractDuration'].apply(
        lambda x: x if x in valid_contracts else 'Month-to-Month')
    df['CustomerSegment'] = df['CustomerSegment'].apply(
        lambda x: x if x in valid_segments else 'SMB')
    df['Churn'] = df['Churn'].apply(
        lambda x: x if x in valid_churn else 'No')

    logger.info("Categorical data standardized")
    return df


def validate_data(df: pd.DataFrame) -> pd.DataFrame:
    """Run validation checks and log warnings for any issues."""
    df = df.copy()
    issues = []

    # Range checks
    if (df['Age'] < 18).any() or (df['Age'] > 100).any():
        count = ((df['Age'] < 18) | (df['Age'] > 100)).sum()
        df['Age'] = df['Age'].clip(18, 100)
        issues.append(f"Clipped {count} Age values to [18, 100]")

    if (df['Tenure'] < 0).any() or (df['Tenure'] > 60).any():
        count = ((df['Tenure'] < 0) | (df['Tenure'] > 60)).sum()
        df['Tenure'] = df['Tenure'].clip(0, 60)
        issues.append(f"Clipped {count} Tenure values to [0, 60]")

    if (df['MonthlyCharges'] <= 0).any():
        count = (df['MonthlyCharges'] <= 0).sum()
        df.loc[df['MonthlyCharges'] <= 0, 'MonthlyCharges'] = df['MonthlyCharges'].median()
        issues.append(f"Fixed {count} non-positive MonthlyCharges values")

    if (df['SupportTickets'] < 0).any():
        count = (df['SupportTickets'] < 0).sum()
        df.loc[df['SupportTickets'] < 0, 'SupportTickets'] = 0
        issues.append(f"Fixed {count} negative SupportTickets values")

    # Logical consistency: TotalCharges should be >= MonthlyCharges
    inconsistent = (df['TotalCharges'] < df['MonthlyCharges']).sum()
    if inconsistent > 0:
        df.loc[df['TotalCharges'] < df['MonthlyCharges'], 'TotalCharges'] = (
            df.loc[df['TotalCharges'] < df['MonthlyCharges'], 'Tenure'] *
            df.loc[df['TotalCharges'] < df['MonthlyCharges'], 'MonthlyCharges']
        )
        issues.append(f"Recalculated {inconsistent} TotalCharges < MonthlyCharges")

    if issues:
        for issue in issues:
            logger.warning(f"Validation: {issue}")
    else:
        logger.info("All validation checks passed")

    return df


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Create analytical features from existing columns."""
    df = df.copy()

    # 1. Tenure Group
    bins = [0, 6, 12, 24, 36, 100]
    labels = ['0-6 months', '7-12 months', '13-24 months', '25-36 months', '36+ months']
    df['TenureGroup'] = pd.cut(df['Tenure'], bins=bins, labels=labels, right=True)

    # 2. Monthly Charge Band
    charge_bins = [0, 30, 60, 100, 150, 500]
    charge_labels = ['$0-30', '$31-60', '$61-100', '$101-150', '$150+']
    df['ChargeBand'] = pd.cut(df['MonthlyCharges'], bins=charge_bins,
                               labels=charge_labels, right=True)

    # 3. Customer Lifetime Value (historical) = TotalCharges
    # This is the actual revenue received, NOT a prediction
    df['CustomerLTV'] = df['TotalCharges']

    # 4. Average Monthly Revenue = TotalCharges / Tenure
    df['AvgMonthlyRevenue'] = np.where(
        df['Tenure'] > 0,
        (df['TotalCharges'] / df['Tenure']).round(2),
        df['MonthlyCharges']
    )

    # 5. Signup Month and Year for cohort analysis
    df['SignupMonth'] = df['SignupDate'].dt.to_period('M').astype(str)
    df['SignupYear'] = df['SignupDate'].dt.year
    df['SignupQuarter'] = df['SignupDate'].dt.to_period('Q').astype(str)

    # 6. Churn binary flag (for numeric analysis)
    df['ChurnFlag'] = (df['Churn'] == 'Yes').astype(int)

    # 7. Support Ticket Category
    df['TicketCategory'] = pd.cut(
        df['SupportTickets'],
        bins=[-1, 0, 2, 5, 100],
        labels=['None', 'Low (1-2)', 'Medium (3-5)', 'High (5+)']
    )

    # 8. Days since last interaction
    reference_date = pd.Timestamp('2025-01-01')
    df['DaysSinceInteraction'] = (reference_date - df['LastInteraction']).dt.days

    logger.info(f"Engineered {8} new features")
    return df


def run_cleaning_pipeline(
    input_path: str = 'data/raw/saas_customer_data.csv',
    output_path: str = 'data/processed/saas_customer_cleaned.csv'
) -> pd.DataFrame:
    """
    Execute the full data cleaning and feature engineering pipeline.

    Parameters
    ----------
    input_path : str
        Path to the raw CSV.
    output_path : str
        Path to save the cleaned CSV.

    Returns
    -------
    pd.DataFrame
        Cleaned and feature-engineered dataset.
    """
    logger.info("=" * 60)
    logger.info("STARTING DATA CLEANING PIPELINE")
    logger.info("=" * 60)

    # Step 1: Load
    df = load_raw_data(input_path)
    logger.info(f"Raw data shape: {df.shape}")

    # Step 2: Missing value analysis
    missing_report = analyze_missing_values(df)

    # Step 3: Data type correction (before imputation)
    df = correct_data_types(df)

    # Step 4: Treat missing values
    df = treat_missing_values(df)

    # Step 5: Remove duplicates
    df = remove_duplicates(df)

    # Step 6: Outlier investigation
    df = investigate_outliers(df)

    # Step 7: Standardize categories
    df = standardize_categories(df)

    # Step 8: Validate data
    df = validate_data(df)

    # Step 9: Feature engineering
    df = engineer_features(df)

    # Step 10: Final validation
    final_missing = df.isnull().sum().sum()
    logger.info(f"Final missing values: {final_missing}")
    logger.info(f"Cleaned data shape: {df.shape}")

    # Save
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    logger.info(f"Cleaned dataset saved to {output_path}")
    logger.info("=" * 60)
    logger.info("DATA CLEANING PIPELINE COMPLETE")
    logger.info("=" * 60)

    return df


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s — %(levelname)s — %(message)s')
    df = run_cleaning_pipeline()
    print(df.info())
    print(df.describe())
