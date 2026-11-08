#!/usr/bin/env python3
"""THE TERRITORY inputs for the Golden Gate Park quadrant around the California Academy of Sciences.
All outputs EPSG:32610, north-up, float32 m NAVD88 (heights), NoData -9999. Rerunnable: downloads are skipped when on disk.

    python -X utf8 research/cal-academy/scripts/territory_rasters.py [core|region|naip|water|labels|all]

Outputs in exports/territory/ (git-ignored).
"""
import concurrent.futures as cf, json, pathlib, sys, time
import numpy as np, requests, laspy, rasterio
from rasterio.transform import from_origin
from rasterio.crs import CRS
from rasterio.enums import Resampling
from rasterio.warp import reproject
from pyproj import Transformer
from scipy import ndimage

def _get(url, timeout=60, tries=6):
    for i in range(tries):
        try: return requests.get(url, timeout=timeout)
        except requests.exceptions.RequestException: time.sleep(2 * (i + 1))
    raise RuntimeError('giving up ' + url)


ROOT = pathlib.Path(__file__).resolve().parents[3]
BASE = 'https://s3-us-west-2.amazonaws.com/usgs-lidar-public/CA_SanFrancisco_1_B23'
D = ROOT / 'data' / 'cal-academy'; N = D / 'lidar2023' / 'ept_nodes'; DEMD = D / 'dem'
OUT = ROOT / 'exports' / 'territory'; OUT.mkdir(parents=True, exist_ok=True)
TAG = '2026_11_07A'
CRS32610 = CRS.from_epsg(32610)
ND = -9999.0
# core grid (1 m), snapped outward from the lon/lat bbox
CORE = dict(x0=546140, y1=4180880, w=1780, h=900)
# region grid (5 m)
REG = dict(x0=544023, y1=4183411, w=1200, h=1200, res=5)   # 6000 m / 5 m (E 544023..550023, N 4177411..4183411)
BB_LL = (-122.4760, 37.7660, -122.4560, 37.7740)
WATER_BB = (-122.511, 37.742, -122.443, 37.796)


def core_transform(): return from_origin(CORE['x0'], CORE['y1'], 1, 1)
def reg_transform(): return from_origin(REG['x0'], REG['y1'], REG['res'], REG['res'])


# ---------- EPT (hierarchy walk + download, copied from lidar_ept_site.py) ----------
def ept_nodes(X0, X1, Y0, Y1):
    ept = _get(f'{BASE}/ept.json').json(); b = ept['bounds']; size = b[3] - b[0]
    def inter(key):
        d, x, y, z = map(int, key.split('-')); st = size / 2 ** d
        x0, x1, y0, y1 = b[0] + x * st, b[0] + (x + 1) * st, b[1] + y * st, b[1] + (y + 1) * st
        return not (x1 < X0 or x0 > X1 or y1 < Y0 or y0 > Y1)
    hier = {}
    def walk(hkey):
        h = _get(f'{BASE}/ept-hierarchy/{hkey}.json').json()
        for k, v in h.items():
            if not inter(k): continue
            if v == -1: walk(k)
            elif v > 0: hier[k] = v
    walk('0-0-0-0'); return hier


def download(hier, threads=10):
    N.mkdir(parents=True, exist_ok=True)
    def dl(k):
        fn = N / f'{k}.laz'
        if fn.exists() and fn.stat().st_size > 0: return k, 'cached'
        r = _get(f'{BASE}/ept-data/{k}.laz', 300)
        if r.status_code != 200: return k, r.status_code
        fn.write_bytes(r.content); return k, 'ok'
    with cf.ThreadPoolExecutor(threads) as ex: res = list(ex.map(dl, hier.keys()))
    bad = [k for k, r in res if r not in ('cached', 'ok')]
    print('nodes', len(res), 'failed', len(bad), file=sys.stderr); return [k for k in hier if k not in bad]


def write_tif(path, arr, transform, nodata=None, desc=None):
    arr = np.asarray(arr)
    if arr.ndim == 2: arr = arr[None]
    with rasterio.open(path, 'w', driver='GTiff', height=arr.shape[1], width=arr.shape[2], count=arr.shape[0], dtype=arr.dtype,
                       crs=CRS32610, transform=transform, nodata=nodata, compress='deflate', tiled=True, blockxsize=256, blockysize=256) as d:
        d.write(arr)
        if desc: d.update_tags(DESCRIPTION=desc)


