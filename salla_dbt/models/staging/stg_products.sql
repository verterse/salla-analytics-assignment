WITH source AS (
    SELECT * FROM {{ source('raw', 'products') }}
)

SELECT
    product_id
    , COALESCE(LOWER(product_category_name), 'unknown') AS product_category_name
    , CAST(product_photos_qty AS INTEGER) AS product_photos_qty
    , CAST(product_weight_g AS REAL) AS product_weight_g
    , CAST(product_length_cm AS REAL) AS product_length_cm
    , CAST(product_height_cm AS REAL) AS product_height_cm
    , CAST(product_width_cm AS REAL) AS product_width_cm
FROM
    source
