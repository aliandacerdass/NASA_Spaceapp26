"""Sample Curiosity's RAD dose rate over the whole mission (Gale crater).

The PDS archive holds one text file per sol (about 18 MB each). Every file
starts with the first observation of that sol, and its total dose rate in the
plastic E detector (microgray per hour) sits within the first kilobytes. So
only the head of every 15th sol file is read with an HTTP range request:
a few MB in total instead of tens of GB.

Source: MSL RAD RDR archive, PDS Planetary Plasma Interactions node,
        data set MSL-M-RAD-3-RDR-V1.0
Output: data/processed/radiation.json

Usage: python pipeline/fetch_rad.py
"""
import json
import re
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
BASE = "https://pds-ppi.igpp.ucla.edu/data/MSL-M-RAD-3-RDR-V1.0/DATA/"
EVERY = 15
HEAD_BYTES = 24000
MIN_VALID_UGY_H = 2.0  # below this the observation was cut short (one case in the sample)


def get(url, head=None):
    headers = {"User-Agent": "Mozilla/5.0"}
    if head:
        headers["Range"] = f"bytes=0-{head - 1}"
    req = urllib.request.Request(url, headers=headers)
    for attempt in range(4):
        try:
            return urllib.request.urlopen(req, timeout=60).read().decode("latin-1")
        except OSError:
            if attempt == 3:
                raise


def sol_files():
    folders = sorted(set(re.findall(r'href="(SOL_\d+_\d+/)"', get(BASE))))
    files = []
    for folder in folders:
        names = sorted(set(re.findall(r'href="(RAD_RDR_[\d_]+V\d+\.TXT)"', get(BASE + folder))))
        files += [BASE + folder + n for n in names]
    return files


def first_dose(url):
    """(sol, UTC start, microgray per hour in detector E) of a file's first observation."""
    text = get(url, HEAD_BYTES)
    sol = re.search(r"START_SOL=(\d+)", text)
    utc = re.search(r'START_OBS_UTC="([^"]+)"', text)
    dose = re.search(r"\[DOSIMETRY_TOTAL_DOSE_E: 00\]\s+([-\d.eE+]+)", text)
    if not (sol and utc and dose) or float(dose.group(1)) < MIN_VALID_UGY_H:
        return None
    return int(sol.group(1)), utc.group(1), float(dose.group(1))


def main():
    files = sol_files()
    sample = files[::EVERY]
    with ThreadPoolExecutor(8) as pool:
        rows = [r for r in pool.map(first_dose, sample) if r]
    rates = np.array([r[2] for r in rows]) * 24 / 1000  # milligray per day
    out = {
        "source": "MSL RAD RDR, PDS PPI node, MSL-M-RAD-3-RDR-V1.0 (detector E total dose)",
        "place": "Gale crater (Curiosity), not Jezero",
        "sol_files_in_archive": len(files),
        "sampled_observations": len(rows),
        "sampling": f"first observation of every {EVERY}th sol file",
        "sol_range": [rows[0][0], rows[-1][0]],
        "utc_range": [rows[0][1], rows[-1][1]],
        "absorbed_dose_mgy_per_day": {
            "min": round(float(rates.min()), 3),
            "mean": round(float(rates.mean()), 3),
            "median": round(float(np.median(rates)), 3),
            "max": round(float(rates.max()), 3),
        },
        "series": [[sol, round(rate, 3)] for (sol, _, _), rate in zip(rows, rates.tolist())],
    }
    (ROOT / "data/processed/radiation.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps({k: v for k, v in out.items() if k != "series"}, indent=2))


if __name__ == "__main__":
    main()
