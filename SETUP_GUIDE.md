# Setup Guide - Salla Analytics Pipeline

## Complete Setup Instructions

### Step 1: Environment Setup

```bash
# Create and activate virtual environment (if not already done)
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Load Raw Data

```bash
# Load raw CSV data into SQLite
python scripts/load_raw_data.py
```

### Step 3: Run dbt Transformations

```bash
# Navigate to dbt project
cd salla_dbt

# Build all models and run tests
dbt build

# Return to project root
cd ..
```

## Pipeline 1: Python-Only Stack (Lightweight Fallback Option)

Launch Streamlit Dashboard

```bash
# Run from project root
streamlit run dashboard.py
```

Access:
- **Streamlit Dashboard:** http://localhost:8501

## Key Files

- `scripts/load_raw_data.py` - Data ingestion
- `salla_dbt/models/` - All dbt models
- `semantic_layer_mocked/queries.py` - 7 business query functions
- `dashboard.py` - Interactive dashboard
- `ASSUMPTIONS.md` - Project assumptions documentation

## Pipeline 2: Docker-Based Stack (Recommended Option)

For the fully-fledged semantic layer experience:

```bash
# Run from project root (where docker-compose.yml is located)

# Pull Docker images (Cube Core and Metabase)
docker-compose pull

# Start containers in detached mode
docker-compose up -d
```

Access:
- **Cube Core Playground:** http://localhost:4000
- **Metabase:** http://localhost:3000

### Metabase First-Time Setup

When accessing Metabase for the first time, you'll need to:

1. **Create Account:** Provide email and password to create your Metabase account
2. **Connect to Database:** Configure connection to Cube Core SQL API with the following credentials:
   - **Database Type:** `PostgreSQL`
   - **Host:** `cube`
   - **Port:** `15432`
   - **Database Name:** `db`
   - **Username:** `admin`
   - **Password:** _Leave blank_

Once connected, you can create dashboards and queries using the semantic layer exposed by Cube Core.

## Troubleshooting

### Issue: dbt commands fail with mashumaro-related errors
**Solution:** Python 3.13+ is not compatible with dbt-core due to the `mashumaro` package dependency. Downgrade to Python 3.12 or lower and recreate your virtual environment.

### Issue: Module not found errors
**Solution:** Ensure virtual environment is activated and dependencies are installed

### Issue: Database not found
**Solution:** Run `python scripts/load_raw_data.py` first

### Issue: dbt models not found
**Solution:** Run `cd salla_dbt` and `dbt build` before launching semantic layer or dashboards

### Issue: Streamlit won't start
**Solution:** 
- Check if port 8501 is available
- Try: `streamlit run dashboard.py --server.port 8502`

## Additional Resources

- **dbt Documentation:** Run `cd salla_dbt && dbt docs generate && dbt docs serve` to view lineage and model documentation at http://localhost:8080
- **README.md:** Project overview and pipeline comparison
- **ASSUMPTIONS.md:** Key assumptions and design decisions
