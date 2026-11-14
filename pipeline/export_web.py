"""Export everything the web interface reads into web/data and web/assets.

Input : data/processed/*, data/layers/*  (run the other pipeline and route scripts first)
Output: web/data/mission.json   targets, routes with profiles, return scenario, validation
        web/data/height.bin     Uint16 little-endian, 1000 x 1000, row 0 = north
                                (0..65535 spans grid.height_min_m..height_max_m)
        web/data/basemap.jpg    CTX image on the mission grid, tinted to Mars colours
        web/data/normal.jpg     object-space normal map from the full 5 m elevation grid
        web/data/slope.png, thermal.png   transparent overlays
        web/data/mars.jpg       global Viking colour mosaic for the globe (NASA Mars Trek)
        web/assets/astronaut.jpg  Apollo 11 photo AS11-40-5903 (NASA, public domain)
        web/assets/arrival/*.jpg  Perseverance Navcam photos taken at the science stops

Downloads about 4 MB on the first run (globe tiles, photos, weather feed).

Usage: python pipeline/export_web.py
"""
import io
import json
import urllib.request
from pathlib import Path

import numpy as np
from matplotlib import colormaps
from PIL import Image
from scipy.ndimage import gaussian_filter, zoom

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data/processed"
LAYERS = ROOT / "data/layers"
WEB = ROOT / "web/data"
ASSETS = ROOT / "web/assets"

MESH = 1000     # terrain mesh resolution (cells per side)
RELIEF = 2.0    # vertical exaggeration used by the 3D view
# CTX is a single-band image; these stops tint it from shadow to sunlit dust.
TINT = [(0.0, (18, 9, 6)), (0.3, (92, 48, 30)), (0.62, (176, 108, 68)), (1.0, (240, 205, 160))]
PROFILE = 160   # samples per route profile

TREK = ("https://trek.nasa.gov/tiles/Mars/EQ/Mars_Viking_MDIM21_ClrMosaic_global_232m/"
        "1.0.0/default/default028mm/2/{row}/{col}.jpg")
ASTRONAUT = "https://images-assets.nasa.gov/image/as11-40-5903/as11-40-5903~large.jpg"

# Navcam frames taken by Perseverance while parked at each stop (sol, raw image URL).
RAW = "https://mars.nasa.gov/mars2020-raw-images/pub/ods/surface/sol/"
PHOTOS = {
    "rochette": (180, "00180/ids/edr/browse/ncam/NLF_0180_0682927330_919ECM_N0070000NCAM02180_01_195J04_1200.jpg"),
    "wildcat_ridge": (502, "00502/ids/edr/browse/ncam/NLF_0502_0711508459_901ECM_N0261222NCAM04502_01_195J01_1200.jpg"),
    "amalik": (565, "00565/ids/edr/browse/ncam/NLF_0565_0717106894_160ECM_N0290000NCAM03565_01_195J01_1200.jpg"),
    "three_forks": (652, "00652/ids/edr/browse/ncam/NLF_0652_0724830144_855ECM_N0320148NCAM03652_05_095J01_1200.jpg"),
    "berea": (736, "00736/ids/edr/browse/ncam/NLF_0736_0732292608_746ECM_N0370000NCAM03736_01_195J01_1200.jpg"),
    "belva": (770, "00770/ids/edr/browse/ncam/NLF_0770_0735307364_034ECM_N0390650NCAM00709_01_095J01_1200.jpg"),
}
WEATHER_FEED = "https://mars.nasa.gov/rss/api/?feed=weather&category=mars2020&feedtype=json"

# Representative surface radiation: Curiosity RAD in Gale crater, not Jezero.
# Dose equivalent is the published 2012-2013 mean; the absorbed dose statistics
# come from pipeline/fetch_rad.py (measured, whole mission).
DOSE_EQUIVALENT_MSV_PER_DAY = 0.67


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    return urllib.request.urlopen(req, timeout=60).read()


def globe_texture():
    out = WEB / "mars.jpg"
    if out.exists():
        return
    sheet = Image.new("RGB", (8 * 256, 4 * 256))
    for row in range(4):
        for col in range(8):
            tile = Image.open(io.BytesIO(get(TREK.format(row=row, col=col))))
            sheet.paste(tile, (col * 256, row * 256))
    sheet.save(out, quality=88)


def astronaut_photo():
    out = ASSETS / "astronaut.jpg"
    if not out.exists():
        out.write_bytes(get(ASTRONAUT))


