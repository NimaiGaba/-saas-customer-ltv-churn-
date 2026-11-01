-- ============================================================================
-- REVENUE ANALYSIS QUERIES
-- ============================================================================
-- Database: SQLite (saas_analytics.db)
-- Table: customers (loaded from cleaned dataset)
--
-- Formulas & Assumptions:
--   MRR = SUM(MonthlyCharges) for active customers
--   ARPU = MRR / COUNT(active customers)
--   Revenue contribution = customer TotalCharges / SUM(all TotalCharges)
-- ============================================================================

-- B1. Monthly Recurring Revenue (MRR) from active customers
-- MRR represents the total predictable revenue from all active subscriptions.
SELECT 
    ROUND(SUM(MonthlyCharges), 2) AS MonthlyRecurringRevenue,
    COUNT(*) AS ActiveSubscriptions
FROM customers
WHERE Churn = 'No';

-- B2. Average Revenue Per User (ARPU)
-- ARPU = Total MRR / Number of active customers
SELECT 
    ROUND(SUM(MonthlyCharges) / COUNT(*), 2) AS ARPU
FROM customers
WHERE Churn = 'No';

-- B3. Revenue by subscription type
SELECT 
    SubscriptionType,
    COUNT(*) AS CustomerCount,
    ROUND(SUM(TotalCharges), 2) AS TotalRevenue,
    ROUND(AVG(TotalCharges), 2) AS AvgRevenue,
    ROUND(SUM(MonthlyCharges), 2) AS CurrentMRR,
    ROUND(AVG(MonthlyCharges), 2) AS AvgMonthlyCharge,
    ROUND(SUM(TotalCharges) * 100.0 / (SELECT SUM(TotalCharges) FROM customers), 2) AS RevenueSharePct
FROM customers
GROUP BY SubscriptionType
ORDER BY TotalRevenue DESC;

-- B4. Revenue by customer segment
SELECT 
    CustomerSegment,
    COUNT(*) AS CustomerCount,
    ROUND(SUM(TotalCharges), 2) AS TotalRevenue,
    ROUND(AVG(TotalCharges), 2) AS AvgRevenuePerCustomer,
    ROUND(SUM(MonthlyCharges), 2) AS CurrentMRR,
    ROUND(AVG(MonthlyCharges), 2) AS AvgMonthlyCharge,
    ROUND(SUM(TotalCharges) * 100.0 / (SELECT SUM(TotalCharges) FROM customers), 2) AS RevenueSharePct
FROM customers
GROUP BY CustomerSegment
ORDER BY TotalRevenue DESC;

-- B5. Monthly revenue trends (by signup month)
-- This shows revenue acquisition over time, not billing cycle revenue.
SELECT 
    SignupMonth,
    COUNT(*) AS NewCustomers,
    ROUND(SUM(MonthlyCharges), 2) AS MRR_Acquired,
    ROUND(AVG(MonthlyCharges), 2) AS AvgMonthlyCharge,
    ROUND(SUM(TotalCharges), 2) AS TotalLifetimeRevenue
FROM customers
GROUP BY SignupMonth
ORDER BY SignupMonth;

-- B6. Revenue contribution by individual customer (Top 20)
-- Pareto analysis: identifying high-revenue customers
SELECT 
    CustomerID,
    CustomerSegment,
    SubscriptionType,
    ContractDuration,
    Tenure,
    MonthlyCharges,
    TotalCharges,
    ROUND(TotalCharges * 100.0 / (SELECT SUM(TotalCharges) FROM customers), 4) AS RevenueContributionPct
FROM customers
ORDER BY TotalCharges DESC
LIMIT 20;

-- B7. Revenue distribution by monthly charge bands
SELECT 
    ChargeBand,
    COUNT(*) AS CustomerCount,
    ROUND(SUM(TotalCharges), 2) AS TotalRevenue,
    ROUND(AVG(TotalCharges), 2) AS AvgRevenue,
    ROUND(SUM(TotalCharges) * 100.0 / (SELECT SUM(TotalCharges) FROM customers), 2) AS RevenueSharePct
FROM customers
GROUP BY ChargeBand
ORDER BY 
    CASE ChargeBand
        WHEN '$0-30' THEN 1
        WHEN '$31-60' THEN 2
        WHEN '$61-100' THEN 3
        WHEN '$101-150' THEN 4
        WHEN '$150+' THEN 5
    END;

-- B8. MRR contribution by contract type (active customers only)
SELECT 
    ContractDuration,
    COUNT(*) AS ActiveCustomers,
    ROUND(SUM(MonthlyCharges), 2) AS MRR,
    ROUND(AVG(MonthlyCharges), 2) AS ARPU,
    ROUND(SUM(MonthlyCharges) * 100.0 / 
        (SELECT SUM(MonthlyCharges) FROM customers WHERE Churn = 'No'), 2) AS MRR_SharePct
FROM customers
WHERE Churn = 'No'
GROUP BY ContractDuration
ORDER BY MRR DESC;

-- B9. Revenue at risk (from customers who eventually churned)
SELECT 
    'Churned' AS Status,
    COUNT(*) AS Customers,
    ROUND(SUM(MonthlyCharges), 2) AS Lost_MRR,
    ROUND(SUM(TotalCharges), 2) AS Total_Revenue_Before_Churn,
    ROUND(AVG(MonthlyCharges), 2) AS Avg_Monthly_Before_Churn
FROM customers
WHERE Churn = 'Yes'

UNION ALL

SELECT 
    'Active' AS Status,
    COUNT(*) AS Customers,
    ROUND(SUM(MonthlyCharges), 2) AS Current_MRR,
    ROUND(SUM(TotalCharges), 2) AS Total_Lifetime_Revenue,
    ROUND(AVG(MonthlyCharges), 2) AS Avg_Monthly_Charge
FROM customers
WHERE Churn = 'No';

-- B10. Annualized Revenue Run Rate (ARR)
-- ARR = MRR × 12
SELECT 
    ROUND(SUM(MonthlyCharges), 2) AS MRR,
    ROUND(SUM(MonthlyCharges) * 12, 2) AS ARR,
    COUNT(*) AS ActiveCustomers,
    ROUND(SUM(MonthlyCharges) / COUNT(*), 2) AS ARPU,
    ROUND(SUM(MonthlyCharges) / COUNT(*) * 12, 2) AS Annualized_ARPU
FROM customers
WHERE Churn = 'No';
