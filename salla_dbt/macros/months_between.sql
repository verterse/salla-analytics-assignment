{% macro months_between(end_date, start_date) %}

{#
    Calculate exact month difference between two dates.
    Returns: Integer representing months elapsed (e.g., Jan to Mar = 2)
    Example: months_between('2017-03-01', '2017-01-01') → 2
#}
    (
        CAST(STRFTIME('%Y', {{ end_date }}) AS INTEGER) * 12 + CAST(STRFTIME('%m', {{ end_date }}) AS INTEGER)
        - CAST(STRFTIME('%Y', {{ start_date }}) AS INTEGER) * 12 + CAST(STRFTIME('%m', {{ start_date }}) AS INTEGER)
    )

{% endmacro %}
