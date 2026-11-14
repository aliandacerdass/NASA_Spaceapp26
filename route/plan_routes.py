"""Plan the three rover routes (fastest / safest / most efficient) with D* Lite.

Input : data/processed/elevation.npy, slope.npy, meta.json  (pipeline/build_grid.py)
        data/layers/jezero_thermal_inertia_100m.tif  (THEMIS thermal inertia, same area)
Output: data/processed/routes.json, routes.png

Usage: python -m route.plan_routes
"""
import json
import math
from array import array
from pathlib import Path

import numpy as np
from PIL import Image
from scipy.ndimage import zoom

from route.dstar_lite import INF, MOVES, DStarLite

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data/processed"
THERMAL = ROOT / "data/layers/jezero_thermal_inertia_100m.tif"

# Mission endpoints (lat, lon in degrees).
START = (18.4446, 77.4509)  # Perseverance landing site, crater floor
GOAL = (18.4868, 77.4065)   # team-chosen target on the delta top, behind the scarp

# Places where Perseverance actually stopped (lat, lon from NASA's M20 waypoints).
STOPS = [
    ("rochette", "Rochette", 18.43074, 77.44437, "First two rock cores of the mission"),
    ("three_forks", "Three Forks", 18.45263, 77.40776, "Sample depot at the delta base"),
    ("amalik", "Amalik", 18.45073, 77.40144, "Sulfate- and carbonate-bearing mudstone"),
    ("wildcat_ridge", "Wildcat Ridge", 18.45865, 77.40592, "Strongest organic detections of the mission"),
    ("berea", "Berea", 18.47021, 77.38399, "Delta-top core of river-borne sediment"),
    ("belva", "Belva crater viewpoint", 18.48293, 77.36901, "Layers exposed in the crater wall"),
]

G_MARS = 3.71  # m/s^2

# PLACEHOLDER vehicle and crew numbers: replace with the team's rover specs.
ROVER = {
    "mass_kg": 200.0,
    "speed_ms": 0.5,           # on flat ground
    "drive_efficiency": 0.6,
    "idle_power_w": 100.0,     # avionics, heaters
    "battery_wh": 3000.0,
    "battery_reserve": 0.2,
}
# PLACEHOLDER ground model: thermal inertia (J m-2 K-1 s-1/2) tells loose sand
# (low) from firm rock (high); wheels lose more energy on loose ground.
SOIL = {
    "thermal_inertia_loose": 150.0, "rolling_resistance_loose": 0.25,
    "thermal_inertia_firm": 350.0, "rolling_resistance_firm": 0.10,
}
# Crew numbers are sourced but lunar: 8 h EVA design requirement (NASA xEMU),
# 3.3 km/h planned walking speed and 20% emergency walk-back pad (Apollo).
CREW = {"walk_speed_ms": 3.3 / 3.6, "oxygen_h": 8.0, "oxygen_reserve": 0.20}

PROFILES = {
    "fastest": "Shortest driving time",
    "safest": "Avoids slopes above the safe limit",
    "efficient": "Lowest battery use",
}


def speed_factor(slope, max_slope):
    """Fraction of flat-ground speed kept on a slope (30% at the limit)."""
    return 1.0 - 0.7 * slope / max_slope


def rolling_resistance(shape):
    """Per-cell rolling resistance from the thermal inertia layer (bilinear to the grid)."""
    inertia = np.array(Image.open(THERMAL), dtype=float)
    inertia = zoom(inertia, (shape[0] / inertia.shape[0], shape[1] / inertia.shape[1]), order=1)
    s = SOIL
    return inertia, np.interp(
        inertia, [s["thermal_inertia_loose"], s["thermal_inertia_firm"]],
        [s["rolling_resistance_loose"], s["rolling_resistance_firm"]])


def edge_terms(elev, slope, crr, meta):
    """Per-direction arrays for every move: length, slope, climb, resistance, validity."""
    cell, max_slope = meta["cell_m"], meta["max_slope_deg"]
    h, w = elev.shape
    for dr, dc in MOVES:
        src = (slice(max(0, -dr), h - max(0, dr)), slice(max(0, -dc), w - max(0, dc)))
        dst = (slice(max(0, dr), h - max(0, -dr)), slice(max(0, dc), w - max(0, -dc)))
        length = np.full((h, w), cell * math.hypot(dr, dc))
        s = np.full((h, w), np.inf)
        s[src] = np.maximum(slope[src], slope[dst])
        climb = np.zeros((h, w))
        climb[src] = np.maximum(elev[dst] - elev[src], 0.0)
        resistance = crr.copy()
        resistance[src] = np.maximum(crr[src], crr[dst])
        yield length, s, climb, resistance, s <= max_slope


