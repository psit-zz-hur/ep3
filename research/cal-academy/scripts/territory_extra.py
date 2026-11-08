#!/usr/bin/env python3
"""THE TERRITORY extension 2026-11-07: neighbourhoods (E), building footprints (F), scheduled buses (G), NAIP on the park grid (B).
Outputs EPSG:32610 north-up rasters / WGS84 GeoJSON in exports/territory/ (git-ignored).

    python -X utf8 research/cal-academy/scripts/territory_extra.py [neigh|bldg|bus|naip|all]
"""
import sys, json, csv, time, io, zipfile, pathlib, math, datetime
import numpy as np, requests, rasterio
from rasterio.features import rasterize
from rasterio.transform import from_origin
from rasterio.enums import Resampling
from rasterio.warp import reproject
from pyproj import Transformer
from shapely.geometry import shape, mapping, box, LineString, Point
from shapely.ops import transform as sh_transform
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import territory_rasters as T
from territory_rasters import OUT, TAG, ND, CRS32610, REG, write_tif, verify, reg_transform

X = T.D / 'extra'; X.mkdir(parents=True, exist_ok=True)
U2W = Transformer.from_crs(32610, 4326, always_xy=True).transform
W2U = Transformer.from_crs(4326, 32610, always_xy=True).transform
REGBOX_U = box(REG['x0'], REG['y1'] - REG['h'] * REG['res'], REG['x0'] + REG['w'] * REG['res'], REG['y1'])   # 6 km box in UTM
# park grid A, snapped outward to multiples of 3 m so that a 0.6 m NAIP grid has exactly the same bounds
PARK_LL = (-122.5120, 37.7635, -122.4520, 37.7750)


def park_grid():
    pts = []
    for t in np.linspace(0, 1, 50):
        for lo, la in ((PARK_LL[0] + t * (PARK_LL[2] - PARK_LL[0]), PARK_LL[1]), (PARK_LL[0] + t * (PARK_LL[2] - PARK_LL[0]), PARK_LL[3]),
                       (PARK_LL[0], PARK_LL[1] + t * (PARK_LL[3] - PARK_LL[1])), (PARK_LL[2], PARK_LL[1] + t * (PARK_LL[3] - PARK_LL[1]))):
            pts.append(W2U(lo, la))
    xs, ys = zip(*pts)
    x0 = math.floor(min(xs) / 3) * 3; x1 = math.ceil(max(xs) / 3) * 3; y0 = math.floor(min(ys) / 3) * 3; y1 = math.ceil(max(ys) / 3) * 3
    return dict(x0=x0, y1=y1, w=x1 - x0, h=y1 - y0)


PARK = park_grid()
def park_transform(res=1): return from_origin(PARK['x0'], PARK['y1'], res, res)


def jget(url, tries=4, **kw):
    for i in range(tries):
        try:
            r = requests.get(url, timeout=180, **kw)
            if r.status_code == 200: return r
            print('HTTP', r.status_code, url[:90], file=sys.stderr)
        except requests.exceptions.RequestException as e: print('retry', e, file=sys.stderr)
        time.sleep(30 if i == 0 else 10 * (i + 1))
    raise RuntimeError('giving up ' + url)


