import duckdb
import requests
from pathlib import Path

WEBHOOK_URL = "PASTE YOUR SLACK EMAIL WEEBHOOK URL HERE"

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "storage" / "atmosync.duckdb"

conn = duckdb.connect(DB)

rows = conn.execute("""
SELECT
    container_id,
    commodity,
    temperature_c,
    spoilage_pct,
    arbitrage_score,
    reroute_priority,
    recommended_market
FROM mart_current_container_status
WHERE reroute_priority = 'High Priority'
ORDER BY arbitrage_score DESC;
""").fetchall()

conn.close()

if not rows:
    print("No high priority containers.")
    exit()

message = "🚨 *AtmoSync Arbitrage Alert* 🚨\n\n"

for row in rows:

    message += (
        f"*Container:* {row[0]}\n"
        f"Commodity: {row[1]}\n"
        f"Temperature: {row[2]}°C\n"
        f"Spoilage: {row[3]}%\n"
        f"Arbitrage Score: {row[4]}\n"
        f"Recommended Market: {row[6]}\n"
        "-----------------------------\n"
    )

requests.post(
    WEBHOOK_URL,
    json={"text": message}
)

print("Slack alert sent.")
