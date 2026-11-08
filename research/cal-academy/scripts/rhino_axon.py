#!/usr/bin/env python3
"""A picture of what is in the Rhino file: plan + axon of the lidar DSM (coloured points), the building massing and the
splat point clouds, drawn from the same sources the exporter uses. For the status board.

    python research/cal-academy/scripts/rhino_axon.py   # -> boards/img/17_rhino_content.png
"""
import json, pathlib, sys
import numpy as np
from PIL import Image
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle

ROOT = pathlib.Path(__file__).resolve().parents[3]; A = ROOT / 'game' / 'assets'; OUT = ROOT / 'boards' / 'img'; OUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from export_rhino_3dm import BOXES, CYLS, BBOX, LV  # noqa: E402


def main():
    meta = json.load(open(A / 'site_meta.json'))
    dsm = np.asarray(Image.open(A / 'site_dsm_rg.png').convert('RGB')).astype(np.float64)
    bld = np.asarray(Image.open(A / 'site_bldg_mask.png').convert('L')) > 127
    h = (dsm[..., 0] * 256 + dsm[..., 1]) * meta['z_scale'] + meta['z_base_m'] - meta['ground_m']
    H, W = h.shape; res = meta['res_m']
    x0, y0, x1, y1 = meta['bldg_bbox_px']; p = int(70 / res); j0, j1, i0, i1 = max(0, y0 - p), min(H, y1 + p), max(0, x0 - p), min(W, x1 + p)
    st = 2; jj, ii = np.mgrid[j0:j1:st, i0:i1:st]
    X = -meta['width_m'] / 2 + ii * res; Z = -meta['height_m'] / 2 + jj * res; Y = h[jj, ii]; isb = bld[jj, ii]
    # rhino frame: x = X, y = -Z, z = Y
    rx, ry, rz = X.ravel(), -Z.ravel(), Y.ravel(); b = isb.ravel()
    fig = plt.figure(figsize=(16, 9), dpi=160, facecolor='white')
    # plan
    ax = fig.add_axes([0.03, 0.08, 0.40, 0.86]); ax.set_aspect('equal'); ax.set_facecolor('white')
    ax.scatter(rx[~b], ry[~b], c=rz[~b], cmap='Greens', s=0.6, vmin=-5, vmax=40, linewidths=0, rasterized=True)
    ax.scatter(rx[b], ry[b], c=rz[b], cmap='Greys', s=0.6, vmin=0, vmax=30, linewidths=0, rasterized=True)
    for n, X0, X1, Z0, Z1, Y0, Y1 in BOXES: ax.add_patch(Rectangle((X0, -Z1), X1 - X0, Z1 - Z0, fill=False, lw=0.6, ec='#000'))
    for n, x, z, rad, yy, kind in CYLS: ax.add_patch(Circle((x, -z), rad, fill=False, lw=0.6, ec='#000'))
    bx0, bx1, bz0, bz1 = BBOX; ax.add_patch(Rectangle((bx0, -bz1), bx1 - bx0, bz1 - bz0, fill=False, lw=1.2, ec='#ff4400'))
    ax.set_xlim(rx.min(), rx.max()); ax.set_ylim(ry.min(), ry.max()); ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values(): s.set_visible(False)
    ax.set_title('PLAN · lidar DSM (points) · massing (black) · envelope (red)', loc='left', fontsize=9, family='monospace')
    # axon (projection: x right, y back at 30 deg, z up)
    ax2 = fig.add_axes([0.46, 0.08, 0.52, 0.86]); ax2.set_aspect('equal'); ax2.set_facecolor('white')
    ca, sa = np.cos(np.radians(30)), np.sin(np.radians(30))
    def proj(x, y, z): return x + y * ca, z + y * sa
    order = np.argsort(ry)[::-1]
    px, py = proj(rx[order], ry[order], rz[order])
    cols = np.where(b[order], 0.0, 1.0)
    ax2.scatter(px[cols == 1], py[cols == 1], c=rz[order][cols == 1], cmap='Greens', s=0.5, vmin=-5, vmax=40, linewidths=0, rasterized=True)
    ax2.scatter(px[cols == 0], py[cols == 0], c=rz[order][cols == 0], cmap='Greys', s=0.5, vmin=0, vmax=30, linewidths=0, rasterized=True)
    def box_edges(X0, X1, Z0, Z1, Y0, Y1, **kw):
        ys = (-Z1, -Z0)
        for yv in ys:
            for zv in (Y0, Y1): a, bb = proj(np.array([X0, X1]), np.array([yv, yv]), np.array([zv, zv])); ax2.plot(a, bb, **kw)
            for xv in (X0, X1): a, bb = proj(np.array([xv, xv]), np.array([yv, yv]), np.array([Y0, Y1])); ax2.plot(a, bb, **kw)
        for xv in (X0, X1):
            for zv in (Y0, Y1): a, bb = proj(np.array([xv, xv]), np.array(ys), np.array([zv, zv])); ax2.plot(a, bb, **kw)
    for n, X0, X1, Z0, Z1, Y0, Y1 in BOXES: box_edges(X0, X1, Z0, Z1, Y0, Y1, color='#000', lw=0.5)
    box_edges(bx0, bx1, bz0, bz1, LV['aquarium'], LV['roofSlab'], color='#ff4400', lw=1.0)
    for n, x, z, rad, yy, kind in CYLS:
        t = np.linspace(0, 2 * np.pi, 80); zc = yy if kind == 'sphere' else yy[1]
        a, bb = proj(x + rad * np.cos(t), -z + rad * np.sin(t), np.full_like(t, zc)); ax2.plot(a, bb, color='#000', lw=0.5)
    ax2.set_xticks([]); ax2.set_yticks([])
    for s in ax2.spines.values(): s.set_visible(False)
    ax2.set_title('AXON · the same, 30 deg · Z up · metres · origin = main floor, building centre', loc='left', fontsize=9, family='monospace')
    fig.text(0.03, 0.025, 'CALACADEMY_SITE_2026_11_07A.3dm · layers: LIDAR 2023 DSM 0.5 m · LIDAR DSM coarse · BUILDING massing · LEVELS · NAMES · SPLATS/lidar_building · SPLATS/lidar_site · POINTCLOUD (B) · FRAME', fontsize=8, family='monospace')
    fig.savefig(OUT / '17_rhino_content.png'); print('wrote', OUT / '17_rhino_content.png')


if __name__ == '__main__':
    main()