# ---------- E: neighbourhoods ----------
def neigh():
    p = X / 'neigh.geojson'
    if not p.exists() or p.stat().st_size < 1000:
        p.write_bytes(jget('https://data.sf.gov/api/geospatial/j2bu-swwd?method=export&format=GeoJSON').content)   # p5b7-5n3h is the map view of table j2bu-swwd
    feats = []
    for f in json.loads(p.read_text(encoding='utf-8'))['features']:
        g = shape(f['geometry'])
        gu = sh_transform(W2U, g).buffer(0).intersection(REGBOX_U)
        if gu.is_empty: continue
        feats.append((f['properties']['nhood'], gu))
    feats.sort(key=lambda t: t[0])
    out = [{'type': 'Feature', 'properties': {'nhood': n, 'code': i + 1}, 'geometry': mapping(sh_transform(U2W, g))} for i, (n, g) in enumerate(feats)]
    (OUT / f'CALACADEMY_NEIGHBORHOODS_{TAG}.geojson').write_text(json.dumps({'type': 'FeatureCollection', 'features': out}), encoding='utf-8')
    ras = rasterize([(g, i + 1) for i, (n, g) in enumerate(feats)], out_shape=(REG['h'], REG['w']), transform=reg_transform(), fill=0, dtype='uint8')
    q = OUT / f'CALACADEMY_REGION_NEIGHBORHOODS_5m_UTM10N_{TAG}.tif'
    write_tif(q, ras, reg_transform(), 0, 'uint8 neighbourhood code, 0 = none (ocean); legend in the CSV'); verify(q)
    with open(OUT / f'CALACADEMY_REGION_NEIGHBORHOODS_LEGEND_{TAG}.csv', 'w', newline='', encoding='utf-8') as fh:
        w = csv.writer(fh); w.writerow(['code', 'nhood', 'cells_5m'])
        w.writerow([0, '(none / ocean)', int((ras == 0).sum())])
        for i, (n, g) in enumerate(feats): w.writerow([i + 1, n, int((ras == i + 1).sum())])
    print('neighbourhoods', [(i + 1, n) for i, (n, g) in enumerate(feats)], file=sys.stderr)


# ---------- F: building footprints ----------
BF = ['sf16_bldgid', 'mblr', 'hgt_mediancm', 'hgt_median_m', 'hgt_maxcm', 'gnd_min_m', 'median_1st_m', 'peak_1st_m', 'p2010_name', 'data_as_of', 'globalid']
UNION_LL = (-122.5120, 37.7426, -122.4318, 37.7971)   # park box + 6 km box


def bldg_fetch():
    p = X / 'footprints_union.geojson'
    if p.exists() and p.stat().st_size > 1000: return json.loads(p.read_text(encoding='utf-8'))['features']
    w, s, e, n = UNION_LL; feats = []; off = 0
    where = f'within_box(shape,{s},{w},{n},{e})'
    while True:
        r = jget('https://data.sf.gov/resource/ynuv-fyni.geojson', params={'$where': where, '$limit': 10000, '$offset': off, '$order': ':id', '$select': ','.join(BF) + ',shape'})
        fs = r.json()['features']; feats += fs; print(' footprints', len(feats), file=sys.stderr)
        if len(fs) < 10000: break
        off += 10000; time.sleep(3)
    p.write_text(json.dumps({'type': 'FeatureCollection', 'features': feats}), encoding='utf-8'); return feats


def bldg_polys():
    """list of (utm_geom, height_m) for the union area"""
    out = []
    for f in bldg_fetch():
        if not f.get('geometry'): continue
        pr = f['properties']
        try: h = float(pr.get('hgt_mediancm')) / 100.0
        except (TypeError, ValueError): h = float('nan')
        out.append((sh_transform(W2U, shape(f['geometry'])).buffer(0), h, f))
    return out


def bldg():
    items = bldg_polys()
    # year: the dataset has no construction-year column; 'data_as_of' (survey vintage) is kept as the date field
    keep = []
    for g, h, f in items:
        if g.is_empty or not g.intersects(REGBOX_U): continue
        pr = dict(f['properties'])
        geo = f['geometry'] if REGBOX_U.contains(g) else mapping(sh_transform(U2W, g.intersection(REGBOX_U)))
        keep.append({'type': 'Feature', 'properties': pr, 'geometry': geo})
    (OUT / f'CALACADEMY_FOOTPRINTS_{TAG}.geojson').write_text(json.dumps({'type': 'FeatureCollection', 'features': keep}), encoding='utf-8')
    print('footprints in 6 km box', len(keep), 'of', len(items), 'with height', sum(1 for g, h, f in items if not math.isnan(h)), file=sys.stderr)
    # height raster: ascending so the tallest wins where footprints share a cell; all_touched so 5 m cells see small buildings
    sh = sorted([(g, h) for g, h, f in items if not g.is_empty and not math.isnan(h) and g.intersects(REGBOX_U)], key=lambda t: t[1])
    ras = rasterize([(g, np.float32(h)) for g, h in sh], out_shape=(REG['h'], REG['w']), transform=reg_transform(), fill=ND, dtype='float32', all_touched=True)
    q = OUT / f'CALACADEMY_REGION_BLDG_HEIGHT_5m_UTM10N_{TAG}.tif'
    write_tif(q, ras, reg_transform(), ND, 'DataSF building height above ground, m (hgt_mediancm/100); tallest footprint per cell, all_touched; NoData outside footprints'); verify(q)


