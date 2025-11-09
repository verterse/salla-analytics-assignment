"""
This script performs the Extract and Load phases of ELT:
- Load raw data from backend DB (mocked by CSV files) into the data warehouse (mocked by SQLite)
- Loads into raw_salla_data.db without transformations
- Creates raw tables: customers, orders, order_items, products
"""

import sqlite3
import pandas as pd
from pathlib import Path

CSV_DIR = Path('problem_statement')
DB_PATH = Path('data_warehouse/raw_salla_data.db')

CSV_FILES = {
    'customers': 'customers.csv',
    'orders': 'orders.csv',
    'order_items': 'order_items.csv',
    'products': 'products.csv'
}

def main():
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    
    for table_name, csv_file in CSV_FILES.items():
        csv_path = CSV_DIR / csv_file
        
        if not csv_path.exists():
            print(f"Warning: {csv_path} not found, skipping {table_name}")
            continue
        
        df = pd.read_csv(csv_path)
        df.to_sql(table_name, conn, if_exists='replace', index=False)
        print(f"Loaded {table_name}: {len(df):,} rows")
    
    conn.close()
    print(f"\nCompleted loading into {DB_PATH}")

if __name__ == '__main__':
    main()
