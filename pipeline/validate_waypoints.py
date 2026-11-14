"""Check our grid against where Perseverance actually drove.

NASA publishes the rover's localized stops (position, elevation, tilt). For
every stop inside the mission area this compares NASA's elevation with our
5 m elevation grid, and the rover's recorded tilt with our slope.

Input : data/processed/elevation.npy, slope.npy, meta.json
        NASA M20 waypoints (about 0.6 MB, cached in data/raw/)
Output: data/processed/validation.json

Usage: python pipeline/validate_waypoints.py
"""
import json
import urllib.request
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data/processed"
CACHE = ROOT / "data/raw/M20_waypoints.json"
URL = "https://mars.nasa.gov/mmgis-maps/M20/Layers/json/M20_waypoints.json"


def main():
    if not CACHE.exists():
        req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"})
        CACHE.write_bytes(urllib.request.urlopen(req, timeout=60).read())
    stops = [f["properties"] for f in json.loads(CACHE.read_text())["features"]]
    meta = json.loads((DATA / "meta.json").read_text())
    elev = np.load(DATA / "elevation.npy")
    slope = np.load(DATA / "slope.npy").astype(float)
    n_rows, n_cols = meta["shape"]

    diffs, tilts, slopes, sols = [], [], [], []
    for s in stops:
        row = int((meta["north_lat"] - s["lat"]) / (meta["north_lat"] - meta["south_lat"]) * n_rows)
        col = int((s["lon"] - meta["west_lon"]) / (meta["east_lon"] - meta["west_lon"]) * n_cols)
        if 0 <= row < n_rows and 0 <= col < n_cols:
            diffs.append(s["elev_geoid"] - float(elev[row, col]))
            tilts.append(s["tilt"])
            slopes.append(slope[row, col])
            sols.append(s["sol"])
    diffs = np.array(diffs)
    out = {
        "source": URL,
        "rover_stops_in_area": len(diffs),
        "sol_range": [min(sols), max(sols)],
        "elevation_difference_m": {
            "mean": round(float(diffs.mean()), 2),
            "std": round(float(diffs.std()), 2),
            "max_abs": round(float(np.abs(diffs).max()), 2),
        },
        "rover_tilt_deg": {"median": round(float(np.median(tilts)), 1),
                           "max": round(float(np.max(tilts)), 1)},
        "grid_slope_at_stops_deg": {"median": round(float(np.median(slopes)), 1),
                                    "max": round(float(np.max(slopes)), 1)},
    }
    (DATA / "validation.json").write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
