#!/usr/bin/env python3
"""Georeference NOAA Coast Survey T-sheet T00382 (1852, 'Part of the Coast of California from Point Lobos Southward', 1:10 000)
from control points and warp it onto the territory grids.

Control points (pixel in the 8395 x 14356 NOAA JPG -> geographic):
  1. the 1947 pencil datum note 'NA 1927 Datum 122 31' / 37 45'  (green crosshair) at px (1250, 5510)   [NAD27]
  2. the 1947 pencil datum note '122 30' / 37 42' (green crosshair) at px (2405, 12200)                [NAD27]
  3. 'Round Top' summit ring = Strawberry Hill, px (5846, 3500)   <-> OSM Strawberry Hill nodes (mean)  [WGS84]
  4. summit ring of Grand View Hill, px (6083, 5127)             <-> OSM Grand View Hill node            [WGS84]
Model: 6-parameter affine pixel -> EPSG:32610; RMS and leave-one-out reported.

    python -X utf8 research/cal-academy/scripts/precolonial_georef.py
Outputs in exports/territory/precolonial/ (git-ignored) and data/cal-academy/precolonial/.
"""
import json, os, pathlib, numpy as np, rasterio
from rasterio.transform import Affine
from rasterio.crs import CRS
from rasterio.warp import reproject
from rasterio.enums import Resampling
from PIL import Image
from pyproj import Transformer
Image.MAX_IMAGE_PIXELS = None
ROOT = pathlib.Path(__file__).resolve().parents[3]
SRC = ROOT / 'data' / 'cal-academy' / 'precolonial' / 'noaa_tsheets' / 'T00382-00-1852.jpg'
OUT = ROOT / 'exports' / 'territory' / 'precolonial'; OUT.mkdir(parents=True, exist_ok=True)
TAG = '2026_11_07A'
t27 = Transformer.from_crs(4267, 32610, always_xy=True)
t83 = Transformer.from_crs(4326, 32610, always_xy=True)
GCP = [  # name, px, py, E, N, note
    ('datum1 122d31 37d45 (NAD27)', 1250, 5510, *t27.transform(-(122 + 31 / 60), 37.75)),
    ('datum2 122d30 37d42 (NAD27)', 2405, 12200, *t27.transform(-122.5, 37.70)),
    ('Round Top = Strawberry Hill', 5846, 3500, *t83.transform(-122.47552, 37.76860)),
    ('Grand View Hill', 6083, 5127, *t83.transform(-122.4718262, 37.756326)),
]
def fit(g):
    A = np.array([[p[1], p[2], 1] for p in g], float)
    ex = np.linalg.lstsq(A, np.array([p[3] for p in g]), rcond=None)[0]
    ny = np.linalg.lstsq(A, np.array([p[4] for p in g]), rcond=None)[0]
    return ex, ny
def apply(ex, ny, x, y): return ex[0] * x + ex[1] * y + ex[2], ny[0] * x + ny[1] * y + ny[2]
ex, ny = fit(GCP)
res = []
for n, x, y, E, N in GCP:
    e, nn = apply(ex, ny, x, y); res.append(np.hypot(e - E, nn - N)); print(f'{n}: residual {res[-1]:.1f} m')
rms = float(np.sqrt(np.mean(np.square(res)))); print('affine RMS (4 GCP, 6 params) m:', round(rms, 1))
loo = []
for i in range(len(GCP)):
    e2, n2 = fit([g for j, g in enumerate(GCP) if j != i])
    e, nn = apply(e2, n2, GCP[i][1], GCP[i][2]); loo.append(float(np.hypot(e - GCP[i][3], nn - GCP[i][4])))
print('leave-one-out error m:', [round(v, 1) for v in loo])
aff = Affine(ex[0], ex[1], ex[2], ny[0], ny[1], ny[2])   # pixel (col,row) -> E,N
print('pixel size m', np.hypot(ex[0], ny[0]), np.hypot(ex[1], ny[1]), 'rotation deg', np.degrees(np.arctan2(ny[0], ex[0])))
json.dump({'sheet': 'T00382-00-1852', 'affine_px_to_utm10n': list(aff)[:6], 'gcps': [dict(name=g[0], px=g[1], py=g[2], E=g[3], N=g[4]) for g in GCP],
           'rms_m': rms, 'leave_one_out_m': loo, 'datum_note': 'datum notes are NAD27 (converted with pyproj NAD27->NAD83); hills tied to WGS84/NAD83'},
          open(OUT / f'CALACADEMY_TSHEET_T00382_GEOREF_{TAG}.json', 'w'), indent=1)

