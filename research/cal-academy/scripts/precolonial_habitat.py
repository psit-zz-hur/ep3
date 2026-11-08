#!/usr/bin/env python3
"""Pre-colonial habitat class raster for the Golden Gate Park / Outer Lands territory.
Grid CW = grid C (EPSG:32610, E 544023..550023, N 4177411..4183411, 5 m) extended 1500 m west (Ocean Beach) and 1000 m south (Lake Merced):
E 542523..550023, N 4172411..4183411, 1500 x 2200.  Grid C itself is written as an exact clip.
Inputs: the georeferenced 1852 T-sheet features (precolonial_georef.py + precolonial_features.py), USGS 1 m bare-earth DEM tiles, OSM (modern outlines of
the pre-city lakes only), the OMCA/SFEI historical creeks layer (CNRA service).  See research/cal-academy/21-precolonial-sources-2026_11_07A.md METHOD.
    python -X utf8 research/cal-academy/scripts/precolonial_habitat.py
"""
import csv, glob, json, pathlib, sys, numpy as np, cv2, rasterio
from rasterio.transform import Affine
from rasterio.crs import CRS
from rasterio.warp import reproject
from rasterio.enums import Resampling
from rasterio.features import rasterize, shapes
from scipy import ndimage as ndi
from pyproj import Transformer
sys.path.insert(0, str(pathlib.Path(__file__).parent))
ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = ROOT / 'exports' / 'territory' / 'precolonial'
PRE = ROOT / 'data' / 'cal-academy' / 'precolonial'
TAG = '2026_11_07A'
CRS32610 = CRS.from_epsg(32610)
X0, Y1, W, H, RES = 542523, 4183411, 1500, 2200, 5
TR = Affine(RES, 0, X0, 0, -RES, Y1)
C_OFF = (1500 // RES, 0)   # grid C starts at col 300, row 0, size 1200x1200 inside CW
PAL = {0: ('unknown / open sea', '#b9c4c9'), 1: ('beach strand', '#e8dcc0'), 2: ('foredune / bare sand dune', '#d9c8a0'), 3: ('dune scrub', '#8f9a7a'),
       4: ('coastal prairie / dune grass', '#c9b87a'), 5: ('coastal scrub', '#6f7f5a'), 6: ('willow riparian', '#4a5f3a'), 7: ('freshwater marsh', '#6a8f6a'),
       8: ('lake', '#5b8fb5'), 9: ('rocky shore', '#7a7066'), 10: ('oak-bay woodland', '#4f5f3f')}

def dem_cw():
    p = PRE / 'dem_cw_5m.npy'
    if p.exists(): return np.load(p)
    acc = np.zeros((H, W)); cnt = np.zeros((H, W))
    for t in sorted(glob.glob(str(ROOT / 'data' / 'cal-academy' / 'dem' / 'USGS_1M_10_x5[45]y41[89]_CA*.tif'))):
        with rasterio.open(t) as s:
            tmp = np.full((H, W), -9999, np.float32)
            reproject(rasterio.band(s, 1), tmp, dst_transform=TR, dst_crs=CRS32610, src_nodata=s.nodata, dst_nodata=-9999, resampling=Resampling.average)
            m = tmp != -9999; acc[m] += tmp[m]; cnt[m] += 1
    d = np.where(cnt > 0, acc / np.maximum(cnt, 1), np.nan).astype(np.float32); np.save(p, d); return d

def sheet_features():
    g = json.load(open(OUT / f'CALACADEMY_TSHEET_T00382_GEOREF_{TAG}.json'))
    a = g['affine_px_to_utm10n']; aff = Affine(*a)
    f = np.load(PRE / 't00382_features_f6.npz'); F = int(f['F'])
    aff6 = aff * Affine.scale(F)
    ink = cv2.GaussianBlur(f['ink'], (0, 0), 3); red = cv2.GaussianBlur(f['red'], (0, 0), 3); dark = cv2.GaussianBlur(f['dark'], (0, 0), 3)
    content = (ink > 0.004) | (red > 0.004)
    # restrict to the drawn map area: east cut-off of the survey ~ px 6430 (col 1071), title block above row 330
    content[:, 1075:] = False; content[:330] = False
    closed = cv2.morphologyEx(content.astype(np.uint8), cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (31, 31))).astype(bool)
    filled = ndi.binary_fill_holes(closed)
    # beach/coast: ocean side is open so not filled; lakes are enclosed holes
    holes = filled & ~closed
    lab, n = ndi.label(holes); sizes = ndi.sum(holes, lab, range(1, n + 1))
    cy = ndi.center_of_mass(holes, lab, range(1, n + 1))
    lake = np.isin(lab, [i + 1 for i, s in enumerate(sizes) if s >= 120 and cy[i][0] > 500])    # >= 120 cells ~ 3 ha; rows < 500 (y < 3000 px) are the blank margin under the title
    valid = filled.copy(); valid[:, 1070:] = False   # drawn survey ends at sheet px ~6430 (col 1071)
    stack = np.stack([ink, dark, red, lake.astype(np.float32), valid.astype(np.float32)])
    out = np.zeros((5, H, W), np.float32)
    for i in range(5):
        reproject(stack[i], out[i], src_transform=aff6, src_crs=CRS32610, dst_transform=TR, dst_crs=CRS32610, resampling=Resampling.bilinear)
    return out, (lake, valid, aff6)

