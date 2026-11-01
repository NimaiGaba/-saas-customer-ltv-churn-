"""
Tests for Data Cleaning & Feature Engineering Pipeline
"""

import os
import sys
import pytest
import pandas as pd
import numpy as np

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from src.data_cleaning import (
    load_raw_data,
    treat_missing_values,
    remove_duplicates,
    correct_data_types,
    investigate_outliers,
    standardize_categories,
    validate_data,
    engineer_features,
    run_cleaning_pipeline
)

RAW_DATA_PATH = os.path.join(PROJECT_ROOT, "data", "raw", "saas_customer_data.csv")


@pytest.fixture(scope="module")
def sample_raw_data():
    """Load sample raw dataset."""
    if not os.path.exists(RAW_DATA_PATH):
        pytest.skip("Raw data not generated yet")
    return pd.read_csv(RAW_DATA_PATH).head(500)


def test_missing_value_treatment(sample_raw_data):
    """Verify missing values are handled via group medians and defaults."""
    df_raw = sample_raw_data.copy()
    df_raw.loc[0, 'MonthlyCharges'] = np.nan
    df_raw.loc[1, 'TotalCharges'] = np.nan
    df_raw.loc[2, 'SupportTickets'] = np.nan
    
    df_treated = treat_missing_values(df_raw)
    
    assert df_treated['MonthlyCharges'].isna().sum() == 0
    assert df_treated['TotalCharges'].isna().sum() == 0
    assert df_treated['SupportTickets'].isna().sum() == 0


def test_remove_duplicates(sample_raw_data):
    """Verify duplicate detection by CustomerID."""
    df_raw = sample_raw_data.copy()
    duplicate_row = df_raw.iloc[0:1].copy()
    df_with_dupes = pd.concat([df_raw, duplicate_row], ignore_index=True)
    
    assert len(df_with_dupes) == len(df_raw) + 1
    df_deduped = remove_duplicates(df_with_dupes)
    assert len(df_deduped) == len(df_raw)
    assert df_deduped['CustomerID'].is_unique


def test_feature_engineering_creates_expected_columns(sample_raw_data):
    """Verify analytical features are created correctly."""
    df_types = correct_data_types(sample_raw_data.copy())
    featured_df = engineer_features(df_types)
    
    expected_cols = [
        'TenureGroup',
        'ChargeBand',
        'CustomerLTV',
        'AvgMonthlyRevenue',
        'SignupMonth',
        'SignupQuarter',
        'ChurnFlag',
        'TicketCategory',
        'DaysSinceInteraction'
    ]
    for col in expected_cols:
        assert col in featured_df.columns, f"Expected engineered column {col} missing"
        
    assert set(featured_df['ChurnFlag'].unique()).issubset({0, 1})
    assert featured_df['CustomerLTV'].equals(featured_df['TotalCharges'])


def test_validate_data_corrections(sample_raw_data):
    """Verify range checks and corrections in validate_data."""
    df = treat_missing_values(correct_data_types(sample_raw_data.copy()))
    df.loc[0, 'Tenure'] = -5
    df.loc[1, 'MonthlyCharges'] = -50.0
    
    df_corrected = validate_data(df)
    assert (df_corrected['Tenure'] >= 0).all()
    assert (df_corrected['MonthlyCharges'] > 0).all()
    assert (df_corrected['TotalCharges'] >= 0).all()
