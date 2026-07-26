# Week 1 — Ingestion Architecture & BI Foundations

**Project:** AtmoSync — Micro-Climate Arbitrage Analytics  
**Intern:** Syznx  
**Organization:** Infotact Solutions  
**Duration:** Week 1 of 4  
**Status:** ✅ Complete

---

## Overview

Week 1 focused on building the complete data ingestion backbone of the 
AtmoSync pipeline. The objective was to simulate real-world IoT sensor 
behavior from shipping containers, stream that data through Apache Kafka, 
persist it into a database, and deploy a live Business Intelligence 
dashboard using Apache Superset.

By the end of Week 1, a fully functional end-to-end data pipeline was 
operational — from data generation to real-time visualization.

---

## Pipeline Architecture

IoT Simulator (Python)
↓
Apache Kafka (container-telemetry topic)
↓
Kafka Consumer Script (Python)
↓
SQLite Database (atmosync.db)
↓
Apache Superset (Docker)
↓
AtmoSync Dashboard (Container Health Monitor)

---

## What Was Built

### 1. Python IoT Simulator (`kafka/IoTSimulator.py`)

A custom Python script was developed to simulate real-time telemetry data 
from 5 shipping containers carrying agricultural commodities across the 
Mumbai to Delhi corridor.

**Containers Simulated:**

| Container ID | Commodity    | Route              | Status   |
|--------------|--------------|--------------------|----------|
| A42          | Avocado      | Mumbai → Delhi     | 🔴 At Risk |
| B17          | Mango        | Pune → Delhi       | 🟢 Healthy |
| C91          | Tomato       | Mumbai → Bhopal    | 🔴 At Risk |
| D55          | Leafy Greens | Mumbai → Agra      | 🟢 Healthy |
| E33          | Grapes       | Pune → Delhi       | 🔴 At Risk |

**Each sensor event includes:**
- Container ID and commodity type
- Origin, destination, and current GPS location
- Real-time latitude and longitude coordinates
- Temperature (°C), humidity (%), and vibration readings
- Calculated spoilage percentage based on threshold breach
- Reroute recommendation (True/False)
- Recommended nearest market for rerouting
- Dynamic selling price calculated to preserve minimum profit margin
- UTC timestamp

**Key Features:**
- Emits one event per container every 2 seconds
- Containers A42, C91, and E33 simulate refrigeration failure through 
  gradual temperature drift
- Containers B17 and D55 remain within healthy ranges throughout
- Spoilage percentage increases dynamically as temperature drifts above 
  commodity-specific thresholds
- Recommended selling price decreases proportionally as spoilage increases
- All events are serialized as JSON and published to Kafka

---

### 2. Apache Kafka Streaming Pipeline

Apache Kafka was configured as the high-throughput event streaming layer 
between the IoT simulator and the storage layer.

**Configuration:**
- Kafka version: 3.9.2
- Zookeeper port: 2181
- Kafka broker port: 9092
- Topic name: `container-telemetry`
- Partitions: 1
- Replication factor: 1

**What Kafka does in this pipeline:**
Kafka acts as a fault-tolerant buffer between the simulator and the 
consumer. Even if the consumer is temporarily unavailable, Kafka retains 
all messages and delivers them reliably when the consumer reconnects. This 
mimics production-grade IoT streaming architectures used in real supply 
chain systems.

**Verified throughput:**
- 5 events per batch
- 1 batch every 2 seconds
- 2000+ total events streamed during Week 1 testing

---

### 3. Kafka Consumer & Storage Layer (`storage/kafka_to_sqlite.py`)

A Python Kafka consumer script was developed to read events from the 
`container-telemetry` topic and persist them into a local SQLite database 
in real time.

**Database:** `storage/atmosync.db`  
**Table:** `iot_events`

**Schema:**

| Column | Type | Description |
|---|---|---|
| container_id | TEXT | Unique container identifier |
| commodity | TEXT | Agricultural commodity being transported |
| origin | TEXT | Shipment origin city |
| destination | TEXT | Intended destination city |
| current_location | TEXT | Current waypoint city |
| latitude | REAL | GPS latitude coordinate |
| longitude | REAL | GPS longitude coordinate |
| temperature_c | REAL | Container internal temperature in Celsius |
| humidity_pct | REAL | Container internal humidity percentage |
| vibration | REAL | Vibration reading in m/s² |
| spoilage_pct | REAL | Calculated spoilage percentage |
| reroute_needed | INTEGER | 1 if reroute recommended, 0 if not |
| recommended_market | TEXT | Nearest market for rerouting |
| reroute_reason | TEXT | Explanation for reroute decision |
| base_price_per_kg | REAL | Original commodity price per kg in ₹ |
| recommended_price_kg | REAL | Adjusted selling price per kg in ₹ |
| timestamp | TEXT | UTC event timestamp |

