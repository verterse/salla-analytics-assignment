/*
    Test: Order Items Price Calculation
    
    Validates that unit_item_price * quantity = total_item_price
    Allows for small floating point rounding differences (< 0.01)
*/

SELECT
    order_item_id
    , (unit_item_price * quantity) AS calculated_total_item_price
    , ABS(total_item_price - (unit_item_price * quantity)) AS price_difference

FROM
    {{ ref('int_order_items') }}

WHERE
    ABS(total_item_price - (unit_item_price * quantity)) > 0.01
