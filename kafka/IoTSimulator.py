import json
import time
import random
from datetime import datetime
from kafka import KafkaProducer

# ─────────────────────────────────────────────
#  KAFKA CONFIGURATION
# ─────────────────────────────────────────────
KAFKA_BROKER = "localhost:9092"      # change if your broker is on a different host
KAFKA_TOPIC  = "container-telemetry"

producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
)

# ─────────────────────────────────────────────
#  COMMODITY IDEAL CONDITIONS
#  If temp or humidity drifts outside these ranges, spoilage begins
# ─────────────────────────────────────────────
COMMODITIES = {
    "Avocado":      {"ideal_temp": (8,  12), "ideal_humidity": (85, 90), "spoil_above_temp": 15},
    "Tomato":       {"ideal_temp": (12, 15), "ideal_humidity": (85, 90), "spoil_above_temp": 20},
    "Leafy Greens": {"ideal_temp": (0,   4), "ideal_humidity": (90, 95), "spoil_above_temp": 10},
    "Mango":        {"ideal_temp": (13, 13), "ideal_humidity": (85, 90), "spoil_above_temp": 18},
    "Grapes":       {"ideal_temp": (0,   2), "ideal_humidity": (90, 95), "spoil_above_temp": 8},
}

# ─────────────────────────────────────────────
#  ROUTE WAYPOINTS  (Mumbai → Delhi corridor)
#  Each waypoint = a city the container passes through
#  lat/lon are real approximate coordinates
# ─────────────────────────────────────────────
ROUTE_WAYPOINTS = [
    {"city": "Mumbai",      "lat": 19.0760, "lon": 72.8777},
    {"city": "Pune",        "lat": 18.5204, "lon": 73.8567},
    {"city": "Aurangabad",  "lat": 19.8762, "lon": 75.3433},
    {"city": "Nagpur",      "lat": 21.1458, "lon": 79.0882},
    {"city": "Bhopal",      "lat": 23.2599, "lon": 77.4126},
    {"city": "Agra",        "lat": 27.1767, "lon": 78.0081},
    {"city": "Delhi",       "lat": 28.6139, "lon": 77.2090},
]

# ─────────────────────────────────────────────
#  CONTAINER DEFINITIONS
#  Each container has a fixed origin/destination
#  and a commodity it carries.
#  "waypoint_index" tracks where it is on the route.
#  "drift" controls whether this container is
#  malfunctioning (True = temp will rise over time).
# ─────────────────────────────────────────────
CONTAINERS = [
    {
        "container_id":    "A42",
        "commodity":       "Avocado",
        "origin":          "Mumbai",
        "destination":     "Delhi",
        "waypoint_index":  2,          # currently near Aurangabad
        "drift":           True,       # this container is malfunctioning!
        "drift_rate":      0.15,       # temp rises 0.15°C every event
    },
    {
        "container_id":    "B17",
        "commodity":       "Mango",
        "origin":          "Pune",
        "destination":     "Delhi",
        "waypoint_index":  1,          # currently near Pune
        "drift":           False,
        "drift_rate":      0.0,
    },
    {
        "container_id":    "C91",
        "commodity":       "Tomato",
        "origin":          "Mumbai",
        "destination":     "Bhopal",
        "waypoint_index":  3,          # currently near Nagpur
        "drift":           True,
        "drift_rate":      0.10,
    },
    {
        "container_id":    "D55",
        "commodity":       "Leafy Greens",
        "origin":          "Mumbai",
        "destination":     "Agra",
        "waypoint_index":  0,          # just left Mumbai
        "drift":           False,
        "drift_rate":      0.0,
    },
    {
        "container_id":    "E33",
        "commodity":       "Grapes",
        "origin":          "Pune",
        "destination":     "Delhi",
        "waypoint_index":  2,
        "drift":           True,
        "drift_rate":      0.20,       # fastest degrading container
    },
]

# ─────────────────────────────────────────────
#  RUNTIME STATE
#  Tracks current temp/humidity per container
#  so drift accumulates over time realistically
# ─────────────────────────────────────────────
container_state = {}

def initialize_state():
    for c in CONTAINERS:
        cid        = c["container_id"]
        commodity  = COMMODITIES[c["commodity"]]
        ideal_temp = commodity["ideal_temp"]
        ideal_hum  = commodity["ideal_humidity"]
        container_state[cid] = {
            "current_temp":     round(random.uniform(ideal_temp[0], ideal_temp[1]), 2),
            "current_humidity": round(random.uniform(ideal_hum[0],  ideal_hum[1]),  2),
        }

# ─────────────────────────────────────────────
#  GPS SIMULATION
#  Adds small random noise around the waypoint
#  coordinates to mimic a moving vehicle
# ─────────────────────────────────────────────
def simulate_gps(waypoint_index):
    waypoint = ROUTE_WAYPOINTS[waypoint_index]
    lat = waypoint["lat"] + random.uniform(-0.05, 0.05)
    lon = waypoint["lon"] + random.uniform(-0.05, 0.05)
    return round(lat, 6), round(lon, 6), waypoint["city"]

# ─────────────────────────────────────────────
#  SPOILAGE SCORE CALCULATION
#  Simple linear model:
#  every degree above spoil_above_temp = +5% spoilage
#  every % humidity above 95 = +2% spoilage
#  capped at 100%
# ─────────────────────────────────────────────
def calculate_spoilage(commodity_name, temp, humidity):
    commodity       = COMMODITIES[commodity_name]
    spoil_threshold = commodity["spoil_above_temp"]
    spoilage        = 0.0

    if temp > spoil_threshold:
        spoilage += (temp - spoil_threshold) * 5.0   # 5% per degree over threshold

    if humidity > 95:
        spoilage += (humidity - 95) * 2.0             # 2% per % over 95

    return round(min(spoilage, 100.0), 2)

