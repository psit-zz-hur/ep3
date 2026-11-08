#!/usr/bin/env python3
"""Proof image: left the habitat raster (naturalistic palette) with park outline + today's shoreline, right the T-sheet clip. -> boards/img/23_precolonial_habitat.png"""
import csv, json, pathlib, numpy as np, rasterio
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch
from pyproj import Transformer
ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = ROOT / 'exports' / 'territory'; PRE = OUT / 'precolonial'; TAG = '2026_11_07A'
leg = list(csv.DictReader(open(PRE / f'CALACADEMY_PRECOLONIAL_HABITAT_LEGEND_{TAG}.csv', encoding='utf8')))
cmap = ListedColormap([r['colour_hex'] for r in leg])
with rasterio.open(PRE / f'CALACADEMY_PRECOLONIAL_HABITAT_5m_CW_UTM10N_{TAG}.tif') as d: cls = d.read(1); b = d.bounds
with rasterio.open(PRE / f'CALACADEMY_TSHEET_1850s_5m_CW_UTM10N_{TAG}.tif') as d: ts = np.moveaxis(d.read(), 0, 2); tm = d.read(1) == 0
ext = (b.left, b.right, b.bottom, b.top)
t = Transformer.from_crs(4326, 32610, always_xy=True)
fig, ax = plt.subplots(1, 2, figsize=(16, 12.2), dpi=110, gridspec_kw={'wspace': 0.03})
ax[0].imshow(cls, cmap=cmap, vmin=0, vmax=10, interpolation='nearest', extent=ext)
# shoreline = boundary of class 0 connected sea
import scipy.ndimage as ndi
sea = cls == 0
ax[0].contour(np.linspace(b.left + 2.5, b.right - 2.5, cls.shape[1]), np.linspace(b.top - 2.5, b.bottom + 2.5, cls.shape[0]), sea.astype(float), levels=[0.5], colors=['#12354f'], linewidths=0.8)
po = json.load(open(OUT / 'CALACADEMY_PARK_OUTLINE_2026_11_07A.geojson'))
def rings(g):
    if g['type'] == 'Polygon': return g['coordinates']
    if g['type'] == 'MultiPolygon': return [r for p in g['coordinates'] for r in p]
    return []
for f in po['features']:
    for r in rings(f['geometry']):
        xy = np.array([t.transform(*p[:2]) for p in r]); ax[0].plot(xy[:, 0], xy[:, 1], color='#b00020', lw=1.4)
ax[0].set_title('Habitat before the city (1852 sheet symbols + DTM rules)' + chr(10) + 'red = Golden Gate Park outline, dark blue = shoreline today', fontsize=9)
ax[0].legend(handles=[Patch(fc=r['colour_hex'], ec='#555', label=f"{r['code']} {r['class']}") for r in leg if int(r['cells_CW']) > 0], loc='lower right', fontsize=7.5, framealpha=0.92)
shown = ts.copy(); shown[tm] = 255
ax[1].imshow(shown, extent=ext)
ax[1].set_title('US Coast Survey T-sheet T00382, 1852, 1:10 000 (public domain)' + chr(10) + 'georeferenced from 1947 NAD27 datum notes + 2 hill summits', fontsize=9)
for a in ax: a.set_xlim(ext[0], ext[1]); a.set_ylim(ext[2], ext[3]); a.set_xticks([]); a.set_yticks([])
# 1 km scale bar on left
x0, y0 = ext[0] + 200, ext[2] + 200; ax[0].plot([x0, x0 + 1000], [y0, y0], 'k', lw=3); ax[0].text(x0 + 500, y0 + 60, '1 km', ha='center', fontsize=8)
fig.savefig(ROOT / 'boards' / 'img' / '23_precolonial_habitat.png', bbox_inches='tight', facecolor='white'); print('ok')