**Spoilage Calculation Logic:**

If temperature > commodity threshold:
spoilage += (temperature - threshold) × 5% per degree

If humidity > 95%:
spoilage += (humidity - 95) × 2% per unit

Spoilage is capped at 100%

**Dynamic Pricing Formula:**

recommended_price = base_price × (remaining_quality%) × (1 - min_profit_margin)

Where:

remaining_quality = (100 - spoilage_pct) / 100
min_profit_margin = 15%

---

### 4. Apache Superset Dashboard

Apache Superset was deployed using Docker and connected to the SQLite 
database to provide real-time business intelligence visualization.

**Deployment:**
- Docker image: custom-superset (built from apache/superset base)
- Port: 8088
- Database connection: SQLite via URI

**Dashboard: AtmoSync — Container Health Monitor**

Three charts were built and assembled into the final dashboard:

**Chart 1 — Average Spoilage by Container (Bar Chart)**  
Displays the average spoilage percentage for each container. Containers 
with refrigeration failure (A42, C91, E33) show significantly higher bars 
compared to healthy containers (B17, D55).

**Chart 2 — Container Health Status (Table)**  
A live data table showing the most recent sensor readings for all 5 
containers including temperature, humidity, spoilage percentage, reroute 
status, recommended market, and adjusted selling price.

**Chart 3 — Reroute Alerts (Table)**  
Filtered view showing only containers where reroute_needed = 1. Displays 
the container ID, commodity, current location, spoilage percentage, 
recommended reroute market, recommended selling price, and the reason for 
rerouting. This is the core business intelligence output of AtmoSync.

---

## Commodity Threshold Reference

| Commodity | Ideal Temp (°C) | Ideal Humidity (%) | Spoils Above |
|---|---|---|---|
| Avocado | 8–12 | 85–90 | 15°C |
| Mango | 13 | 85–90 | 18°C |
| Tomato | 12–15 | 85–90 | 20°C |
| Leafy Greens | 0–4 | 90–95 | 10°C |
| Grapes | 0–2 | 90–95 | 8°C |

---

## Simulated Route Waypoints

Mumbai → Pune → Aurangabad → Nagpur → Bhopal → Agra → Delhi

Each waypoint represents a potential reroute market. When spoilage 
exceeds 30%, the system recommends selling at the nearest upcoming 
waypoint rather than continuing to the original destination.

---

## Tools & Technologies Used

| Tool | Version | Purpose |
|---|---|---|
| Python | 3.14 | IoT simulator and Kafka consumer |
| Apache Kafka | 3.9.2 | Real-time event streaming |
| Apache ZooKeeper | 2.7.10 | Kafka cluster coordination |
| SQLite | Built-in | Lightweight local data storage |
| Apache Superset | Latest | Business intelligence dashboard |
| Docker | 29.6.1 | Superset containerization |
| kafka-python | 2.0.2 | Python Kafka client library |

---

## Key Outcomes

- ✅ Real-time IoT simulation generating 5 container streams simultaneously
- ✅ Apache Kafka ingesting 2000+ events without message loss
- ✅ SQLite database capturing and persisting all sensor readings
- ✅ Apache Superset deployed and connected to live data
- ✅ Three operational dashboard charts built
- ✅ Spoilage detection logic working correctly
- ✅ Dynamic reroute recommendations functioning
- ✅ Adjusted selling price calculations verified

---

## Challenges & Solutions

| Challenge | Solution |
|---|---|
| Snowflake required credit card | Switched to SQLite for local storage |
| BigQuery sandbox blocked streaming inserts | Used CSV batch approach then moved to SQLite |
| Docker networking blocked PostgreSQL connection | Used SQLite inside Docker container directly |
| Superset SECRET_KEY error | Passed key as environment variable in docker run command |
| psycopg2 installed in wrong Python environment | Rebuilt custom Docker image with correct pip path |

**But finally used SQLite for primary DB and DuckDB for futher processing over the data coming from SQLite data layer**