def verify(path):
    with rasterio.open(path) as d:
        a = d.read(masked=True)
        ok = d.crs.to_epsg() == 32610 and abs(d.transform.b) < 1e-12 and abs(d.transform.d) < 1e-12 and d.transform.e < 0
        print(f'VERIFY {pathlib.Path(path).name}\n  CRS EPSG:{d.crs.to_epsg()} size {d.width}x{d.height} bands {d.count} {d.dtypes[0]} pixel {d.res} bounds {tuple(round(v,2) for v in d.bounds)} nodata {d.nodata} min {a.min()} max {a.max()} north-up/no-rot {ok}')


# ---------- A: core DSM + lidar RGB ----------
def core():
    tr = Transformer.from_crs('EPSG:32610', 'EPSG:3857', always_xy=True)
    W, H = CORE['w'], CORE['h']; x0, y1 = CORE['x0'], CORE['y1']
    xs, ys = zip(*[tr.transform(x0 + dx, y1 - dy) for dx in (0, W) for dy in (0, H)])
    hier = ept_nodes(min(xs) - 20, max(xs) + 20, min(ys) - 20, max(ys) + 20)
    keys = download(hier); print('core nodes', len(keys), file=sys.stderr)
    inv = Transformer.from_crs('EPSG:3857', 'EPSG:32610', always_xy=True)
    zmax = np.full((H, W), -np.inf, np.float32); rgbsum = np.zeros((H, W, 3), np.float64); rgbn = np.zeros((H, W), np.float64)
    # to keep RGB of the highest returns only: store z of top and rgb of the point at that z
    toprgb = np.zeros((H, W, 3), np.uint8)
    for i, k in enumerate(keys):
        las = laspy.read(N / f'{k}.laz')
        cl = np.asarray(las.classification)
        m = (cl != 7) & (cl != 18)
        if not m.any(): continue
        E, Nn = inv.transform(np.asarray(las.x)[m], np.asarray(las.y)[m]); Z = np.asarray(las.z)[m].astype(np.float32)
        col = np.floor(E - x0).astype(np.int64); row = np.floor(y1 - Nn).astype(np.int64)
        ok = (col >= 0) & (col < W) & (row >= 0) & (row < H)
        if not ok.any(): continue
        col, row, Z = col[ok], row[ok], Z[ok]
        if 'red' in las.point_format.dimension_names:
            rgb = np.stack([np.asarray(las.red)[m][ok], np.asarray(las.green)[m][ok], np.asarray(las.blue)[m][ok]], 1)
        else: rgb = np.zeros((int(ok.sum()), 3), np.uint16)
        rgb8 = (rgb >> 8).astype(np.uint8) if rgb.max() > 255 else rgb.astype(np.uint8)
        idx = row * W + col
        # per-cell max within this node, then merge with running max
        order = np.lexsort((Z, idx)); idx_s, Z_s = idx[order], Z[order]
        last = np.r_[idx_s[1:] != idx_s[:-1], True]       # last of each idx group = max Z
        ui, uz, ur = idx_s[last], Z_s[last], rgb8[order][last]
        flat = zmax.reshape(-1); fr = toprgb.reshape(-1, 3)
        better = uz > flat[ui]
        flat[ui[better]] = uz[better]; fr[ui[better]] = ur[better]
        if i % 100 == 0: print(' node', i, '/', len(keys), file=sys.stderr)
    valid = np.isfinite(zmax); print('cells with data', valid.sum(), 'of', valid.size, file=sys.stderr)
    # fill small holes: nearest neighbour within 3 cells
    dist, (ri, ci) = ndimage.distance_transform_edt(~valid, return_indices=True)
    fill = (~valid) & (dist <= 3)
    dsm = np.where(valid, zmax, ND).astype(np.float32); rgb = toprgb.copy()
    dsm[fill] = zmax[ri[fill], ci[fill]]; rgb[fill] = toprgb[ri[fill], ci[fill]]
    have = valid | fill; dsm[~have] = ND; rgb[~have] = 0
    print('filled', fill.sum(), 'still nodata', (~have).sum(), file=sys.stderr)
    write_tif(OUT / f'CALACADEMY_CORE_DSM_1m_UTM10N_{TAG}.tif', dsm, core_transform(), ND, 'DSM highest return, m NAVD88, classes 7/18 dropped, holes<=3 cells NN-filled')
    verify(OUT / f'CALACADEMY_CORE_DSM_1m_UTM10N_{TAG}.tif')
    np.save(OUT.parent.parent / 'data' / 'cal-academy' / 'lidar2023' / 'core_toprgb.npy', np.dstack([rgb, have.astype(np.uint8)]))  # cache for fallback