# ---------- G: buses ----------
GTFS_URL = 'https://muni-gtfs.apps.sfmta.com/data/muni_gtfs-current.zip'


def bus():
    import pandas as pd
    zp = X / 'gtfs' / 'muni_gtfs-current.zip'; zp.parent.mkdir(exist_ok=True)
    if not zp.exists(): zp.write_bytes(jget(GTFS_URL).content)
    z = zipfile.ZipFile(zp)
    rd = lambda n, **kw: pd.read_csv(z.open(n), dtype=str, **kw)
    routes = rd('routes.txt'); trips = rd('trips.txt'); shapes = rd('shapes.txt'); stops = rd('stops.txt'); cal = rd('calendar.txt'); cd = rd('calendar_dates.txt')
    dirs = rd('directions.txt') if 'directions.txt' in z.namelist() else None
    print('calendar', cal[['service_id', 'start_date', 'end_date', 'wednesday']].to_string(), file=sys.stderr); print('calendar_dates', cd.to_string(), file=sys.stderr)
    # shapes -> UTM lines, those intersecting the 6 km box
    shapes['shape_pt_sequence'] = shapes.shape_pt_sequence.astype(int); shapes = shapes.sort_values(['shape_id', 'shape_pt_sequence'])
    shp = {}
    for sid, g in shapes.groupby('shape_id'):
        lon = g.shape_pt_lon.astype(float).values; lat = g.shape_pt_lat.astype(float).values
        e, n = W2U(lon, lat); ln = LineString(np.c_[e, n])
        if ln.intersects(REGBOX_U): shp[sid] = (ln, lon, lat)
    print('shapes intersecting', len(shp), 'of', shapes.shape_id.nunique(), file=sys.stderr)
    t_in = trips[trips.shape_id.isin(shp)]
    rt = routes[routes.route_id.isin(t_in.route_id.unique())].set_index('route_id')
    dname = {}
    if dirs is not None:
        for _, r in dirs.iterrows(): dname[(r['route_id'], r['direction_id'])] = r.get('direction')
    # routes geojson: one LineString per shape
    feats = []
    sh2trip = t_in.drop_duplicates('shape_id').set_index('shape_id')
    for sid, (ln, lon, lat) in shp.items():
        if sid not in sh2trip.index: continue
        tr = sh2trip.loc[sid]; r = rt.loc[tr.route_id]
        feats.append({'type': 'Feature', 'properties': {'shape_id': sid, 'route_id': tr.route_id, 'route_short_name': r.route_short_name, 'route_long_name': r.route_long_name,
                      'route_color': r.get('route_color'), 'direction_id': tr.direction_id, 'direction': dname.get((tr.route_id, tr.direction_id), tr.get('trip_headsign')), 'length_m': round(ln.length, 1)},
                      'geometry': {'type': 'LineString', 'coordinates': [[round(a, 6), round(b, 6)] for a, b in zip(lon, lat)]}})
    (OUT / f'CALACADEMY_BUS_ROUTES_{TAG}.geojson').write_text(json.dumps({'type': 'FeatureCollection', 'features': feats}), encoding='utf-8')
    # representative weekday: first Wednesday on/after today inside a calendar range, then the service_id with the most trips
    today = datetime.date(2026, 11, 7)
    def active(d):
        ds = d.strftime('%Y%m%d'); s = set(cal[(cal.wednesday == '1') & (cal.start_date <= ds) & (cal.end_date >= ds)].service_id)
        for _, r in cd[cd.date == ds].iterrows(): (s.add if r.exception_type == '1' else s.discard)(r.service_id)
        return s
    d = today + datetime.timedelta(days=(2 - today.weekday()) % 7)
    last = datetime.datetime.strptime(cal.end_date.max(), '%Y%m%d').date()
    if d > last:   # the published feed has expired (valid to `last`): use its last Wednesday
        print('FEED EXPIRED: calendar ends', last, file=sys.stderr); d = last - datetime.timedelta(days=(last.weekday() - 2) % 7)
    while not active(d): d += datetime.timedelta(days=-7 if d > last - datetime.timedelta(days=60) else 7)
    act = active(d); cnt = trips[trips.service_id.isin(act)].groupby('service_id').size().sort_values(ascending=False)
    svc = cnt.index[0]; print('service date', d, 'active', dict(cnt), 'chosen', svc, file=sys.stderr)
    tt = t_in[t_in.service_id == svc]
    st = pd.read_csv(z.open('stop_times.txt'), dtype=str, usecols=['trip_id', 'arrival_time', 'departure_time', 'stop_id', 'stop_sequence', 'shape_dist_traveled'] if 'shape_dist_traveled' in pd.read_csv(z.open('stop_times.txt'), nrows=1).columns else ['trip_id', 'arrival_time', 'departure_time', 'stop_id', 'stop_sequence'])
    st = st[st.trip_id.isin(tt.trip_id)]; st['stop_sequence'] = st.stop_sequence.astype(int); st = st.sort_values(['trip_id', 'stop_sequence'])
    sx = stops.set_index('stop_id'); sec = lambda s: int(s[:2]) * 3600 + int(s[3:5]) * 60 + int(s[6:8])
    sched = []; proj_cache = {}
    tinfo = tt.set_index('trip_id')
    for tid, g in st.groupby('trip_id', sort=False):
        ti = tinfo.loc[tid]; ln = shp[ti.shape_id][0]
        lon = sx.loc[g.stop_id, 'stop_lon'].astype(float).values; lat = sx.loc[g.stop_id, 'stop_lat'].astype(float).values; e, n = W2U(lon, lat)
        dist = np.array([ln.project(Point(a, b)) for a, b in zip(e, n)]); dist = np.maximum.accumulate(dist)
        t = [sec(x) for x in g.departure_time.fillna(g.arrival_time)]
        r = rt.loc[ti.route_id]
        sched.append({'trip_id': tid, 'route': r.route_short_name, 'route_id': ti.route_id, 'direction_id': ti.direction_id, 'direction': dname.get((ti.route_id, ti.direction_id), ti.trip_headsign),
                      'headsign': ti.trip_headsign, 'shape_id': ti.shape_id, 'shape_length_m': round(ln.length, 1),
                      'stops': [[a, round(b, 6), round(c, 6)] for a, b, c in zip(t, lon, lat)], 'stop_dist_m': [round(x, 1) for x in dist], 'stop_ids': list(g.stop_id)})
    meta = {'feed': GTFS_URL, 'service_date': d.isoformat(), 'service_id': svc, 'trip_count': len(sched), 'note': 'one trip per entry; stops[] = [seconds_since_midnight (departure), lon, lat]; stop_dist_m = metres along the shape (UTM10N length, same as shape_length_m)'}
    (OUT / f'CALACADEMY_BUS_SCHEDULE_{TAG}.json').write_text(json.dumps({'meta': meta, 'trips': sched}, separators=(',', ':')), encoding='utf-8')
    used = {s for t in sched for s in t['stop_ids']}
    sf = [{'type': 'Feature', 'properties': {'stop_id': i, 'stop_name': r.stop_name, 'stop_code': r.get('stop_code')}, 'geometry': {'type': 'Point', 'coordinates': [float(r.stop_lon), float(r.stop_lat)]}}
          for i, r in sx.iterrows() if i in used]
    (OUT / f'CALACADEMY_BUS_STOPS_{TAG}.geojson').write_text(json.dumps({'type': 'FeatureCollection', 'features': sf}), encoding='utf-8')
    routes_used = sorted({t['route'] for t in sched}); print('trips', len(sched), 'routes', routes_used, 'stops', len(sf), file=sys.stderr)
    print('ROUTES_ALL_IN_BOX', sorted(rt.route_short_name.unique()), file=sys.stderr)


