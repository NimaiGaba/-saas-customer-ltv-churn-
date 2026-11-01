-- ============================================================================
-- CUSTOMER LIFETIME VALUE (LTV) ANALYSIS QUERIES
-- ============================================================================
-- Database: SQLite (saas_analytics.db)
-- Table: customers (loaded from cleaned dataset)
--
-- IMPORTANT METHODOLOGY NOTE:
-- LTV in this project is calculated as HISTORICAL lifetime value, which is
-- the actual total revenue received from a customer over their entire tenure.
-- 
-- Formula: Historical LTV = TotalCharges (sum of all payments made)
-- Alternative: Historical LTV ≈ Tenure × MonthlyCharges
--
-- This is NOT a predictive LTV model. We are NOT forecasting future revenue.
-- We are analyzing actual revenue patterns to identify high-value segments.
-- ============================================================================

-- D1. Historical customer revenue summary
SELECT 
    COUNT(*) AS TotalCustomers,
    ROUND(SUM(TotalCharges), 2) AS TotalLifetimeRevenue,
    ROUND(AVG(TotalCharges), 2) AS AvgLTV,
    ROUND(MIN(TotalCharges), 2) AS MinLTV,
    ROUND(MAX(TotalCharges), 2) AS MaxLTV,
    ROUND(AVG(MonthlyCharges), 2) AS AvgMonthlyCharge,
    ROUND(AVG(Tenure), 1) AS AvgTenureMonths
FROM customers;

-- D2. Average customer lifetime (tenure) by churn status
-- Active customers: tenure is still growing (right-censored)
-- Churned customers: tenure represents complete lifetime
SELECT 
    Churn,
    COUNT(*) AS CustomerCount,
    ROUND(AVG(Tenure), 1) AS AvgTenureMonths,
    ROUND(MIN(Tenure), 1) AS MinTenure,
    ROUND(MAX(Tenure), 1) AS MaxTenure,
    ROUND(AVG(TotalCharges), 2) AS AvgLTV
FROM customers
GROUP BY Churn;

-- D3. Average LTV by subscription type
SELECT 
    SubscriptionType,
    COUNT(*) AS CustomerCount,
    ROUND(AVG(TotalCharges), 2) AS AvgLTV,
    ROUND(AVG(Tenure), 1) AS AvgTenureMonths,
    ROUND(AVG(MonthlyCharges), 2) AS AvgMonthlyCharge,
    ROUND(SUM(TotalCharges), 2) AS TotalRevenue,
    -- LTV = AvgMonthlyCharge × AvgTenure (cross-check)
    ROUND(AVG(MonthlyCharges) * AVG(Tenure), 2) AS LTV_CrossCheck
FROM customers
GROUP BY SubscriptionType
ORDER BY AvgLTV DESC;

-- D4. LTV by customer segment
SELECT 
    CustomerSegment,
    COUNT(*) AS CustomerCount,
    ROUND(AVG(TotalCharges), 2) AS AvgLTV,
    ROUND(AVG(Tenure), 1) AS AvgTenureMonths,
    ROUND(AVG(MonthlyCharges), 2) AS AvgMonthlyCharge,
    ROUND(SUM(TotalCharges), 2) AS TotalRevenue,
    ROUND(SUM(TotalCharges) * 100.0 / (SELECT SUM(TotalCharges) FROM customers), 2) AS RevenueSharePct
FROM customers
GROUP BY CustomerSegment
ORDER BY AvgLTV DESC;

-- D5. High-value customer identification (Top 50 by LTV)
SELECT 
    CustomerID,
    CustomerSegment,
    SubscriptionType,
    ContractDuration,
    Tenure,
    MonthlyCharges,
    TotalCharges AS CustomerLTV,
    Churn,
    ROUND(TotalCharges * 100.0 / (SELECT SUM(TotalCharges) FROM customers), 4) AS RevenueContributionPct
FROM customers
ORDER BY TotalCharges DESC
LIMIT 50;

