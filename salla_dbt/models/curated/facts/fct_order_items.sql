{{
    config(
        materialized='table',
        tags=['curated', 'sales']
    )
}}

/*
    Fact Table: Order Item Sales

    Grain: One row per order + product + seller combination (item-level)

    Purpose:
    - Single source of truth for all sales analytics
    - Atomic grain allows aggregation to any level (order, product, category, store, time)

    Business Rules:
    - Excludes cancelled orders (assumption: all 7 use cases provided focus on completed sales)
    - Makes a distinction between shipping price and product revenue if needed for separate analysis

    Materialization:
    - Full refresh (table) instead of incremental due to:
      1. Small dataset (~110K rows, rebuilds in <1 second)
      2. SQLite limitations (no native MERGE, uses delete+insert)
      3. Guarantees correctness of late arriving facts without complex incremental logic
*/

WITH customer_orders AS (
    SELECT * FROM {{ ref('int_customer_orders') }}
)

, order_items AS (
    SELECT * FROM {{ ref('int_order_items') }}
)

, joined AS (
    SELECT
        -- Identifiers
        OI.order_item_id
        , OI.order_id
        , OI.product_id
        , OI.seller_id
        , CO.customer_id

        -- Order attributes
        , CO.order_status
        , CO.order_purchase_timestamp
        , CO.order_delivered_carrier_date
        , CO.order_delivered_customer_date
        , CO.order_estimated_delivery_date

        -- Item metrics
        , OI.quantity
        , OI.unit_item_price
        , OI.total_item_price
        , OI.total_shipping_price
    FROM
        customer_orders AS CO
    INNER JOIN
        order_items AS OI ON (
            CO.order_id = OI.order_id
        )
    WHERE
        -- Exclude cancelled orders
        LOWER(CO.order_status) != 'canceled'
)
SELECT * FROM joined
