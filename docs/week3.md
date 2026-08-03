# 🚀 Week 3 – Advanced Analytics & Arbitrage Dashboard

## Overview

Week 3 focused on transforming raw logistics data into actionable business intelligence.

After building the real-time ingestion pipeline (Week 1) and the ELT pipeline using dbt (Week 2), this phase introduced advanced analytics by calculating a custom **Spoilage Arbitrage** metric and developing an operational dashboard that assists logistics teams in making intelligent rerouting decisions.

The objective was to determine which containers require immediate operational attention based on spoilage risk, transportation distance, environmental conditions, and potential financial recovery.

---

# Objectives

- Build advanced dbt analytical models.
- Calculate a custom **Spoilage Arbitrage Score**.
- Combine operational and financial data into a unified analytical model.
- Identify high-risk containers.
- Recommend rerouting priorities.
- Visualize insights through an Apache Superset dashboard.

---

# Architecture

```
Python IoT Simulator
        │
        ▼
Apache Kafka
        │
        ▼
Kafka Consumer
        │
        ▼
SQLite (Raw Events)
        │
        ▼
DuckDB Analytics Warehouse
        │
        ▼
dbt Transformations
        │
        ▼
Apache Superset Dashboard
```

---

# Week 3 Workflow

## Step 1 — Commodity Pricing Seed

A dbt seed table containing simulated commodity prices for multiple destination markets was created.

Purpose:

- Estimate remaining cargo value.
- Calculate recoverable value after spoilage.
- Support financial analytics.

Example fields:

- commodity
- market
- price_per_kg

---

## Step 2 — Market Distance Seed

Another seed table was created containing distances between logistics hubs and recommended destination markets.

Purpose:

- Measure transportation effort.
- Include routing distance in arbitrage calculations.

Example fields:

- current_location
- recommended_market
- distance_km

---

## Step 3 — dbt Seeds

Both CSV files were loaded into DuckDB using:

```bash
dbt seed
```

Result:

- commodity_prices
- market_distances

became permanent analytical tables inside DuckDB.

---

# Advanced Analytics Model

## mart_spoilage_arbitrage.sql

The central analytical model for Week 3.

This model joins:

- IoT container telemetry
- Commodity prices
- Market distances

to calculate operational and financial metrics.

### Input Sources

- fct_container_events
- commodity_prices
- market_distances

---

# Metrics Calculated

## Remaining Shelf Life

```
Remaining Shelf Life = 100 − Spoilage %
```

Represents the usable life remaining in the shipment.

---

## Recoverable Value

```
Recoverable Value =
Commodity Price × Remaining Shelf Life
```

This estimates the remaining financial value of a shipment after spoilage.

---

## Temperature Risk

Containers are categorized into risk levels based on live temperature.

| Temperature | Risk |
|-------------|------|
| Low | Safe |
| Medium | Moderate |
| High | Critical |

---

## Distance Risk

Distance to the recommended destination market is classified into:

- Low
- Medium
- High

Longer routes increase operational risk.

---

## Spoilage Risk

Spoilage percentage is classified into four categories:

- Low
- Medium
- High
- Critical

---

## Spoilage Arbitrage Score

A custom weighted metric combining:

- Spoilage %
- Transportation Distance
- Temperature

Formula:

```
Arbitrage Score =
(Spoilage × 0.5)
+
(Distance × 0.3)
+
(Temperature × 0.2)
```

Higher scores indicate containers requiring urgent operational attention.

---

## Reroute Priority

Based on the Arbitrage Score, each shipment receives an operational recommendation.

Possible values:

- Continue Route
- Monitor
- High Priority
- Immediate Reroute

This enables logistics teams to prioritize interventions.

---

# Current Container Snapshot

## mart_current_container_status.sql

A second analytical model was developed to retain only the latest telemetry record for each shipping container.

Instead of analysing thousands of historical sensor readings, the dashboard displays the most recent operational status for every active container.

Current snapshot contains:

- Container ID
- Latest timestamp
- Commodity
- Temperature
- Spoilage %
- Arbitrage Score
- Recoverable Value
- Recommended Market
- Reroute Priority

---

# Apache Superset Dashboard

The final dashboard was developed in Apache Superset using the `mart_current_container_status` analytical model.

The dashboard provides a real-time operational overview of all active shipping containers and enables business users to identify high-risk shipments requiring immediate action.

---

## Dashboard Visualizations

### 1. At-Risk Containers

**Chart Type:** Table

**Dataset Used:**
`mart_current_container_status`

**Columns Displayed**

- Container ID
- Commodity
- Current Location
- Recommended Market
- Spoilage %
- Arbitrage Score
- Recoverable Value
- Reroute Priority

**Purpose**

Provides a live operational snapshot of every active container and highlights shipments requiring immediate intervention.

---

### 2. Arbitrage Score by Container

**Chart Type:** Horizontal Bar Chart

**Dataset Used:**
`mart_current_container_status`

**X-Axis**

- Arbitrage Score

**Y-Axis**

- Container ID

**Purpose**

Ranks containers according to overall operational risk, allowing logistics teams to prioritize rerouting decisions.

---

### 3. Reroute Priority Distribution

**Chart Type:** Vertical Bar Chart

**Dataset Used:**
`mart_current_container_status`

**X-Axis**

- Reroute Priority

**Y-Axis**

- Number of Containers

**Purpose**

Provides a fleet-wide summary showing how many shipments belong to each operational priority level.

---

### 4. Recoverable Value by Container

**Chart Type:** Horizontal Bar Chart

**Dataset Used:**
`mart_current_container_status`

**X-Axis**

- Recoverable Value

**Y-Axis**

- Container ID

**Purpose**

Shows the remaining financial value of every shipment after spoilage, helping determine whether rerouting is economically justified.

---

## Dashboard Outcome

The dashboard combines operational telemetry with financial analytics, enabling logistics managers to:

- Monitor all active containers in real time.
- Identify containers with high spoilage risk.
- Prioritize rerouting decisions.
- Estimate recoverable shipment value.
- Reduce financial losses by acting before commodities become unsellable.
