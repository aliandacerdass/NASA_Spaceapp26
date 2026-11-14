"""Export the mission-area terrain for the 3D map: GeoTIFF, basemap, info.

Input : data/processed/elevation.npy, meta.json  (pipeline/build_grid.py)
Output: data/export/jezero_dem_5m.tif        Float32 GeoTIFF, metres
        data/export/jezero_10km_basemap.png  CTX image on the same grid
        data/export/terrain_info.txt

The basemap is read from the USGS "Mars 2020 Science Investigation CTX
Orthomosaic" (5 m/pixel, 8-bit, uncompressed) with HTTP range requests, so
only our window (about 4 MB) is downloaded.

Usage: python pipeline/export_terrain.py
"""
import json
import math
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
from PIL import Image, TiffImagePlugin

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data/processed"
OUT = ROOT / "data/export"

R_MARS = 3396190.0
LAT_TS = 18.4663  # equirectangular standard parallel: cells are square in metres
KX = R_MARS * math.cos(math.radians(LAT_TS))

ORTHO_URL = ("https://asc-pds-services.s3.us-west-2.amazonaws.com/mosaic/mars2020_trn/CTX/"
             "ScienceInvestigationMaps_JPL/M20_JezeroCrater_CTXortho_mosaic_5m.tif")
# From the orthomosaic GeoTIFF tags: one row per strip, rows stored back to back.
ORTHO_FIRST_STRIP, ORTHO_WIDTH = 122036, 17766
ORTHO_X0, ORTHO_Y0 = 4329192.10812596, 1143347.424174998
ORTHO_SX, ORTHO_SY = 5.002064681102627, 5.002262971613293

# GeoKey directory of the USGS Jezero CTX products (equirectangular, Mars 2000 sphere).
GEO_KEYS = (1, 1, 0, 20, 1024, 0, 1, 1, 1025, 0, 1, 1, 1026, 34737, 25, 0, 2048, 0, 1, 32767,
            2049, 34737, 117, 25, 2050, 0, 1, 32767, 2054, 0, 1, 9102, 2056, 0, 1, 32767,
            2057, 34736, 1, 5, 2058, 34736, 1, 6, 2061, 34736, 1, 7, 3072, 0, 1, 32767,
            3074, 0, 1, 32767, 3075, 0, 1, 17, 3076, 0, 1, 9001, 3078, 34736, 1, 2,
            3082, 34736, 1, 3, 3083, 34736, 1, 4, 3088, 34736, 1, 1, 3089, 34736, 1, 0)
GEO_DOUBLES = (0.0, 0.0, LAT_TS, 0.0, 0.0, R_MARS, R_MARS, 0.0)
GEO_ASCII = ("Jezero_Crater_Projection|GCS Name = GCS_Mars_2000_Sphere|Datum = Mars_2000_(Sphere)|"
             "Ellipsoid = Mars_2000_Sphere|Primem = Reference_Meridian||")


def write_geotiff(elev, meta):
    x0 = KX * math.radians(meta["west_lon"])
    y0 = R_MARS * math.radians(meta["north_lat"])
    ifd = TiffImagePlugin.ImageFileDirectory_v2()
    for tag, kind, value in (
        (33550, 12, (meta["cell_m"], meta["cell_m"], 0.0)),
        (33922, 12, (0.0, 0.0, 0.0, x0, y0, 0.0)),
        (34735, 3, GEO_KEYS),
        (34736, 12, GEO_DOUBLES),
        (34737, 2, GEO_ASCII),
    ):
        ifd.tagtype[tag] = kind
        ifd[tag] = value
    Image.fromarray(elev.astype(np.float32)).save(OUT / "jezero_dem_5m.tif", tiffinfo=ifd)
    return x0, y0


def write_basemap(meta):
    n_rows, n_cols = meta["shape"]
    lats = meta["north_lat"] - (np.arange(n_rows) + 0.5) / n_rows * (meta["north_lat"] - meta["south_lat"])
    lons = meta["west_lon"] + (np.arange(n_cols) + 0.5) / n_cols * (meta["east_lon"] - meta["west_lon"])
    rows = ((ORTHO_Y0 - R_MARS * np.radians(lats)) / ORTHO_SY).astype(int)
    cols = ((KX * np.radians(lons) - ORTHO_X0) / ORTHO_SX).astype(int)
    first, width = int(cols[0]), int(cols[-1] - cols[0] + 1)

    def fetch_row(row):
        start = ORTHO_FIRST_STRIP + int(row) * ORTHO_WIDTH + first
        req = urllib.request.Request(ORTHO_URL, headers={
            "Range": f"bytes={start}-{start + width - 1}", "User-Agent": "Mozilla/5.0"})
        for attempt in range(6):
            try:
                data = urllib.request.urlopen(req, timeout=60).read()
                return np.frombuffer(data, dtype=np.uint8)[cols - first]
            except OSError:
                if attempt == 5:
                    raise
                time.sleep(1 + attempt)

    with ThreadPoolExecutor(8) as pool:
        image = np.array(list(pool.map(fetch_row, rows)), dtype=np.uint8)
    Image.fromarray(image).save(OUT / "jezero_10km_basemap.png")


def main():
    meta = json.loads((DATA / "meta.json").read_text())
    elev = np.load(DATA / "elevation.npy")
    OUT.mkdir(parents=True, exist_ok=True)
    x0, y0 = write_geotiff(elev, meta)
    write_basemap(meta)
    n_rows, n_cols = meta["shape"]
    (OUT / "terrain_info.txt").write_text(f"""Jezero mission area terrain (10 x 10 km)

Files
  jezero_dem_5m.tif        Float32 GeoTIFF, elevation in metres (MOLA-referenced)
  jezero_10km_basemap.png  8-bit grayscale CTX image on exactly the same grid

Grid
  rows x columns : {n_rows} x {n_cols}
  cell size      : {meta["cell_m"]} m
  first row      : north; first column: west
  nodata         : none (every cell is valid)
  elevation      : {meta["elev_min_m"]:.1f} m to {meta["elev_max_m"]:.1f} m

Bounds (degrees, planetocentric latitude, east longitude)
  north {meta["north_lat"]}   south {meta["south_lat"]}
  west  {meta["west_lon"]}   east  {meta["east_lon"]}

Coordinate system
  Equirectangular, Mars 2000 sphere (radius {R_MARS:.0f} m), standard parallel {LAT_TS}
  upper-left corner: x = {x0:.2f} m, y = {y0:.2f} m

Sources
  Elevation: USGS Astrogeology, Mars 2020 Terrain Relative Navigation HiRISE DTM
             Mosaic (1 m/pixel), resampled to 5 m. https://doi.org/10.5066/P9REJ9JN
  Image    : USGS Astrogeology, Mars 2020 Science Investigation CTX Orthomosaic
             (5 m/pixel), public domain.
""")
    print("wrote", sorted(p.name for p in OUT.iterdir()))


if __name__ == "__main__":
    main()