# ---------- B: NAIP on the park grid ----------
def naip():
    import pystac_client, planetary_computer
    cat = pystac_client.Client.open('https://planetarycomputer.microsoft.com/api/stac/v1', modifier=planetary_computer.sign_inplace)
    w, s, e, n = PARK_LL
    items = list(cat.search(collections=['naip'], bbox=(w - .002, s - .002, e + .002, n + .002), datetime='2020-01-01/2026-12-31').items())
    items.sort(key=lambda i: i.datetime, reverse=True)
    print('naip items', [(i.id, str(i.datetime.date()), i.properties.get('gsd')) for i in items], file=sys.stderr)
    latest = items[0].datetime.year; sel = [i for i in items if i.datetime.year == latest]; gsd = sel[0].properties.get('gsd')
    todo = [(1, 'NAIP_1m')]
    if gsd is not None and abs(float(gsd) - 0.6) < 0.05: todo.append((0.6, 'NAIP_0p6m'))
    for res, name in todo:
        W = int(round(PARK['w'] / res)); H = int(round(PARK['h'] / res)); tr = park_transform(res)
        p = OUT / f'CALACADEMY_PARK_CORE_{name}_UTM10N_{TAG}.tif'
        out = np.zeros((3, H, W), np.uint8); got = np.zeros((H, W), bool)
        for it in sel:
            with rasterio.open(it.assets['image'].href) as src:
                tmp = np.zeros((3, H, W), np.uint8)
                for b in range(3):
                    reproject(rasterio.band(src, b + 1), tmp[b], dst_transform=tr, dst_crs=CRS32610, resampling=Resampling.average if res >= 1 else Resampling.bilinear)
                m = tmp.any(0) & ~got; out[:, m] = tmp[:, m]; got |= m
        write_tif(p, out, tr, None, f'NAIP {latest} RGB item(s) {[i.id for i in sel]}'); verify(p)
        print(name, 'covered', round(got.mean() * 100, 2), '%', file=sys.stderr)


