WITH source AS (
    SELECT * FROM {{ source('raw', 'order_items') }}
)

SELECT
    order_id || '_' || CAST(order_item_id AS TEXT) AS order_item_id
    , order_id
    , CAST(order_item_id AS INTEGER) AS order_item_sequence
    , product_id
    , seller_id
    , {{ parse_timestamp('shipping_limit_date') }} AS shipping_limit_date
    , CAST(price AS REAL) AS item_price
    , CAST(freight_value AS REAL) AS shipping_price
FROM
    source
