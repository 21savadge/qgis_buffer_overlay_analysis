# Automated Buffer & Overlay Analysis (PyQGIS-style)

## What it does
Given a set of monitoring/well points and a set of restricted zones
(protected area, pipeline corridor, etc.), this script:
1. Generates a buffer circle around each point
2. Tests whether each point/buffer intersects a restricted zone
3. Exports a CSV report + a PNG map flagging conflicts

## Why this is a good freelance portfolio piece
- Shows understanding of core spatial algorithms (point-in-polygon, buffering) rather than just calling a library function
- Same logic works as a plugin script inside QGIS's Python console, swapping the synthetic data for `iface.activeLayer()` features
- Deliverable is exactly what a real client asks for: a CSV report + a map image, not just raw code

## How to run
Outputs `analysis_report.csv` and `analysis_map.png`.

## Adapting for a real client project
- Replace `monitoring_points` / `restricted_zones` with data read from a shapefile/GeoJSON (via `fiona`, `pyshp`, or directly in PyQGIS via `QgsVectorLayer`)
- Replace the manual point-in-polygon/buffer functions with `shapely`/`geopandas` calls for production use — kept manual here purely to demonstrate the underlying algorithm
- Buffer radius, zone list, and output paths are the parameters a client would want exposed as CLI args or a small config file
