# Power BI Dashboard Specification & DAX Measures Documentation

## 1. Overview & Architecture

This document provides complete instructions, data modeling schemas, and production DAX formulas for recreating the **SaaS Customer LTV & Churn Executive Dashboard** in Microsoft Power BI.

### 1.1 Data Source Files
All export files are located in `dashboard/exports/`:
- `full_dataset_powerbi.csv`: Primary transactional and customer snapshot table (5,000 records).
- `executive_overview.csv`: Pre-aggregated high-level KPI card metrics.
- `churn_analysis.csv`: Dimension-level churn breakdown by segment, tier, and contract.
- `revenue_ltv_analysis.csv`: Revenue, ARPU, and LTV distribution metrics.
- `cohort_retention.csv`: Monthly acquisition cohort retention matrix.

---

## 2. Power BI Data Model (Star Schema)

For enterprise Power BI implementations, import `full_dataset_powerbi.csv` as `FactSubscriptions` and create the following relationships:

```
                  ┌──────────────────────┐
                  │      DimDate         │
                  │  (Date, Month, Qtr)  │
                  └──────────┬───────────┘
                             │ 1
                             │
                             │ * (SignupDate)
┌──────────────────────┐     ▼     ┌──────────────────────┐
│     DimCustomer      │*         *│      DimContract     │
│ (Segment, Country)   ├───────────┤   (Duration, Tier)   │
└──────────────────────┘           └──────────────────────┘
                             ▲
                             │ *
                             │ 1
                  ┌──────────┴───────────┐
                  │  FactSubscriptions   │
                  │ (Charges, Churn, LTV)│
                  └──────────────────────┘
```

### Table Schema Definition (`FactSubscriptions`):
- `CustomerID` (Text) — Unique customer identifier
- `SignupDate` (Date) — Initial subscription activation date
- `SignupMonth` (Text, Format: YYYY-MM) — Cohort grouping key
- `SignupQuarter` (Text, Format: YYYY-QX) — Quarterly grouping key
- `SubscriptionType` (Text) — 'Basic', 'Standard', 'Premium'
- `ContractDuration` (Text) — 'Month-to-Month', 'One Year', 'Two Year'
- `MonthlyCharges` (Currency / Decimal) — Current recurring subscription fee ($)
- `TotalCharges` (Currency / Decimal) — Cumulative revenue billed ($)
- `Tenure` (Integer) — Lifetime duration in months
- `Churn` (Text) — 'Yes' / 'No'
- `ChurnFlag` (Integer) — 1 = Churned, 0 = Active
- `CustomerSegment` (Text) — 'SMB', 'Mid-Market', 'Enterprise'
- `PaymentMethod` (Text) — 'Credit Card', 'Bank Transfer', 'Electronic Check', 'Mailed Check'
- `SupportTickets` (Integer) — Number of tickets filed
- `TenureGroup` (Text) — '0-6 Months', '7-12 Months', '13-24 Months', '25+ Months'
- `LTV_Segment` (Text) — 'Low (<$500)', 'Medium ($500-$1,500)', 'High (>$1,500)'

---

## 3. Core DAX Measures

Organize all measures inside a dedicated measure table named `_Measures`.

### 3.1 Customer Volume Measures

#### Total Customers
```dax
Total Customers = 
COUNTROWS(FactSubscriptions)
```

#### Active Customers
```dax
Active Customers = 
CALCULATE(
    COUNTROWS(FactSubscriptions),
    FactSubscriptions[Churn] = "No"
)
```

#### Churned Customers
```dax
Churned Customers = 
CALCULATE(
    COUNTROWS(FactSubscriptions),
    FactSubscriptions[Churn] = "Yes"
)
```

#### Overall Churn Rate (%)
```dax
Churn Rate = 
DIVIDE([Churned Customers], [Total Customers], 0)
```

#### Overall Retention Rate (%)
```dax
Retention Rate = 
1 - [Churn Rate]
```

---

### 3.2 Recurring Revenue Measures

#### Monthly Recurring Revenue (MRR)
```dax
MRR = 
CALCULATE(
    SUM(FactSubscriptions[MonthlyCharges]),
    FactSubscriptions[Churn] = "No"
)
```

#### Annual Recurring Revenue (ARR)
```dax
ARR = 
[MRR] * 12
```

#### Average Revenue Per User (ARPU)
```dax
ARPU = 
DIVIDE([MRR], [Active Customers], 0)
```

#### Churned Monthly Revenue (Monthly Revenue Lost)
```dax
Churned MRR = 
CALCULATE(
    SUM(FactSubscriptions[MonthlyCharges]),
    FactSubscriptions[Churn] = "Yes"
)
```