# ---------- B: region DTM ----------
def region():
    tiles = sorted(DEMD.glob('USGS_1M_10_x5[45]y41[89]_*.tif'))
    if len(tiles) < 4: sys.exit('DEM tiles missing')
    dst = np.full((REG['h'], REG['w']), ND, np.float32); tr = reg_transform()
    acc = np.zeros(dst.shape, np.float64); cnt = np.zeros(dst.shape, np.float64)
    for t in tiles:
        with rasterio.open(t) as s:
            print(t.name, s.crs.to_epsg(), s.res, s.bounds, file=sys.stderr)
            # average: reproject sum via Resampling.average per tile, track coverage via mask
            tmp = np.full(dst.shape, ND, np.float32)
            reproject(rasterio.band(s, 1), tmp, dst_transform=tr, dst_crs=CRS32610, src_nodata=s.nodata, dst_nodata=ND, resampling=Resampling.average)
            m = tmp != ND; acc[m] += tmp[m]; cnt[m] += 1
    dst = np.where(cnt > 0, acc / np.maximum(cnt, 1), ND).astype(np.float32)
    p = OUT / f'CALACADEMY_REGION_DTM_5m_UTM10N_{TAG}.tif'
    write_tif(p, dst, tr, ND, 'USGS 1 m DEM (bare-earth DTM, trees removed) mean-resampled to 5 m; source CRS EPSG:26910 tagged 32610'); verify(p)