# ---------- H: park DTM on grid A ----------
def dem_to_grid(tr, W, H, rs=Resampling.bilinear):
    tiles = sorted(T.DEMD.glob('USGS_1M_10_x5[45]y41[89]_*.tif'))
    acc = np.zeros((H, W), np.float64); cnt = np.zeros((H, W), np.float64)
    for t in tiles:
        with rasterio.open(t) as s:
            tmp = np.full((H, W), ND, np.float32)
            reproject(rasterio.band(s, 1), tmp, dst_transform=tr, dst_crs=CRS32610, src_nodata=s.nodata, dst_nodata=ND, resampling=rs)
            m = tmp != ND; acc[m] += tmp[m]; cnt[m] += 1
    return np.where(cnt > 0, acc / np.maximum(cnt, 1), ND).astype(np.float32)


def dtm():
    p = OUT / f'CALACADEMY_PARK_CORE_DTM_1m_UTM10N_{TAG}.tif'
    write_tif(p, dem_to_grid(park_transform(1), PARK['w'], PARK['h']), park_transform(1), ND, 'USGS 1 m DEM bare earth, bilinear to grid A, m NAVD88'); verify(p)


def dtmcw():
    tr = from_origin(542523, 4183411, 5, 5); p = OUT / f'CALACADEMY_REGION_DTM_5m_CW_UTM10N_{TAG}.tif'
    write_tif(p, dem_to_grid(tr, 1500, 2200, Resampling.average), tr, ND, 'USGS 1 m DEM bare earth mean-resampled to 5 m on grid CW (E542523..550023, N4172411..4183411); NoData = no land'); verify(p)


