{{
    config(
        materialized='table',
        tags=['intermediate', 'sales']
    )
}}

/*
    Intermediate: Order Items
    
    Aggregates order items to product level within each order with computed quantity column.
    Raw data has one row per unit (e.g., 5 units = 5 rows), this 
    aggregates to one row per product per order.
    
    Grain: One row per order + product combination
*/

SELECT
    order_id
    , product_id
    , seller_id
    , COUNT(*) AS quantity
    , MIN(order_item_id) AS order_item_id
    , MIN(shipping_limit_date) AS shipping_limit_date
    , MIN(item_price) AS unit_item_price
    , SUM(item_price) AS total_item_price
    , SUM(shipping_price) AS total_shipping_price
FROM
    {{ ref('stg_order_items') }} AS OI
GROUP BY
    1, 2, 3
