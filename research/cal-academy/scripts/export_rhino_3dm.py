#!/usr/bin/env python3
"""Write the Cal Academy site as a Rhino 3dm: lidar DSM mesh, the building massing from the game layout, and every
splat in game/assets/splats/manifest.json as a coloured point cloud, all registered in ONE frame.

Frame: the game frame turned Z-up for Rhino. game (X, Y up, Z) -> rhino (x, y, z) = (X, -Z, Y). Metres.
X = building long axis (east is -X), y = north-ish (+y = concourse side), z up from the main floor (77.05 m NAVD88).
UTM 10N: E = 547023.23 + ..., see the FRAME layer text dot (rotation 137.5 deg about the centre).

    python research/cal-academy/scripts/export_rhino_3dm.py            # -> rhino/CALACADEMY_SITE_<date>A.3dm
    python research/cal-academy/scripts/export_rhino_3dm.py --pad 80 --coarse 2 --max-points 400000
"""
import argparse, datetime, json, math, pathlib, sys
import numpy as np
import rhino3dm as r3
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parents[3]; A = ROOT / 'game' / 'assets'

# ---- layout numbers (game/src/layout.js) ------------------------------------------------------------------------
LV = dict(b2=-12.5, aquarium=-7.6, main=0, mezz=4.6, roofSlab=9.6, deck=11.45, crown=19.3)
BBOX = (-84.5, 84.5, -54.5, 55.5)                        # x0 x1 z0 z1
DOME_R = 13.7
BOXES = [  # name, x0, x1, z0, z1, y0, y1
    ('African Hall', 50, 84, -54, -20, 0, 9.2), ('Penguins (sealed)', 72, 84, -54, -40, 0, 4.6), ('Academy Cafe', 56, 84, 10, 36, 0, 4.6),
    ('Terrace + auditorium', -84.5, -50, -54.5, -30, 0, 4.6), ('Rainforest airlock', -17, -11, 0, 8, 0, 3.2),
    ('Research wing NE', -84.5, -40, 36, 55.5, 0, 9.6), ('Research wing NW', 40, 84.5, 36, 55.5, 0, 9.6), ('Store', -20, 20, -54.5, -44, 0, 4.6),
    ('Philippine Coral Reef', -59, -45, -33, -23, -7.6, 0), ('Reef Lagoon', -19, 3, -34.5, -25.5, -1.6, 0), ('California Coast', 21, 39, -42, -34, -7.6, -1.0),
    ('Piazza skylight (opening)', -10, 10, 3 - 13.7, 3 + 13.7, 9.6, 9.7), ('West stair', 86.5, 89.5, 20, 28, 0, 11.45),
]
CYLS = [('Morrison Planetarium', 29, 4, DOME_R, 5.6, 'sphere'), ('Osher Rainforest', -29, 4, DOME_R, 5.6, 'sphere'),
        ('The Swamp (sealed)', 14, 28, 6, (-7.6, 0), 'cyl'), ('Amazon Flooded Forest (sealed)', -29, 4, 11, (-7.6, -1.0), 'cyl'),
        ('Dive Tower lift', -92, -40, 2.6, (0, 11.45), 'cyl')]


def P(x, y, z):  # game -> rhino
    return r3.Point3d(float(x), float(-z), float(y))


def layer(model, name, color, parent=None):
    l = r3.Layer(); l.Name = name; l.Color = color
    if parent is not None: l.ParentLayerId = parent
    idx = model.Layers.Add(l); return idx, model.Layers[idx].Id


def attrs(layer_index, name=None):
    a = r3.ObjectAttributes(); a.LayerIndex = layer_index
    if name: a.Name = name
    return a


