"""Convert the team's rover CAD model (STEP) into a mesh the web interface loads.

Input : data/raw/rover.step   (the team's own design, not in git)
Output: web/assets/rover.bin  little-endian: uint32 vertex count, uint32 index count,
                              float32 xyz per vertex (metres), uint32 indices
        The mesh is centred on its footprint, wheels on y = 0, y up, front at +z.

Needs: pip install cascadio trimesh

Usage: python pipeline/export_rover.py
"""
import struct
import tempfile
from pathlib import Path

import cascadio
import numpy as np
import trimesh

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data/raw/rover.step"
OUT = ROOT / "web/assets/rover.bin"


def main():
    with tempfile.TemporaryDirectory() as tmp:
        glb = str(Path(tmp) / "rover.glb")
        cascadio.step_to_glb(str(SRC), glb, 0.3, 0.5)
        mesh = trimesh.load(glb).to_geometry()
    v = np.asarray(mesh.vertices, dtype=np.float64)
    # CAD axes: x across, y along (camera arm at -y), z up. Web axes: y up, front at +z.
    xyz = np.column_stack([v[:, 0] - (v[:, 0].min() + v[:, 0].max()) / 2,
                           v[:, 2] - v[:, 2].min(),
                           -(v[:, 1] - (v[:, 1].min() + v[:, 1].max()) / 2)]).astype("<f4")
    faces = np.asarray(mesh.faces, dtype="<u4")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_bytes(struct.pack("<II", len(xyz), faces.size) + xyz.tobytes() + faces.tobytes())
    size = xyz.max(axis=0) - xyz.min(axis=0)
    print(f"{OUT.name}: {len(xyz)} vertices, {len(faces)} triangles, {OUT.stat().st_size / 1e6:.1f} MB")
    print(f"width {size[0]:.3f} m, height {size[1]:.3f} m, length {size[2]:.3f} m")


if __name__ == "__main__":
    main()
