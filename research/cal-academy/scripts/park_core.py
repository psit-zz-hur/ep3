#!/usr/bin/env python3
"""THE TERRITORY 2026-11-07: A whole-park core DSM 1 m (full EPT depth), C rim DSM 5 m (coarse octree levels, DTM-filled), D canopy heights.

    python -X utf8 research/cal-academy/scripts/park_core.py [core|rimscan|rim|canopy]     (rim needs: rim depth via env RIM_DEPTH, default 7)
Reuses territory_rasters (EPT walk, write_tif, verify) and territory_extra (grids, footprints, DEM resampling).
"""
import sys, os, json, time, pathlib, math, concurrent.futures as cf
import numpy as np, laspy, rasterio
from rasterio.features import rasterize
from pyproj import Transformer
from scipy import ndimage
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import territory_rasters as T
import territory_extra as E
from territory_rasters import OUT, TAG, ND, N, write_tif, verify, REG, reg_transform

M2U = None; M_BOX = None


def _init():
    global M2U
    M2U = Transformer.from_crs('EPSG:3857', 'EPSG:32610', always_xy=True)


def _node(args):
    k, x0, y1, W, H, res, mb = args
    las = laspy.read(N / f'{k}.laz')
    x = np.asarray(las.x); y = np.asarray(las.y)
    m = (x >= mb[0]) & (x <= mb[1]) & (y >= mb[2]) & (y <= mb[3])
    n_in = int(m.sum())
    if not m.any(): return k, None, None, 0, int(las.header.point_count)
    cl = np.asarray(las.classification)[m]; keep = (cl != 7) & (cl != 18)
    xx = x[m][keep]; yy = y[m][keep]; z = np.asarray(las.z)[m][keep].astype(np.float32)
    e, n = M2U.transform(xx, yy)
    col = np.floor((e - x0) / res).astype(np.int64); row = np.floor((y1 - n) / res).astype(np.int64)
    ok = (col >= 0) & (col < W) & (row >= 0) & (row < H)
    if not ok.any(): return k, None, None, 0, int(las.header.point_count)
    idx = row[ok] * W + col[ok]; z = z[ok]
    o = np.lexsort((z, idx)); idx = idx[o]; z = z[o]
    last = np.r_[idx[1:] != idx[:-1], True]
    return k, idx[last].astype(np.int64), z[last], int(ok.sum()), int(las.header.point_count)


def merge_nodes(keys, x0, y1, W, H, res, workers=18, label=''):
    inv = Transformer.from_crs('EPSG:32610', 'EPSG:3857', always_xy=True)
    xs, ys = [], []
    for dx in np.linspace(0, W * res, 9):
        for dy in np.linspace(0, H * res, 9):
            a, b = inv.transform(x0 + dx, y1 - dy); xs.append(a); ys.append(b)
    mb = (min(xs) - 30, max(xs) + 30, min(ys) - 30, max(ys) + 30)
    zmax = np.full(H * W, -np.inf, np.float32); pts = 0; seen = 0; t0 = time.time()
    with cf.ProcessPoolExecutor(workers, initializer=_init) as ex:
        futs = ex.map(_node, [(k, x0, y1, W, H, res, mb) for k in keys], chunksize=4)
        for i, (k, idx, z, n_ok, n_all) in enumerate(futs):
            seen += n_all; pts += n_ok
            if idx is not None:
                better = z > zmax[idx]; zmax[idx[better]] = z[better]
            if i % 500 == 0: print(f' {label} node {i}/{len(keys)} pts_in_grid {pts/1e6:.1f}M file_pts {seen/1e6:.1f}M {time.time()-t0:.0f}s', file=sys.stderr, flush=True)
    return zmax.reshape(H, W), pts, seen


def fill_small(z, r=3):
    valid = np.isfinite(z)
    dist, (ri, ci) = ndimage.distance_transform_edt(~valid, return_indices=True)
    fill = (~valid) & (dist <= r)
    out = np.where(valid, z, ND).astype(np.float32); out[fill] = z[ri[fill], ci[fill]]
    return out, int(valid.sum()), int(fill.sum())


def park_keys():
    h = json.load(open(T.D / 'lidar2023' / 'park_hier.json'))
    keys = [k for k in h if (N / f'{k}.laz').exists() and (N / f'{k}.laz').stat().st_size > 0]
    return h, keys


def core():
    P = E.PARK; h, keys = park_keys()
    miss = [k for k in h if k not in set(keys)]
    print('park nodes', len(h), 'on disk', len(keys), 'missing', len(miss), file=sys.stderr)
    maxd = max(int(k.split('-')[0]) for k in keys)
    z, pts, seen = merge_nodes(sorted(keys, key=lambda k: int(k.split('-')[0])), P['x0'], P['y1'], P['w'], P['h'], 1, label='core')
    dsm, nvalid, nfill = fill_small(z, 3)
    print('points inside grid (after class filter)', pts, 'file points scanned', seen, 'cells', dsm.size, 'valid', nvalid, 'filled', nfill, 'nodata', int((dsm == ND).sum()), file=sys.stderr)
    p = OUT / f'CALACADEMY_PARK_CORE_DSM_1m_UTM10N_{TAG}.tif'
    write_tif(p, dsm, E.park_transform(1), ND, f'DSM highest return, m NAVD88, EPT depth 0..{maxd} ({len(keys)} nodes), classes 7/18 dropped, holes<=3 cells NN-filled'); verify(p)
    json.dump({'nodes': len(keys), 'missing': len(miss), 'max_depth': maxd, 'points_in_grid': pts, 'points_scanned': seen, 'valid_cells': nvalid, 'filled': nfill}, open(OUT.parent.parent / 'data' / 'cal-academy' / 'lidar2023' / 'park_core_stats.json', 'w'))


