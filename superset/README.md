# Apache Superset Dashboard Export

This folder contains the exported Apache Superset dashboard assets for the AtmoSync project.

## File

- `atmosync_superset_dashboard_export.zip`

The export contains the dashboard configuration, charts, datasets, and metadata generated from Apache Superset.

### Dashboard Included

- Container Health Status
- Average Spoilage by Container
- Historical Temperature Trend
- Live Container Route Map
- Reroute Alerts

The dashboard is built on the transformed DuckDB models produced by the dbt ELT pipeline.

> Note: The export format is provided as a ZIP archive because newer versions of Apache Superset export dashboard assets in ZIP format instead of JSON.