def arrival_photos():
    folder = ASSETS / "arrival"
    folder.mkdir(exist_ok=True)
    out = {}
    for stop, (sol, path) in PHOTOS.items():
        file = folder / f"{stop}.jpg"
        if not file.exists():
            file.write_bytes(get(RAW + path))
        out[stop] = {"file": f"assets/arrival/{stop}.jpg", "sol": sol, "source": RAW + path,
                     "credit": "NASA/JPL-Caltech"}
    return out


def weather():
    """Air temperature and pressure measured in Jezero by Perseverance's MEDA station."""
    cache = ROOT / "data/raw/m20_weather.json"
    if not cache.exists():
        cache.write_bytes(get(WEATHER_FEED))
    sols = [s for s in json.loads(cache.read_text())["sols"]
            if all(isinstance(s[k], (int, float)) for k in ("min_temp", "max_temp", "pressure"))]
    lows, highs = [s["min_temp"] for s in sols], [s["max_temp"] for s in sols]
    pressure = [s["pressure"] for s in sols]
    return {
        "sols": [int(sols[0]["sol"]), int(sols[-1]["sol"])],
        "air_temp_c": {"min": min(lows), "mean": round(float(np.mean(lows + highs)), 1), "max": max(highs)},
        "pressure_pa": {"min": min(pressure), "mean": round(float(np.mean(pressure)), 1), "max": max(pressure)},
        "source": "Perseverance MEDA, NASA Mars 2020 weather feed",
    }


def radiation():
    rad = json.loads((DATA / "radiation.json").read_text())
    return {
        "dose_equivalent_msv_per_day": DOSE_EQUIVALENT_MSV_PER_DAY,
        "absorbed_mgy_per_day": rad["absorbed_dose_mgy_per_day"],
        "observations": rad["sampled_observations"],
        "sol_range": rad["sol_range"],
        "years": [int(rad["utc_range"][0][:4]), int(rad["utc_range"][1][:4])],
        "source": "Curiosity RAD, Gale crater (PDS MSL-M-RAD-3-RDR-V1.0; Hassler et al. 2014)",
    }


def terrain_textures(elev, meta):
    """Tinted basemap and a normal map that carries the full 5 m relief."""
    grey = np.asarray(Image.open(LAYERS / "jezero_ctx_basemap_5m.png").convert("L"), dtype=float) / 255
    lo, hi = np.percentile(grey, [0.5, 99.5])
    grey = np.clip((grey - lo) / (hi - lo), 0, 1) ** 0.9
    stops = np.array([s for s, _ in TINT])
    rgb = np.stack([np.interp(grey, stops, [c[i] for _, c in TINT]) for i in range(3)], axis=-1)
    Image.fromarray(rgb.astype(np.uint8)).save(WEB / "basemap.jpg", quality=90)

    # World axes: x east, y up, z south. Heights are exaggerated like the mesh.
    dz_south, dz_east = np.gradient(gaussian_filter(elev, 0.7) * RELIEF, meta["cell_m"])
    n = np.stack([-dz_east, np.ones_like(elev), -dz_south], axis=-1)
    n /= np.linalg.norm(n, axis=-1, keepdims=True)
    Image.fromarray(((n * 0.5 + 0.5) * 255).round().astype(np.uint8)).save(WEB / "normal.jpg", quality=93)


def overlays(slope, meta):
    safe, limit = meta["safe_slope_deg"], meta["max_slope_deg"]
    s = slope.reshape(1000, 2, 1000, 2).max(axis=(1, 3))
    rgba = np.zeros((1000, 1000, 4), np.uint8)
    for low, high, colour in ((10, safe, (242, 179, 61, 110)), (safe, limit, (255, 120, 40, 200)),
                              (limit, 91, (229, 72, 77, 255))):
        rgba[(s > low) & (s <= high)] = colour
    Image.fromarray(rgba).save(WEB / "slope.png")

    inertia = np.array(Image.open(LAYERS / "jezero_thermal_inertia_100m.tif"), dtype=float)
    fine = zoom(inertia, 5, order=1)
    scaled = np.clip((fine - 130) / (400 - 130), 0, 1)
    colour = (colormaps["inferno"](scaled) * 255).astype(np.uint8)
    colour[..., 3] = 170
    Image.fromarray(colour).save(WEB / "thermal.png")
    return float(inertia.min()), float(inertia.max())