-- D6. LTV distribution by contract duration
SELECT 
    ContractDuration,
    COUNT(*) AS CustomerCount,
    ROUND(AVG(TotalCharges), 2) AS AvgLTV,
    ROUND(AVG(Tenure), 1) AS AvgTenureMonths,
    ROUND(AVG(MonthlyCharges), 2) AS AvgMonthlyCharge,
    ROUND(SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS ChurnRatePct
FROM customers
GROUP BY ContractDuration
ORDER BY AvgLTV DESC;

-- D7. LTV by subscription + segment combination
SELECT 
    SubscriptionType,
    CustomerSegment,
    COUNT(*) AS CustomerCount,
    ROUND(AVG(TotalCharges), 2) AS AvgLTV,
    ROUND(AVG(Tenure), 1) AS AvgTenureMonths,
    ROUND(AVG(MonthlyCharges), 2) AS AvgMonthlyCharge,
    ROUND(SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS ChurnRatePct
FROM customers
GROUP BY SubscriptionType, CustomerSegment
ORDER BY AvgLTV DESC;

-- D8. LTV quartile analysis
-- Groups customers into LTV quartiles to identify segments
SELECT 
    CASE 
        WHEN TotalCharges <= q1 THEN 'Q1 (Bottom 25%)'
        WHEN TotalCharges <= q2 THEN 'Q2 (25-50%)'
        WHEN TotalCharges <= q3 THEN 'Q3 (50-75%)'
        ELSE 'Q4 (Top 25%)'
    END AS LTV_Quartile,
    COUNT(*) AS CustomerCount,
    ROUND(AVG(TotalCharges), 2) AS AvgLTV,
    ROUND(AVG(Tenure), 1) AS AvgTenure,
    ROUND(AVG(MonthlyCharges), 2) AS AvgMonthlyCharge,
    ROUND(SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS ChurnRate
FROM customers,
    (SELECT 
        -- SQLite doesn't have PERCENTILE_CONT, so use subquery approximation
        (SELECT TotalCharges FROM customers ORDER BY TotalCharges LIMIT 1 
            OFFSET (SELECT COUNT(*) * 25 / 100 FROM customers)) AS q1,
        (SELECT TotalCharges FROM customers ORDER BY TotalCharges LIMIT 1 
            OFFSET (SELECT COUNT(*) * 50 / 100 FROM customers)) AS q2,
        (SELECT TotalCharges FROM customers ORDER BY TotalCharges LIMIT 1 
            OFFSET (SELECT COUNT(*) * 75 / 100 FROM customers)) AS q3
    ) percentiles
GROUP BY LTV_Quartile
ORDER BY 
    CASE LTV_Quartile
        WHEN 'Q1 (Bottom 25%)' THEN 1
        WHEN 'Q2 (25-50%)' THEN 2
        WHEN 'Q3 (50-75%)' THEN 3
        WHEN 'Q4 (Top 25%)' THEN 4
    END;

-- D9. Revenue concentration (Pareto analysis)
-- What percentage of customers generate 80% of revenue?
WITH ranked AS (
    SELECT 
        CustomerID,
        TotalCharges,
        SUM(TotalCharges) OVER (ORDER BY TotalCharges DESC) AS CumulativeRevenue,
        (SELECT SUM(TotalCharges) FROM customers) AS TotalRevenue,
        ROW_NUMBER() OVER (ORDER BY TotalCharges DESC) AS RowNum,
        (SELECT COUNT(*) FROM customers) AS TotalCustomers
    FROM customers
)
SELECT 
    ROUND(RowNum * 100.0 / TotalCustomers, 1) AS TopPctCustomers,
    ROUND(CumulativeRevenue * 100.0 / TotalRevenue, 1) AS CumulativeRevenuePct
FROM ranked
WHERE RowNum IN (
    SELECT CAST(COUNT(*) * pct / 100 AS INTEGER) 
    FROM customers, (SELECT 10 AS pct UNION SELECT 20 UNION SELECT 30 UNION SELECT 50 UNION SELECT 80) p
)
ORDER BY RowNum;

-- D10. LTV comparison: churned vs active customers
SELECT 
    Churn AS CustomerStatus,
    COUNT(*) AS CustomerCount,
    ROUND(AVG(TotalCharges), 2) AS AvgLTV,
    ROUND(SUM(TotalCharges), 2) AS TotalRevenue,
    ROUND(AVG(Tenure), 1) AS AvgTenure,
    ROUND(AVG(MonthlyCharges), 2) AS AvgMonthlyCharge,
    ROUND(AVG(SupportTickets), 1) AS AvgSupportTickets
FROM customers
GROUP BY Churn;