# ─────────────────────────────────────────────
#  REROUTE RECOMMENDATION
#  If spoilage > 30%, flag for reroute to nearest city
# ─────────────────────────────────────────────
def get_reroute_recommendation(spoilage_pct, waypoint_index, destination):
    if spoilage_pct >= 30.0:
        nearest_city = ROUTE_WAYPOINTS[waypoint_index]["city"]
        return {
            "reroute_needed":    True,
            "recommended_market": nearest_city,
            "reason":            f"Spoilage at {spoilage_pct}% — sell at {nearest_city} before further degradation",
        }
    return {
        "reroute_needed":    False,
        "recommended_market": destination,
        "reason":            "Conditions normal — continue to original destination",
    }

# ─────────────────────────────────────────────
#  RECOMMENDED SELLING PRICE CALCULATION
#  recommended_price = base_price × (remaining_quality%) × (1 - min_profit_margin)
# ─────────────────────────────────────────────
BASE_PRICES = {
    "Avocado":      80,    # ₹ per kg
    "Mango":        60,
    "Tomato":       30,
    "Leafy Greens": 40,
    "Grapes":       120,
}
MIN_PROFIT_MARGIN = 0.15   # company wants at least 15% margin

def calculate_recommended_price(commodity_name, spoilage_pct):
    base_price        = BASE_PRICES[commodity_name]
    remaining_quality = (100 - spoilage_pct) / 100
    recommended_price = base_price * remaining_quality * (1 - MIN_PROFIT_MARGIN)
    return round(recommended_price, 2)

# ─────────────────────────────────────────────
#  MAIN EVENT GENERATOR
#  Builds one complete sensor event per container
# ─────────────────────────────────────────────
def generate_event(container):
    cid       = container["container_id"]
    commodity = container["commodity"]
    state     = container_state[cid]

    # drift temperature upward for malfunctioning containers
    if container["drift"]:
        state["current_temp"]     = round(state["current_temp"] + container["drift_rate"], 2)
        state["current_humidity"] = round(min(state["current_humidity"] + 0.05, 99.0), 2)
    else:
        # normal containers fluctuate slightly around ideal
        ideal_temp = COMMODITIES[commodity]["ideal_temp"]
        ideal_hum  = COMMODITIES[commodity]["ideal_humidity"]
        state["current_temp"]     = round(random.uniform(ideal_temp[0], ideal_temp[1]), 2)
        state["current_humidity"] = round(random.uniform(ideal_hum[0],  ideal_hum[1]),  2)

    temp     = state["current_temp"]
    humidity = state["current_humidity"]
    vibration = round(random.uniform(0.1, 2.5), 2)

    lat, lon, current_city = simulate_gps(container["waypoint_index"])
    spoilage_pct            = calculate_spoilage(commodity, temp, humidity)
    reroute                 = get_reroute_recommendation(spoilage_pct, container["waypoint_index"], container["destination"])
    recommended_price       = calculate_recommended_price(commodity, spoilage_pct)

    event = {
        "container_id":         cid,
        "commodity":            commodity,
        "origin":               container["origin"],
        "destination":          container["destination"],
        "current_location":     current_city,
        "latitude":             lat,
        "longitude":            lon,
        "temperature_c":        temp,
        "humidity_pct":         humidity,
        "vibration":            vibration,
        "spoilage_pct":         spoilage_pct,
        "reroute_needed":       reroute["reroute_needed"],
        "recommended_market":   reroute["recommended_market"],
        "reroute_reason":       reroute["reason"],
        "base_price_per_kg":    BASE_PRICES[commodity],
        "recommended_price_kg": recommended_price,
        "timestamp":            datetime.utcnow().isoformat() + "Z",
    }

    return event

# ─────────────────────────────────────────────
#  MAIN LOOP
#  Sends one event per container every 2 seconds
#  Runs forever until you press Ctrl+C
# ─────────────────────────────────────────────
def main():
    print("=" * 60)
    print("  AtmoSync IoT Simulator — Starting")
    print(f"  Kafka Broker : {KAFKA_BROKER}")
    print(f"  Kafka Topic  : {KAFKA_TOPIC}")
    print(f"  Containers   : {[c['container_id'] for c in CONTAINERS]}")
    print("  Press Ctrl+C to stop")
    print("=" * 60)

    initialize_state()
    event_count = 0

    while True:
        for container in CONTAINERS:
            event = generate_event(container)
            producer.send(KAFKA_TOPIC, value=event)
            event_count += 1

            # print a readable summary to terminal
            status = "🔴 REROUTE" if event["reroute_needed"] else "🟢 OK"
            print(
                f"[{event['timestamp']}] "
                f"{event['container_id']} | "
                f"{event['commodity']:<12} | "
                f"Temp: {event['temperature_c']:>5}°C | "
                f"Humidity: {event['humidity_pct']:>5}% | "
                f"Spoilage: {event['spoilage_pct']:>5}% | "
                f"₹{event['recommended_price_kg']}/kg | "
                f"{status}"
            )

        producer.flush()
        print(f"  — batch sent ({event_count} total events) —\n")
        time.sleep(2)   # emit every 2 seconds

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nSimulator stopped.")
        producer.close()
