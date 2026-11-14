"""Convert the team's rover CAD model (STEP) into a mesh the web interface loads.

Input : data/raw/rover.step   (the team's own design, not in git)
Output: web/assets/rover.bin  little-endian: uint32 vertex count, uint32 index count,
                              float32 xyz per vertex (metres), uint32 indices,
                              uint8 rgb per vertex
        The CAD file has no materials, so parts are coloured by where they sit:
        wheels dark, the chassis light, arms and masts metal, sensor heads accented.
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

# Chassis box in CAD coordinates (317 x 675 x 150 mm, from the team's dimension table).
CHASSIS_HALF_WIDTH = 0.165
CHASSIS_Y = (-0.335, 0.365)
CHASSIS_Z = (0.225, 0.46)
WHEEL_TOP = 0.135
CHASSIS, WHEEL, METAL, ACCENT = (232, 224, 208), (38, 40, 48), (142, 134, 124), (210, 112, 63)


def main():
    with tempfile.TemporaryDirectory() as tmp:
        glb = str(Path(tmp) / "rover.glb")
        cascadio.step_to_glb(str(SRC), glb, 0.3, 0.5)
        mesh = trimesh.load(glb).to_geometry()
    # Colour each triangle by where its centre sits (CAD axes, metres from the lowest point).
    centre = mesh.triangles_center - mesh.vertices.min(axis=0)
    x_mid = (mesh.vertices[:, 0].max() - mesh.vertices[:, 0].min()) / 2
    y = mesh.triangles_center[:, 1]
    in_chassis = ((np.abs(centre[:, 0] - x_mid) < CHASSIS_HALF_WIDTH) & (y > CHASSIS_Y[0]) & (y < CHASSIS_Y[1])
                  & (centre[:, 2] > CHASSIS_Z[0]) & (centre[:, 2] < CHASSIS_Z[1]))
    face_rgb = np.tile(np.array(METAL, dtype=np.uint8), (len(mesh.faces), 1))
    face_rgb[centre[:, 2] < WHEEL_TOP] = WHEEL
    face_rgb[centre[:, 2] > CHASSIS_Z[1] + 0.1] = ACCENT
    face_rgb[in_chassis] = CHASSIS
    rgb = np.zeros((len(mesh.vertices), 3), dtype=np.uint8)
    rgb[mesh.faces.ravel()] = np.repeat(face_rgb, 3, axis=0)
    v = np.asarray(mesh.vertices, dtype=np.float64)
    # CAD axes: x across, y along (camera arm at -y), z up. Web axes: y up, front at +z.
    xyz = np.column_stack([v[:, 0] - (v[:, 0].min() + v[:, 0].max()) / 2,
                           v[:, 2] - v[:, 2].min(),
                           -(v[:, 1] - (v[:, 1].min() + v[:, 1].max()) / 2)]).astype("<f4")
    faces = np.asarray(mesh.faces, dtype="<u4")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_bytes(struct.pack("<II", len(xyz), faces.size) + xyz.tobytes() + faces.tobytes()
                    + rgb.tobytes())

    size = xyz.max(axis=0) - xyz.min(axis=0)
    print(f"{OUT.name}: {len(xyz)} vertices, {len(faces)} triangles, {OUT.stat().st_size / 1e6:.1f} MB")
    print(f"width {size[0]:.3f} m, height {size[1]:.3f} m, length {size[2]:.3f} m")


if __name__ == "__main__":
    main()
