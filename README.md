# SaaS Customer Lifetime Value (LTV) & Churn Analytics

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![SQL](https://img.shields.io/badge/SQL-SQLite%20%7C%20PostgreSQL-orange.svg)](https://www.sqlite.org/)
[![Power BI](https://img.shields.io/badge/Power%20BI-Dashboard-yellow.svg)](https://powerbi.microsoft.com/)
[![Tests](https://img.shields.io/badge/Tests-Pytest%2013%2F13%20Passing-brightgreen.svg)](https://pytest.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

An end-to-end, production-grade **Data Analytics and Business Intelligence project** that analyzes customer retention, churn drivers, and lifetime value (LTV) across a 5,000-customer B2B/B2C SaaS subscription platform. 

> **Scope Note:** This is a pure **Data Analytics, Business Analytics, and Business Intelligence** project. It deliberately avoids black-box machine learning algorithms in favor of rigorous statistical exploratory data analysis, advanced SQL cohort modeling, historical LTV calculations, and executive decision-making frameworks.

---

## 📌 Executive Summary & Key Results

| Metric | Measured Value | Business Interpretation |
|:---|:---:|:---|
| **Total Customers Analyzed** | **5,000** | Full 36-month subscription lifecycle cohort window |
| **Active Subscriptions** | **3,361 (67.22%)** | Current retained customer base |
| **Churned Subscriptions** | **1,639 (32.78%)** | Overall platform churn rate |
| **Monthly Recurring Revenue (MRR)** | **$239,434.52** | Contracted recurring revenue from active accounts |
| **Annual Recurring Revenue (ARR)** | **$2,873,214.24** | Annualized run-rate revenue |
| **Average Revenue Per User (ARPU)** | **$71.24 / mo** | Average monthly subscription fee per active user |
| **Average Customer LTV** | **$1,197.08** | Realized cumulative revenue per customer |
| **Annualized Churn Revenue Loss** | **$1,502,609.64** | Uncaptured annual revenue due to contract cancellations |

---

## 🎯 Business Problem & Objectives

Customer acquisition costs (CAC) in SaaS are often 5x to 7x higher than retention costs. When customer churn is unmonitored or poorly understood, revenue growth stalls regardless of top-of-funnel marketing spend.

This project delivers actionable intelligence to answer six executive questions:
1. **Which subscription tiers generate the highest revenue and customer lifetime value?**
2. **Which customer segments and contract types experience elevated churn risk?**
3. **What is the inflection point where customer support friction triggers cancellations?**
4. **How do acquisition cohorts perform over time, and where does early-tenure drop-off occur?**
5. **How much recurring revenue is lost to churn, and what is the dollar ROI of retention interventions?**
6. **How can executive leadership monitor real-time health metrics via an interactive Power BI dashboard?**

---

## 🛠️ Technology Stack & Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      SaaS Analytics Architecture                        │
├──────────────────┬──────────────────┬─────────────────┬─────────────────┤
│  Data Layer      │  Analytics Layer │  SQL / Database │  BI & Reporting │
├──────────────────┼──────────────────┼─────────────────┼─────────────────┤
│ • Synthetic Raw  │ • Pandas 2.2     │ • SQLite DB     │ • Power BI      │
│   SaaS Dataset   │ • NumPy 1.26     │ • 5 SQL Scripts │   Data Model    │
│ • Data Cleaning  │ • Matplotlib 3.9 │ • 54 Queries    │ • 15+ DAX Meas. │
│ • Outlier/Type   │ • Seaborn 0.13   │ • CTEs & Window │ • 12 EDA Charts │
│   Validation     │ • Pytest Suite   │   Functions     │ • Markdown Exec │
│ • Feature Eng.   │ • Logging Engine │ • Views & Aggrs │   Report        │
└──────────────────┴──────────────────┴─────────────────┴─────────────────┘
```

- **Python & Data Engineering**: Data loading, missing value imputation, IQR outlier capping, categorical normalization, tenure grouping, and customer profiling.
- **SQL Analytics Engine**: 5 production SQL scripts executing 54 queries across customer segmentation, revenue tracking, churn drivers, historical LTV quartiles, and retention cohorts.
- **Visualizations**: 12 high-resolution analytical charts + 1 cohort retention heatmap.
- **Business Intelligence**: Power BI star schema, 4-page dashboard specification, and complete DAX measures documentation.
- **Test Automation**: 13 unit tests via `pytest` validating data integrity, analytical logic, and database schemas.

---

## 📊 Core Analytical Findings

### 1. Contract Duration is the #1 Predictor of Customer Retention
- **Month-to-Month:** 44.39% churn rate (Avg tenure: 17.8 months).
- **One-Year Commitments:** 23.89% churn rate (46.2% reduction vs. monthly).
- **Two-Year Commitments:** 18.02% churn rate (59.4% reduction vs. monthly).
*Insight:* Customers with multi-year commitments exhibit significantly higher resilience, insulating the platform from short-term churn shocks.

### 2. Support Ticket Inflection Point at 3+ Tickets
- **0–2 Tickets:** Churn rate remains low between **10.08% and 21.58%**.
- **3 Tickets:** Churn jumps to **35.21%** (a 63% increase over 2 tickets).
- **4+ Tickets:** Churn escalates to **54.23%**, reaching **86.96%** at 7 tickets.
*Insight:* Customer dissatisfaction peaks around the 3rd support ticket. Interventions after 4 tickets arrive too late.

### 3. Premium Plan Drives Revenue but Carries Elevated Churn
- **Premium Tier:** Generates **$2,774,432.93** (46.35% of platform revenue), with an average LTV of **$2,255.64**.
- However, Premium accounts experience a **36.59% churn rate** compared to **30.47% for Basic** accounts.
*Insight:* Higher-paying customers have higher feature expectations and lower tolerance for unresolved friction.

### 4. Early-Tenure Drop-off (First 6 Months)
- Customers in their first 6 months account for **22.5% of all cancellations** (368 early churners).
- Cohort retention heatmaps reveal that retention stabilizes significantly once a customer crosses the 12-month tenure mark.

---

## 💡 Strategic Business Recommendations & ROI

| Recommendation | Target Audience | Tactical Action | Projected Financial Impact |
|:---|:---|:---|:---:|
| **1. Annual Contract Migration** | Month-to-Month subscribers at month 3 milestone | Offer a 15–20% discount on 1-year contract renewals | **+$150,260 / year** (retaining 10% of monthly churn) |
| **2. Proactive Support Escalation** | Accounts opening their 3rd support ticket | Auto-route to Tier 2 Customer Success Managers within 2 hours | **+$185,000 / year** in protected ARR |
| **3. Structured 90-Day Onboarding** | All new signups across SMB & Mid-Market | Automated milestones at Days 7, 30, 60, and 90 with guided product tours | **+$112,000 / year** by cutting early drop-off |
| **4. Premium Account Health Monitoring** | Premium subscribers ($95–$200/mo) | Dedicated onboarding specialist and quarterly business reviews (QBRs) | **+$220,000 / year** in preserved enterprise LTV |

---

## 📁 Repository Structure

```
saas-customer-ltv-churn/
├── dashboard/                      # Business Intelligence & Dashboard Assets
│   ├── charts/                     # 12 Generated High-Res Visualizations
│   │   ├── 01_churn_distribution.png
│   │   ├── 02_churn_by_subscription.png
│   │   ├── 03_churn_by_contract.png
│   │   ├── 04_churn_by_tenure.png
│   │   ├── 05_ltv_distribution.png
│   │   ├── 06_churn_by_payment.png
│   │   ├── 07_churn_by_support_tickets.png
│   │   ├── 08_revenue_by_subscription.png
│   │   ├── 09_customer_segments.png
│   │   ├── 10_mrr_trends.png
│   │   ├── 11_retention_trends.png
│   │   ├── 12_correlation_heatmap.png
│   │   ├── cohort_retention_heatmap.png
│   │   └── notebook_eda_summary.png
│   ├── exports/                    # Cleaned CSV Datasets for Power BI
│   │   ├── executive_overview.csv
│   │   ├── churn_analysis.csv
│   │   ├── revenue_ltv_analysis.csv
│   │   ├── cohort_retention.csv
│   │   └── full_dataset_powerbi.csv
│   └── dax_measures.md             # Complete DAX formulas & Power BI guide
├── data/                           # Data Storage
│   ├── raw/                        # Raw subscription data (5,000 rows)
│   │   └── saas_customer_data.csv
│   └── processed/                  # Cleaned & feature-engineered data
│       └── saas_customer_cleaned.csv
├── notebooks/                      # Exploratory Data Analysis Scripts
│   └── churn_eda_pipeline.py       # Standalone Python EDA analysis
├── reports/                        # Executive Deliverables
│   └── business_insights_report.md # Strategic Executive Insights Report
├── sql/                            # Production SQL Analysis Scripts
│   ├── customer_analysis.sql       # 11 queries: Customer counts & demographics
│   ├── revenue_analysis.sql        # 11 queries: MRR, ARR, ARPU, concentration
│   ├── churn_analysis.sql          # 11 queries: Churn drivers & ticket impacts
│   ├── ltv_analysis.sql            # 11 queries: Historical LTV & quartiles
│   └── cohort_analysis.sql         # 10 queries: Monthly/quarterly retention
├── src/                            # Modular Python Analytics Source Code
│   ├── __init__.py
│   ├── data_generation.py          # Synthetic SaaS benchmark dataset generator
│   ├── data_cleaning.py            # Data hygiene & feature engineering
│   ├── eda.py                      # 12 matplotlib/seaborn visualization suite
│   ├── customer_analysis.py        # Customer KPIs & demographic profiling
│   ├── revenue_analysis.py         # MRR, ARR, Pareto revenue concentration
│   ├── ltv_analysis.py             # Historical LTV distribution & quartiles
│   └── cohort_analysis.py          # Acquisition cohort retention matrix
├── tests/                          # Automated Pytest Suite
│   ├── test_data_cleaning.py       # Imputation, deduplication, feature tests
│   ├── test_analytics.py           # Metric calculation & aggregation tests
│   └── test_sql.py                 # SQLite database and query integrity tests
├── .gitignore                      # Git ignore patterns
├── main.py                         # End-to-end pipeline orchestrator
├── README.md                       # Project documentation
├── requirements.txt                # Python dependencies
└── saas_analytics.db               # SQLite database file
```

---

## 🚀 Installation & Execution

### Prerequisites
- Python 3.10 or higher
- Power BI Desktop (optional, for viewing `.pbix` dashboards)

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/saas-customer-ltv-churn.git
cd saas-customer-ltv-churn
```

### 2. Set Up Virtual Environment & Install Dependencies
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Run the Full Analytics Pipeline
Execute the end-to-end orchestration pipeline with a single command:
```bash
python main.py
```
**Pipeline Execution Steps:**
1. Generates 5,000 synthetic SaaS customer records (`data/raw/`).
2. Cleans data, handles missing values, removes duplicates, and engineers features (`data/processed/`).
3. Generates 12 high-resolution EDA figures (`dashboard/charts/`).
4. Ingests data into SQLite (`saas_analytics.db`).
5. Executes all 54 analytical SQL queries across 5 scripts.
6. Conducts in-depth customer, revenue, LTV, and cohort analytics.
7. Exports dashboard-ready CSVs (`dashboard/exports/`).
8. Generates the executive markdown report (`reports/business_insights_report.md`).

### 4. Run the Test Suite
Validate all data pipelines, SQL queries, and analytics modules:
```bash
pytest tests/ -v
```
*Result: 13 passed tests in ~2.7s.*

---

## 📈 Power BI Dashboard Setup

Detailed DAX measures, table schemas, and layout instructions are documented in [`dashboard/dax_measures.md`](dashboard/dax_measures.md).

### Quick Setup:
1. Open **Power BI Desktop**.
2. Select **Get Data** > **Text/CSV** and select `dashboard/exports/full_dataset_powerbi.csv`.
3. Create a calculated table `_Measures` and paste the DAX formulas provided in [`dashboard/dax_measures.md`](dashboard/dax_measures.md).
4. Build the 4-page dashboard following the layout specifications.

---

## 📄 License & Attribution

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. Built for data analytics, business intelligence, and customer success portfolio demonstrations.
