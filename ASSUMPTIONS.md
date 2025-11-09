# Project Assumptions

Key assumptions made during development. These would be validated with business or technical stakeholders in a real-world scenario.

## Customer Data Model

- `customer_unique_id` is the true customer identifier (natural key), while `customer_id` is an order-level reference key
- Regional sales analysis requires attributing sales to the customer's address **at the time of order**, not their current or most recent address. This calls for an SCD type 2 customer model.
- Surrogate keys are not essential for SCD Type 2 implementation; as we use a modern dbt workflow, we can instead use natural keys combined with date ranges (`effective_from`, `effective_to`)
- Address changes can only be detected through order history (no explicit address change events available in source data)
- City + State combination is sufficient granularity to identify different addresses


## Order Items Data Model

- Within a single order, the same product cannot be sold by multiple sellers. However, across separate orders, the same product may be sold by multiple sellers
- `order_item_id` is just a sequence number within each order (1, 2, 3...), not a globally unique identifier


## Product Data

- Products with `product_category_name = NULL` are legitimate products that should be included in analysis (not data quality issues requiring exclusion)
- These uncategorized products should count toward sales metrics and be labeled as 'unknown' category


## Timestamp and Currency

- All timestamps across all tables are in the same local timezone
- No timezone conversion is needed for time-based aggregations
- All monetary values are in local currency SAR (Saudi Riyal)
- No currency conversion is needed


## Business Logic

- "Sales" refers to completed transactions only (cancelled orders should be excluded)
- Total sales includes both item price and shipping price (not just product revenue alone)
- Freight charges are stored separately from product revenue to enable independent or combined analysis


## Technical Environment

- SQLite is acceptable for this use case despite its cross-schema view limitations
- Dataset size (~112K rows) will remain small enough for full refresh materialization
- Reviewers may not have Docker installed, requiring a Python-only fallback option


## Analytical Definitions

- **"Store":** Refers to `seller_id`
- **"Region":** Refers to customer's address at time of order
- **"Popular Categories":** Measured by total sales (not order count or item count)
- **"Cohort":** Defined by month of first purchase

## About

**Author:** Baheej Anwar  
**Email:** anwar.baheej@gmail.com  
**Date:** November 2025
