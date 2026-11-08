#!/usr/bin/env python3
"""Turn the game's lidar DSM (assets/site_dsm_rg.png, 0.5 m, game frame) into a 3DGS PLY so the splat pipeline can be
exercised before the Scaniverse scans are in: one Gaussian per DSM cell around the building, coloured like site.js.

    python research/cal-academy/scripts/lidar_to_splat_ply.py            # -> game/assets/splats/lidar_dsm.ply (git-ignored)
    python research/cal-academy/scripts/lidar_to_splat_ply.py --pad 60 --step 1
"""
import argparse, json, pathlib
import numpy as np
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parents[3]; A = ROOT / 'game' / 'assets'
FIELDS = ['x', 'y', 'z', 'nx', 'ny', 'nz', 'f_dc_0', 'f_dc_1', 'f_dc_2', 'opacity', 'scale_0', 'scale_1', 'scale_2', 'rot_0', 'rot_1', 'rot_2', 'rot_3']


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--pad', type=float, default=40, help='metres around the building bbox')
    ap.add_argument('--step', type=int, default=1)
    ap.add_argument('--out', default=str(A / 'splats' / 'lidar_dsm.ply'))
    a = ap.parse_args()
    meta = json.load(open(A / 'site_meta.json'))
    dsm = np.asarray(Image.open(A / 'site_dsm_rg.png').convert('RGB')).astype(np.float64)
    dtm = np.asarray(Image.open(A / 'site_dtm_rg.png').convert('RGB')).astype(np.float64)
    bld = np.asarray(Image.open(A / 'site_bldg_mask.png').convert('L')) > 127
    h = (dsm[..., 0] * 256 + dsm[..., 1]) * meta['z_scale'] + meta['z_base_m'] - meta['ground_m']
    g = (dtm[..., 0] * 256 + dtm[..., 1]) * meta['z_scale'] + meta['z_base_m'] - meta['ground_m']
    H, W = h.shape; res = meta['res_m']
    x0, y0, x1, y1 = meta['bldg_bbox_px']; p = int(a.pad / res)
    j0, j1, i0, i1 = max(0, y0 - p), min(H, y1 + p), max(0, x0 - p), min(W, x1 + p)
    jj, ii = np.mgrid[j0:j1:a.step, i0:i1:a.step]
    X = -meta['width_m'] / 2 + ii * res; Z = -meta['height_m'] / 2 + jj * res; Y = h[jj, ii]
    above = Y - g[jj, ii]; isb = bld[jj, ii]
    # colours as in site.js (sRGB), to SH DC: (c - 0.5) / 0.28209
    cGround, cTree, cRoof, cHigh, cPath = [np.array(v) / 255 for v in ((0x1b, 0x2a, 0x24), (0x3b, 0x6b, 0x45), (0x6e, 0x7a, 0x5a), (0xb8, 0xc2, 0x9a), (0x2b, 0x2f, 0x33))]
    col = np.empty(Y.shape + (3,))
    t = np.clip((Y - 11.45) / 8, 0, 1)[..., None]; col[isb] = (cRoof + (cHigh - cRoof) * t)[isb]
    tr = above > 2.5; t2 = np.clip((above - 3) / 25, 0, 0.8)[..., None]; col[tr & ~isb] = (cTree + (cHigh - cTree) * t2)[tr & ~isb]
    gr = ~tr & ~isb; t3 = (np.clip(above / 1.5, 0, 1) * 0.5)[..., None]; col[gr] = (cGround + (cPath - cGround) * t3)[gr]
    n = Y.size; s = np.log(res * a.step * 0.7)
    # slope-aware: a flat disc on flat cells, rounder on steep ones (trees, facades)
    gy, gx = np.gradient(h[j0:j1:a.step, i0:i1:a.step], res * a.step)
    slope = np.clip(np.hypot(gx, gy), 0, 1)
    sy = np.log(res * a.step * (0.15 + 0.55 * slope))
    dc = (col - 0.5) / 0.28209479177
    rows = np.zeros(n, dtype=[(k, '<f4') for k in FIELDS])
    rows['x'] = X.ravel(); rows['y'] = Y.ravel(); rows['z'] = Z.ravel(); rows['ny'] = 1
    rows['f_dc_0'] = dc[..., 0].ravel(); rows['f_dc_1'] = dc[..., 1].ravel(); rows['f_dc_2'] = dc[..., 2].ravel()
    rows['opacity'] = 4.0  # sigmoid -> 0.98
    rows['scale_0'] = s; rows['scale_1'] = sy.ravel(); rows['scale_2'] = s; rows['rot_0'] = 1
    out = pathlib.Path(a.out); out.parent.mkdir(parents=True, exist_ok=True)
    header = 'ply\nformat binary_little_endian 1.0\nelement vertex %d\n' % n + ''.join('property float %s\n' % k for k in FIELDS) + 'end_header\n'
    with open(out, 'wb') as f:
        f.write(header.encode('ascii')); f.write(rows.tobytes())
    print('wrote', out, n, 'splats', out.stat().st_size // 1024, 'KB; frame = game (identity)')


if __name__ == '__main__':
    main()
