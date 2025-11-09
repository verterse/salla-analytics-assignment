{% macro parse_timestamp(column_name) %}

{#
    Parse timestamp stringinto SQLite datetime (YYYY-MM-DD HH:MM:00).
    Example: '9/4/2016 21:15' -> '2016-09-04 21:15:00'
#}

    (
        CASE 
            WHEN {{ column_name }} IS NULL THEN NULL
            ELSE datetime(
                printf(
                    '%04d-%02d-%02d %02d:%02d:00',
                    substr({{ column_name }},
                        instr({{ column_name }}, '/') +
                        instr(substr({{ column_name }}, instr({{ column_name }}, '/') + 1), '/') + 1,
                        4),
                    substr({{ column_name }}, 1, instr({{ column_name }}, '/') - 1),
                    substr({{ column_name }},
                        instr({{ column_name }}, '/') + 1,
                        instr(substr({{ column_name }}, instr({{ column_name }}, '/') + 1), '/') - 1),
                    substr({{ column_name }},
                        instr({{ column_name }}, ' ') + 1,
                        instr(substr({{ column_name }}, instr({{ column_name }}, ' ') + 1), ':') - 1),
                    substr({{ column_name }}, instr({{ column_name }}, ':') + 1)
                )
            )
        END
    )

{% endmacro %}

