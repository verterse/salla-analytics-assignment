WITH source AS (
    SELECT * FROM {{ source('raw', 'customers') }}
)

SELECT
    customer_unique_id AS customer_id
    , customer_id AS customer_order_reference_id
    , TRIM(customer_city) AS customer_city
    , UPPER(TRIM(customer_state)) AS customer_state
FROM
    source
