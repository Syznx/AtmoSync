WITH container_data AS (

    SELECT *
    FROM {{ ref('fct_container_events') }}

),

market_distance AS (

    SELECT *
    FROM {{ ref('market_distances') }}

),

commodity_price AS (

    SELECT *
    FROM {{ ref('commodity_prices') }}

)

SELECT

    c.container_id,
    c.timestamp,
    c.commodity,
    c.current_location,
    c.destination,
    c.recommended_market,

    c.temperature_c,
    c.humidity_pct,
    c.spoilage_pct,

    m.distance_km,

    p.price_per_kg,

(100 - c.spoilage_pct) AS remaining_shelf_life_pct,

ROUND(
    p.price_per_kg * (100 - c.spoilage_pct) / 100.0,
    2
) AS recoverable_value,

CASE
    WHEN c.temperature_c >= 25 THEN 'High'
    WHEN c.temperature_c >= 18 THEN 'Medium'
    ELSE 'Low'
END AS temperature_risk,

CASE
    WHEN m.distance_km > 400 THEN 'High'
    WHEN m.distance_km > 200 THEN 'Medium'
    ELSE 'Low'
END AS distance_risk,

CASE
    WHEN c.spoilage_pct >= 80 THEN 'Critical'
    WHEN c.spoilage_pct >= 50 THEN 'High'
    WHEN c.spoilage_pct >= 20 THEN 'Medium'
    ELSE 'Low'
END AS spoilage_risk,

ROUND(
    (
        (c.spoilage_pct * 0.5) +
        (m.distance_km * 0.3 / 10.0) +
        (c.temperature_c * 0.2)
    ),
    2
) AS arbitrage_score,

CASE
    WHEN
        (
            (c.spoilage_pct * 0.5) +
            (m.distance_km * 0.3 / 10.0) +
            (c.temperature_c * 0.2)
        ) >= 70
    THEN 'Immediate Reroute'

    WHEN
        (
            (c.spoilage_pct * 0.5) +
            (m.distance_km * 0.3 / 10.0) +
            (c.temperature_c * 0.2)
        ) >= 50
    THEN 'High Priority'

    WHEN
        (
            (c.spoilage_pct * 0.5) +
            (m.distance_km * 0.3 / 10.0) +
            (c.temperature_c * 0.2)
        ) >= 30
    THEN 'Monitor'

    ELSE 'Continue Route'
END AS reroute_priority

FROM container_data c

LEFT JOIN market_distance m
ON c.current_location = m.current_location
AND c.recommended_market = m.recommended_market

LEFT JOIN commodity_price p
ON c.commodity = p.commodity
AND c.recommended_market = p.market
