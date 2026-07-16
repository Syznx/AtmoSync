import json
import sqlite3
from datetime import datetime
from kafka import KafkaConsumer

# ── SQLite config ─────────────────────────────
DB_PATH = r"C:\Users\yatin\OneDrive\Desktop\atmoSync\bigquery\atmosync.db"

# ── Kafka config ──────────────────────────────
KAFKA_BROKER = "localhost:9092"
KAFKA_TOPIC  = "container-telemetry"

# ── Connect to SQLite ─────────────────────────
conn   = sqlite3.connect(DB_PATH, check_same_thread=False)
cursor = conn.cursor()

# ── Create table if not exists ────────────────
cursor.execute("""
CREATE TABLE IF NOT EXISTS iot_events (
    container_id          TEXT,
    commodity             TEXT,
    origin                TEXT,
    destination           TEXT,
    current_location      TEXT,
    latitude              REAL,
    longitude             REAL,
    temperature_c         REAL,
    humidity_pct          REAL,
    vibration             REAL,
    spoilage_pct          REAL,
    reroute_needed        INTEGER,
    recommended_market    TEXT,
    reroute_reason        TEXT,
    base_price_per_kg     REAL,
    recommended_price_kg  REAL,
    timestamp             TEXT
)
""")
conn.commit()
print("✅ Connected to SQLite database")

# ── Connect to Kafka ──────────────────────────
consumer = KafkaConsumer(
    KAFKA_TOPIC,
    bootstrap_servers=KAFKA_BROKER,
    value_deserializer=lambda m: json.loads(m.decode("utf-8")),
    auto_offset_reset="latest",
)
print("✅ Connected to Kafka — saving to SQLite...")

# ── Main loop ─────────────────────────────────
row_count = 0
for message in consumer:
    event = message.value

    cursor.execute("""
        INSERT INTO iot_events VALUES (
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
        )
    """, (
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
        1 if event["reroute_needed"] else 0,
        event["recommended_market"],
        event["reroute_reason"],
        event["base_price_per_kg"],
        event["recommended_price_kg"],
        event["timestamp"],
    ))
    conn.commit()
    row_count += 1

    print(
        f"[{row_count}] {event['container_id']} | "
        f"{event['commodity']} | "
        f"Spoilage: {event['spoilage_pct']}% | "
        f"Reroute: {event['reroute_needed']}"
    )