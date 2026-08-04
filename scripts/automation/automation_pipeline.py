import subprocess
from pathlib import Path

# ---------------------------------------------------
# AtmoSync Automation Pipeline
# ---------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

MIGRATION_SCRIPT = BASE_DIR / "scripts" / "migrate_sqlite_to_duckdb.py"
DBT_DIR = BASE_DIR / "dbt" / "atmosync"

print("=" * 60)
print("AtmoSync Automation Pipeline")
print("=" * 60)


def run_step(name, command, cwd=None):
    print(f"\n{name}")
    print("-" * 60)

    result = subprocess.run(
        command,
        cwd=cwd,
        text=True
    )

    if result.returncode != 0:
        print(f"\n❌ {name} FAILED")
        exit(result.returncode)

    print(f"✅ {name} COMPLETED")


# -----------------------------------------
# Step 1
# SQLite → DuckDB Migration
# -----------------------------------------

run_step(
    "SQLite → DuckDB Migration",
    ["python", str(MIGRATION_SCRIPT)]
)

# -----------------------------------------
# Step 2
# dbt Run
# -----------------------------------------

run_step(
    "dbt Models",
    ["dbt", "run"],
    cwd=DBT_DIR
)

print("\n" + "=" * 60)
print("🎉 PIPELINE COMPLETED SUCCESSFULLY")
print("=" * 60)
