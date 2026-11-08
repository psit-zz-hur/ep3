#!/usr/bin/env python3
"""Clip the raw 2023 USGS lidar tile(s) to the site and write them in the GAME frame as a binary PLY (xyz, rgb,
classification), so the real point cloud (90 pts/m2) sits exactly on the DSM mesh, the massing and the splats.

    python research/cal-academy/scripts/lidar_laz_to_game.py                    # all data/cal-academy/lidar2023/*.laz
    python research/cal-academy/scripts/lidar_laz_to_game.py --pad 120 --max 2000000

Output: data/cal-academy/lidar2023/<tile>_game.ply (git-ignored). export_rhino_3dm.py picks these up as POINTCLOUD layers.
Frame chain: tile CRS (read from the LAZ header; EPSG:7131 SF CS13 US ft, or 3857 for EPT nodes) -> EPSG:26910 UTM 10N m
-> game (site_meta.json: rotation about the centre, ground 77.05 m). Heights: NAVD88 metres assumed (USGS 3DEP standard).
"""
import argparse, json, math, pathlib, sys
import numpy as np
import laspy
from pyproj import CRS, Transformer

ROOT = pathlib.Path(__file__).resolve().parents[3]; A = ROOT / 'game' / 'assets'
CLASS_RGB = {1: (150, 150, 150), 2: (120, 100, 70), 3: (90, 150, 80), 4: (70, 140, 70), 5: (40, 120, 50), 6: (200, 90, 60), 7: (255, 0, 255), 9: (60, 120, 200), 17: (200, 200, 120), 18: (255, 0, 255)}


def utm_to_game(meta):
    th = math.radians(meta['rotation_deg_applied']); c, s = math.cos(th), math.sin(th); E0, N0 = meta['centre_utm10n']; g0 = meta['ground_m']
    def f(E, N, Z):
        dE, dN = E - E0, N - N0
        return c * dE - s * dN, Z - g0, -(s * dE + c * dN)   # X, Y(up), Z
    return f


DT = [('x', '<f4'), ('y', '<f4'), ('z', '<f4'), ('red', 'u1'), ('green', 'u1'), ('blue', 'u1'), ('classification', 'u1')]


def write_ply(out, rows):
    header = ('ply\nformat binary_little_endian 1.0\ncomment 2023 USGS 3DEP CA_SanFrancisco_1_B23, game frame (see site_meta.json)\nelement vertex %d\n' % len(rows)
              + 'property float x\nproperty float y\nproperty float z\nproperty uchar red\nproperty uchar green\nproperty uchar blue\nproperty uchar classification\nend_header\n')
    with open(out, 'wb') as fo: fo.write(header.encode('ascii')); fo.write(rows.tobytes())
    print('wrote', out, len(rows), 'pts', out.stat().st_size // 1024 // 1024, 'MB')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('files', nargs='*'); ap.add_argument('--pad', type=float, default=100, help='metres around the building bbox (game frame)')
    ap.add_argument('--max', type=int, default=1500000); ap.add_argument('--crs', default=None, help='override the tile CRS, e.g. EPSG:7131')
    ap.add_argument('--drop-noise', action='store_true', default=True)
    ap.add_argument('--merge-out', default=None, help='write ONE ply from all inputs (EPT nodes) instead of one per file')
    a = ap.parse_args()
    meta = json.load(open(A / 'site_meta.json')); to_game = utm_to_game(meta)
    bw, bd = meta['bldg_size_m']; X0, X1, Z0, Z1 = -bw / 2 - a.pad, bw / 2 + a.pad, -bd / 2 - a.pad, bd / 2 + a.pad
    files = []
    for f in a.files:
        f = pathlib.Path(f); files += sorted(f.glob('*.laz')) if f.is_dir() else [f]
    files = files or sorted((ROOT / 'data' / 'cal-academy' / 'lidar2023').glob('*.laz'))
    files = [f for f in files if not f.name.endswith('_game.ply')]
    if not files: sys.exit('no .laz in data/cal-academy/lidar2023 (run laptop-bootstrap.sh)')
    merged = []
    for f in files:
        try:
            las = laspy.read(str(f))
        except Exception as e:
            print('skip', f.name, e, file=sys.stderr); continue
        crs = None
        if a.crs: crs = CRS.from_user_input(a.crs)
        else:
            try: crs = las.header.parse_crs()
            except Exception: crs = None
        if crs is None: print('no CRS in', f.name, '- pass --crs', file=sys.stderr); continue
        tr = Transformer.from_crs(crs, CRS.from_epsg(26910), always_xy=True)
        x, y, z = np.asarray(las.x), np.asarray(las.y), np.asarray(las.z)
        # vertical unit: if the CRS is in US survey feet, 3DEP delivers Z in the same unit
        unit = crs.axis_info[0].unit_name.lower() if crs.axis_info else 'metre'
        zf = 0.3048006096012192 if 'foot' in unit or 'feet' in unit else 1.0
        E, N = tr.transform(x, y); Z = z * zf
        X, Y, Zg = to_game(E, N, Z)
        keep = (X > X0) & (X < X1) & (Zg > Z0) & (Zg < Z1)
        cls = np.asarray(las.classification)
        if a.drop_noise: keep &= ~np.isin(cls, (7, 18))
        idx = np.nonzero(keep)[0]
        print(f.name, 'crs', crs.to_epsg(), 'unit', unit, 'points in clip', len(idx), 'of', len(x), file=sys.stderr)
        if len(idx) == 0: continue
        if len(idx) > a.max and not a.merge_out: idx = np.random.default_rng(0).choice(idx, a.max, replace=False)
        if 'red' in las.point_format.dimension_names:
            r, g, b = (np.asarray(las.red)[idx] >> 8), (np.asarray(las.green)[idx] >> 8), (np.asarray(las.blue)[idx] >> 8)
        else:
            lut = np.array([CLASS_RGB.get(i, (160, 160, 160)) for i in range(256)], np.uint8); c = lut[cls[idx]]; r, g, b = c[:, 0], c[:, 1], c[:, 2]
        rows = np.zeros(len(idx), dtype=DT)
        rows['x'] = X[idx]; rows['y'] = Y[idx]; rows['z'] = Zg[idx]; rows['red'] = r; rows['green'] = g; rows['blue'] = b; rows['classification'] = cls[idx]
        if a.merge_out: merged.append(rows); continue
        write_ply(f.with_name(f.stem.replace('.copc', '') + '_game.ply'), rows)
    if a.merge_out and merged:
        allrows = np.concatenate(merged)
        if len(allrows) > a.max: allrows = allrows[np.random.default_rng(0).choice(len(allrows), a.max, replace=False)]
        write_ply(pathlib.Path(a.merge_out), allrows)


if __name__ == '__main__':
    main()
