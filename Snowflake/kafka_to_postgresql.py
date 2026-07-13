import json
from datetime import datetime
from kafka import KafkaConsumer
import psycopg2

# ── PostgreSQL config ─────────────────────────
DB_CONFIG = {
    "host":     "localhost",
    "database": "atmosync",
    "user":     "postgres",
    "password": "Hallo@wiuefwn+9523.036894",
    "port":     "5432"
}

# ── Kafka config ──────────────────────────────
KAFKA_BROKER = "localhost:9092"
KAFKA_TOPIC  = "container-telemetry"

# ── Connect to PostgreSQL ─────────────────────
conn   = psycopg2.connect(**DB_CONFIG)
cursor = conn.cursor()
print("✅ Connected to PostgreSQL")

# ── Connect to Kafka ──────────────────────────
consumer = KafkaConsumer(
    KAFKA_TOPIC,
    bootstrap_servers=KAFKA_BROKER,
    value_deserializer=lambda m: json.loads(m.decode("utf-8")),
    auto_offset_reset="latest",
)
print("✅ Connected to Kafka — listening...")

# ── Insert SQL ────────────────────────────────
INSERT_SQL = """
INSERT INTO iot_events (
    container_id, commodity, origin, destination,
    current_location, latitude, longitude,
    temperature_c, humidity_pct, vibration,
    spoilage_pct, reroute_needed, recommended_market,
    reroute_reason, base_price_per_kg, recommended_price_kg,
    timestamp
) VALUES (
    %s, %s, %s, %s, %s, %s, %s,
    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
)
"""

# ── Main loop ─────────────────────────────────
row_count = 0
for message in consumer:
    event = message.value

    # fix timestamp
    ts = datetime.fromisoformat(
        event["timestamp"].replace("Z", "+00:00")
    )

    cursor.execute(INSERT_SQL, (
        event["container_id"],
        event["commodity"],
        event["origin"],
        event["destination"],
        event["current_location"],
        event["latitude"],
        event["longitude"],
        event["temperature_c"],
        event["humidity_pct"],
        event["vibration"],
        event["spoilage_pct"],
        event["reroute_needed"],
        event["recommended_market"],
        event["reroute_reason"],
        event["base_price_per_kg"],
        event["recommended_price_kg"],
        ts
    ))
    conn.commit()
    row_count += 1

    print(
        f"[{row_count}] {event['container_id']} | "
        f"{event['commodity']} | "
        f"Spoilage: {event['spoilage_pct']}% | "
        f"Reroute: {event['reroute_needed']}"
    )