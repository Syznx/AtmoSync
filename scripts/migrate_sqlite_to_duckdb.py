import sqlite3
import duckdb
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

sqlite_db = BASE_DIR / "storage" / "atmosync.db"
duckdb_db = BASE_DIR / "storage" / "atmosync.duckdb"

print("=" * 60)
print("AtmoSync SQLite → DuckDB Migration")
print("=" * 60)

print(f"SQLite : {sqlite_db}")
print(f"DuckDB : {duckdb_db}")

# Connect
sqlite_conn = sqlite3.connect(sqlite_db)
duck_conn = duckdb.connect(str(duckdb_db))

# Read SQLite
df = pd.read_sql_query("SELECT * FROM iot_events", sqlite_conn)

print(f"\nLoaded {len(df)} rows from SQLite.")

# Create raw schema
duck_conn.execute("CREATE SCHEMA IF NOT EXISTS raw")

# Register dataframe
duck_conn.register("temp_df", df)

# Create table
duck_conn.execute("""
CREATE OR REPLACE TABLE raw.iot_events AS
SELECT *
FROM temp_df
""")

rows = duck_conn.execute(
    "SELECT COUNT(*) FROM raw.iot_events"
).fetchone()[0]

print(f"Copied {rows} rows into raw.iot_events")

sqlite_conn.close()
duck_conn.close()

print("\nMigration completed successfully!")