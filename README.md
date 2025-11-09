# Salla Analytics Engineering Assignment

## Architecture Overview

Modern analytics engineering pipeline using medallion architecture (Raw → Staging → Intermediate → Curated) with dbt transformations and a semantic layer.

### Technology Stack
- **Data Warehouse:** SQLite
- **Transformation Layer:** dbt Core
- **Semantic Layer:** Cube Core (Docker) + Python mock layer
- **Visualization:** Streamlit Dashboard + Metabase
- **Architecture:** Medallion pattern with dimensional modeling

### Data Flow

```
CSV Files → Python Loader → Raw Layer (SQLite)
    ↓
dbt Staging (cleaned, typecasted)
    ↓
dbt Intermediate (joins, base transformations)
    ↓
dbt Curated (fact, dimension tables)
    ↓
Semantic Layer (Mock python script, Cube Core)
    ↓
Dashboards (Streamlit, Metabase)
```

## Prerequisites

**Python Version:** 3.9, 3.10, 3.11, or 3.12

> **Important:** Python 3.13+ is not yet compatible with dbt-core due to the `mashumaro` package dependency. This is a known issue across the dbt ecosystem. dbt commands like `dbt run` or `dbt build` can fail if Python is 3.13 or above

**Other Requirements:**
- Docker & Docker Compose (optional - required only for Pipeline 2)
- SQLite (included with Python)

## Two Analytics Pipelines Available

This project provides two complete analytics workflows to minimize evaluation friction. **Pipeline 2 (Docker) is the recommended approach** as it demonstrates a fully-fledged semantic layer with BI capabilities. However, Pipeline 1 (Python-only) is provided as a fallback for reviewers without Docker installed, ensuring the project can be evaluated regardless of local setup constraints.

### Pipeline 1: Python-Only Stack (Fallback Option - No Docker Required)
**Components:**
- Mock semantic layer (Python-based query functions)
- Streamlit dashboard for visualization

**Use Case:** Fallback option for environments without Docker. All analytics run through Python scripts directly querying SQLite databases.

**To Run:**
```bash
python scripts/load_raw_data.py
cd salla_dbt && dbt build && cd ..
streamlit run dashboard.py
```

### Pipeline 2: Fully-Fledged Stack (Recommended - Docker Required)
**Components:**
- Cube Core semantic layer (metrics engine with SQL API)
- Metabase BI tool (drag-and-drop analytics interface)

**Use Case:** **Recommended evaluation path.** Demonstrates full semantic layer capabilities with proper metric definitions, pre-aggregations, and BI tooling.

**To Run:**
```bash
python scripts/load_raw_data.py
cd salla_dbt && dbt build && cd ..
docker-compose up -d
```

Both pipelines consume the same dbt-transformed data from the curated layer (`main_curated.db`).

**Access Points:**
- Pipeline 1: Streamlit Dashboard → http://localhost:8501
- Pipeline 2: 
  - Cube Core Playground → http://localhost:4000
  - Metabase → http://localhost:3000 (first-time setup requires email/password signup and database connection to Cube Core SQL API - see [SETUP_GUIDE.md](SETUP_GUIDE.md) for connection details)

## Project Structure

```
salla-analytics-assignment/
├── scripts/
│   └── load_raw_data.py              # Load CSVs to SQLite
│
├── salla_dbt/                        # dbt repository
│   ├── models/
│   │   ├── sources.yml               # Raw data sources
│   │   ├── staging/                  # Silver layer
│   │   │   ├── stg_customers.sql
│   │   │   ├── stg_orders.sql
│   │   │   ├── stg_order_items.sql
│   │   │   └── stg_products.sql
│   │   ├── intermediate/             # Joins and transformations
│   │   │   ├── int_customer_orders.sql
│   │   │   └── int_order_items.sql
│   │   └── curated/                  # Gold layer
│   │       ├── facts/
│   │       │   └── fct_order_items.sql
│   │       └── dimensions/
│   │           ├── dim_customers.sql
│   │           ├── dim_products.sql
│   │           └── dim_sellers.sql
│   ├── macros/
│   │   ├── parse_timestamp.sql       # Parse timestamp from string
│   │   └── months_between.sql        # Month difference calculator
│   └── tests/
│       └── assert_order_items_price_calculation.sql
│
├── semantic_layer_cube/              # Cube Core semantic layer
│   └── model/
│       ├── cubes/                    # Metric definitions
│       └── views/                    # Expose measures and dimensions downstream
│
├── semantic_layer_mocked/            # Semantic layer mocked in Python
│   ├── connection.py
│   └── queries.py
│
├── dashboard.py                      # Streamlit dashboard
│
├── data_warehouse/                   # SQLite databases
│   ├── raw_salla_data.db             # Raw layer
│   ├── main_staging.db               # Staging layer
│   ├── main_intermediate.db          # Intermediate layer
│   └── main_curated.db               # Curated (gold) layer
│
├── problem_statement/                # Assignment materials
│   ├── use_case.txt
│   ├── Tables_Description.csv
│   └── *.csv                         # Source data
│
├── docker-compose.yml                # Required for Cube Core and Metabase
├── requirements.txt
├── ASSUMPTIONS.md
├── SETUP_GUIDE.md
└── README.md
```

## Assignment Tasks

### SQL Analysis (Tasks 1-4)
1. Top selling products by region
2. Most popular categories
3. Monthly, quarterly, and yearly sales
4. Average sales by category and top product categories by customer location

### Python Analysis (Tasks 5-7)
5. Top 10 stores by average daily sales
6. Monthly growth percentage by store
7. Customer cohort analysis with retention heatmap

All tasks implemented in both the mock semantic layer and Streamlit dashboard.

## Key Design Decisions

**Dimensional Modeling**
- Star schema with fact table at order item grain
- SCD Type 2 for customer dimension (tracks address changes)
- Conformed dimensions for products and sellers

**Distribution of Complexity**
- dbt layer: Prepares and cleans final dimension and fact tables only (no joins between them)
- Semantic layer: Handles joins between facts and dimensions, defines metrics, and manages business logic
- Complexity intentionally split: dbt handles ELT and data structure, semantic layer manages relationships and analytics logic
- Approach maximizes flexibility, follows best practices and aids performance by leveraging each layer's strengths

**Semantic Layer**
- Cube Core for metric definitions, pre-aggregations, and SQL API
- Python mock layer for direct SQLite queries
- Centralized business logic

See [ASSUMPTIONS.md](ASSUMPTIONS.md) for design assumptions and [SETUP_GUIDE.md](SETUP_GUIDE.md) for deployment instructions.

## Data Quality

The `dbt build` command runs both transformations and tests. To run tests independently:
```bash
cd salla_dbt
dbt test
```

Generate dbt documentation:
```bash
dbt docs generate
dbt docs serve  # Access at http://localhost:8080
```

## Limitations

- **Staging Layer Materialization:** Ideally, staging models should be materialized as views for better maintainability and to avoid data duplication. However, in this project, staging models are materialized as tables. This is an SQLite limitation as dbt-sqlite implements schemas as separate `.db` files, and SQLite views cannot reference objects across different database files. See [dbt-sqlite docs](https://docs.getdbt.com/docs/core/connect-data-platform/sqlite-setup) for details.

- **Pre-aggregations in Cube Core:** Pre-aggregation support in Cube Core is limited in a local SQLite setup and has been commented out in the cube definitions.

## About

**Author:** Baheej Anwar  
**Email:** anwar.baheej@gmail.com  
**Date:** November 2025