# ---------- C: NAIP ----------
def naip():
    import pystac_client, planetary_computer
    cat = pystac_client.Client.open('https://planetarycomputer.microsoft.com/api/stac/v1', modifier=planetary_computer.sign_inplace)
    inv = Transformer.from_crs('EPSG:32610', 'EPSG:4326', always_xy=True)
    bb = (*inv.transform(REG['x0'], REG['y1'] - 6000), *inv.transform(REG['x0'] + 6000, REG['y1']))
    items = list(cat.search(collections=['naip'], bbox=bb, datetime='2020-01-01/2026-12-31').items())
    items.sort(key=lambda i: i.datetime, reverse=True)
    print('naip items', [(i.id, str(i.datetime.date())) for i in items], file=sys.stderr)
    latest = items[0].datetime.year; sel = [i for i in items if i.datetime.year == latest]
    for name, tr, w, h, res in (('CORE', core_transform(), CORE['w'], CORE['h'], 1), ('REGION', reg_transform(), REG['w'], REG['h'], REG['res'])):
        if (OUT / f'CALACADEMY_{name}_NAIP_{res}m_UTM10N_{TAG}.tif').exists(): verify(OUT / f'CALACADEMY_{name}_NAIP_{res}m_UTM10N_{TAG}.tif'); continue   # rerun: skip done
        out = np.zeros((3, h, w), np.uint8); got = np.zeros((h, w), bool)
        for it in sel:
            with rasterio.open(it.assets['image'].href) as s:
                tmp = np.zeros((3, h, w), np.uint8)
                if res > 1:   # read a decimated window (uses the COG overviews), then warp: fast for the 6 km region
                    from rasterio.windows import from_bounds
                    L, B, R, T = rasterio.transform.array_bounds(h, w, tr)[0], rasterio.transform.array_bounds(h, w, tr)[1], rasterio.transform.array_bounds(h, w, tr)[2], rasterio.transform.array_bounds(h, w, tr)[3]
                    win = from_bounds(L - 30, B - 30, R + 30, T + 30, s.transform).round_offsets().round_lengths()
                    f = max(1, int(res / s.res[0]) - 1); oh, ow = max(1, int(win.height) // f), max(1, int(win.width) // f)
                    data = s.read([1, 2, 3], window=win, out_shape=(3, oh, ow), resampling=Resampling.average, boundless=True, fill_value=0)
                    st = s.window_transform(win) * rasterio.Affine.scale(win.width / ow, win.height / oh)
                    for b in range(3):
                        reproject(data[b], tmp[b], src_transform=st, src_crs=s.crs, dst_transform=tr, dst_crs=CRS32610, resampling=Resampling.bilinear)
                else:
                    for b in range(3):
                        reproject(rasterio.band(s, b + 1), tmp[b], dst_transform=tr, dst_crs=CRS32610, resampling=Resampling.bilinear)
                m = tmp.any(0) & ~got; out[:, m] = tmp[:, m]; got |= m
        p = OUT / f'CALACADEMY_{name}_NAIP_{res}m_UTM10N_{TAG}.tif'
        write_tif(p, out, tr, None, f'NAIP {latest} RGB'); verify(p)


def core_lidar_rgb():
    p = OUT.parent.parent / 'data' / 'cal-academy' / 'lidar2023' / 'core_toprgb.npy'
    a = np.load(p); out = np.moveaxis(a[..., :3], 2, 0).copy()
    q = OUT / f'CALACADEMY_CORE_LIDARRGB_1m_UTM10N_{TAG}.tif'
    write_tif(q, out, core_transform(), None, 'mean-less: RGB of highest return per cell, 16-bit>>8'); verify(q)


# ---------- D/E: Overpass ----------
def overpass(q):
    for attempt in range(2):
        r = requests.post('https://overpass-api.de/api/interpreter', data={'data': q}, timeout=180, headers={'User-Agent': 'territory-rasters/1.0 (research)'})
        if r.status_code == 200: return r.json()
        print('overpass', r.status_code, file=sys.stderr)
        if r.status_code in (429, 504) and attempt == 0: time.sleep(30)
        else: r.raise_for_status()


def ring_join(ways):
    """join way geometries (lists of (lon,lat)) into closed rings"""
    ways = [list(w) for w in ways if len(w) > 1]; rings = []
    while ways:
        cur = ways.pop(0)
        while cur[0] != cur[-1]:
            for i, w in enumerate(ways):
                if w[0] == cur[-1]: cur += w[1:]
                elif w[-1] == cur[-1]: cur += w[::-1][1:]
                elif w[-1] == cur[0]: cur = w[:-1] + cur
                elif w[0] == cur[0]: cur = w[::-1][:-1] + cur
                else: continue
                ways.pop(i); break
            else: break
        if cur[0] != cur[-1]: cur.append(cur[0])
        if len(cur) >= 4: rings.append(cur)
    return rings


def water():
    s, w, n, e = WATER_BB[1], WATER_BB[0], WATER_BB[3], WATER_BB[2]
    q = f'[out:json][timeout:120];(way["natural"="water"]({s},{w},{n},{e});relation["natural"="water"]({s},{w},{n},{e});way["water"]({s},{w},{n},{e});relation["water"]({s},{w},{n},{e});way["amenity"="fountain"]({s},{w},{n},{e}););out geom;'
    js = overpass(q); feats = []; seen = set()
    for el in js['elements']:
        key = (el['type'], el['id'])
        if key in seen: continue
        seen.add(key); tags = el.get('tags', {})
        if el['type'] == 'way':
            ring = [(p['lon'], p['lat']) for p in el.get('geometry', [])]
            rings = ring_join([ring]) if len(ring) > 3 else []
            polys = [[r] for r in rings]
        else:
            outers = [[(p['lon'], p['lat']) for p in m['geometry']] for m in el.get('members', []) if m.get('role') == 'outer' and 'geometry' in m]
            inners = [[(p['lon'], p['lat']) for p in m['geometry']] for m in el.get('members', []) if m.get('role') == 'inner' and 'geometry' in m]
            polys = [[r] for r in ring_join(outers)]   # outers only (approximation)
        for pl in polys:
            feats.append({'type': 'Feature', 'properties': {'osm_type': el['type'], 'osm_id': el['id'], **tags, 'name': tags.get('name', '')},
                          'geometry': {'type': 'Polygon', 'coordinates': [[list(p) for p in pl[0]]]}})
    (OUT / f'CALACADEMY_WATER_{TAG}.geojson').write_text(json.dumps({'type': 'FeatureCollection', 'features': feats}, ensure_ascii=False), encoding='utf-8')
    print('water features', len(feats), 'named:', sorted({f['properties']['name'] for f in feats if f['properties']['name']}), file=sys.stderr)


LABELS = ['California Academy of Sciences', 'de Young Museum', 'Music Concourse', 'Japanese Tea Garden', 'Spreckels Temple of Music', 'Conservatory of Flowers',
          'Stow Lake', 'Strawberry Hill', 'San Francisco Botanical Garden', 'Shakespeare Garden', 'Rideout Fountain', 'Golden Gate Park Band Shell']
APPROX = {'California Academy of Sciences': (-122.46608, 37.76983), 'de Young Museum': (-122.4687, 37.7715), 'Music Concourse': (-122.4686, 37.7701),
          'Japanese Tea Garden': (-122.4703, 37.7701), 'Spreckels Temple of Music': (-122.4690, 37.7699), 'Conservatory of Flowers': (-122.4600, 37.7726),
          'Stow Lake': (-122.4755, 37.7704), 'Strawberry Hill': (-122.4755, 37.7706), 'San Francisco Botanical Garden': (-122.4695, 37.7660),
          'Shakespeare Garden': (-122.4665, 37.7694), 'Rideout Fountain': (-122.4688, 37.7700), 'Golden Gate Park Band Shell': (-122.4690, 37.7699)}


def labels():
    s, w, n, e = WATER_BB[1], WATER_BB[0], WATER_BB[3], WATER_BB[2]
    pat = '|'.join(['Academy of Sciences', 'de Young', 'Music Concourse', 'Japanese Tea Garden', 'Temple of Music', 'Conservatory of Flowers', '^Stow Lake$', 'Strawberry Hill',
                    'Botanical Garden', 'Shakespeare Garden', 'Rideout', 'Band ?[Ss]hell', 'Bandshell'])
    q = f'[out:json][timeout:120];(nwr["name"~"{pat}"]({s},{w},{n},{e}););out center tags;'
    try: js = overpass(q)
    except Exception as ex: print('labels overpass failed', ex, file=sys.stderr); js = {'elements': []}
    cands = []
    for el in js['elements']:
        c = (el['lon'], el['lat']) if el['type'] == 'node' else (el['center']['lon'], el['center']['lat'])
        cands.append((el['tags'].get('name', ''), c, el['type'], el['id']))
    match = {'California Academy of Sciences': 'Academy of Sciences', 'de Young Museum': 'de Young', 'Music Concourse': 'Music Concourse', 'Japanese Tea Garden': 'Japanese Tea Garden',
             'Spreckels Temple of Music': 'Temple of Music', 'Conservatory of Flowers': 'Conservatory of Flowers', 'Stow Lake': 'Stow Lake', 'Strawberry Hill': 'Strawberry Hill',
             'San Francisco Botanical Garden': 'Botanical Garden', 'Shakespeare Garden': 'Shakespeare Garden', 'Rideout Fountain': 'Rideout', 'Golden Gate Park Band Shell': 'hell'}
    feats = []
    for lab in LABELS:
        pool = [c for c in cands if match[lab].lower().strip('^$') in c[0].lower()]
        if lab == 'Stow Lake': pool = [c for c in pool if c[0].lower() == 'stow lake']
        if lab == 'Golden Gate Park Band Shell': pool = [c for c in pool if 'band' in c[0].lower()]
        if lab == 'de Young Museum': pool = [c for c in pool if 'museum' in c[0].lower()] or pool
        if lab == 'California Academy of Sciences': pool = [c for c in pool if c[3] == 28695389] or pool   # the museum building way
        if lab == 'Music Concourse': pool = [c for c in pool if c[3] == 30899551]                           # the leisure=park way
        if lab == 'Golden Gate Park Band Shell': pool = []   # = Spreckels Temple of Music; the OSM 'Bandshell' hits are parking lots
        if pool:
            nm, (lo, la), t, i = pool[0]
            props = {'name': lab, 'osm_name': nm, 'osm': f'{t}/{i}', 'approx': False}
        else:
            lo, la = APPROX[lab]; props = {'name': lab, 'approx': True, 'note': 'not found on Overpass; well-known coordinate'}
            if lab == 'Stow Lake': lo, la = -122.4745, 37.7690; props['note'] = 'Stow Lake is mapped in OSM as relation 12908 (named Blue Heron Lake); centre approx'
            if lab == 'Golden Gate Park Band Shell': props['note'] = 'same place as Spreckels Temple of Music (not distinct in OSM); approx'
        feats.append({'type': 'Feature', 'properties': props, 'geometry': {'type': 'Point', 'coordinates': [lo, la]}})
    (OUT / f'CALACADEMY_LABELS_{TAG}.geojson').write_text(json.dumps({'type': 'FeatureCollection', 'features': feats}, ensure_ascii=False, indent=1), encoding='utf-8')
    for f in feats: print(' ', f['properties']['name'], f['geometry']['coordinates'], 'APPROX' if f['properties']['approx'] else f['properties']['osm'], file=sys.stderr)


if __name__ == '__main__':
    what = sys.argv[1:] or ['all']
    steps = dict(core=core, region=region, naip=naip, water=water, labels=labels)
    for s in (steps if 'all' in what else what): print('==', s, file=sys.stderr); steps[s]()
    if 'lidarrgb' in what: core_lidar_rgb()
