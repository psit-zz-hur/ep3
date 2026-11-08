#!/usr/bin/env python3
"""Elk herd loops for THE TERRITORY, schema ggp-elk-herds/1. Loops are jittered ellipses (1-3 km) on habitat classes 2/3/4 of the pre-colonial raster, off water.
V1: outside the Golden Gate Park outline; V2: anywhere. Seeded (reproducible)."""
import json, pathlib, numpy as np, rasterio
import scipy.ndimage as ndi
from scipy.interpolate import splprep, splev
from shapely.geometry import shape, Point, LineString, Polygon
from shapely.ops import unary_union, transform as shtr
from pyproj import Transformer
ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = ROOT / 'exports' / 'territory' / 'precolonial'; TAG = '2026_11_07A'
with rasterio.open(OUT / f'CALACADEMY_PRECOLONIAL_HABITAT_5m_CW_UTM10N_{TAG}.tif') as d: cls = d.read(1); TR = d.transform
H, W = cls.shape
allowed = np.isin(cls, [2, 3, 4])
wet = np.isin(cls, [7, 8, 0, 1, 6])
dwet = ndi.distance_transform_edt(~wet) * 5
# erode allowed by 30 m so loops keep off the edges
ok_cell = allowed & (dwet > 30)
to10 = Transformer.from_crs(4326, 32610, always_xy=True); to84 = Transformer.from_crs(32610, 4326, always_xy=True)
po = json.load(open(OUT.parent / 'CALACADEMY_PARK_OUTLINE_2026_11_07A.geojson'))
park = unary_union([shtr(lambda x, y, z=None: to10.transform(x, y), shape(f['geometry'])) for f in po['features'] if f['geometry']['type'] in ('Polygon', 'MultiPolygon')])
park_buf = park.buffer(40)
def cell(E, N): return int((TR.f - N) / 5), int((E - TR.c) / 5)
def valid_pt(E, N):
    r, c = cell(E, N)
    return 0 <= r < H and 0 <= c < W and ok_cell[r, c]
def resample(xy, step=15.0):
    seg = np.hypot(*np.diff(xy, axis=0).T); s = np.r_[0, np.cumsum(seg)]; n = max(8, int(s[-1] / step)); t = np.linspace(0, s[-1], n, endpoint=False)
    return np.c_[np.interp(t, s, xy[:, 0]), np.interp(t, s, xy[:, 1])]
def make_loop(rng, E0, N0, a, b, rot):
    th = np.linspace(0, 2 * np.pi, 48, endpoint=False)
    jit = 1 + 0.18 * np.sin(2 * th + rng.uniform(0, 6.28)) + 0.10 * np.sin(3 * th + rng.uniform(0, 6.28))
    x = a * jit * np.cos(th); y = b * jit * np.sin(th)
    X = E0 + x * np.cos(rot) - y * np.sin(rot); Y = N0 + x * np.sin(rot) + y * np.cos(rot)
    pts = np.c_[X, Y]; pts = np.vstack([pts, pts[:1]])
    tck, _ = splprep([pts[:, 0], pts[:, 1]], s=0, per=True)
    u = np.linspace(0, 1, 400); xs, ys = splev(u, tck)
    return resample(np.c_[xs, ys][:-1])
NAMES = {2: 'foredune', 3: 'dune_scrub', 4: 'coastal_prairie'}
def build(version, n_herds, seed, avoid_park):
    rng = np.random.default_rng(seed); herds = []; centres = []; tries = 0
    cand = np.argwhere(ok_cell & (dwet > 80))
    while len(herds) < n_herds and tries < 20000:
        tries += 1
        r, c = cand[rng.integers(len(cand))]; E0 = TR.c + (c + 0.5) * 5; N0 = TR.f - (r + 0.5) * 5
        if any(np.hypot(E0 - e, N0 - n) < 700 for e, n in centres): continue
        if avoid_park and park_buf.distance(Point(E0, N0)) < 150: continue
        a = rng.uniform(140, 330); b = a * rng.uniform(0.45, 0.8); rot = rng.uniform(0, np.pi)
        pts = make_loop(rng, E0, N0, a, b, rot)
        length = float(np.hypot(*np.diff(np.vstack([pts, pts[:1]]), axis=0).T).sum())
        if not (1000 <= length <= 3000): continue
        if not all(valid_pt(x, y) for x, y in pts): continue
        if avoid_park and LineString(np.vstack([pts, pts[:1]])).intersects(park_buf): continue
        ks = [int(cls[cell(x, y)]) for x, y in pts]
        cnt = {k: ks.count(k) for k in (2, 3, 4)}
        top = [NAMES[k] for k in sorted(cnt, key=cnt.get, reverse=True) if cnt[k] > 0][:2]
        ll = [[round(lat, 6), round(lon, 6)] for lon, lat in (to84.transform(x, y) for x, y in pts)]
        ll.append(ll[0])
        i = len(herds) + 1
        herds.append({'id': f'h{i}', 'name': f'{version} herd {i}', 'count': int(rng.integers(6, 21)), 'speed_mps': round(float(rng.uniform(1.0, 1.8)), 2), 'spread_m': int(rng.integers(15, 41)),
                      'loop': True, 'phase': round(float(rng.uniform(0, 1)), 3), 'habitat': top, 'pts': ll, '_len_m': round(length)})
        centres.append((E0, N0))
    return herds
def validate(herds, avoid_park):
    rep = []
    for h in herds:
        P = np.array([to10.transform(lon, lat) for lat, lon in h['pts']])
        ks = [int(cls[cell(x, y)]) for x, y in P]
        gaps = np.hypot(*np.diff(P, axis=0).T)
        bad = [k for k in ks if k not in (2, 3, 4)]
        inpark = int(sum(park.contains(Point(x, y)) for x, y in P)) if avoid_park else None
        rep.append((h['id'], len(P), round(float(gaps.max()), 1), round(h['_len_m']), dict((k, ks.count(k)) for k in set(ks)), len(bad), inpark))
    return rep
for ver, n, seed, avoid in (('v1', 6, 11, True), ('v2', 7, 29, False)):
    herds = build(ver, n, seed, avoid)
    rep = validate(herds, avoid)
    for r in rep: print(ver, r)
    for h in herds: h.pop('_len_m')
    js = {'schema': 'ggp-elk-herds/1', 'source': f'scripts/precolonial_elk.py seed {seed}: jittered ellipses (1-3 km, pts every 15 m) snapped by rejection to habitat classes 2 foredune, 3 dune scrub, 4 coastal prairie of CALACADEMY_PRECOLONIAL_HABITAT_5m_CW_UTM10N_{TAG}.tif, >=30 m from lake/marsh/willow/beach/sea cells; ' + ('V1: kept >=40 m outside the Golden Gate Park outline' if avoid else 'V2: may cross the park (dunes in V2)') + '. Illustrative paths, not documented elk movements.', 'herds': herds}
    (OUT / f'CALACADEMY_ELK_HERDS_{ver}_{TAG}.json').write_text(json.dumps(js, ensure_ascii=False), encoding='utf-8')
    print(ver, 'herds', len(herds), 'animals', sum(h['count'] for h in herds))