def dsm_mesh(meta, h, g, bld, j0, j1, i0, i1, step):
    res = meta['res_m']
    jj = np.arange(j0, j1, step); ii = np.arange(i0, i1, step)
    X = -meta['width_m'] / 2 + ii * res; Z = -meta['height_m'] / 2 + jj * res
    m = r3.Mesh(); nj, ni = len(jj), len(ii)
    cGround, cTree, cRoof, cHigh = (27, 42, 36), (59, 107, 69), (110, 122, 90), (184, 194, 154)
    for a, j in enumerate(jj):
        for b, i in enumerate(ii):
            y = h[j, i]; m.Vertices.Add(float(X[b]), float(-Z[a]), float(y))
            above = y - g[j, i]
            if bld[j, i]: t = min(max((y - LV['deck']) / 8, 0), 1); c = tuple(int(cRoof[k] + (cHigh[k] - cRoof[k]) * t) for k in range(3))
            elif above > 2.5: t = min(max((above - 3) / 25, 0), 0.8); c = tuple(int(cTree[k] + (cHigh[k] - cTree[k]) * t) for k in range(3))
            else: c = cGround
            m.VertexColors.Add(c[0], c[1], c[2])
    for a in range(nj - 1):
        for b in range(ni - 1):
            k = a * ni + b; m.Faces.AddFace(k, k + 1, k + ni + 1, k + ni)
    m.Normals.ComputeNormals(); m.Compact(); return m


def read_splat_ply(path, max_points):
    from plyfile import PlyData
    v = PlyData.read(str(path))['vertex'].data
    n = len(v); idx = np.arange(n)
    if n > max_points: idx = np.random.default_rng(0).choice(n, max_points, replace=False)
    xyz = np.stack([v['x'][idx], v['y'][idx], v['z'][idx]], 1).astype(np.float64)
    if 'f_dc_0' in v.dtype.names:
        rgb = np.clip(0.5 + 0.28209479177 * np.stack([v['f_dc_0'][idx], v['f_dc_1'][idx], v['f_dc_2'][idx]], 1), 0, 1)
    elif 'red' in v.dtype.names: rgb = np.stack([v['red'][idx], v['green'][idx], v['blue'][idx]], 1) / 255
    else: rgb = np.full((len(idx), 3), 0.6)
    if 'opacity' in v.dtype.names:
        keep = 1 / (1 + np.exp(-v['opacity'][idx])) > 0.3; xyz, rgb = xyz[keep], rgb[keep]
    return xyz, (rgb * 255).astype(int)


def manifest_matrix(e, meta):
    """4x4 (numpy) taking scan coords into the game frame, as splats.js does."""
    M = np.eye(4)
    if isinstance(e.get('matrix'), list) and len(e['matrix']) == 16: M = np.array(e['matrix'], float).reshape(4, 4)
    else:
        p = e.get('position') or e.get('guess') or [0, 0, 0]; M[:3, 3] = p
        if e.get('rotationDeg'):
            rx, ry, rz = [math.radians(a) for a in e['rotationDeg']]
            Rx = np.array([[1, 0, 0], [0, math.cos(rx), -math.sin(rx)], [0, math.sin(rx), math.cos(rx)]]); Ry = np.array([[math.cos(ry), 0, math.sin(ry)], [0, 1, 0], [-math.sin(ry), 0, math.cos(ry)]]); Rz = np.array([[math.cos(rz), -math.sin(rz), 0], [math.sin(rz), math.cos(rz), 0], [0, 0, 1]])
            M[:3, :3] = Rz @ Ry @ Rx
        s = e.get('scale', 1); M[:3, :3] *= s
    if e.get('frame') == 'utm10n':
        th = math.radians(meta['rotation_deg_applied']); c, s = math.cos(th), math.sin(th); E0, N0 = meta['centre_utm10n']; g0 = meta['ground_m']
        T = np.array([[c, -s, 0, -(c * E0 - s * N0)], [0, 0, 1, -g0], [-s, -c, 0, (s * E0 + c * N0)], [0, 0, 0, 1]])
        M = T @ M
    if e.get('yDown'): M = M @ np.diag([1, -1, -1, 1])
    return M


