-- ============================================================================
-- COHORT ANALYSIS QUERIES
-- ============================================================================
-- Database: SQLite (saas_analytics.db)
-- Table: customers (loaded from cleaned dataset)
--
-- Methodology:
-- - Cohorts are defined by the month a customer signed up (SignupMonth)
-- - Retention is measured as: customers still active / total in cohort × 100
-- - This is a snapshot-based retention (not event-based)
-- - Reference date for analysis: 2025-01-01
-- ============================================================================

-- E1. Monthly acquisition cohorts — summary
SELECT 
    SignupMonth AS Cohort,
    COUNT(*) AS CohortSize,
    SUM(CASE WHEN Churn = 'No' THEN 1 ELSE 0 END) AS StillActive,
    SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) AS Churned,
    ROUND(SUM(CASE WHEN Churn = 'No' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS RetentionRatePct,
    ROUND(SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS ChurnRatePct
FROM customers
GROUP BY SignupMonth
ORDER BY SignupMonth;

-- E2. Quarterly acquisition cohorts
SELECT 
    SignupQuarter AS Cohort,
    COUNT(*) AS CohortSize,
    SUM(CASE WHEN Churn = 'No' THEN 1 ELSE 0 END) AS StillActive,
    ROUND(SUM(CASE WHEN Churn = 'No' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS RetentionRatePct,
    ROUND(AVG(Tenure), 1) AS AvgTenureMonths,
    ROUND(SUM(TotalCharges), 2) AS TotalCohortRevenue,
    ROUND(AVG(TotalCharges), 2) AS AvgLTV
FROM customers
GROUP BY SignupQuarter
ORDER BY SignupQuarter;

-- E3. Cohort retention matrix (monthly cohorts × tenure buckets)
-- Shows what percentage of each cohort is retained at each tenure milestone
SELECT 
    SignupMonth AS Cohort,
    COUNT(*) AS CohortSize,
    -- Retention at various tenure milestones
    ROUND(SUM(CASE WHEN Tenure >= 3 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS Retained_3mo,
    ROUND(SUM(CASE WHEN Tenure >= 6 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS Retained_6mo,
    ROUND(SUM(CASE WHEN Tenure >= 12 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS Retained_12mo,
    ROUND(SUM(CASE WHEN Tenure >= 18 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS Retained_18mo,
    ROUND(SUM(CASE WHEN Tenure >= 24 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS Retained_24mo,
    -- Overall retention (not churned)
    ROUND(SUM(CASE WHEN Churn = 'No' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS CurrentRetention
FROM customers
GROUP BY SignupMonth
ORDER BY SignupMonth;

-- E4. Revenue by acquisition cohort (quarterly)
SELECT 
    SignupQuarter AS Cohort,
    COUNT(*) AS CohortSize,
    ROUND(SUM(TotalCharges), 2) AS TotalCohortRevenue,
    ROUND(AVG(TotalCharges), 2) AS AvgRevenuePerCustomer,
    ROUND(SUM(MonthlyCharges), 2) AS CurrentMRR,
    ROUND(AVG(MonthlyCharges), 2) AS AvgMonthlyCharge,
    ROUND(SUM(CASE WHEN Churn = 'No' THEN MonthlyCharges ELSE 0 END), 2) AS ActiveMRR
FROM customers
GROUP BY SignupQuarter
ORDER BY SignupQuarter;

-- E5. Cohort retention by subscription type
SELECT 
    SignupQuarter AS Cohort,
    SubscriptionType,
    COUNT(*) AS CohortSize,
    SUM(CASE WHEN Churn = 'No' THEN 1 ELSE 0 END) AS StillActive,
    ROUND(SUM(CASE WHEN Churn = 'No' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS RetentionRatePct,
    ROUND(AVG(TotalCharges), 2) AS AvgLTV
FROM customers
GROUP BY SignupQuarter, SubscriptionType
ORDER BY SignupQuarter, SubscriptionType;

-- E6. Early churn analysis by cohort
-- Customers who churned within the first 6 months
SELECT 
    SignupQuarter AS Cohort,
    COUNT(*) AS CohortSize,
    SUM(CASE WHEN Churn = 'Yes' AND Tenure <= 6 THEN 1 ELSE 0 END) AS EarlyChurners,
    ROUND(SUM(CASE WHEN Churn = 'Yes' AND Tenure <= 6 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS EarlyChurnRatePct,
    ROUND(AVG(CASE WHEN Churn = 'Yes' AND Tenure <= 6 THEN MonthlyCharges ELSE NULL END), 2) AS AvgEarlyChurnCharge
FROM customers
GROUP BY SignupQuarter
ORDER BY SignupQuarter;

-- E7. Best and worst performing cohorts
SELECT 
    SignupQuarter AS Cohort,
    COUNT(*) AS CohortSize,
    ROUND(SUM(CASE WHEN Churn = 'No' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS RetentionRatePct,
    ROUND(AVG(TotalCharges), 2) AS AvgLTV,
    ROUND(SUM(TotalCharges), 2) AS TotalRevenue
FROM customers
GROUP BY SignupQuarter
HAVING COUNT(*) >= 50  -- Only cohorts with meaningful size
ORDER BY RetentionRatePct DESC;

-- E8. Cohort health score
-- Combines retention rate, average LTV, and support ticket metrics
SELECT 
    SignupQuarter AS Cohort,
    COUNT(*) AS CohortSize,
    ROUND(SUM(CASE WHEN Churn = 'No' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS RetentionPct,
    ROUND(AVG(TotalCharges), 2) AS AvgLTV,
    ROUND(AVG(SupportTickets), 1) AS AvgSupportTickets,
    ROUND(AVG(MonthlyCharges), 2) AS AvgMonthlyCharge,
    -- Health score: weighted combination (higher is better)
    ROUND(
        (SUM(CASE WHEN Churn = 'No' THEN 1 ELSE 0 END) * 100.0 / COUNT(*)) * 0.5 +
        (AVG(TotalCharges) / (SELECT MAX(AVG(TotalCharges)) FROM customers GROUP BY SignupQuarter) * 100) * 0.3 -
        (AVG(SupportTickets) * 5) * 0.2
    , 2) AS HealthScore
FROM customers
GROUP BY SignupQuarter
ORDER BY HealthScore DESC;
