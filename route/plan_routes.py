"""Plan the three rover routes (fastest / safest / most efficient) with D* Lite.

Input : data/processed/elevation.npy, slope.npy, meta.json  (pipeline/build_grid.py)
Output: data/processed/routes.json, routes.png

Usage: python -m route.plan_routes
"""
import json
import math
from pathlib import Path

import numpy as np

from route.dstar_lite import INF, MOVES, DStarLite

DATA = Path(__file__).resolve().parent.parent / "data/processed"

# Mission endpoints (lat, lon in degrees).
START = (18.4446, 77.4509)  # Perseverance landing site, crater floor
GOAL = (18.4868, 77.4065)   # science target on top of the western delta

G_MARS = 3.71  # m/s^2

# PLACEHOLDER vehicle and crew numbers: replace with the team's rover specs.
ROVER = {
    "mass_kg": 200.0,
    "speed_ms": 0.5,           # on flat ground
    "rolling_resistance": 0.15,
    "drive_efficiency": 0.6,
    "idle_power_w": 100.0,     # avionics, heaters
    "battery_wh": 3000.0,
    "battery_reserve": 0.2,
}
CREW = {"walk_speed_ms": 1.0, "oxygen_h": 8.0, "oxygen_reserve": 0.25}

PROFILES = {
    "fastest": "Shortest driving time",
    "safest": "Avoids slopes above the safe limit",
    "efficient": "Lowest battery use",
}


def speed_factor(slope, max_slope):
    """Fraction of flat-ground speed kept on a slope (30% at the limit)."""
    return 1.0 - 0.7 * slope / max_slope


def edge_terms(elev, slope, meta):
    """Per-direction arrays for every move: length, slope, climb, validity."""
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
        yield length, s, climb, s <= max_slope


def edge_costs(profile, elev, slope, meta):
    """costs[d] (flat lists) for a profile and the lowest straight-move cost."""
    r, max_slope, safe = ROVER, meta["max_slope_deg"], meta["safe_slope_deg"]
    costs = []
    for length, s, climb, ok in edge_terms(elev, slope, meta):
        with np.errstate(invalid="ignore"):
            time_s = length / (r["speed_ms"] * speed_factor(s, max_slope))
            if profile == "fastest":
                c = time_s
            elif profile == "safest":
                c = length * (1.0 + (s / safe) ** 3)
            else:
                c = energy_wh(length, climb, time_s)
        costs.append(np.where(ok, c, INF).ravel().tolist())
    flat = {
        "fastest": meta["cell_m"] / r["speed_ms"],
        "safest": meta["cell_m"],
        "efficient": energy_wh(meta["cell_m"], 0.0, meta["cell_m"] / r["speed_ms"]),
    }[profile]
    return costs, flat


def energy_wh(length, climb, time_s):
    r = ROVER
    traction = r["mass_kg"] * G_MARS * (r["rolling_resistance"] * length + climb)
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


def leg_stats(cells, elev, slope, meta):
    """Distance, rover time/energy and crew walking time for one direction."""
    max_slope = meta["max_slope_deg"]
    dist = time_s = energy = walk_s = 0.0
    for (r0, c0), (r1, c1) in zip(cells, cells[1:]):
        length = meta["cell_m"] * math.hypot(r1 - r0, c1 - c0)
        s = max(slope[r0, c0], slope[r1, c1])
        t = length / (ROVER["speed_ms"] * speed_factor(s, max_slope))
        dist += length
        time_s += t
        energy += energy_wh(length, max(elev[r1, c1] - elev[r0, c0], 0.0), t)
        walk_s += length / (CREW["walk_speed_ms"] * speed_factor(s, max_slope))
    return dist, time_s, energy, walk_s


def describe(name, cells, elev, slope, meta):
    out_leg = leg_stats(cells, elev, slope, meta)
    back_leg = leg_stats(cells[::-1], elev, slope, meta)
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

    routes = []
    for name in PROFILES:
        costs, flat = edge_costs(name, elev, slope, meta)
        planner = DStarLite(costs, width, start[0] * width + start[1],
                            goal[0] * width + goal[1], min_step_cost=flat)
        path = planner.path()
        if path is None:
            raise SystemExit(f"{name}: goal unreachable")
        cells = [divmod(u, width) for u in path]
        routes.append(describe(name, cells, elev, slope, meta))

    out = {
        "grid": meta,
        "start": {"cell": list(start), "lonlat": to_lonlat(*start, meta)},
        "goal": {"cell": list(goal), "lonlat": to_lonlat(*goal, meta)},
        "rover": ROVER,
        "crew": CREW,
        "assumptions": "Rover and crew numbers are placeholders; rover motion is simulated.",
        "routes": routes,
    }
    (DATA / "routes.json").write_text(json.dumps(out, separators=(",", ":")) + "\n")
    for r in routes:
        print({k: v for k, v in r.items() if k not in ("cells", "path")})
    preview(elev, slope, meta, routes)


def preview(elev, slope, meta, routes):
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
    ax.legend(loc="lower left", fontsize=9)
    ax.set_title("Jezero delta: start (circle) to goal (star); red = slope above safe limit")
    ax.axis("off")
    plt.tight_layout()
    plt.savefig(DATA / "routes.png", dpi=80)


if __name__ == "__main__":
    main()
