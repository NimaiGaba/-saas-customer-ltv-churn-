# SaaS Customer Lifetime Value (LTV) & Churn Risk Engine

## 📌 Executive Summary
Customer retention is the primary growth lever for this B2B SaaS platform. This project ingests subscription and billing data to predict which customer segments are at the highest risk of churning. By applying Exploratory Data Analysis (EDA) in Python and calculating Lifetime Value (LTV) cohorts in SQL, this pipeline feeds into an executive Power BI dashboard designed to empower the Customer Success team.

## 🛠 Tech Stack & Architecture
- **Data Engineering:** Python (Pandas, NumPy, SQLAlchemy)
- **Machine Learning / Statistics:** Scikit-Learn (Logistic Regression for risk scoring)
- **Visualization:** Matplotlib, Seaborn, Power BI

## 📊 Key Business Findings
- **High-Risk Segment:** Month-to-month subscribers with add-on features disabled showed a staggering 41.8% attrition rate compared to 2.7% for annual commitment accounts.
- **Support Ticket Correlation:** Customers who opened >3 support tickets in their first 30 days and had a resolution time >24 hours were 3x more likely to churn.
- **Onboarding Drop-off:** (Custom Insight) Accounts onboarded on Fridays showed a 15% lower 30-day retention rate compared to mid-week signups, indicating potential gaps in weekend automated support workflows.

## 💡 Strategic Recommendations
1. Deploy an automated targeted discount campaign offering 20% off for month-to-month users who upgrade to an annual plan after month 3.
2. Introduce weekend coverage for the onboarding success team to plug the Friday signup retention leak.

## 📁 Repository Structure
- `/notebooks/`: Python scripts for data wrangling and churn modeling
- `/dashboard/`: Dashboard design assets and DAX measures