# ---------- C: rim ----------
def region_hier():
    f = T.D / 'lidar2023' / 'region_hier.json'
    if f.exists(): return json.load(open(f))
    tr = Transformer.from_crs('EPSG:32610', 'EPSG:3857', always_xy=True)
    xs, ys = zip(*[tr.transform(REG['x0'] + a, REG['y1'] - b) for a in np.linspace(0, 6000, 7) for b in np.linspace(0, 6000, 7)])
    h = T.ept_nodes(min(xs) - 40, max(xs) + 40, min(ys) - 40, max(ys) + 40); json.dump(h, open(f, 'w')); return h


def rimscan():
    h = region_hier(); import collections
    c = collections.Counter(); p = collections.Counter(); miss = collections.Counter()
    for k, v in h.items():
        d = int(k.split('-')[0]); c[d] += 1; p[d] += v
        if not (N / f'{k}.laz').exists(): miss[d] += 1
    for d in sorted(c): print('depth', d, 'nodes', c[d], 'points', p[d], 'missing', miss[d], 'ground spacing m ~', round(21110.0 / 2 ** d / 128 / 1.2646, 2))


def rim():
    D = int(os.environ.get('RIM_DEPTH', '7')); h = region_hier()
    keys = [k for k in h if int(k.split('-')[0]) <= D]
    need = [k for k in keys if not (N / f'{k}.laz').exists()]
    print('rim depth <=', D, 'nodes', len(keys), 'to download', len(need), file=sys.stderr)
    if need: T.download({k: h[k] for k in need}, 10)
    keys = [k for k in keys if (N / f'{k}.laz').exists() and (N / f'{k}.laz').stat().st_size > 0]
    z, pts, seen = merge_nodes(keys, REG['x0'], REG['y1'], REG['w'], REG['h'], REG['res'], label='rim')
    dtm = rasterio.open(OUT / f'CALACADEMY_REGION_DTM_5m_UTM10N_{TAG}.tif').read(1)
    have = np.isfinite(z); dsm = np.where(have, z, ND).astype(np.float32)
    gap = (~have) & (dtm != ND); dsm[gap] = dtm[gap]
    print('rim cells', dsm.size, 'from cloud', int(have.sum()), 'DTM-filled', int(gap.sum()), 'nodata', int((dsm == ND).sum()), 'points', pts, file=sys.stderr)
    p = OUT / f'CALACADEMY_REGION_DSM_5m_UTM10N_{TAG}.tif'
    write_tif(p, dsm, reg_transform(), ND, f'DSM highest return per 5 m cell from EPT depth<= {D} ({len(keys)} nodes), classes 7/18 dropped; DTM where no return'); verify(p)
    np.save(OUT.parent.parent / 'data' / 'cal-academy' / 'lidar2023' / 'rim_cloudmask.npy', have)
    json.dump({'depth': D, 'nodes': len(keys), 'points': pts, 'cloud': int(have.sum()), 'dtm_filled': int(gap.sum()), 'nodata': int((dsm == ND).sum())}, open(OUT.parent.parent / 'data' / 'cal-academy' / 'lidar2023' / 'rim_stats.json', 'w'))


# ---------- D: canopy ----------
def canopy():
    items = E.bldg_polys()
    P = E.PARK
    for name, dsm_p, dtm_arr, tr, W, H in (
            ('PARK_CORE_CANOPY_1m', OUT / f'CALACADEMY_PARK_CORE_DSM_1m_UTM10N_{TAG}.tif', None, E.park_transform(1), P['w'], P['h']),
            ('REGION_CANOPY_5m', OUT / f'CALACADEMY_REGION_DSM_5m_UTM10N_{TAG}.tif', None, reg_transform(), REG['w'], REG['h'])):
        dsm = rasterio.open(dsm_p).read(1)
        dtm = rasterio.open(OUT / (f'CALACADEMY_PARK_CORE_DTM_1m_UTM10N_{TAG}.tif' if 'PARK' in name else f'CALACADEMY_REGION_DTM_5m_UTM10N_{TAG}.tif')).read(1)
        ok = (dsm != ND) & (dtm != ND)
        can = np.where(ok, np.maximum(dsm - dtm, 0), ND).astype(np.float32)
        from shapely.geometry import box
        L, B, R, Tp = tr.c, tr.f - H * tr.a, tr.c + W * tr.a, tr.f
        bx = box(L, B, R, Tp)
        polys = [(g, 1) for g, hh, f in items if not g.is_empty and g.intersects(bx)]
        mask = rasterize(polys, out_shape=(H, W), transform=tr, fill=0, dtype='uint8').astype(bool) if polys else np.zeros((H, W), bool)
        can[mask & ok] = 0
        p = OUT / f'CALACADEMY_{name}_UTM10N_{TAG}.tif'
        write_tif(p, can, tr, ND, 'canopy height = max(DSM - bare earth, 0), m; 0 inside DataSF building footprints; NoData where DSM or DTM missing'); verify(p)
        v = can[can != ND]; print(name, 'footprints', len(polys), 'masked cells', int(mask.sum()), 'canopy>2 m cells', int((v > 2).sum()), 'p99', float(np.percentile(v, 99)), file=sys.stderr)


if __name__ == '__main__':
    steps = dict(core=core, rimscan=rimscan, rim=rim, canopy=canopy)
    for s in sys.argv[1:]: print('==', s, file=sys.stderr); steps[s]()
