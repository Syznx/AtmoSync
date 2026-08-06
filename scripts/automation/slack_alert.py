import requests
import duckdb
from config import SLACK_WEBHOOK_URL


def send_slack_alert(message):
    payload = {"text": message}

    response = requests.post(
        SLACK_WEBHOOK_URL,
        json=payload
    )

    if response.status_code == 200:
        print("✅ Slack alert sent successfully!")
    else:
        print(response.text)


def check_high_priority_containers():

    conn = duckdb.connect("storage/atmosync.duckdb")

    rows = conn.execute("""
        SELECT
            container_id,
            commodity,
            temperature_c,
            spoilage_pct,
            arbitrage_score,
            recommended_market
        FROM mart_current_container_status
        WHERE reroute_priority = 'High Priority'
        ORDER BY arbitrage_score DESC;
    """).fetchall()

    conn.close()

    if not rows:
        print("No High Priority containers found.")
        return

    message = "🚨 *AtmoSync Arbitrage Alert* 🚨\n\n"

    for row in rows:

        message += (
            f"📦 Container : {row[0]}\n"
            f"🥬 Commodity : {row[1]}\n"
            f"🌡 Temperature : {row[2]} °C\n"
            f"⚠ Spoilage : {row[3]}%\n"
            f"📈 Arbitrage Score : {row[4]}\n"
            f"📍 Recommended Market : {row[5]}\n\n"
        )

    send_slack_alert(message)