def edge_costs(profile, elev, slope, crr, meta):
    """costs[d] (flat arrays) for a profile and the lowest straight-move cost."""
    r, max_slope, safe = ROVER, meta["max_slope_deg"], meta["safe_slope_deg"]
    costs = []
    for length, s, climb, resistance, ok in edge_terms(elev, slope, crr, meta):
        with np.errstate(invalid="ignore"):
            time_s = length / (r["speed_ms"] * speed_factor(s, max_slope))
            if profile == "fastest":
                c = time_s
            elif profile == "safest":
                c = length * (1.0 + (s / safe) ** 3)
                ok = ok & (s <= safe)  # never enters cells above the safe limit
            else:
                c = energy_wh(length, climb, time_s, resistance)
        costs.append(array("d", np.where(ok, c, INF).tobytes()))
    flat = {
        "fastest": meta["cell_m"] / r["speed_ms"],
        "safest": meta["cell_m"],
        "efficient": energy_wh(meta["cell_m"], 0.0, meta["cell_m"] / r["speed_ms"],
                               SOIL["rolling_resistance_firm"]),
    }[profile]
    return costs, flat


def energy_wh(length, climb, time_s, resistance):
    r = ROVER
    traction = r["mass_kg"] * G_MARS * (resistance * length + climb)
    return (traction / r["drive_efficiency"] + r["idle_power_w"] * time_s) / 3600.0


def to_cell(latlon, meta):
    n_rows, n_cols = meta["shape"]
    row = (meta["north_lat"] - latlon[0]) / (meta["north_lat"] - meta["south_lat"]) * n_rows
    col = (latlon[1] - meta["west_lon"]) / (meta["east_lon"] - meta["west_lon"]) * n_cols
    return int(row), int(col)


def to_lonlat(row, col, meta):
    n_rows, n_cols = meta["shape"]
    lat = meta["north_lat"] - (row + 0.5) / n_rows * (meta["north_lat"] - meta["south_lat"])
    lon = meta["west_lon"] + (col + 0.5) / n_cols * (meta["east_lon"] - meta["west_lon"])
    return round(lon, 6), round(lat, 6)


def leg_stats(cells, elev, slope, crr, meta):
    """Distance, rover time/energy and crew walking time for one direction."""
    max_slope = meta["max_slope_deg"]
    dist = time_s = energy = walk_s = 0.0
    for (r0, c0), (r1, c1) in zip(cells, cells[1:]):
        length = meta["cell_m"] * math.hypot(r1 - r0, c1 - c0)
        s = max(slope[r0, c0], slope[r1, c1])
        t = length / (ROVER["speed_ms"] * speed_factor(s, max_slope))
        dist += length
        time_s += t
        energy += energy_wh(length, max(elev[r1, c1] - elev[r0, c0], 0.0), t,
                            max(crr[r0, c0], crr[r1, c1]))
        walk_s += length / (CREW["walk_speed_ms"] * speed_factor(s, max_slope))
    return dist, time_s, energy, walk_s


def describe(name, cells, elev, slope, inertia, crr, meta):
    out_leg = leg_stats(cells, elev, slope, crr, meta)
    back_leg = leg_stats(cells[::-1], elev, slope, crr, meta)
    slopes = np.array([slope[r, c] for r, c in cells])
    battery = ROVER["battery_wh"] * (1 - ROVER["battery_reserve"])
    oxygen_h = CREW["oxygen_h"] * (1 - CREW["oxygen_reserve"])
    round_trip_wh = out_leg[2] + back_leg[2]
    round_trip_walk_h = (out_leg[3] + back_leg[3]) / 3600.0
    return {
        "id": name,
        "label": PROFILES[name],
        "distance_m": round(out_leg[0]),
        "rover_time_min": round(out_leg[1] / 60.0, 1),
        "rover_energy_wh": round(out_leg[2], 1),
        "max_slope_deg": round(float(slopes.max()), 1),
        "above_safe_m": round(float((slopes > meta["safe_slope_deg"]).mean()) * out_leg[0]),
        "mean_thermal_inertia": round(float(np.mean([inertia[r, c] for r, c in cells]))),
        "round_trip_energy_wh": round(round_trip_wh, 1),
        "battery_ok": bool(round_trip_wh <= battery),
        "round_trip_walk_h": round(round_trip_walk_h, 2),
        "oxygen_ok": bool(round_trip_walk_h <= oxygen_h),
        "cells": [[int(r), int(c)] for r, c in cells],
        "path": [[*to_lonlat(r, c, meta), round(float(elev[r, c]), 1)] for r, c in cells],
    }


