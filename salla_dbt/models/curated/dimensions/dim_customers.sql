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
    Surrogate Key: customer_surrogate_id (generated for this dimension)

    Change Detection Logic:
    - Uses LAG to detect when address changes
    - Concatenates city+state for comparison (handles A -> B -> A scenarios)
    - Only creates new row when address actually changes
*/

WITH customer_orders AS (
    SELECT
        customer_id
        , order_purchase_timestamp
        , customer_city
        , customer_state

    FROM
        {{ ref('int_customer_orders') }}

    WHERE
        order_purchase_timestamp IS NOT NULL
)

, address_comparison AS (
    SELECT
        customer_id
        , customer_city
        , customer_state
        , order_purchase_timestamp
        , LAG(COALESCE(customer_city, '') || '|' || COALESCE(customer_state, '')) OVER (
            PARTITION BY customer_id 
            ORDER BY order_purchase_timestamp
        ) AS prev_address
        , COALESCE(customer_city, '') || '|' || COALESCE(customer_state, '') AS current_address

    FROM
        customer_orders
)

, address_change_points AS (
    SELECT
        customer_id
        , customer_city
        , customer_state
        , order_purchase_timestamp AS effective_from
    FROM
        address_comparison
    WHERE
        current_address != prev_address 
        OR prev_address IS NULL
)

, address_periods AS (
    SELECT
        customer_id
        , customer_city
        , customer_state
        , effective_from
        , LEAD(effective_from) OVER (
            PARTITION BY customer_id 
            ORDER BY effective_from
        ) AS effective_to
    FROM
        address_change_points
)

SELECT
    -- primary key
    ROW_NUMBER() OVER (
        ORDER BY customer_id, effective_from
    ) AS customer_address_id

    -- natural key
    , customer_id

    -- dimensions
    , customer_city
    , customer_state
    , effective_from
    , COALESCE(effective_to, '9999-12-31 00:00:00') AS effective_to
    , (
        CASE 
            WHEN effective_to IS NULL THEN TRUE 
            ELSE FALSE 
        END
    ) AS is_current_address
FROM
    address_periods
