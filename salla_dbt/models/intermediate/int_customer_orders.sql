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

    Address change detection logic for dim_customer SCD Type 2 model in curated layer:
    - Uses LAG to detect when address changes
    - Concatenates city + state for comparison (handles A -> B -> A scenarios)
    - Only creates new row when address actually changes
*/

WITH orders AS (
    SELECT * FROM {{ ref('stg_orders') }}
)

, customers AS (
    SELECT * FROM {{ ref('stg_customers') }}
)

, orders_customers_joined AS (
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
        , COALESCE(C.customer_city, '') || '|' || COALESCE(C.customer_state, '') AS customer_full_address
    FROM
        {{ ref('stg_orders') }} AS O
    INNER JOIN
        {{ ref('stg_customers') }} AS C ON (
            O.customer_order_reference_id = C.customer_order_reference_id
        )
)

, previous_addresses AS (
	SELECT
		*
		, customer_full_address != COALESCE(
            LAG(customer_full_address) OVER (
                PARTITION BY customer_id
                ORDER BY order_purchase_timestamp, order_id -- include order_id to make the result set deterministic
            )
            , 'dummy_value'
        ) AS is_change_point
    FROM
        orders_customers_joined
)

, add_surrogate_key AS (
	SELECT
		*
        -- cumulative sum of change points to generate customer_address_id surrogate key
		, SUM(is_change_point) OVER (
            ORDER BY customer_id, order_purchase_timestamp, order_id
        ) AS customer_address_id
	FROM
        previous_addresses
)

SELECT * FROM add_surrogate_key
