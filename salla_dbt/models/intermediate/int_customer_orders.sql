{{
    config(
        materialized='table',
        tags=['intermediate', 'sales']
    )
}}

/*
    Intermediate: Customer Orders
    
    Reusable base join between customers and orders.
    This table is used by both dim_customers and fct_orders to avoid
    duplicating the join operation.
    
    Grain: One row per order
*/

SELECT
    O.order_id
    , O.customer_order_reference_id
    , C.customer_id
    , C.customer_city
    , C.customer_state
    , O.order_status
    , O.order_purchase_timestamp
    , O.order_approved_at
    , O.order_delivered_carrier_date
    , O.order_delivered_customer_date
    , O.order_estimated_delivery_date
FROM
    {{ ref('stg_orders') }} AS O
INNER JOIN
    {{ ref('stg_customers') }} AS C ON (
        O.customer_order_reference_id = C.customer_order_reference_id
    )
