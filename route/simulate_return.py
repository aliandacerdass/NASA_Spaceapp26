"""Simulate the rover's return trip with an obstacle the map does not show.

The rover drives back from the science target to base on the safest route.
A rock field that is invisible in the orbital data lies on that route; the
rover only sees the part of it within sensor range, and D* Lite repairs the
plan each time new blocked cells are seen.

Input : same as route.plan_routes
Output: data/processed/return_scenario.json, return_scenario.png

Usage: python -m route.simulate_return
"""
import json
import math
import time

import numpy as np

from route import plan_routes as P
from route.dstar_lite import DStarLite

PROFILE = "safest"
# PLACEHOLDER scenario numbers: we place the obstacle ourselves.
SCENARIO = {
    "obstacle_at_fraction": 0.32,  # how far along the planned return route
    "obstacle_radius_m": 100.0,
    "sensor_range_m": 30.0,
}


def length_m(cells, cell_m):
    return sum(cell_m * math.hypot(r1 - r0, c1 - c0) for (r0, c0), (r1, c1) in zip(cells, cells[1:]))


def main():
    elev = np.load(P.DATA / "elevation.npy").astype(float)
    slope = np.load(P.DATA / "slope.npy").astype(float)
    meta = json.loads((P.DATA / "meta.json").read_text())
    width, cell = meta["shape"][1], meta["cell_m"]
    inertia, crr = P.rolling_resistance(elev.shape)
    sun = P.sunlight(elev, meta)
    base, target = P.to_cell(P.START, meta), P.to_cell(P.GOAL, meta)
    flat = lambda rc: rc[0] * width + rc[1]

    costs, min_step = P.edge_costs(PROFILE, elev, slope, crr, sun, meta)
    t0 = time.perf_counter()
    planner = DStarLite(costs, width, flat(target), flat(base), min_step)
    first_plan_s = time.perf_counter() - t0
    planned = [divmod(u, width) for u in planner.path()]

    # Hidden rock field centred on the planned route.
    centre = planned[int(len(planned) * SCENARIO["obstacle_at_fraction"])]
    reach = int(SCENARIO["obstacle_radius_m"] / cell) + 1
    hidden = np.array([(centre[0] + dr, centre[1] + dc)
                       for dr in range(-reach, reach + 1) for dc in range(-reach, reach + 1)
                       if cell * math.hypot(dr, dc) <= SCENARIO["obstacle_radius_m"]])
    known = np.zeros(len(hidden), bool)

    driven, path, i = [planned[0]], planned, 0
    events, repair_s = [], 0.0
    while driven[-1] != base:
        here = driven[-1]
        seen = ~known & (cell * np.hypot(hidden[:, 0] - here[0], hidden[:, 1] - here[1])
                         <= SCENARIO["sensor_range_m"])
        if seen.any():
            known |= seen
            t0 = time.perf_counter()
            planner.replan(flat(here), [flat(rc) for rc in hidden[seen].tolist()])
            repair_s += time.perf_counter() - t0
            new_path = planner.path()
            if new_path is None:
                raise SystemExit("base unreachable after the obstacle")
            path, i = [divmod(u, width) for u in new_path], 0
            events.append({"at_cell": [int(here[0]), int(here[1])],
                           "at_lonlat": P.to_lonlat(*here, meta),
                           "new_blocked_cells": int(seen.sum())})
        i += 1
        driven.append(path[i])

    # Planning again from scratch at the first detection, for comparison.
    t0 = time.perf_counter()
    first = events[0]["at_cell"]
    DStarLite(costs, width, flat(first), flat(base), min_step)
    fresh_plan_s = time.perf_counter() - t0

    blocked = set(map(tuple, hidden.tolist()))
    assert not blocked & set(driven), "driven route crosses the obstacle"
    out = {
        "profile": PROFILE,
        "scenario": SCENARIO,
        "assumptions": "The obstacle is placed by us; rover motion and sensing are simulated.",
        "obstacle": {"centre_cell": [int(centre[0]), int(centre[1])],
                     "centre_lonlat": P.to_lonlat(*centre, meta),
                     "cells": hidden.tolist()},
        "planned_distance_m": round(length_m(planned, cell)),
        "driven_distance_m": round(length_m(driven, cell)),
        "replans": len(events),
        "first_plan_s": round(first_plan_s, 2),
        "repair_total_s": round(repair_s, 3),
        "fresh_plan_at_first_detection_s": round(fresh_plan_s, 2),
        "events": events,
        "planned": P.describe(PROFILE, planned, elev, slope, inertia, crr, sun, meta),
        "driven": P.describe(PROFILE, driven, elev, slope, inertia, crr, sun, meta),
    }
    (P.DATA / "return_scenario.json").write_text(json.dumps(out, separators=(",", ":")) + "\n")
    print({k: v for k, v in out.items() if k not in ("obstacle", "events", "planned", "driven")})
    preview(elev, meta, planned, driven, hidden, events)


def preview(elev, meta, planned, driven, hidden, events):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.colors import LightSource

    rows = [r for r, _ in planned + driven]
    cols = [c for _, c in planned + driven]
    pad = 60
    r0, r1 = max(min(rows) - pad, 0), min(max(rows) + pad, elev.shape[0])
    c0, c1 = max(min(cols) - pad, 0), min(max(cols) + pad, elev.shape[1])
    fig, ax = plt.subplots(figsize=(9, 9))
    shade = LightSource(315, 45).shade(elev[r0:r1, c0:c1], cmap=plt.cm.copper, vert_exag=3,
                                       dx=meta["cell_m"], dy=meta["cell_m"], blend_mode="soft")
    ax.imshow(shade, extent=(c0, c1, r1, r0))
    ax.plot([c for _, c in planned], [r for r, _ in planned], "--", color="white", lw=1.5,
            label="planned return route")
    ax.plot([c for _, c in driven], [r for r, _ in driven], color="#7CFC00", lw=2,
            label="driven route after replanning")
    ax.scatter(hidden[:, 1], hidden[:, 0], s=4, color="#ff3b30", label="hidden obstacle")
    ax.plot(events[0]["at_cell"][1], events[0]["at_cell"][0], "o", color="#ffd60a", ms=8,
            label="first detection")
    ax.legend(loc="lower left", fontsize=9)
    ax.set_title("Return trip: obstacle not in the orbital map, D* Lite repairs the route")
    ax.axis("off")
    plt.tight_layout()
    plt.savefig(P.DATA / "return_scenario.png", dpi=80)


if __name__ == "__main__":
    main()
