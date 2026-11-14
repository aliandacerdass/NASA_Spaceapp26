"""Build the mission-area elevation and slope grids from the Jezero HiRISE DTM.

Source: USGS "Mars 2020 Terrain Relative Navigation HiRISE DTM Mosaic", a
1.84 GB uncompressed GeoTIFF (1 m/pixel, one row per strip). Instead of
downloading it, every 5th row of our window is read with HTTP range requests
(about 85 MB, cached in data/raw/) and columns are averaged to the same size.

Output: data/processed/elevation.npy (float32 m), slope.npy (float16 deg),
        meta.json, preview.png

Usage: python pipeline/build_grid.py
"""
import json
import math
import struct
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
from scipy.ndimage import gaussian_filter

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data/raw/hirise_5m.npy"
OUT = ROOT / "data/processed"

URL = ("https://planetarymaps.usgs.gov/mosaic/mars2020_trn/HiRISE/"
       "JEZ_hirise_soc_006_DTM_MOLAtopography_DeltaGeoid_1m_Eqc_latTs0_lon0_blend40.tif")
R_MARS = 3396190.0  # the mosaic is equirectangular with lat_ts = 0, 1 m/pixel
X0, Y0 = 4577366.0, 1106618.0  # map coordinates of pixel (0, 0), from the GeoTIFF tags
STRIP_OFFSETS_TAG = 273

# Mission area: 10 x 10 km around the Jezero western delta (degrees).
NORTH_LAT, SOUTH_LAT = 18.554291, 18.385585
WEST_LON, EAST_LON = 77.321150, 77.499014
CELL_M = 5.0
N = 2000
SMOOTH_SIGMA_PX = 1.0  # damps row-sampling noise before taking the gradient

# Rover limits (degrees). Above MAX the cell is impassable.
MAX_SLOPE_DEG = 30.0
SAFE_SLOPE_DEG = 15.0


def read(offset, size):
    req = urllib.request.Request(URL, headers={
        "Range": f"bytes={offset}-{offset + size - 1}",
        "User-Agent": "Mozilla/5.0",  # the server rejects the default Python agent
    })
    for attempt in range(4):
        try:
            return urllib.request.urlopen(req, timeout=60).read()
        except OSError:
            if attempt == 3:
                raise


def strip_offsets_position():
    ifd = struct.unpack("<I", read(4, 4))[0]
    count = struct.unpack("<H", read(ifd, 2))[0]
    entries = read(ifd + 2, count * 12)
    for i in range(count):
        tag, _type, _n, value = struct.unpack("<HHII", entries[i * 12:(i + 1) * 12])
        if tag == STRIP_OFFSETS_TAG:
            return value
    raise SystemExit("strip offsets tag not found")


def fetch_window():
    col0 = math.radians(WEST_LON) * R_MARS - X0
    col1 = math.radians(EAST_LON) * R_MARS - X0
    row0 = Y0 - math.radians(NORTH_LAT) * R_MARS
    row1 = Y0 - math.radians(SOUTH_LAT) * R_MARS

    rows = (row0 + (np.arange(N) + 0.5) * (row1 - row0) / N).astype(int)
    edges = np.round(np.linspace(col0, col1, N + 1)).astype(int)
    first, width = int(edges[0]), int(edges[-1] - edges[0])
    starts, counts = edges[:-1] - first, np.diff(edges)

    table = strip_offsets_position()
    raw = read(table + 4 * int(rows[0]), 4 * int(rows[-1] - rows[0] + 1))
    offsets = np.frombuffer(raw, dtype="<u4")[rows - rows[0]]

    def fetch_row(offset):
        line = np.frombuffer(read(int(offset) + 4 * first, 4 * width), dtype="<f4")
        return np.add.reduceat(line.astype(np.float64), starts) / counts

    with ThreadPoolExecutor(8) as pool:
        grid = np.array(list(pool.map(fetch_row, offsets)), dtype=np.float32)
    if (grid < -1e20).any() or not np.isfinite(grid).all():
        raise SystemExit("window contains nodata cells")
    RAW.parent.mkdir(parents=True, exist_ok=True)
    np.save(RAW, grid)


def main():
    if not RAW.exists():
        print("downloading the HiRISE window (about 85 MB, several minutes)")
        fetch_window()
    elev = np.load(RAW)

    gy, gx = np.gradient(gaussian_filter(elev.astype(float), SMOOTH_SIGMA_PX), CELL_M)
    slope = np.degrees(np.arctan(np.hypot(gx, gy)))

    OUT.mkdir(parents=True, exist_ok=True)
    np.save(OUT / "elevation.npy", elev)
    np.save(OUT / "slope.npy", slope.astype(np.float16))
    meta = {
        "source": "USGS Mars 2020 TRN HiRISE DTM Mosaic, 1 m, resampled to 5 m",
        "shape": [N, N],
        "cell_m": CELL_M,
        "north_lat": NORTH_LAT,
        "south_lat": SOUTH_LAT,
        "west_lon": WEST_LON,
        "east_lon": EAST_LON,
        "elev_min_m": float(elev.min()),
        "elev_max_m": float(elev.max()),
        "max_slope_deg": MAX_SLOPE_DEG,
        "safe_slope_deg": SAFE_SLOPE_DEG,
        "impassable_pct": round(100 * float((slope > MAX_SLOPE_DEG).mean()), 2),
        "above_safe_pct": round(100 * float((slope > SAFE_SLOPE_DEG).mean()), 2),
    }
    (OUT / "meta.json").write_text(json.dumps(meta, indent=2) + "\n")
    print(json.dumps(meta, indent=2))
    preview(elev, slope)


def preview(elev, slope):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.colors import LightSource

    fig, ax = plt.subplots(1, 2, figsize=(14, 7))
    shade = LightSource(315, 45).shade(
        elev, cmap=plt.cm.copper, vert_exag=3, dx=CELL_M, dy=CELL_M, blend_mode="soft")
    ax[0].imshow(shade)
    ax[0].set_title("Elevation (hillshade)")
    ax[1].imshow(slope, cmap="gray_r", vmin=0, vmax=MAX_SLOPE_DEG)
    ax[1].imshow(np.ma.masked_less_equal(slope, SAFE_SLOPE_DEG), cmap="autumn_r",
                 vmin=SAFE_SLOPE_DEG, vmax=MAX_SLOPE_DEG, alpha=0.7)
    ax[1].contourf(slope > MAX_SLOPE_DEG, levels=[0.5, 1], colors=["#00e5ff"])
    ax[1].set_title(f"Slope: orange > {SAFE_SLOPE_DEG:.0f} deg, cyan > {MAX_SLOPE_DEG:.0f} deg (impassable)")
    for a in ax:
        a.axis("off")
    plt.tight_layout()
    plt.savefig(OUT / "preview.png", dpi=80)


if __name__ == "__main__":
    main()
