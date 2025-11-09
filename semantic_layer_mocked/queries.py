"""
Semantic Layer Query Functions

This module contains all business logic for the 7 analytics tasks.
Tasks 1-4 use SQL (as required), Tasks 5-7 use Python.
"""

import pandas as pd
import numpy as np
from .connection import get_connection


# ============================================================================
# TASK 1: Top Selling Products (General + By Region)
# ============================================================================

def get_top_products_by_region():
    """
    Task: What are the top selling products in general, and by region.
    
    Business Logic:
    - "Top selling" = highest total revenue (item_revenue)
    - Returns product sales grouped by product_id AND customer_state
    - Streamlit dashboard handles filtering and aggregation for "overall" view
    - Region = customer_state from dim_customers (using SCD Type 2 join)
    
    Returns:
        pd.DataFrame: Product sales by region with columns:
            - product_id
            - customer_state
            - total_revenue
            - total_quantity
            - num_orders
    """
    conn = get_connection()
    
    query = """
    SELECT
        F.product_id
        , C.customer_state
        , SUM(F.total_item_price + F.total_shipping_price) AS total_revenue
        , SUM(F.quantity) AS total_quantity
        , COUNT(DISTINCT F.order_id) AS num_orders
    
    FROM
        fct_order_items AS F
    
    INNER JOIN
        dim_customers AS C
        ON F.customer_id = C.customer_id
        AND F.order_purchase_timestamp >= C.effective_from
        AND F.order_purchase_timestamp < C.effective_to
    
    GROUP BY
        F.product_id
        , C.customer_state
    
    ORDER BY
        total_revenue DESC
    """
    
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    return df


# ============================================================================
# TASK 2: Most Popular Categories
# ============================================================================

def get_popular_categories(top_n=10):
    """
    Task: What are the most popular categories?
    
    Business Logic:
    - "Popular" = combination of revenue and order count
    - Joins fact table with product dimension to get category
    
    Args:
        top_n (int): Number of top categories to return
    
    Returns:
        pd.DataFrame: Popular categories with columns:
            - product_category_name
            - total_revenue
            - total_quantity
            - num_orders
            - num_unique_products
    """
    conn = get_connection()
    
    query = f"""
    SELECT
        P.product_category_name
        , SUM(F.total_item_price + F.total_shipping_price) AS total_revenue
        , SUM(F.quantity) AS total_quantity
        , COUNT(DISTINCT F.order_id) AS num_orders
        , COUNT(DISTINCT F.product_id) AS num_unique_products
    
    FROM
        fct_order_items AS F
    
    INNER JOIN
        dim_products AS P
        ON F.product_id = P.product_id
    
    GROUP BY
        P.product_category_name
    
    ORDER BY
        total_revenue DESC
        , num_orders DESC
    
    LIMIT {top_n}
    """
    
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    return df


# ============================================================================
# TASK 3: Time Series Sales (Monthly, Quarterly, Yearly)
# ============================================================================

def get_time_series_sales():
    """
    Task: Calculate monthly, quarterly and yearly sales. (All products combined).
    
    Business Logic:
    - Uses order_purchase_timestamp for time grouping
    - Returns monthly grain with year/quarter columns for aggregation in Streamlit
    - Calculates total revenue (item_revenue) across all products
    
    Returns:
        pd.DataFrame: Monthly sales data with columns:
            - year_month (YYYY-MM)
            - year (YYYY)
            - quarter (Q1, Q2, Q3, Q4)
            - year_quarter (YYYY-Q1, etc.)
            - total_revenue
            - total_quantity
            - num_orders
    """
    conn = get_connection()
    
    query = """
    SELECT
        STRFTIME('%Y-%m', order_purchase_timestamp) AS year_month
        , STRFTIME('%Y', order_purchase_timestamp) AS year
        , 'Q' || CAST((CAST(STRFTIME('%m', order_purchase_timestamp) AS INTEGER) + 2) / 3 AS TEXT) AS quarter
        , STRFTIME('%Y', order_purchase_timestamp) || '-Q' || 
          CAST((CAST(STRFTIME('%m', order_purchase_timestamp) AS INTEGER) + 2) / 3 AS TEXT) AS year_quarter
        , SUM(total_item_price + total_shipping_price) AS total_revenue
        , SUM(quantity) AS total_quantity
        , COUNT(DISTINCT order_id) AS num_orders
    
    FROM
        fct_order_items
    
    GROUP BY
        STRFTIME('%Y-%m', order_purchase_timestamp)
    
    ORDER BY
        year_month
    """
    
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    return df


# ============================================================================
# TASK 4a: Average Sale by Product Category
# ============================================================================