CRS32610 = CRS.from_epsg(32610)
def grid(x0, y1, w, h, res): return Affine(res, 0, x0, 0, -res, y1), w, h
GRIDS = {
    'C5': grid(544023, 4183411, 1200, 1200, 5),            # grid C (region)
    'CW5': grid(542523, 4183411, 1500, 2200, 5),           # grid C extended 1500 m west (Ocean Beach) and 1000 m south (Lake Merced)
}
def warp_rgb(arr3, dst_tr, w, h, resampling):
    out = np.zeros((3, h, w), np.uint8)
    for b in range(3):
        reproject(arr3[b], out[b], src_transform=aff, src_crs=CRS32610, dst_transform=dst_tr, dst_crs=CRS32610, resampling=resampling)
    return out
def write(path, arr, tr, nodata=0, desc=''):
    with rasterio.open(path, 'w', driver='GTiff', height=arr.shape[1], width=arr.shape[2], count=arr.shape[0], dtype=arr.dtype, crs=CRS32610, transform=tr,
                       nodata=nodata, compress='deflate', tiled=True, blockxsize=256, blockysize=256) as d:
        d.write(arr); d.update_tags(DESCRIPTION=desc)

if __name__ == '__main__':
    im = np.moveaxis(np.asarray(Image.open(SRC).convert('RGB')), 2, 0).copy(); print('sheet', im.shape)
    # footprint mask: warp a ones band so the paper margin / outside is nodata
    valid = np.ones(im.shape[1:], np.uint8)
    desc = 'US Coast Survey T-sheet T00382 (1852, A.D. Bache Supt., surveyed by A.M. Harrison) georeferenced by control points, RMS %.0f m; NOAA Office of Coast Survey Historical Map & Chart Collection, public domain' % rms
    for key, suffix in (('C5', '5m'), ('CW5', '5m_CW')):
        tr, w, h = GRIDS[key]
        out = warp_rgb(im, tr, w, h, Resampling.average)
        vm = np.zeros((h, w), np.uint8); reproject(valid, vm, src_transform=aff, src_crs=CRS32610, dst_transform=tr, dst_crs=CRS32610, resampling=Resampling.nearest)
        out[:, vm == 0] = 0; out[out == 0] = 1; out[:, vm == 0] = 0
        write(OUT / f'CALACADEMY_TSHEET_1850s_{suffix}_UTM10N_{TAG}.tif', out, tr, 0, desc)
        print('wrote', suffix, 'covered cells', int((vm > 0).sum()))
    # 1 m clip on the park bbox lon -122.5120..-122.4520, lat 37.7635..37.7750 (scan is 0.845 m/px so 1 m is supported)
    x0, y0 = t83.transform(-122.5120, 37.7635); x1, y1 = t83.transform(-122.4520, 37.7750)
    E0, E1 = int(np.floor(min(x0, x1))), int(np.ceil(max(x0, x1))); N0, N1 = int(np.floor(min(y0, y1))), int(np.ceil(max(y0, y1)))
    tr, w, h = grid(E0, N1, E1 - E0, N1 - N0, 1)
    out = warp_rgb(im, tr, w, h, Resampling.cubic)
    vm = np.zeros((h, w), np.uint8); reproject(valid, vm, src_transform=aff, src_crs=CRS32610, dst_transform=tr, dst_crs=CRS32610, resampling=Resampling.nearest)
    out[:, vm == 0] = 0; out[(out == 0) & (vm > 0)[None]] = 1
    write(OUT / f'CALACADEMY_TSHEET_1850s_PARKBBOX_1m_UTM10N_{TAG}.tif', out, tr, 0, desc)
    print('1 m park clip', w, h, 'bounds', E0, N0, E1, N1, 'covered', int((vm > 0).sum()))
