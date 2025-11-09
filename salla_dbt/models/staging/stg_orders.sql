WITH source AS (
    SELECT * FROM {{ source('raw', 'orders') }}
)

SELECT
    order_id
    , customer_id AS customer_order_reference_id
    , LOWER(order_status) AS order_status
    , {{ parse_timestamp('order_purchase_timestamp') }} AS order_purchase_timestamp
    , {{ parse_timestamp('order_approved_at') }} AS order_approved_at
    , {{ parse_timestamp('order_delivered_carrier_date') }} AS order_delivered_carrier_date
    , {{ parse_timestamp('order_delivered_customer_date') }} AS order_delivered_customer_date
    , {{ parse_timestamp('order_estimated_delivery_date') }} AS order_estimated_delivery_date
FROM
    source
