{{
    config(
        materialized='table',
        tags=['curated', 'sales']
    )
}}

WITH products AS (
    SELECT * FROM {{ ref('stg_products') }}
)

SELECT
    product_id
    , product_id AS product_name -- Placeholder: would be actual name if present
    , product_category_name
    , product_photos_qty
FROM
    products
