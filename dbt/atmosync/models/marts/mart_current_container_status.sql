WITH ranked_events AS (

    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY container_id
            ORDER BY timestamp DESC
        ) AS rn

    FROM {{ ref('mart_spoilage_arbitrage') }}

)

SELECT *

FROM ranked_events

WHERE rn = 1