# ---------- I: park outline + masks ----------
def park():
    q = '[out:json][timeout:120];(relation["leisure"="park"]["name"="Golden Gate Park"](37.74,-122.52,37.80,-122.43);way["leisure"="park"]["name"="Golden Gate Park"](37.74,-122.52,37.80,-122.43););out geom;'
    geoms = []; src = 'OSM via Overpass (leisure=park, name=Golden Gate Park)'
    try:
        js = T.overpass(q)
        for el in js['elements']:
            if el['type'] == 'way':
                ring = [(p_['lon'], p_['lat']) for p_ in el['geometry']]
                if len(ring) >= 4 and ring[0] == ring[-1]: geoms.append(('way/%d' % el['id'], shape({'type': 'Polygon', 'coordinates': [ring]}).buffer(0)))
            else:
                outers = T.ring_join([[(p_['lon'], p_['lat']) for p_ in m['geometry']] for m in el['members'] if m['role'] == 'outer' and 'geometry' in m])
                inners = T.ring_join([[(p_['lon'], p_['lat']) for p_ in m['geometry']] for m in el['members'] if m['role'] == 'inner' and 'geometry' in m])
                g = None
                for r in outers:
                    pg = shape({'type': 'Polygon', 'coordinates': [r]}).buffer(0); g = pg if g is None else g.union(pg)
                for r in inners:
                    g = g.difference(shape({'type': 'Polygon', 'coordinates': [r]}).buffer(0))
                if g is not None: geoms.append(('relation/%d' % el['id'], g))
        print('overpass park elements', [(n, round(g.area * 1.0e4 * 0.79, 1)) for n, g in geoms], file=sys.stderr)
    except Exception as ex: print('overpass failed', ex, file=sys.stderr); geoms = []
    if not geoms:
        src = 'DataSF parks (data/cal-academy/vector/sf_parks.geojson) fallback'
        for f in json.loads((T.D.parent.parent / 'data' / 'cal-academy' / 'vector' / 'sf_parks.geojson').read_text(encoding='utf-8'))['features']:
            if 'golden gate park' in json.dumps(f['properties']).lower(): geoms.append(('datasf', shape(f['geometry']).buffer(0)))
    g = geoms[0][1]
    for n, h in geoms[1:]:
        if h.area > g.area * 0.5: g = h
    feat = {'type': 'Feature', 'properties': {'name': 'Golden Gate Park', 'source': src, 'element': geoms[0][0]}, 'geometry': mapping(g)}
    (OUT / f'CALACADEMY_PARK_OUTLINE_{TAG}.geojson').write_text(json.dumps({'type': 'FeatureCollection', 'features': [feat]}), encoding='utf-8')
    gu = sh_transform(W2U, g)
    for res, tr, W, H, name in ((1, park_transform(1), PARK['w'], PARK['h'], f'CALACADEMY_PARK_MASK_1m_UTM10N_{TAG}.tif'), (5, reg_transform(), REG['w'], REG['h'], f'CALACADEMY_REGION_PARK_MASK_5m_UTM10N_{TAG}.tif')):
        ras = rasterize([(gu, 1)], out_shape=(H, W), transform=tr, fill=0, dtype='uint8')
        write_tif(OUT / name, ras, tr, None, 'uint8 1 = Golden Gate Park, 0 = outside; ' + src); verify(OUT / name); print(name, 'park cells', int(ras.sum()), 'area km2', round(ras.sum() * res * res / 1e6, 3), file=sys.stderr)


if __name__ == '__main__':
    what = sys.argv[1:] or ['all']; steps = dict(neigh=neigh, bldg=bldg, bus=bus, naip=naip, dtm=dtm, park=park, dtmcw=dtmcw)
    print('PARK grid', PARK, file=sys.stderr)
    for s in (steps if 'all' in what else what): print('==', s, file=sys.stderr); steps[s]()