def get_avg_sale_by_category():
    """
    Task (Part 1): What is the average sale by product category?
    
    Business Logic:
    - Calculates average item_revenue per category across all sales
    - Groups by product_category_name only (overall average, not by location)
    
    Returns:
        pd.DataFrame: Average sale by category with columns:
            - product_category_name
            - avg_sale (average item_revenue)
            - total_revenue
            - total_quantity
            - num_orders
    """
    conn = get_connection()
    
    query = """
    SELECT
        P.product_category_name
        , AVG(F.total_item_price + F.total_shipping_price) AS avg_sale
        , SUM(F.total_item_price + F.total_shipping_price) AS total_revenue
        , SUM(F.quantity) AS total_quantity
        , COUNT(DISTINCT F.order_id) AS num_orders
    
    FROM
        fct_order_items AS F
    
    INNER JOIN
        dim_products AS P
        ON F.product_id = P.product_id
    
    GROUP BY
        P.product_category_name
    
    ORDER BY
        avg_sale DESC
    """
    
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    return df


# ============================================================================
# TASK 4b: Top Product Categories by Customer Location
# ============================================================================

def get_top_categories_by_location(top_n=10):
    """
    Task (Part 2): What are the top product category based on customer location?
    
    Business Logic:
    - Identifies top revenue-driving categories for each customer_state
    - Uses window function to rank categories within each location
    - Joins fact with product dimension (category) and customer dimension (location)
    
    Args:
        top_n (int): Number of top categories per location
    
    Returns:
        pd.DataFrame: Top categories by location with columns:
            - customer_state
            - product_category_name
            - total_revenue
            - total_quantity
            - num_orders
            - rank_in_state (1 = top category for that state)
    """
    conn = get_connection()
    
    query = f"""
    WITH category_by_state AS (
        SELECT
            C.customer_state
            , P.product_category_name
            , SUM(F.total_item_price + F.total_shipping_price) AS total_revenue
            , SUM(F.quantity) AS total_quantity
            , COUNT(DISTINCT F.order_id) AS num_orders
        
        FROM
            fct_order_items AS F
        
        INNER JOIN
            dim_products AS P
            ON F.product_id = P.product_id
        
        INNER JOIN
            dim_customers AS C
            ON F.customer_id = C.customer_id
            AND F.order_purchase_timestamp >= C.effective_from
            AND F.order_purchase_timestamp < C.effective_to
        
        GROUP BY
            C.customer_state
            , P.product_category_name
    )
    
    , ranked AS (
        SELECT
            customer_state
            , product_category_name
            , total_revenue
            , total_quantity
            , num_orders
            , ROW_NUMBER() OVER (
                PARTITION BY customer_state 
                ORDER BY total_revenue DESC
            ) AS rank_in_state
        
        FROM
            category_by_state
    )
    
    SELECT
        customer_state
        , product_category_name
        , total_revenue
        , total_quantity
        , num_orders
        , rank_in_state
    
    FROM
        ranked
    
    WHERE
        rank_in_state <= {top_n}
    
    ORDER BY
        customer_state
        , rank_in_state
    """
    
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    return df


# ============================================================================
# TASK 5: Top 10 Stores by Average Daily Sales (PYTHON)
# ============================================================================

def get_top_stores_by_daily_sales(top_n=10):
    """
    Task: Calculate the top 10 stores with the highest average daily sales.
    
    Business Logic (Python):
    - Store = seller_id
    - Calculate total revenue per seller per day
    - Average across all days the store had sales
    - Return top N stores
    
    Args:
        top_n (int): Number of top stores to return
    
    Returns:
        pd.DataFrame: Top stores with columns:
            - seller_id
            - avg_daily_sales
            - total_revenue
            - days_active
            - total_orders
    """
    conn = get_connection()
    
    # Load fact data
    df = pd.read_sql_query("""
        SELECT
            seller_id,
            DATE(order_purchase_timestamp) as order_date,
            total_item_price + total_shipping_price as total_revenue,
            order_id
        FROM fct_order_items
    """, conn)
    conn.close()
    
    # Calculate daily sales per store
    daily_sales = df.groupby(['seller_id', 'order_date']).agg({
        'total_revenue': 'sum',
        'order_id': 'nunique'
    }).reset_index()
    
    daily_sales.columns = ['seller_id', 'order_date', 'daily_revenue', 'daily_orders']
    
    # Calculate average daily sales per store
    store_metrics = daily_sales.groupby('seller_id').agg({
        'daily_revenue': ['mean', 'sum'],
        'order_date': 'count',
        'daily_orders': 'sum'
    }).reset_index()
    
    store_metrics.columns = ['seller_id', 'avg_daily_sales', 'total_revenue', 'days_active', 'total_orders']
    
    # Get top N stores
    top_stores = store_metrics.nlargest(top_n, 'avg_daily_sales')
    
    return top_stores


