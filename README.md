## 📑 Table of Contents

- [Project Overview](#-project-overview)
- [Features](#-features)
- [Tech Stack](#️-tech-stack)
- [System Architecture](#️-system-architecture)
- [Repository Structure](#-repository-structure)
- [Data Pipeline Flow](#-data-pipeline-flow)
- [Screenshots](#-screenshots)
- [Installation](#-installation)
- [Running the Simulator](#-running-the-simulator)
- [Running Kafka](#-running-kafka)
- [Running dbt](#-running-dbt)
- [Launching Superset](#-launching-superset)
- [Dashboard Preview](#-dashboard-preview)
- [Future Improvements](#-future-improvements)
- [License](#-license)

# 🌍 AtmoSync – Real-Time Micro-Climate Supply Chain Analytics

> A real-time data engineering and analytics platform that monitors perishable commodity shipments using streaming IoT telemetry, transforms raw events into analytics-ready datasets with dbt, and visualizes live operational insights using Apache Superset.

![Python](https://img.shields.io/badge/Python-3.13-blue)
![Kafka](https://img.shields.io/badge/Apache-Kafka-orange)
![DuckDB](https://img.shields.io/badge/DuckDB-Analytics-yellow)
![dbt](https://img.shields.io/badge/dbt-Core-orange)
![Superset](https://img.shields.io/badge/Apache-Superset-green)
![Docker](https://img.shields.io/badge/Docker-Container-blue)
![License](https://img.shields.io/badge/License-MIT-success)

---

## 🚀 Project Overview

AtmoSync simulates a fleet of refrigerated shipping containers transporting temperature-sensitive commodities across India.

The platform continuously streams IoT sensor data, processes the incoming events through an ELT pipeline, enriches the data with market pricing information, and delivers live operational dashboards for monitoring container health, spoilage risk, routing decisions, and historical trends.

This project demonstrates a modern Data Engineering workflow using streaming ingestion, analytical data modeling, and business intelligence visualization.

---

## ✨ Features

- 📡 Real-time IoT telemetry simulator
- ⚡ Apache Kafka streaming pipeline
- 💾 Event persistence into DuckDB
- 🔄 ELT transformations with dbt Core
- 📊 Interactive dashboards using Apache Superset
- 🌡 Container health monitoring
- 📉 Spoilage prediction analytics
- 🚚 Reroute recommendation tracking
- 📍 Live container location visualization

---

# 🛠️ Tech Stack

| Category | Technology |
|-----------|------------|
| Language | Python 3.13 |
| Streaming | Apache Kafka |
| Database | DuckDB |
| Data Transformation | dbt Core |
| Data Modeling | SQL |
| Dashboard | Apache Superset |
| Containerization | Docker |
| Version Control | Git & GitHub |

---

# 🏗️ System Architecture

The following diagram illustrates the complete end-to-end data pipeline used in AtmoSync.

```mermaid
flowchart LR

A[📡 IoT Simulator] -->|Real-Time Telemetry| B[Apache Kafka]

B --> C[Kafka Consumer]

C --> D[(SQLite)]

D --> E[DuckDB]

E --> F[dbt Core]

F --> G[Staging Models]

G --> H[Fact Models]

H --> I[Mart Models]

I --> J[Apache Superset]

J --> K[📊 Interactive Dashboard]
```

---

# 📂 Repository Structure

```text
AtmoSync/
│
├── dbt/
│   └── atmosync/
│       ├── models/
│       │   ├── staging/
│       │   ├── intermediate/
│       │   └── marts/
│       ├── seeds/
│       ├── macros/
│       ├── snapshots/
│       ├── tests/
│       ├── dbt_project.yml
│       └── packages.yml
│
├── docs/
│   ├── README.md
│   ├── screenshots/
│   └── dashboard_export/
│
├── images/
│
├── kafka/
│   ├── kafka_consumer.py
│   ├── kafka_producer.py
│   └── iot_simulator.py
│
├── scripts/
│   └── migrate_sqlite_to_duckdb.py
│
├── storage/
│   ├── kafka_to_sqlite.py
│   ├── atmosync.db
│   └── atmosync.duckdb
│
├── superset/
│
├── .gitignore
├── docker-compose.yml
├── LICENSE
├── README.md
└── requirements.txt
```

---

# 🔄 Data Pipeline Flow

AtmoSync follows a modern ELT (Extract, Load, Transform) architecture to process real-time IoT telemetry from refrigerated shipping containers.

## Step 1 — IoT Data Simulation 📡

A Python-based IoT simulator continuously generates realistic telemetry for multiple shipping containers, including:

- Container ID
- Commodity
- GPS Coordinates
- Temperature
- Humidity
- Vibration
- Spoilage Percentage
- Recommended Market
- Timestamp

Each record represents a live sensor reading generated every few seconds.

---

## Step 2 — Event Streaming ⚡

The simulator publishes every telemetry event to an Apache Kafka topic.

Kafka acts as the event streaming platform, enabling high-throughput, real-time data ingestion while decoupling data producers from downstream consumers.

---

## Step 3 — Event Persistence 💾

A Python Kafka Consumer subscribes to the telemetry topic and continuously stores incoming events into a local SQLite database.

SQLite serves as the project's raw operational data store.

---

## Step 4 — Analytical Storage 🦆

The SQLite database is migrated into DuckDB, providing a high-performance analytical database optimized for OLAP-style queries.

This database becomes the source for all analytical transformations.

---

## Step 5 — Data Transformation 🔄

dbt Core transforms the raw IoT events into analytics-ready models through a layered architecture:

- **Staging Layer** – Cleans and standardizes raw telemetry.
- **Intermediate Layer** – Creates business-focused fact tables.
- **Mart Layer** – Produces reporting-ready datasets for dashboards.

Mock commodity pricing data is also integrated during this stage to enrich business insights.

---

## Step 6 — Business Intelligence 📊

Apache Superset connects directly to the transformed DuckDB models to provide interactive dashboards for monitoring:

- Container Health
- Historical Temperature Trends
- Average Spoilage
- Live Container Locations
- Reroute Alerts
- Commodity Market Insights

The dashboard updates whenever new telemetry is processed through the pipeline.

## Installation

### Prerequisites
Make sure the following are installed on your system before proceeding:

- Python 3.10+
- Apache Kafka 3.7+
- Java 17+ (required for Kafka)
- Docker Desktop
- Git

### Clone the Repository
```bash
git clone https://github.com/Syznx/AtmoSync.git
cd AtmoSync
```

### Install Python Dependencies
```bash
pip install kafka-python
pip install psycopg2-binary
```

### Kafka Setup
1. Download Apache Kafka from https://kafka.apache.org/downloads
2. Extract to `C:\kafka\`
3. Add PATH variable:
```powershell
$env:PATH += ";C:\Program Files\Java\jdk-17\bin"
```

### Docker Setup
Pull and build the custom Superset image:
```bash
docker build -t custom-superset .
```

## Running the Simulator

### Step 1 — Start Zookeeper
Open a terminal and run:
```bash
cd C:\kafka
.\bin\windows\zookeeper-server-start.bat .\config\zookeeper.properties
```

### Step 2 — Start Kafka Broker
Open a new terminal and run:
```bash
cd C:\kafka
.\bin\windows\kafka-server-start.bat .\config\server.properties
```

### Step 3 — Create Kafka Topic
Open a new terminal and run:
```bash
cd C:\kafka
.\bin\windows\kafka-topics.bat --create --topic container-telemetry --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
```

### Step 4 — Run IoT Simulator
```bash
cd kafka
python IoTSimulator.py
```

You will see live output like this:
[2026-07-09T...] A42 | Avocado | Temp: 18.5°C | Humidity: 91.2% | Spoilage: 32.5% | ₹44.88/kg | 🔴 REROUTE
[2026-07-09T...] B17 | Mango | Temp: 13.0°C | Humidity: 87.3% | Spoilage: 0.0% | ₹51.00/kg | 🟢 OK

### Step 5 — Run Kafka to SQLite Consumer
Open a new terminal and run:
```bash
cd storage
python kafka_to_sqlite.py
```

Data will start flowing into `storage/atmosync.db` in real time.

## Running Kafka

AtmoSync uses Apache Kafka as the streaming backbone. The pipeline requires
three components running simultaneously:

| Component | Command | Port |
|---|---|---|
| Zookeeper | zookeeper-server-start.bat | 2181 |
| Kafka Broker | kafka-server-start.bat | 9092 |
| IoT Simulator | python IoTSimulator.py | — |

To verify Kafka is running correctly, list all topics:
```bash
cd C:\kafka
.\bin\windows\kafka-topics.bat --list --bootstrap-server localhost:9092
```

You should see `container-telemetry` in the output.

To monitor live messages flowing through Kafka:
```bash
.\bin\windows\kafka-console-consumer.bat --bootstrap-server localhost:9092 --topic container-telemetry --from-beginning
```