def sample(values, count):
    values = np.asarray(values, dtype=float)
    idx = np.linspace(0, len(values) - 1, min(count, len(values))).round().astype(int)
    return [round(float(v), 2) for v in values[idx]]


def stats(values):
    values = np.asarray(values, dtype=float)
    return {"min": round(float(values.min()), 1), "mean": round(float(values.mean()), 1),
            "max": round(float(values.max()), 1)}


def enrich(route, elev, slope, inertia, cell_m):
    cells = np.array(route["cells"])
    r, c = cells[:, 0], cells[:, 1]
    steps = np.hypot(np.diff(r), np.diff(c)) * cell_m
    dist = np.concatenate([[0.0], np.cumsum(steps)])
    e, s, t = elev[r, c], slope[r, c], inertia[r, c]
    out = {k: v for k, v in route.items() if k != "path"}
    out["profile"] = {"dist": sample(dist, PROFILE), "elev": sample(e, PROFILE),
                      "slope": sample(s, PROFILE)}
    out["stats"] = {"slope_deg": stats(s), "elevation_m": stats(e), "thermal_inertia": stats(t)}
    return out


def main():
    WEB.mkdir(parents=True, exist_ok=True)
    ASSETS.mkdir(parents=True, exist_ok=True)
    meta = json.loads((DATA / "meta.json").read_text())
    elev = np.load(DATA / "elevation.npy").astype(float)
    slope = np.load(DATA / "slope.npy").astype(float)
    routes = json.loads((DATA / "routes.json").read_text())
    scenario = json.loads((DATA / "return_scenario.json").read_text())
    validation = json.loads((DATA / "validation.json").read_text())
    n = meta["shape"][0]

    block = n // MESH
    height = elev.reshape(MESH, block, MESH, block).mean(axis=(1, 3))
    h_min, h_max = float(height.min()), float(height.max())
    ((height - h_min) / (h_max - h_min) * 65535).round().astype("<u2").tofile(WEB / "height.bin")
    terrain_textures(elev, meta)
    ti_min, ti_max = overlays(slope, meta)
    inertia = zoom(np.array(Image.open(LAYERS / "jezero_thermal_inertia_100m.tif"), dtype=float),
                   n / 100, order=1)

    photos = arrival_photos()

    def target(target_id, name, why, kind, cell, lonlat, route_list):
        return {"id": target_id, "name": name, "why": why, "kind": kind, "cell": cell,
                "lonlat": lonlat, "photo": photos.get(target_id),
                "routes": [enrich(r, elev, slope, inertia, meta["cell_m"]) for r in route_list]}

    targets = [target("delta_top", "Delta top", "Team-chosen target behind the delta scarp", "team",
                      routes["goal"]["cell"], routes["goal"]["lonlat"], routes["routes"])]
    targets += [target(s["id"], s["name"], s["why"], "perseverance", s["cell"], s["lonlat"],
                       s["routes"]) for s in routes["stops"]]

    mission = {
        "grid": {**meta, "mesh": MESH, "relief": RELIEF, "height_min_m": h_min,
                 "height_max_m": h_max,
                 "thermal_inertia_range": [ti_min, ti_max]},
        "base": {"name": "Octavia E. Butler Landing", **routes["start"]},
        "targets": targets,
        "rover": routes["rover"], "soil": routes["soil"], "crew": routes["crew"],
        "radiation": radiation(),
        "weather": weather(),
        "validation": validation,
        "scenario": {
            "target": "delta_top", "profile": scenario["profile"],
            "planned_cells": scenario["planned"]["cells"],
            "driven_cells": scenario["driven"]["cells"],
            "obstacle_centre": scenario["obstacle"]["centre_cell"],
            "obstacle_radius_m": scenario["scenario"]["obstacle_radius_m"],
            "sensor_range_m": scenario["scenario"]["sensor_range_m"],
            "first_detection_cell": scenario["events"][0]["at_cell"],
            **{k: scenario[k] for k in ("planned_distance_m", "driven_distance_m", "replans",
                                         "repair_total_s", "fresh_plan_at_first_detection_s")},
        },
    }
    (WEB / "mission.json").write_text(json.dumps(mission, separators=(",", ":")) + "\n")
    globe_texture()
    astronaut_photo()
    for p in sorted(list(WEB.iterdir()) + [q for q in ASSETS.rglob("*") if q.is_file()]):
        print(f"{p.stat().st_size / 1024:8.0f} KB  {p.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
