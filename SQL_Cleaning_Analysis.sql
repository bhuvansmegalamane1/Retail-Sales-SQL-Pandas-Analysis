-- ===========================================
-- SQL DATA CLEANING & ANALYSIS PROJECT
-- Dataset: Retail Sales (Customers, Products, Orders)
-- ===========================================

-- 1. DATA CLEANING
-- -------------------------------------------

-- Removing Duplicates from Customers (Assuming there's a staging_customers table)
-- We'll use a Common Table Expression (CTE) to find and remove duplicates
WITH cte AS (
    SELECT 
        customer_id, 
        customer_name, 
        ROW_NUMBER() OVER (
            PARTITION BY customer_id, customer_name, location 
            ORDER BY customer_id
        ) as row_num
    FROM customers_raw
)
DELETE FROM customers_raw 
WHERE customer_id IN (SELECT customer_id FROM cte WHERE row_num > 1);

-- Handling Missing Values (Standardizing NULL locations to 'Unknown')
UPDATE customers_raw
SET location = 'Unknown'
WHERE location IS NULL;

-- Standardizing Date Formats (Cleaning inconsistent dates)
-- SQLite doesn't have a single "TO_DATE" like PostgreSQL, so we'll often use SUBSTR or COALESCE logic
-- In realistic scenarios, you'd perform this transformation during the 'loading' phase.

-- Handling Missing Quantities (Filling with a default value like 0 or the Mean)
UPDATE orders_raw
SET quantity = 0
WHERE quantity IS NULL;


-- 2. DATA ANALYSIS (Equivalent to Pandas Analysis)
-- -------------------------------------------

-- Q1: Total Sales by Category
SELECT 
    p.category, 
    SUM(o.quantity * p.price) as total_revenue,
    COUNT(o.order_id) as total_orders
FROM orders_raw o
JOIN products_raw p ON o.product_id = p.product_id
GROUP BY p.category
ORDER BY total_revenue DESC;

-- Q2: Identify Top 5 High-Value Customers
SELECT 
    c.customer_name, 
    c.location, 
    SUM(o.quantity * p.price) as lifetime_value
FROM orders_raw o
INNER JOIN customers_raw c ON o.customer_id = c.customer_id
INNER JOIN products_raw p ON o.product_id = p.product_id
GROUP BY c.customer_id
ORDER BY lifetime_value DESC
LIMIT 5;

-- Q3: Monthly Revenue Trend
-- We need to handle the mixed date formats here carefully using SQLite's date functions
SELECT 
    strftime('%Y-%m', 
        CASE 
            WHEN order_date LIKE '%-%-%' THEN substr(order_date, 1, 10) 
            ELSE order_date 
        END
    ) as month,
    SUM(o.quantity * p.price) as monthly_revenue
FROM orders_raw o
JOIN products_raw p ON o.product_id = p.product_id
GROUP BY month
ORDER BY month ASC;
