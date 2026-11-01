-- ============================================================================
-- CUSTOMER ANALYSIS QUERIES
-- ============================================================================
-- Database: SQLite (saas_analytics.db)
-- Table: customers (loaded from cleaned dataset)
-- 
-- This script contains queries for customer segmentation, distribution
-- analysis, and acquisition tracking.
-- ============================================================================

-- A1. Total number of customers
SELECT 
    COUNT(DISTINCT CustomerID) AS TotalCustomers
FROM customers;

-- A2. Active customers (not churned)
SELECT 
    COUNT(DISTINCT CustomerID) AS ActiveCustomers
FROM customers
WHERE Churn = 'No';

-- A3. Churned customers
SELECT 
    COUNT(DISTINCT CustomerID) AS ChurnedCustomers
FROM customers
WHERE Churn = 'Yes';

-- A4. Customer count and percentage by churn status
SELECT 
    Churn,
    COUNT(*) AS CustomerCount,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM customers), 2) AS Percentage
FROM customers
GROUP BY Churn
ORDER BY CustomerCount DESC;

-- A5. Customer segmentation breakdown
SELECT 
    CustomerSegment,
    COUNT(*) AS CustomerCount,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM customers), 2) AS Percentage,
    SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) AS ChurnedCount,
    ROUND(SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS ChurnRate
FROM customers
GROUP BY CustomerSegment
ORDER BY CustomerCount DESC;

-- A6. New customer acquisition by year and quarter
SELECT 
    SignupYear,
    SignupQuarter,
    COUNT(*) AS NewCustomers,
    SUM(CASE WHEN Churn = 'No' THEN 1 ELSE 0 END) AS StillActive,
    ROUND(SUM(CASE WHEN Churn = 'No' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS RetentionRate
FROM customers
GROUP BY SignupYear, SignupQuarter
ORDER BY SignupYear, SignupQuarter;

-- A7. Customer distribution by subscription type
SELECT 
    SubscriptionType,
    COUNT(*) AS CustomerCount,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM customers), 2) AS Percentage,
    SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) AS ChurnedCount,
    ROUND(SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS ChurnRate
FROM customers
GROUP BY SubscriptionType
ORDER BY CustomerCount DESC;

-- A8. Customer distribution by contract duration
SELECT 
    ContractDuration,
    COUNT(*) AS CustomerCount,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM customers), 2) AS Percentage,
    SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) AS ChurnedCount,
    ROUND(SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS ChurnRate
FROM customers
GROUP BY ContractDuration
ORDER BY ChurnRate DESC;

-- A9. Customer distribution by payment method
SELECT 
    PaymentMethod,
    COUNT(*) AS CustomerCount,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM customers), 2) AS Percentage,
    ROUND(AVG(MonthlyCharges), 2) AS AvgMonthlyCharge,
    SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) AS ChurnedCount,
    ROUND(SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS ChurnRate
FROM customers
GROUP BY PaymentMethod
ORDER BY ChurnRate DESC;

-- A10. Customer age distribution analysis
SELECT 
    CASE 
        WHEN Age BETWEEN 18 AND 25 THEN '18-25'
        WHEN Age BETWEEN 26 AND 35 THEN '26-35'
        WHEN Age BETWEEN 36 AND 45 THEN '36-45'
        WHEN Age BETWEEN 46 AND 55 THEN '46-55'
        ELSE '55+'
    END AS AgeGroup,
    COUNT(*) AS CustomerCount,
    ROUND(AVG(MonthlyCharges), 2) AS AvgMonthlyCharge,
    ROUND(AVG(Tenure), 1) AS AvgTenure,
    ROUND(SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS ChurnRate
FROM customers
GROUP BY AgeGroup
ORDER BY AgeGroup;

-- A11. Customer tenure distribution
SELECT 
    TenureGroup,
    COUNT(*) AS CustomerCount,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM customers), 2) AS Percentage,
    ROUND(SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS ChurnRate
FROM customers
GROUP BY TenureGroup
ORDER BY 
    CASE TenureGroup
        WHEN '0-6 months' THEN 1
        WHEN '7-12 months' THEN 2
        WHEN '13-24 months' THEN 3
        WHEN '25-36 months' THEN 4
        ELSE 5
    END;
