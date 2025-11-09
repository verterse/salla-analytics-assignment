"""
Database connection helper for the semantic layer
"""
import sqlite3
from pathlib import Path

def get_connection():
    """
    Get a connection to the curated database.
    
    Returns:
        sqlite3.Connection: Database connection object
    """
    db_path = Path(__file__).parent.parent / 'data_warehouse' / 'main_curated.db'
    return sqlite3.connect(str(db_path))

