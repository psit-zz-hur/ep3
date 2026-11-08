#!/usr/bin/env python3
"""Fetch the 2023 USGS 3DEP point cloud for the Academy site straight from the public EPT on S3 (no throttling, unlike
the rockyweb LAZ tiles), then write it in the game frame via lidar_laz_to_game.py.

    python research/cal-academy/scripts/lidar_ept_site.py              # building + 100 m, all depths
    python research/cal-academy/scripts/lidar_ept_site.py --pad 160 --threads 12

Nodes land in data/cal-academy/lidar2023/ept_nodes/<key>.laz (EPSG:3857, LAZ 1.4), the merged clip in
data/cal-academy/lidar2023/ept_site_game.ply (POINTCLOUD layer of the Rhino export).
"""
import argparse, concurrent.futures as cf, json, math, pathlib, subprocess, sys
import requests
from pyproj import Transformer

ROOT = pathlib.Path(__file__).resolve().parents[3]; A = ROOT / 'game' / 'assets'
BASE = 'https://s3-us-west-2.amazonaws.com/usgs-lidar-public/CA_SanFrancisco_1_B23'
D = ROOT / 'data' / 'cal-academy' / 'lidar2023'; N = D / 'ept_nodes'


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--pad', type=float, default=100); ap.add_argument('--threads', type=int, default=10); ap.add_argument('--max', type=int, default=1500000)
    a = ap.parse_args(); N.mkdir(parents=True, exist_ok=True)
    meta = json.load(open(A / 'site_meta.json'))
    # site bbox: game-frame square around the building -> UTM corners -> 3857
    th = math.radians(meta['rotation_deg_applied']); c, s = math.cos(th), math.sin(th); E0, N0 = meta['centre_utm10n']; bw, bd = meta['bldg_size_m']
    hx, hz = bw / 2 + a.pad, bd / 2 + a.pad
    tr = Transformer.from_crs('EPSG:26910', 'EPSG:3857', always_xy=True)
    xs, ys = [], []
    for X, Z in ((-hx, -hz), (hx, -hz), (hx, hz), (-hx, hz)):
        yup = -Z; E = E0 + c * X + s * yup; Nn = N0 - s * X + c * yup   # inverse of the rotation in splats.js / site_meta
        x, y = tr.transform(E, Nn); xs.append(x); ys.append(y)
    X0, X1, Y0, Y1 = min(xs), max(xs), min(ys), max(ys)
    print('clip 3857', round(X0), round(X1), round(Y0), round(Y1), file=sys.stderr)
    ept = requests.get(f'{BASE}/ept.json', timeout=60).json(); b = ept['bounds']; size = b[3] - b[0]
    def node_bounds(key):
        d, x, y, z = map(int, key.split('-')); st = size / 2 ** d
        return (b[0] + x * st, b[0] + (x + 1) * st, b[1] + y * st, b[1] + (y + 1) * st)
    def inter(key):
        x0, x1, y0, y1 = node_bounds(key); return not (x1 < X0 or x0 > X1 or y1 < Y0 or y0 > Y1)
    hier = {}
    def walk(hkey):
        h = requests.get(f'{BASE}/ept-hierarchy/{hkey}.json', timeout=60).json()
        for k, v in h.items():
            if not inter(k): continue
            if v == -1: walk(k)
            elif v > 0: hier[k] = v
    walk('0-0-0-0'); print('nodes', len(hier), 'points', sum(hier.values()), file=sys.stderr)
    def dl(k):
        fn = N / f'{k}.laz'
        if fn.exists() and fn.stat().st_size > 0: return k, 'cached'
        r = requests.get(f'{BASE}/ept-data/{k}.laz', timeout=300)
        if r.status_code != 200: return k, r.status_code
        fn.write_bytes(r.content); return k, 'ok'
    with cf.ThreadPoolExecutor(a.threads) as ex: res = list(ex.map(dl, hier.keys()))
    bad = [k for k, r in res if r not in ('cached', 'ok')]; print('downloaded', len(res) - len(bad), 'failed', len(bad), file=sys.stderr)
    # merge + transform into the game frame (one PLY)
    files = [str(N / f'{k}.laz') for k in hier if (N / f'{k}.laz').exists()]
    cmd = [sys.executable, '-X', 'utf8', str(pathlib.Path(__file__).with_name('lidar_laz_to_game.py')), '--crs', 'EPSG:3857', '--pad', str(a.pad), '--max', str(a.max), '--merge-out', str(D / 'ept_site_game.ply')] + files
    subprocess.run(cmd, check=True)


if __name__ == '__main__':
    main()
