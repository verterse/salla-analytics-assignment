{{
    config(
        materialized='table',
        tags=['curated', 'sales']
    )
}}

/*
    SCD Type 2 Customer Dimension

    Tracks historical address changes for each customer to enable
    accurate regional sales analysis over time.

    Natural Key: customer_id
    Surrogate Key: customer_address_id
*/

WITH customer_orders AS (
    SELECT * FROM {{ ref('int_customer_orders') }}
)

, add_date_ranges AS (
    SELECT
        customer_address_id
        , customer_id
        , customer_city
        , customer_state
        , order_purchase_timestamp AS effective_from
        , COALESCE(
            LEAD(order_purchase_timestamp) OVER (
                PARTITION BY customer_id
                ORDER BY order_purchase_timestamp, customer_address_id
            )
            , DATETIME('9999-12-31 00:00:00')
        ) AS effective_to
    FROM
        customer_orders
    WHERE
        is_change_point = TRUE
)

SELECT
    -- primary key
    customer_address_id

    -- natural key
    , customer_id

    -- dimensions
    , customer_city
    , customer_state
    , effective_from
    , effective_to
    , (
        effective_to = DATETIME('9999-12-31 00:00:00')
    ) AS is_current_address

FROM
    add_date_ranges
