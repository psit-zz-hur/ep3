#!/usr/bin/env python3
"""Lost-water GeoJSON (WGS84): lakes (sheet-derived 1852 extents + modern outlines of the pre-city lakes) and creeks (OMCA/SFEI historical creeks, OSM Lobos Creek)."""
import json, pathlib, numpy as np, requests, rasterio
from rasterio.features import shapes
from rasterio.transform import Affine
from shapely.geometry import shape, mapping, LineString, box, Polygon
from shapely.ops import transform as sh_transform, unary_union
from pyproj import Transformer
ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = ROOT / 'exports' / 'territory' / 'precolonial'; PRE = ROOT / 'data' / 'cal-academy' / 'precolonial'; TAG = '2026_11_07A'
TR = Affine(5, 0, 542523, 0, -5, 4183411)
to84 = Transformer.from_crs(32610, 4326, always_xy=True); to10 = Transformer.from_crs(4326, 32610, always_xy=True)
feats = []
def add(geom, **p): feats.append({'type': 'Feature', 'properties': p, 'geometry': mapping(geom)})
# 1. sheet lakes
lake = np.load(PRE / 'lake_sheet_cw.npy').astype(np.uint8)
import scipy.ndimage as ndi
lab, n = ndi.label(lake)
for i in range(1, n + 1):
    m = (lab == i).astype(np.uint8)
    polys = [shape(g) for g, v in shapes(m, mask=m.astype(bool), transform=TR) if v == 1]
    g = unary_union(polys).simplify(3)
    a = g.area
    if a < 20000: continue
    cy = g.centroid.y
    name = 'Lake Merced (Laguna de la Merced), 1852 extent' if cy < 4177500 else 'unnamed lake'
    add(sh_transform(lambda x, y, z=None: to84.transform(x, y), g), kind='lake', name=name, area_ha=round(a / 1e4, 1), source='NOAA/US Coast Survey T-sheet T00382 (1852), enclosed symbol-free water area, georeferenced (RMS ~4 m fit, 10-45 m leave-one-out)', confidence='high on the sheet; edge +/- 30 m', licence='public domain')
# 2. modern outlines of pre-city lakes (OSM, ODbL)
osm = json.load(open(PRE / 'osm_ref.json'))
keep = {16650677: ('Mountain Lake', 'pre-city lake, modern outline'), 30969894: ('Laguna Honda', 'pre-city lake, modern outline (today a reservoir)'), 31860201: ('Pine Lake (Laguna Puerca)', 'pre-city lake, modern outline')}
for el in osm['elements']:
    if el['id'] in keep and el['type'] == 'way' and 'geometry' in el:
        ring = [(p['lon'], p['lat']) for p in el['geometry']]
        add(Polygon(ring), kind='lake', name=keep[el['id']][0], note=keep[el['id']][1], source=f'OSM way {el["id"]} (ODbL), modern outline; the 1850s extent is not drawn on T00382 for Mountain Lake and Laguna Honda', confidence='medium', licence='ODbL')
    if el['type'] == 'relation' and el['id'] == 16308125:
        rings = [[(p['lon'], p['lat']) for p in m['geometry']] for m in el.get('members', []) if m.get('role') == 'outer' and 'geometry' in m]
        for r in rings:
            if len(r) > 3 and r[0] == r[-1]: add(Polygon(r), kind='lake_reference', name='Lake Merced today (reference only)', source='OSM relation 16308125 (ODbL)', confidence='n/a', licence='ODbL')
# 3. creeks: OMCA/SFEI historical creeks (CNRA service), clipped to the study window
r = requests.get('https://gis.cnra.ca.gov/arcgis/rest/services/Ocean/CSMW_San_Francisco_Bay_Historical_Creeks/MapServer/0/query', params=dict(where='1=1', geometry='-122.52,37.70,-122.40,37.80', geometryType='esriGeometryEnvelope', inSR=4326, spatialRel='esriSpatialRelIntersects', outFields='*', f='geojson'), timeout=60)
win = box(-122.5200, 37.7200, -122.4400, 37.8000)
for f in r.json().get('features', []):
    g = shape(f['geometry']).intersection(win)
    if g.is_empty or g.length < 1e-4: continue
    p = f['properties']; nm = (p.get('NAME') or '').strip()
    add(g, kind='creek', name=nm or 'unnamed historical creek', stream_type=p.get('STREAM_TYPE'), source='Oakland Museum of California / SFEI / William Lettis & Associates historical creeks (CNRA ArcGIS service CSMW_San_Francisco_Bay_Historical_Creeks, layer 0)', confidence='as drawn by OMCA; mostly east of the study core', licence='not stated on the service [unverified]')
# 4. Lobos Creek (modern alignment of the historic channel) from OSM
q = '[out:json][timeout:60];(way["waterway"~"stream|river|drain|canal"]["name"~"Lobos|Mountain Lake|Sutro|Lake Merced"](37.70,-122.53,37.80,-122.43););out geom;'
try:
    o = requests.post('https://overpass-api.de/api/interpreter', data={'data': q}, timeout=90, headers={'User-Agent': 'territory-precolonial/1.0'}).json()
    for el in o.get('elements', []):
        add(LineString([(p['lon'], p['lat']) for p in el['geometry']]), kind='creek', name=el['tags'].get('name', 'unnamed'), source=f'OSM way {el["id"]} (ODbL), modern mapped alignment; Lobos Creek is the Presidio creek that drained the western dunes; historic alignment not independently verified', confidence='medium', licence='ODbL')
except Exception as ex: print('overpass lobos failed', ex)
json.dump({'type': 'FeatureCollection', 'name': 'CALACADEMY_PRECOLONIAL_WATER', 'features': feats}, open(OUT / f'CALACADEMY_PRECOLONIAL_WATER_{TAG}.geojson', 'w'), ensure_ascii=False)
from collections import Counter
print(Counter((f['properties']['kind'], f['properties']['name']) for f in feats))
