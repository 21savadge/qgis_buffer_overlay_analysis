"""
Automated Buffer & Point-in-Polygon Overlay Analysis
------------------------------------------------------
Use case: Given a set of well/monitoring points and a set of restricted
zones (e.g. protected areas, pipeline corridors, flood zones), automatically
1) generate buffer zones around each point,
2) flag which points fall inside restricted polygons,
3) export a summary report (CSV) and a static map (PNG).

This mirrors a common PyQGIS batch-processing task (Processing Toolbox:
Buffer + Intersect), but is written as a standalone script using only
numpy/matplotlib so it can run anywhere -- inside QGIS's Python console,
as a PyQGIS plugin script, or as a plain automation pipeline. The geometry
functions (buffer as circle polygon, ray-casting point-in-polygon) are
implemented from scratch to show understanding of the underlying spatial
algorithms, not just library calls.

Author: <your name>
"""

import csv
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MplPolygon


# ---------------------------------------------------------------------
# 1. Geometry primitives (the kind of thing PyQGIS / Shapely do for you,
#    written manually here as a demonstration of core GIS algorithms)
# ---------------------------------------------------------------------

def make_circle_polygon(center, radius, n_points=36):
    """Approximate a buffer circle as an n-sided polygon."""
    angles = np.linspace(0, 2 * np.pi, n_points, endpoint=False)
    x = center[0] + radius * np.cos(angles)
    y = center[1] + radius * np.sin(angles)
    return list(zip(x, y))


def point_in_polygon(point, polygon):
    """Ray-casting algorithm for point-in-polygon test."""
    x, y = point
    n = len(polygon)
    inside = False
    x1, y1 = polygon[0]
    for i in range(1, n + 1):
        x2, y2 = polygon[i % n]
        if y > min(y1, y2):
            if y <= max(y1, y2):
                if x <= max(x1, x2):
                    if y1 != y2:
                        x_intersect = (y - y1) * (x2 - x1) / (y2 - y1) + x1
                    if x1 == x2 or x <= x_intersect:
                        inside = not inside
        x1, y1 = x2, y2
    return inside


def polygons_intersect_bbox(poly_a, poly_b):
    """Cheap bounding-box pre-check before a full intersection test."""
    ax = [p[0] for p in poly_a]
    ay = [p[1] for p in poly_a]
    bx = [p[0] for p in poly_b]
    by = [p[1] for p in poly_b]
    return not (max(ax) < min(bx) or min(ax) > max(bx) or
                max(ay) < min(by) or min(ay) > max(by))


# ---------------------------------------------------------------------
# 2. Synthetic input data (replace with real coordinates / shapefile
#    read via fiona, pyshp, or QGIS's own iface.activeLayer() in a
#    real PyQGIS plugin)
# ---------------------------------------------------------------------

np.random.seed(42)
monitoring_points = {
    f"P{i+1}": (np.random.uniform(0, 1000), np.random.uniform(0, 1000))
    for i in range(15)
}

restricted_zones = {
    "Zone_A_Protected": [(200, 200), (450, 220), (430, 480), (180, 460)],
    "Zone_B_Pipeline": [(600, 100), (900, 150), (880, 400), (620, 380)],
}

BUFFER_RADIUS = 50  # meters


# ---------------------------------------------------------------------
# 3. Run the analysis
# ---------------------------------------------------------------------

def run_analysis():
    results = []
    for name, coord in monitoring_points.items():
        buffer_poly = make_circle_polygon(coord, BUFFER_RADIUS)
        flagged_zones = []
        for zone_name, zone_poly in restricted_zones.items():
            if polygons_intersect_bbox(buffer_poly, zone_poly):
                # if any buffer vertex or the center falls inside the zone,
                # flag it (simplified intersection test for this demo)
                if point_in_polygon(coord, zone_poly) or any(
                    point_in_polygon(v, zone_poly) for v in buffer_poly
                ):
                    flagged_zones.append(zone_name)
        results.append({
            "point_id": name,
            "x": round(coord[0], 2),
            "y": round(coord[1], 2),
            "buffer_radius_m": BUFFER_RADIUS,
            "conflicts_with": "; ".join(flagged_zones) if flagged_zones else "none",
            "status": "REVIEW REQUIRED" if flagged_zones else "clear",
        })
    return results


def export_csv(results, path="analysis_report.csv"):
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)
    print(f"Report written to {path}")


def export_map(results, path="analysis_map.png"):
    fig, ax = plt.subplots(figsize=(9, 9))

    for zone_name, poly in restricted_zones.items():
        patch = MplPolygon(poly, closed=True, alpha=0.3, color="red",
                            label=zone_name)
        ax.add_patch(patch)

    for r in results:
        color = "red" if r["status"] == "REVIEW REQUIRED" else "green"
        ax.plot(r["x"], r["y"], "o", color=color, markersize=6)
        circle = plt.Circle((r["x"], r["y"]), BUFFER_RADIUS,
                             fill=False, linestyle="--", color=color, alpha=0.6)
        ax.add_patch(circle)
        ax.annotate(r["point_id"], (r["x"], r["y"]), fontsize=8,
                     xytext=(4, 4), textcoords="offset points")

    ax.set_xlim(-50, 1050)
    ax.set_ylim(-50, 1050)
    ax.set_aspect("equal")
    ax.set_title("Monitoring Points vs Restricted Zones\n(green = clear, red = review required)")
    ax.set_xlabel("X (m)")
    ax.set_ylabel("Y (m)")
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    print(f"Map written to {path}")


if __name__ == "__main__":
    results = run_analysis()
    export_csv(results, "/home/claude/portfolio/project1_pyqgis_automation/analysis_report.csv")
    export_map(results, "/home/claude/portfolio/project1_pyqgis_automation/analysis_map.png")

    n_flagged = sum(1 for r in results if r["status"] == "REVIEW REQUIRED")
    print(f"\n{n_flagged} of {len(results)} points require review.")
