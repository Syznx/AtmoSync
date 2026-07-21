{{ config(materialized='table') }}

SELECT
    container_id,
    commodity,
    AVG(spoilage_pct) AS avg_spoilage_pct,
    MAX(spoilage_pct) AS max_spoilage_pct,
    MIN(spoilage_pct) AS min_spoilage_pct,
    COUNT(*) AS total_events

FROM {{ ref('fct_container_events') }}

GROUP BY
    container_id,
    commodity
