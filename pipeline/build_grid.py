"""Crop the Jezero CTX DEM to the mission area and derive the slope grid.

Input : data/raw/M20_JezeroCrater_CTXDEM_20m.tif  (not in git, see README)
Output: data/processed/elevation.npy, slope.npy, meta.json, preview.png

Usage: python pipeline/build_grid.py
"""
import json
import math
from pathlib import Path

import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data/raw/M20_JezeroCrater_CTXDEM_20m.tif"
OUT = ROOT / "data/processed"

# Mission area: 10 x 10 km around the Jezero western delta.
CENTER_LAT, CENTER_LON = 18.47, 77.41  # degrees, planetocentric / east
SIZE_KM = 10.0
SMOOTH_SIGMA_PX = 1.0  # hides DEM mosaic seams before taking the gradient

# Rover limits (degrees). Above MAX the cell is impassable.
MAX_SLOPE_DEG = 30.0
SAFE_SLOPE_DEG = 15.0

# Projection stored in the GeoTIFF: equirectangular on the Mars 2000 sphere.
R_MARS = 3396190.0
LAT_TS = 18.4663


def main():
    Image.MAX_IMAGE_PIXELS = None
    im = Image.open(SRC)
    tags = im.tag_v2
    px = float(tags[33550][0])
    x0, y0 = tags[33922][3], tags[33922][4]  # map coords of pixel (0, 0)
    nodata = float(str(tags[42113]).strip("\x00 "))

    kx = R_MARS * math.cos(math.radians(LAT_TS))
    col_c = (math.radians(CENTER_LON) * kx - x0) / px
    row_c = (y0 - math.radians(CENTER_LAT) * R_MARS) / px
    n = int(round(SIZE_KM * 1000 / px))
    c0, r0 = int(round(col_c - n / 2)), int(round(row_c - n / 2))

    elev = np.array(im.crop((c0, r0, c0 + n, r0 + n)), dtype=np.float32)
    if (elev == np.float32(nodata)).any():
        raise SystemExit("mission area contains nodata cells; move the centre")

    smooth = gaussian_filter(elev, SMOOTH_SIGMA_PX)
    gy, gx = np.gradient(smooth, px)
    slope = np.degrees(np.arctan(np.hypot(gx, gy))).astype(np.float32)

    OUT.mkdir(parents=True, exist_ok=True)
    np.save(OUT / "elevation.npy", elev)
    np.save(OUT / "slope.npy", slope)
    meta = {
        "source": SRC.name,
        "shape": [n, n],
        "cell_m": px,
        "north_lat": math.degrees((y0 - r0 * px) / R_MARS),
        "south_lat": math.degrees((y0 - (r0 + n) * px) / R_MARS),
        "west_lon": math.degrees((x0 + c0 * px) / kx),
        "east_lon": math.degrees((x0 + (c0 + n) * px) / kx),
        "elev_min_m": float(elev.min()),
        "elev_max_m": float(elev.max()),
        "max_slope_deg": MAX_SLOPE_DEG,
        "safe_slope_deg": SAFE_SLOPE_DEG,
        "impassable_pct": round(100 * float((slope > MAX_SLOPE_DEG).mean()), 2),
        "above_safe_pct": round(100 * float((slope > SAFE_SLOPE_DEG).mean()), 2),
    }
    (OUT / "meta.json").write_text(json.dumps(meta, indent=2) + "\n")
    print(json.dumps(meta, indent=2))
    preview(elev, slope, px)


def preview(elev, slope, px):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.colors import LightSource

    fig, ax = plt.subplots(1, 2, figsize=(14, 7))
    shade = LightSource(315, 45).shade(
        elev, cmap=plt.cm.copper, vert_exag=3, dx=px, dy=px, blend_mode="soft")
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