def add_drawings(model):
    """DRAWINGS layer group: per RPBW sheet a textured 1:1 raster plane + traced vector polylines, from
    data/cal-academy/drawings/DRAWINGS_REGISTRATION_*.json (made by drawings_register.py). (c) RPBW, reference only."""
    reg_files = sorted((ROOT / 'data' / 'cal-academy' / 'drawings').glob('DRAWINGS_REGISTRATION_*.json'))
    if not reg_files: print('no DRAWINGS registration json; skipping', file=sys.stderr); return
    reg = json.load(open(reg_files[-1]))
    L_root, id_root = layer(model, 'DRAWINGS', (90, 90, 90, 255))
    for e in reg['sheets']:
        if not e.get('placed'): continue
        cls, sid = e['cls'], e['sheet']
        unplaced = e['cls'] == 'detail'
        tag = f"{cls} {sid}" + (' UNPLACED' if unplaced else '')
        s = e['scale_m_per_px']; s = s if isinstance(s, (int, float)) else (s[0] if abs(s[0] - s[1]) < 1e-9 else f'{s[0]:.4f}x{s[1]:.4f}')
        desc = f"{sid} | {cls} | {s if isinstance(s, str) else f'{s:.4f}'} m/px | {e['plane']} | conf {e['conf']} | {e['method']}"
        # raster plane
        li, _ = layer(model, tag, (60, 60, 60, 255), id_root)
        png = e['raster_png']
        mat = r3.Material(); mat.Name = f'DRAWING {sid}'
        mat.DiffuseColor = (255, 255, 255, 255); mat.AmbientColor = (255, 255, 255, 255)
        try: mat.SetBitmapTexture(png)
        except Exception as ex: print('texture failed', sid, ex, file=sys.stderr)
        midx = model.Materials.Add(mat)
        bl, br, tr, tl = [r3.Point3d(*c) for c in e['corners_bl_br_tr_tl']]
        mesh = r3.Mesh()
        for p_ in (bl, br, tr, tl): mesh.Vertices.Add(p_.X, p_.Y, p_.Z)
        mesh.Faces.AddFace(0, 1, 2, 3)
        wv = np.array([br.X - bl.X, br.Y - bl.Y, br.Z - bl.Z]); hv = np.array([tl.X - bl.X, tl.Y - bl.Y, tl.Z - bl.Z])
        w_, h_ = float(np.linalg.norm(wv)), float(np.linalg.norm(hv)); wv, hv = wv / w_, hv / h_
        pln = r3.Plane(bl, r3.Vector3d(*wv), r3.Vector3d(*hv))
        tm = r3.TextureMapping.CreatePlaneMapping(pln, r3.Interval(0, w_), r3.Interval(0, h_), r3.Interval(0, 1))
        mesh.SetTextureCoordinates(tm, r3.Transform.Identity(), False)
        mesh.Normals.ComputeNormals(); mesh.Compact()
        at = attrs(li, f'{desc} | raster {png}')
        at.MaterialIndex = midx; at.MaterialSource = r3.ObjectMaterialSource.MaterialFromObject
        at.SetUserString('png', png); at.SetUserString('registration', desc); at.SetUserString('licence', 'RPBW / Fondazione Renzo Piano copyright, reference use only')
        model.Objects.AddMesh(mesh, at)
        # traced vectors
        vf = e.get('vector_json')
        if vf and pathlib.Path(vf).exists():
            lv, _ = layer(model, f'{tag} vector', (80, 80, 80, 255) if e.get('vector') == 'traced' else (0, 0, 0, 255), id_root)
            n = 0
            for pts in json.load(open(vf))['polylines3d']:
                if len(pts) < 2: continue
                at2 = attrs(lv, f'{sid} TRACED {s if isinstance(s, str) else f"{s:.4f}"} m/px {e["plane"]}')
                at2.ColorSource = r3.ObjectColorSource.ColorFromObject; at2.ObjectColor = (80, 80, 80, 255)
                model.Objects.AddPolyline(r3.Polyline([r3.Point3d(*p_) for p_ in pts]), at2); n += 1
            print('drawing', sid, 'raster + ', n, 'traced polylines', file=sys.stderr)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--pad', type=float, default=60); ap.add_argument('--coarse', type=int, default=4); ap.add_argument('--max-points', type=int, default=400000)
    ap.add_argument('--out', default=None); ap.add_argument('--no-open', action='store_true')
    a = ap.parse_args()
    meta = json.load(open(A / 'site_meta.json'))
    dsm = np.asarray(Image.open(A / 'site_dsm_rg.png').convert('RGB')).astype(np.float64)
    dtm = np.asarray(Image.open(A / 'site_dtm_rg.png').convert('RGB')).astype(np.float64)
    bld = np.asarray(Image.open(A / 'site_bldg_mask.png').convert('L')) > 127
    h = (dsm[..., 0] * 256 + dsm[..., 1]) * meta['z_scale'] + meta['z_base_m'] - meta['ground_m']
    g = (dtm[..., 0] * 256 + dtm[..., 1]) * meta['z_scale'] + meta['z_base_m'] - meta['ground_m']
    H, W = h.shape; res = meta['res_m']

    model = r3.File3dm(); model.Settings.ModelUnitSystem = r3.UnitSystem.Meters
    note = ('Cal Academy site, game frame turned Z-up: rhino (x,y,z) = (game X, -game Z, game Y). Metres. Origin = building centre at the main floor '
                   f"(77.05 m NAVD88). UTM 10N centre E {meta['centre_utm10n'][0]:.2f} N {meta['centre_utm10n'][1]:.2f}; the game frame is rotated {meta['rotation_deg_applied']} deg from grid north. "
                   'Made by research/cal-academy/scripts/export_rhino_3dm.py from the 2023 USGS 3DEP lidar (public domain), game/src/layout.js and game/assets/splats/manifest.json.')
    try: model.Strings.SetString('note', note)
    except Exception: pass
    L_lidar, _ = layer(model, 'LIDAR 2023 DSM 0.5 m', (120, 130, 100, 255))
    L_lidar2, _ = layer(model, 'LIDAR 2023 DSM coarse', (160, 170, 140, 255))
    L_bldg, _ = layer(model, 'BUILDING massing', (60, 60, 60, 255))
    L_levels, _ = layer(model, 'LEVELS', (0, 0, 0, 255))
    L_names, _ = layer(model, 'NAMES', (0, 0, 0, 255))
    L_splat, id_splat = layer(model, 'SPLATS', (255, 68, 0, 255))
    L_frame, _ = layer(model, 'FRAME', (44, 146, 255, 255))
    def dot(tp, at): model.Objects.AddTextDot(tp[0], tp[1], at)

    # lidar
    x0, y0, x1, y1 = meta['bldg_bbox_px']; p = int(a.pad / res)
    j0, j1, i0, i1 = max(0, y0 - p), min(H, y1 + p), max(0, x0 - p), min(W, x1 + p)
    print('DSM fine', (j1 - j0), 'x', (i1 - i0), file=sys.stderr)
    model.Objects.AddMesh(dsm_mesh(meta, h, g, bld, j0, j1, i0, i1, 1), attrs(L_lidar, 'lidar 2023 DSM 0.5 m, building + %d m' % int(a.pad)))
    model.Objects.AddMesh(dsm_mesh(meta, h, g, bld, 0, H, 0, W, a.coarse), attrs(L_lidar2, 'lidar 2023 DSM %.1f m, whole tile' % (res * a.coarse)))

    # building massing
    bx0, bx1, bz0, bz1 = BBOX
    def box(name, X0, X1, Z0, Z1, Y0, Y1, lay):
        bb = r3.BoundingBox(P(X0, Y0, Z1), P(X1, Y1, Z0))  # -z flips the second axis
        brep = r3.Brep.CreateFromBox(r3.Box(bb)); model.Objects.AddBrep(brep, attrs(lay, name))
        dot((name, P((X0 + X1) / 2, Y1, (Z0 + Z1) / 2)), attrs(L_names, name))
    box('Building envelope (roof slab)', bx0, bx1, bz0, bz1, LV['roofSlab'], LV['roofSlab'] + 0.3, L_bldg)
    box('Main floor slab', bx0, bx1, bz0, bz1, -0.3, 0, L_bldg)
    box('Aquarium level slab', bx0, bx1, bz0, bz1, LV['aquarium'] - 0.3, LV['aquarium'], L_bldg)
    for n, X0, X1, Z0, Z1, Y0, Y1 in BOXES: box(n, X0, X1, Z0, Z1, Y0, Y1, L_bldg)
    for n, x, z, rad, yy, kind in CYLS:
        if kind == 'sphere':
            model.Objects.AddBrep(r3.Brep.CreateFromSphere(r3.Sphere(P(x, yy, z), rad)), attrs(L_bldg, n)); dot((n, P(x, yy + rad, z)), attrs(L_names, n))
        else:
            y0_, y1_ = yy; cyl = r3.Cylinder(r3.Circle(P(x, y0_, z), rad), y1_ - y0_)
            model.Objects.AddBrep(r3.Brep.CreateFromCylinder(cyl, True, True), attrs(L_bldg, n)); dot((n, P(x, y1_, z)), attrs(L_names, n))
    # whale line
    model.Objects.AddLine(P(-64 - 13, 6.4, 6), P(-64 + 13, 6.4, 6), attrs(L_bldg, 'Blue whale skeleton, 26 m, over Giants of Land and Sea'))
    # level rectangles
    for n, y in LV.items():
        pl = r3.Polyline([P(bx0, y, bz0), P(bx1, y, bz0), P(bx1, y, bz1), P(bx0, y, bz1), P(bx0, y, bz0)])
        model.Objects.AddPolyline(pl, attrs(L_levels, f'{n} {y:+.2f} m')); dot((f'{n} {y:+.2f}', P(bx1 + 4, y, bz1)), attrs(L_levels, n))

    # splats
    man = json.load(open(A / 'splats' / 'manifest.json'))
    for e in man.get('scans', []):
        f = A / 'splats' / e['file']
        if not f.exists() or e.get('enabled') is False: continue
        xyz, rgb = read_splat_ply(f, a.max_points); M = manifest_matrix(e, meta)
        pts = (M[:3, :3] @ xyz.T).T + M[:3, 3]
        pc = r3.PointCloud()
        for (x, y, z), (r, g_, b) in zip(pts, rgb): pc.Add(P(x, y, z), (int(r), int(g_), int(b), 255))
        li, _ = layer(model, f"SPLAT {e.get('space', e['file'])}", (255, 68, 0, 255), id_splat)
        model.Objects.AddPointCloud(pc, attrs(li, f"{e.get('space')} · {e['file']} · frame {e.get('frame')} · {len(pts)} pts"))
        print('splat', e.get('space'), len(pts), 'points', file=sys.stderr)

    # raw lidar point cloud(s) in the game frame, from scripts/lidar_laz_to_game.py
    L_pc, id_pc = layer(model, 'POINTCLOUD lidar 2023 (90 pts/m2)', (90, 90, 90, 255))
    for f in sorted((ROOT / 'data' / 'cal-academy' / 'lidar2023').glob('*_game.ply')):
        xyz, rgb = read_splat_ply(f, a.max_points)
        pc = r3.PointCloud()
        for (x, y, z), (r, g_, b) in zip(xyz, rgb): pc.Add(P(x, y, z), (int(r), int(g_), int(b), 255))
        li, _ = layer(model, f'POINTCLOUD {f.stem}', (90, 90, 90, 255), id_pc)
        model.Objects.AddPointCloud(pc, attrs(li, f'{f.name} · {len(xyz)} pts of the 2023 USGS 3DEP cloud, game frame'))
        print('pointcloud', f.name, len(xyz), 'points', file=sys.stderr)

    # frame
    model.Objects.AddLine(P(0, 0, 0), P(50, 0, 0), attrs(L_frame, 'game +X (building long axis; east is -X), 50 m'))
    model.Objects.AddLine(P(0, 0, 0), P(0, 0, -50), attrs(L_frame, 'game -Z = rhino +y (towards the concourse, north side), 50 m'))
    model.Objects.AddLine(P(0, 0, 0), P(0, 50, 0), attrs(L_frame, 'game +Y = rhino +z (up), 50 m'))
    nx, ny = meta['north_vec_xy']  # rotated-frame (x right, y up) vector; rhino y = that y
    model.Objects.AddLine(P(0, 0, 0), r3.Point3d(nx * 80, ny * 80, 0), attrs(L_frame, 'TRUE NORTH, 80 m'))
    dot((f"ORIGIN = main floor, building centre · UTM10N E {meta['centre_utm10n'][0]:.1f} N {meta['centre_utm10n'][1]:.1f} · NAVD88 {meta['ground_m']:.2f} m · frame rotated {meta['rotation_deg_applied']} deg", P(0, 0, 0)), attrs(L_frame, 'origin'))

    add_drawings(model)

    out = pathlib.Path(a.out) if a.out else ROOT / 'rhino' / f"CALACADEMY_SITE_{datetime.date.today().strftime('%Y_%m_%d')}A.3dm"
    out.parent.mkdir(parents=True, exist_ok=True); ok = model.Write(str(out), 8)
    print('wrote' if ok else 'FAILED', out, out.stat().st_size // 1024 if out.exists() else 0, 'KB')


if __name__ == '__main__':
    main()
