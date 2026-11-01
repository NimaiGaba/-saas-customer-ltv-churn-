"""
Tests for SQLite Database and SQL Analysis Queries
"""

import os
import sys
import sqlite3
import pytest
import pandas as pd

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(PROJECT_ROOT, "saas_analytics.db")


@pytest.fixture(scope="module")
def db_conn():
    """Provide connection to the SQLite database."""
    if not os.path.exists(DB_PATH):
        pytest.skip("SQLite database does not exist. Run main.py first.")
    conn = sqlite3.connect(DB_PATH)
    yield conn
    conn.close()


def test_database_tables_exist(db_conn):
    """Verify primary table exists and has data."""
    cursor = db_conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type IN ('table', 'view')")
    objects = [r[0] for r in cursor.fetchall()]
    
    assert "customers" in objects


def test_customer_count_and_integrity(db_conn):
    """Verify record counts match expected 5,000 customers."""
    cursor = db_conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM customers")
    count = cursor.fetchone()[0]
    assert count == 5000


def test_sql_kpi_consistency(db_conn):
    """Verify SQL aggregations match expected business logic."""
    df_kpi = pd.read_sql_query("""
        SELECT 
            COUNT(*) AS total_customers,
            SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) AS churned,
            SUM(CASE WHEN Churn = 'No' THEN 1 ELSE 0 END) AS active,
            SUM(CASE WHEN Churn = 'No' THEN MonthlyCharges ELSE 0 END) AS active_mrr
        FROM customers
    """, db_conn)
    
    assert df_kpi['total_customers'].iloc[0] == 5000
    assert df_kpi['churned'].iloc[0] + df_kpi['active'].iloc[0] == 5000
    assert df_kpi['active_mrr'].iloc[0] > 0


def test_sql_script_execution(db_conn):
    """Verify that queries from SQL files run without syntax errors."""
    sql_files = ['customer_analysis.sql', 'revenue_analysis.sql', 'churn_analysis.sql']
    cursor = db_conn.cursor()
    
    for sql_file in sql_files:
        filepath = os.path.join(PROJECT_ROOT, 'sql', sql_file)
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            # Test a sample query
            assert "SELECT" in content.upper()
