{{ config(materialized='table') }}

SELECT
    container_id,
    commodity,
    origin,
    destination,
    current_location,
    temperature_c,
    humidity_pct,
    vibration,
    spoilage_pct,
    reroute_needed,
    recommended_market,
    reroute_reason,
    base_price_per_kg,
    recommended_price_kg,
    timestamp,

    CASE
        WHEN spoilage_pct >= 50 THEN 'Critical'
        WHEN spoilage_pct >= 20 THEN 'Warning'
        ELSE 'Healthy'
    END AS health_status

FROM {{ ref('fct_container_events') }}