def main():
    dem = dem_cw(); ocean_nan = ~np.isfinite(dem)
    lab, n = ndi.label(ocean_nan); edge = set(lab[:, 0]) | set(lab[0, :]); edge.discard(0)
    ocean = np.isin(lab, list(edge))
    dz = np.where(np.isfinite(dem), dem, 0).astype(np.float32)
    gy, gx = np.gradient(dz, RES); slope = np.degrees(np.arctan(np.hypot(gx, gy)))
    shore = ndi.distance_transform_edt(~ocean) * RES            # metres from ocean (0 at ocean)
    ink, dark, red, lake_f, valid_f = sheet_features()[0]
    sheet = valid_f > 0.5
    ink_c = cv2.GaussianBlur(ink, (0, 0), 5)      # 25 m smoothing for the symbol-density classes (hatch rows alias at cell scale)
    dz_s = cv2.GaussianBlur(dz, (0, 0), 2); gy2, gx2 = np.gradient(dz_s, RES); slope_s = np.degrees(np.arctan(np.hypot(gx2, gy2)))
    cls = np.zeros((H, W), np.uint8); conf = np.zeros((H, W), np.uint8)
    land = ~ocean
    # --- 1. sheet symbols (confidence 3) ---
    grass = sheet & land & (ink_c > 0.018)
    bare = sheet & land & (ink_c < 0.007) & (lake_f < 0.5)
    mid = sheet & land & ~grass & ~bare & (lake_f < 0.5)
    cls[grass] = 4; cls[bare] = 2; cls[mid] = 3; conf[sheet & land] = 3
    # dark symbol clumps: willow (near water) / scrub / stippled ponds (marsh)
    water_sheet = lake_f > 0.5
    dwater = ndi.distance_transform_edt(~water_sheet) * RES
    darkclump = sheet & land & (dark > 0.035) & (shore > 250) & (lake_f < 0.5)
    dl, dn = ndi.label(darkclump); dsz = ndi.sum(darkclump, dl, range(1, dn + 1))
    darkclump = np.isin(dl, [i + 1 for i, z in enumerate(dsz) if z >= 40])      # drop survey-station dots and letters (< 1000 m2)
    low = dz < 12
    cls[darkclump & low & (dwater < 600)] = 6
    cls[darkclump & low & (dwater >= 600) & (shore < 900)] = 7      # stippled ponds / wet hollows behind the dunes (Sunset sloughs)
    cls[darkclump & ~(low & (dwater < 900))] = 5
    cls[water_sheet & sheet] = 8
    # --- 2. extrapolation outside the sheet (confidence 1): nearest sheet class within 1.5 km, steep/high ground scrub, else prairie ---
    ref = (cls > 0) & (conf == 3) & np.isin(cls, [2, 3, 4])
    rf = ref.astype(np.float32)
    norm = cv2.GaussianBlur(rf, (0, 0), 120)                       # normalized convolution, sigma 600 m: smooth carry-over of the sheet's mix into unmapped ground
    wk = np.stack([cv2.GaussianBlur((ref & (cls == k)).astype(np.float32), (0, 0), 120) / np.maximum(norm, 1e-6) for k in (2, 3, 4)])
    pick = np.array([2, 3, 4], np.uint8)[wk.argmax(0)]
    pick = np.where(norm < 0.01, 4, pick)
    ext = land & ~sheet
    cls[ext] = pick[ext]; conf[ext] = 1
    hill = ext & ((dz > 110) | (slope_s > 18)); cls[hill] = 5
    # --- 3. modern pre-city lakes outside the sheet's coverage (Mountain Lake, Laguna Honda, Pine Lake) from OSM, confidence 2 ---
    osm = json.load(open(PRE / 'osm_ref.json')) if (PRE / 'osm_ref.json').exists() else None
    t = Transformer.from_crs(4326, 32610, always_xy=True)
    polys = []
    if osm:
        keep = {16650677: 'Mountain Lake', 30969894: 'Laguna Honda', 31860201: 'Pine Lake'}
        for el in osm['elements']:
            if el['type'] == 'way' and el['id'] in keep and 'geometry' in el:
                ring = [t.transform(p['lon'], p['lat']) for p in el['geometry']]
                polys.append({'type': 'Polygon', 'coordinates': [ring]})
    if polys:
        lk = rasterize([(p, 1) for p in polys], out_shape=(H, W), transform=TR, fill=0, dtype=np.uint8).astype(bool)
        add = lk & ~(sheet & ~(cls == 8) & False)
        cls[lk] = 8; conf[lk] = np.maximum(conf[lk], 2)
    water = cls == 8
    # --- 4. marsh fringe: 0-60 m around lakes, low flat ground (confidence 1) ---
    dw = ndi.distance_transform_edt(~water) * RES
    fringe = land & (dw > 0) & (dw <= 60) & (dz < 15) & (slope < 4) & ~water & np.isin(cls, [2, 3, 4])
    cls[fringe] = 7; conf[fringe] = 1
    # --- 5. DTM rules (confidence 2): beach strand, rocky shore at Lands End / Sutro ---
    N_arr = Y1 - (np.arange(H) + 0.5) * RES; Narr = np.broadcast_to(N_arr[:, None], (H, W))
    beach = land & (dz < 3.0) & (shore <= 300) & ~water
    cls[beach] = 1; conf[beach] = 2
    rocky = land & (shore <= 150) & (slope > 30) & (Narr > 4181300) & ~water
    cls[rocky] = 9; conf[rocky] = 2
    cls[ocean] = 0; conf[ocean] = 0
    # keep isolated 1-3 cell specks out of the legend: median-ish cleanup on prairie/bare/scrub only
    sm = ndi.median_filter(cls, size=3)
    mask = np.isin(cls, [2, 3, 4]) & np.isin(sm, [2, 3, 4]); cls[mask] = sm[mask]
    # --- write ---
    def wr(path, arr, desc, nodata=None):
        with rasterio.open(path, 'w', driver='GTiff', height=arr.shape[0], width=arr.shape[1], count=1, dtype='uint8', crs=CRS32610, transform=TR if arr.shape == (H, W) else Affine(RES, 0, 544023, 0, -RES, 4183411),
                           compress='deflate', tiled=True, blockxsize=256, blockysize=256, nodata=nodata) as d:
            d.write(arr[None]); d.update_tags(DESCRIPTION=desc)
    d0 = 'Pre-colonial habitat classes 0 unknown/sea 1 beach 2 foredune 3 dune scrub 4 coastal prairie 5 coastal scrub 6 willow 7 marsh 8 lake 9 rocky shore 10 oak-bay; see legend csv + METHOD in 21-precolonial-sources md'
    cw_p = OUT / f'CALACADEMY_PRECOLONIAL_HABITAT_5m_CW_UTM10N_{TAG}.tif'; wr(cw_p, cls, d0)
    r0, c0 = C_OFF[1], C_OFF[0]
    wr(OUT / f'CALACADEMY_PRECOLONIAL_HABITAT_5m_UTM10N_{TAG}.tif', cls[r0:r0 + 1200, c0:c0 + 1200].copy(), d0)
    wr(OUT / f'CALACADEMY_PRECOLONIAL_HABITAT_CONF_5m_CW_UTM10N_{TAG}.tif', conf, 'confidence 3 = T-sheet symbol read, 2 = DTM rule or modern outline of a pre-city lake, 1 = extrapolated/fringe rule, 0 = none')
    with open(OUT / f'CALACADEMY_PRECOLONIAL_HABITAT_LEGEND_{TAG}.csv', 'w', newline='', encoding='utf8') as f:
        wcsv = csv.writer(f); wcsv.writerow(['code', 'class', 'colour_hex', 'cells_C', 'pct_C_land', 'cells_CW', 'main_source', 'confidence'])
        srcs = {0: 'DEM no-data = open sea; plus unclassified', 1: 'DTM < 3 m within 300 m of the shoreline', 2: 'T00382 blank (symbol-free) ground = bare drifting sand ("Sand Hills")',
                3: 'T00382 sparse tufts (ecotone between bare sand and grass)', 4: 'T00382 grass-tuft symbol field', 5: 'T00382 dark scrub clumps off water; extrapolated hills/steep ground outside the sheet',
                6: 'T00382 dark clumps on low ground within 600 m of lakes', 7: 'T00382 stippled ponds / wet hollows + 60 m fringe of lakes (rule)', 8: 'T00382 enclosed blank water areas (Lake Merced etc.); OSM outline for Mountain Lake, Laguna Honda, Pine Lake',
                9: 'DTM slope > 30 deg within 150 m of the sea, N of 4181300 (Lands End / Sutro)', 10: 'none: no source in hand places oak-bay woodland in this window'}
        confs = {0: '-', 1: 'medium', 2: 'medium (sheet symbol, interpreted)', 3: 'low', 4: 'medium (sheet symbol, interpreted)', 5: 'low-medium', 6: 'low', 7: 'low', 8: 'high on the sheet, medium for modern outlines', 9: 'medium', 10: 'n/a'}
        cC = cls[r0:r0 + 1200, c0:c0 + 1200]; landC = (cC > 0).sum()
        for k in range(11):
            nC = int((cC == k).sum()); nW = int((cls == k).sum())
            wcsv.writerow([k, PAL[k][0], PAL[k][1], nC, round(100 * nC / max(landC, 1), 2) if k else '', nW, srcs[k], confs[k]])
    print('class counts (grid C):', {k: int((cC == k).sum()) for k in range(11)})
    print('class counts (grid CW):', {k: int((cls == k).sum()) for k in range(11)})
    print('conf counts (CW):', {k: int((conf == k).sum()) for k in range(4)})
    np.save(PRE / 'habitat_cw.npy', cls); np.save(PRE / 'habitat_dem_slope_cw.npy', np.stack([dz, slope, shore]))
    # lake polygons (sheet-derived) for the water geojson
    np.save(PRE / 'lake_sheet_cw.npy', (lake_f > 0.5) & sheet)
if __name__ == '__main__': main()