#### Annualized Revenue Lost to Churn
```dax
Annualized Lost Revenue = 
[Churned MRR] * 12
```

---

### 3.3 Customer Lifetime Value (LTV) Measures

#### Cumulative Realized Revenue
```dax
Total Historical Revenue = 
SUM(FactSubscriptions[TotalCharges])
```

#### Average Realized Customer LTV
```dax
Avg Customer LTV = 
AVERAGE(FactSubscriptions[TotalCharges])
```

#### Modeled LTV (ARPU / Churn Rate)
```dax
Modeled LTV = 
IF(
    [Churn Rate] > 0,
    DIVIDE([ARPU], [Churn Rate], 0),
    BLANK()
)
```

#### LTV to Support Ticket Ratio
```dax
Avg LTV per Ticket Group = 
DIVIDE([Total Historical Revenue], SUM(FactSubscriptions[SupportTickets]), 0)
```

---

### 3.4 Cohort Analysis Measures

#### Cohort Size
```dax
Cohort Initial Size = 
CALCULATE(
    COUNTROWS(FactSubscriptions),
    ALLEXCEPT(FactSubscriptions, FactSubscriptions[SignupMonth])
)
```

#### Cohort Retention Rate (%)
```dax
Cohort Retention % = 
VAR ActiveInCohort = 
    CALCULATE(
        COUNTROWS(FactSubscriptions),
        FactSubscriptions[Churn] = "No"
    )
RETURN
    DIVIDE(ActiveInCohort, [Cohort Initial Size], 0)
```

---

## 4. Dashboard Visual Layout (4-Page Architecture)

### Page 1: Executive KPI Summary
- **Top Header**: Date range filter, Subscription Type slicer, Customer Segment slicer.
- **KPI Cards (Row 1)**:
  1. MRR (`$239,435`) | Target: `+5.2% MoM`
  2. ARR (`$2,873,214`)
  3. Total Customers (`5,000`) | Active: `3,361`
  4. Churn Rate (`32.78%`) | Target: `<25.0%`
  5. Average Realized LTV (`$1,197`)
- **Visual 1 (Donut Chart)**: Customers by Subscription Tier (Basic, Standard, Premium).
- **Visual 2 (Clustered Bar Chart)**: Churn Rate by Contract Duration (Month-to-Month vs. 1-Year vs. 2-Year).
- **Visual 3 (Stacked Column Chart)**: Total Revenue Contribution by Customer Segment.

### Page 2: Churn & Risk Deep Dive
- **Visual 1 (Scatter / Line Plot)**: Support Tickets vs. Churn Rate (shows inflection point at 3+ tickets).
- **Visual 2 (Bar Chart)**: Churn Rate by Payment Method (shows Electronic Check drop-off).
- **Visual 3 (Histogram / Bar)**: Churn Rate by Customer Tenure Group (0-6m, 7-12m, 13-24m, 25+m).
- **KPI Callout Box**: Early Tenure Warning (368 customers churned in <=3 months, accounting for 22.5% of all churn).

### Page 3: Revenue & LTV Optimization
- **Visual 1 (Treemap)**: Total Charges generated by Subscription Type and Segment.
- **Visual 2 (Box & Whisker / Distribution)**: Monthly Charges spread across customer tiers.
- **Visual 3 (Table / Matrix)**:
  - Rows: `CustomerSegment`
  - Columns: `ContractDuration`
  - Values: `[Active Customers]`, `[MRR]`, `[Avg Customer LTV]`, `[Churn Rate]`

### Page 4: Cohort Retention Matrix
- **Matrix Visual**:
  - Rows: `SignupMonth` (or `SignupQuarter`)
  - Columns: `TenureGroup`
  - Values: `[Cohort Retention %]`
  - Conditional Formatting: Background color scale from Red (0%) -> Yellow (50%) -> Deep Green (100%).

---

## 5. Deployment & Refresh Instructions

1. Open **Power BI Desktop**.
2. Select **Get Data** > **Text/CSV** and select `dashboard/exports/full_dataset_powerbi.csv`.
3. In Power Query Editor, verify data types:
   - `MonthlyCharges`, `TotalCharges` -> **Decimal Number / Currency**
   - `Tenure`, `SupportTickets`, `ChurnFlag` -> **Whole Number**
   - `SignupDate` -> **Date**
4. Click **Close & Apply**.
5. Create a new calculated table for measures: `_Measures = ROW("Setup", 1)`.
6. Copy and paste each DAX formula from Section 3.
7. Format all currency measures as `$#,##0` and percentage measures as `0.0%`.
8. Save file as `SaaS_Customer_Analytics.pbix`.
