#!/usr/bin/env python3
"""Export the game's lidar DSM mesh (the "Lidar site (2023 DSM)" layer) as OBJ + PLY with vertex colours, plus a JSON
frame note, so another session (THE VIEW, Rhino, Blender) can use the same surface.

    python research/cal-academy/scripts/export_lidar_mesh.py                 # whole tile at 0.5 m (1.08 M verts)
    python research/cal-academy/scripts/export_lidar_mesh.py --step 2        # 1 m
    python research/cal-academy/scripts/export_lidar_mesh.py --zup           # Rhino / Blender convention (x, -z, y)

Output: exports/CALACADEMY_LIDAR_DSM_<date>A.obj / .ply / _frame.json (git-ignored).
Frame (default): the game frame, metres, Y up. X = building long axis (east is -X), Z = short axis (+Z north side),
origin = building centre at the main floor = 77.05 m NAVD88 = UTM 10N E 547023.23 N 4180411.34; the frame is rotated
137.5 deg from grid north (see _frame.json for the exact 4x4 to UTM).
"""
import argparse, datetime, json, math, pathlib
import numpy as np
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parents[3]; A = ROOT / 'game' / 'assets'


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--step', type=int, default=1); ap.add_argument('--zup', action='store_true'); ap.add_argument('--out', default=None)
    a = ap.parse_args()
    meta = json.load(open(A / 'site_meta.json'))
    dsm = np.asarray(Image.open(A / 'site_dsm_rg.png').convert('RGB')).astype(np.float64)
    dtm = np.asarray(Image.open(A / 'site_dtm_rg.png').convert('RGB')).astype(np.float64)
    bld = np.asarray(Image.open(A / 'site_bldg_mask.png').convert('L')) > 127
    h = (dsm[..., 0] * 256 + dsm[..., 1]) * meta['z_scale'] + meta['z_base_m'] - meta['ground_m']
    g = (dtm[..., 0] * 256 + dtm[..., 1]) * meta['z_scale'] + meta['z_base_m'] - meta['ground_m']
    H, W = h.shape; res = meta['res_m']; st = a.step
    jj, ii = np.mgrid[0:H:st, 0:W:st]; nj, ni = jj.shape
    X = -meta['width_m'] / 2 + ii * res; Z = -meta['height_m'] / 2 + jj * res; Y = h[jj, ii]
    above = Y - g[jj, ii]; isb = bld[jj, ii]
    cGround, cTree, cRoof, cHigh, cPath = [np.array(v) / 255 for v in ((0x1b, 0x2a, 0x24), (0x3b, 0x6b, 0x45), (0x6e, 0x7a, 0x5a), (0xb8, 0xc2, 0x9a), (0x2b, 0x2f, 0x33))]
    col = np.empty(Y.shape + (3,))
    t = np.clip((Y - 11.45) / 8, 0, 1)[..., None]; col[isb] = (cRoof + (cHigh - cRoof) * t)[isb]
    tr = above > 2.5; t2 = np.clip((above - 3) / 25, 0, 0.8)[..., None]; col[tr & ~isb] = (cTree + (cHigh - cTree) * t2)[tr & ~isb]
    gr = ~tr & ~isb; t3 = (np.clip(above / 1.5, 0, 1) * 0.5)[..., None]; col[gr] = (cGround + (cPath - cGround) * t3)[gr]
    if a.zup: V = np.stack([X.ravel(), -Z.ravel(), Y.ravel()], 1)
    else: V = np.stack([X.ravel(), Y.ravel(), Z.ravel()], 1)
    C = (col.reshape(-1, 3) * 255).astype(np.uint8)
    idx = np.arange(nj * ni).reshape(nj, ni)
    a_ = idx[:-1, :-1].ravel(); b_ = idx[:-1, 1:].ravel(); c_ = idx[1:, :-1].ravel(); d_ = idx[1:, 1:].ravel()
    F = np.concatenate([np.stack([a_, c_, b_], 1), np.stack([b_, c_, d_], 1)])   # same winding as site.js
    tag = datetime.date.today().strftime('%Y_%m_%d') + 'A'
    out = pathlib.Path(a.out) if a.out else ROOT / 'exports' / f'CALACADEMY_LIDAR_DSM_{tag}'
    out.parent.mkdir(parents=True, exist_ok=True)
    # OBJ with vertex colours (x y z r g b, the common extension)
    with open(str(out) + '.obj', 'w') as f:
        f.write(f'# Cal Academy lidar DSM mesh, 2023 USGS 3DEP (public domain), {res * st} m grid, {"Z up (x,-z,y)" if a.zup else "game frame Y up"}; see {out.name}_frame.json\n')
        f.write('o lidar_dsm_2023\n')
        for (x, y, z), (r, g_, b) in zip(V, C / 255): f.write(f'v {x:.3f} {y:.3f} {z:.3f} {r:.4f} {g_:.4f} {b:.4f}\n')
        for tri in F + 1: f.write(f'f {tri[0]} {tri[1]} {tri[2]}\n')
    # binary PLY with colours
    verts = np.zeros(len(V), dtype=[('x', '<f4'), ('y', '<f4'), ('z', '<f4'), ('red', 'u1'), ('green', 'u1'), ('blue', 'u1')])
    verts['x'], verts['y'], verts['z'] = V[:, 0], V[:, 1], V[:, 2]; verts['red'], verts['green'], verts['blue'] = C[:, 0], C[:, 1], C[:, 2]
    faces = np.zeros(len(F), dtype=[('n', 'u1'), ('i', '<i4', (3,))]); faces['n'] = 3; faces['i'] = F
    with open(str(out) + '.ply', 'wb') as f:
        f.write((f'ply\nformat binary_little_endian 1.0\nelement vertex {len(V)}\nproperty float x\nproperty float y\nproperty float z\nproperty uchar red\nproperty uchar green\nproperty uchar blue\n'
                 f'element face {len(F)}\nproperty list uchar int vertex_indices\nend_header\n').encode('ascii')); f.write(verts.tobytes()); f.write(faces.tobytes())
    th = math.radians(meta['rotation_deg_applied']); c, s = math.cos(th), math.sin(th); E0, N0 = meta['centre_utm10n']; g0 = meta['ground_m']
    frame = {
        'source': '2023 USGS 3DEP CA_SanFrancisco_1_B23 lidar (public domain), resampled to a 0.5 m DSM in game/assets/site_dsm_rg.png',
        'grid_m': res * st, 'vertices': int(len(V)), 'faces': int(len(F)), 'units': 'metres',
        'axes': 'Z up: x = game X, y = -game Z, z = game Y' if a.zup else 'Y up (three.js): X = building long axis (east is -X), Y up from the main floor, Z = short axis (+Z = north / concourse side)',
        'origin': {'description': 'building centre at the main floor', 'utm10n_E': E0, 'utm10n_N': N0, 'navd88_m': g0, 'wgs84_lon_lat': meta['centre_wgs84']},
        'rotation_deg_from_grid_north': meta['rotation_deg_applied'],
        'game_to_utm10n': {'E': f'{E0} + {c:.6f}*X + {-s:.6f}*(-Z)', 'N': f'{N0} + {s:.6f}*X + {c:.6f}*(-Z)', 'Z_navd88': f'{g0} + Y',
                           'note': 'with (X, Y, Z) in the game frame; for the --zup file use (x, z, -y) for (X, Y, Z)'},
        'true_north_in_game_xz': [meta['north_vec_xy'][0], -meta['north_vec_xy'][1]],
        'building': {'size_m': meta['bldg_size_m'], 'levels_m': {'aquarium': -7.6, 'main': 0, 'mezzanine': 4.6, 'roof_slab': 9.6, 'deck': 11.45, 'dome_crowns': 19.3}},
    }
    json.dump(frame, open(str(out) + '_frame.json', 'w'), indent=1)
    print('wrote', str(out) + '.obj', str(out) + '.ply', str(out) + '_frame.json', len(V), 'verts', len(F), 'faces')


if __name__ == '__main__':
    main()
