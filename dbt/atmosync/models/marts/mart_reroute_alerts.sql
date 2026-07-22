{{ config(materialized='table') }}

SELECT
    container_id,
    commodity,
    current_location,
    destination,
    recommended_market,
    reroute_needed,
    reroute_reason,
    spoilage_pct,
    recommended_price_kg,
    timestamp

FROM {{ ref('fct_container_events') }}

WHERE reroute_needed = 1

ORDER BY
    spoilage_pct DESC,
    timestamp DESC
