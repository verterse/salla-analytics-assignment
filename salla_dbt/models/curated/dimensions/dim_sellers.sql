{{
    config(
        materialized='table',
        tags=['curated', 'sales']
    )
}}

/*
    Dimension Table: Sellers (Stores)

    Grain: One row per unique seller/store

    Purpose:
    - Mocks store/seller attributes for analysis
    - Enables store-level filtering and grouping

    Notes:
    - Currently only contains seller_id as we don't have additional seller attributes in source data
    - In production, would include: store_name, store_location, store_type, registration_date, etc.
*/

WITH order_items AS (
    SELECT * FROM {{ ref('int_order_items') }}
)

, unique_sellers AS (
    SELECT DISTINCT seller_id FROM order_items
)

SELECT
    seller_id
    , seller_id AS seller_name -- Placeholder: would be actual name if present
FROM
    unique_sellers