def main():
    elev = np.load(DATA / "elevation.npy").astype(float)
    slope = np.load(DATA / "slope.npy").astype(float)
    meta = json.loads((DATA / "meta.json").read_text())
    width = meta["shape"][1]
    start, goal = to_cell(START, meta), to_cell(GOAL, meta)
    inertia, crr = rolling_resistance(elev.shape)

    all_costs = {name: edge_costs(name, elev, slope, crr, meta) for name in PROFILES}

    def plan(goal):
        routes = []
        for name, (costs, flat) in all_costs.items():
            planner = DStarLite(costs, width, start[0] * width + start[1],
                                goal[0] * width + goal[1], min_step_cost=flat)
            path = planner.path()
            if path is None:
                raise SystemExit(f"{name}: goal {goal} unreachable")
            cells = [divmod(u, width) for u in path]
            routes.append(describe(name, cells, elev, slope, inertia, crr, meta))
        return routes

    routes = plan(goal)
    stops = []
    for stop_id, label, lat, lon, why in STOPS:
        cell = to_cell((lat, lon), meta)
        stops.append({"id": stop_id, "name": label, "why": why, "cell": list(cell),
                      "lonlat": to_lonlat(*cell, meta), "routes": plan(cell)})

    out = {
        "grid": meta,
        "start": {"cell": list(start), "lonlat": to_lonlat(*start, meta)},
        "goal": {"cell": list(goal), "lonlat": to_lonlat(*goal, meta)},
        "rover": ROVER,
        "soil": SOIL,
        "crew": CREW,
        "assumptions": "Rover and soil numbers are placeholders; crew numbers are lunar values; "
                       "rover motion is simulated.",
        "routes": routes,
        "stops": stops,
    }
    (DATA / "routes.json").write_text(json.dumps(out, separators=(",", ":")) + "\n")
    for r in routes:
        print({k: v for k, v in r.items() if k not in ("cells", "path")})
    for s in stops:
        print(s["name"], [(r["id"], r["distance_m"], r["max_slope_deg"]) for r in s["routes"]])
    preview(elev, slope, meta, routes, stops)


def preview(elev, slope, meta, routes, stops):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.colors import LightSource

    fig, ax = plt.subplots(figsize=(9, 9))
    ax.imshow(LightSource(315, 45).shade(elev, cmap=plt.cm.copper, vert_exag=3,
                                         dx=meta["cell_m"], dy=meta["cell_m"], blend_mode="soft"))
    ax.contourf(slope > meta["safe_slope_deg"], levels=[0.5, 1], colors=["#ff3b30"], alpha=0.6)
    for r, color in zip(routes, ["#00e5ff", "#7CFC00", "#ffd60a"]):
        rows, cols = zip(*r["cells"])
        ax.plot(cols, rows, color=color, lw=2,
                label=f'{r["id"]}: {r["distance_m"] / 1000:.2f} km, {r["rover_time_min"]:.0f} min, '
                      f'{r["rover_energy_wh"]:.0f} Wh, max {r["max_slope_deg"]:.0f} deg')
    (r0, c0), (r1, c1) = routes[0]["cells"][0], routes[0]["cells"][-1]
    ax.plot(c0, r0, "wo", ms=9)
    ax.plot(c1, r1, "w*", ms=16)
    for s in stops:
        ax.plot(s["cell"][1], s["cell"][0], "s", color="white", ms=5)
        ax.annotate(s["name"], (s["cell"][1], s["cell"][0]), color="white", fontsize=8,
                    xytext=(5, 4), textcoords="offset points")
    ax.legend(loc="lower left", fontsize=9)
    ax.set_title("Jezero delta: start (circle) to goal (star); red = slope above safe limit")
    ax.axis("off")
    plt.tight_layout()
    plt.savefig(DATA / "routes.png", dpi=80)


if __name__ == "__main__":
    main()