# ============================================================================
# TASK 6: Monthly Growth Rate by Store (PYTHON)
# ============================================================================

def get_monthly_growth_by_store():
    """
    Task: Calculate the percentage of monthly growth in sales for each store.
    
    Business Logic (Python):
    - Store = seller_id
    - Group sales by seller_id and month
    - Calculate month-over-month growth percentage
    - Growth % = ((current_month - prev_month) / prev_month) * 100
    
    Returns:
        pd.DataFrame: Monthly growth by store with columns:
            - seller_id
            - month (YYYY-MM)
            - monthly_revenue
            - prev_month_revenue
            - growth_pct
    """
    conn = get_connection()
    
    # Load fact data
    df = pd.read_sql_query("""
        SELECT
            seller_id,
            STRFTIME('%Y-%m', order_purchase_timestamp) as month,
            total_item_price + total_shipping_price as total_revenue
        FROM fct_order_items
    """, conn)
    conn.close()
    
    # Calculate monthly revenue per store
    monthly_sales = df.groupby(['seller_id', 'month']).agg({
        'total_revenue': 'sum'
    }).reset_index()
    
    monthly_sales.columns = ['seller_id', 'month', 'monthly_revenue']
    
    # Sort by seller and month
    monthly_sales = monthly_sales.sort_values(['seller_id', 'month'])
    
    # Calculate previous month's revenue
    monthly_sales['prev_month_revenue'] = monthly_sales.groupby('seller_id')['monthly_revenue'].shift(1)
    
    # Calculate growth percentage
    monthly_sales['growth_pct'] = (
        (monthly_sales['monthly_revenue'] - monthly_sales['prev_month_revenue']) / 
        monthly_sales['prev_month_revenue'] * 100
    )
    
    # Remove first month for each store (no growth to calculate)
    monthly_sales = monthly_sales[monthly_sales['prev_month_revenue'].notna()]
    
    return monthly_sales


# ============================================================================
# TASK 7: Cohort Analysis (PYTHON)
# ============================================================================

def get_cohort_analysis():
    """
    Task: Conduct cohort analysis on customers' orders. Analyze the cohorts based on 
    the month in which the customer made their first purchase and analyze their behavior 
    over time.
    
    Business Logic (Python):
    - Cohort = month of customer's first purchase (cohort_month)
    - Track revenue behavior over subsequent months (cohort_age)
    - Returns data suitable for heatmap visualization
    
    Returns:
        pd.DataFrame: Cohort data with columns:
            - cohort_month (YYYY-MM of first purchase)
            - cohort_age (months since first purchase: 0, 1, 2, ...)
            - num_customers (unique customers active in that cohort age)
            - num_orders
            - total_revenue
            - avg_revenue_per_customer
    """
    conn = get_connection()
    
    # Load fact data with customer and order info
    df = pd.read_sql_query("""
        SELECT
            customer_id,
            order_id,
            order_purchase_timestamp,
            total_item_price + total_shipping_price as total_revenue
        FROM fct_order_items
    """, conn)
    conn.close()
    
    # Convert timestamp to datetime
    df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])
    df['order_month'] = df['order_purchase_timestamp'].dt.to_period('M')
    
    # Identify first purchase month for each customer (cohort)
    customer_cohorts = df.groupby('customer_id')['order_month'].min().reset_index()
    customer_cohorts.columns = ['customer_id', 'cohort_month']
    
    # Merge cohort back to orders
    df = df.merge(customer_cohorts, on='customer_id', how='left')
    
    # Calculate cohort age (months since first purchase)
    df['cohort_age'] = (df['order_month'] - df['cohort_month']).apply(lambda x: x.n)
    
    # Aggregate by cohort and cohort age
    cohort_data = df.groupby(['cohort_month', 'cohort_age']).agg({
        'customer_id': 'nunique',
        'order_id': 'nunique',
        'total_revenue': 'sum'
    }).reset_index()
    
    cohort_data.columns = ['cohort_month', 'cohort_age', 'num_customers', 'num_orders', 'total_revenue']
    
    # Calculate average revenue per customer
    cohort_data['avg_revenue_per_customer'] = (
        cohort_data['total_revenue'] / cohort_data['num_customers']
    )
    
    # Convert period back to string for easier handling
    cohort_data['cohort_month'] = cohort_data['cohort_month'].astype(str)
    
    return cohort_data

