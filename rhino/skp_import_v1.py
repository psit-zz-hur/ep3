#! python 3
import math, os, traceback
import rhinoscriptsyntax as rs
import Rhino
import scriptcontext as sc
import System

LOG = r"C:\Users\bryan\Documents\Claude\ep3\rhino\skp_import_log.txt"
SKP = r"C:\Users\bryan\Documents\Claude\ep3\CALACADEMY_3D_ASSETS\CAS_3DWAREHOUSE_2014_SketchUp.skp"
OUT = r"C:\Users\bryan\Documents\Claude\ep3\rhino\CALACADEMY_SITE_2026_11_07C.3dm"
PARENT = "3D WAREHOUSE (2014 SketchUp massing)"

def log(s):
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(str(s) + "\n")

def verts_of(g):
    pts = []
    if isinstance(g, Rhino.Geometry.Mesh):
        pts = [Rhino.Geometry.Point3d(v) for v in g.Vertices]
    elif isinstance(g, Rhino.Geometry.Brep):
        pts = [v.Location for v in g.Vertices]
    elif isinstance(g, Rhino.Geometry.Extrusion):
        b = g.ToBrep()
        if b: pts = [v.Location for v in b.Vertices]
    elif isinstance(g, Rhino.Geometry.InstanceReferenceGeometry):
        pass
    return pts

def collect_vertices(ids):
    out = []
    for i in ids:
        o = sc.doc.Objects.FindId(i)
        if o is None: continue
        out.extend(verts_of(o.Geometry))
    return out

def bbox_of(ids):
    bb = Rhino.Geometry.BoundingBox.Empty
    for i in ids:
        o = sc.doc.Objects.FindId(i)
        if o is None: continue
        bb.Union(o.Geometry.GetBoundingBox(True))
    return bb

def fmt_bb(bb):
    return "min(%.2f,%.2f,%.2f) max(%.2f,%.2f,%.2f) size(%.2f,%.2f,%.2f)" % (
        bb.Min.X, bb.Min.Y, bb.Min.Z, bb.Max.X, bb.Max.Y, bb.Max.Z,
        bb.Max.X-bb.Min.X, bb.Max.Y-bb.Min.Y, bb.Max.Z-bb.Min.Z)

def transform_ids(ids, xf):
    for i in ids:
        sc.doc.Objects.Transform(i, xf, True)

def cluster(pts, radius):
    cl = []  # [sx, sy, sz, n]
    for p in sorted(pts, key=lambda q: -q.Z):
        placed = False
        for c in cl:
            mx, my = c[0]/c[3], c[1]/c[3]
            if math.hypot(p.X-mx, p.Y-my) <= radius:
                c[0]+=p.X; c[1]+=p.Y; c[2]+=p.Z; c[3]+=1; placed=True; break
        if not placed:
            cl.append([p.X, p.Y, p.Z, 1])
    cl.sort(key=lambda c: -c[3])
    return cl

try:
    open(LOG, "w").close()
    log("start")
    doc = sc.doc
    path = doc.Path or ""
    log("active doc: " + path + " modified=" + str(doc.Modified))
    if not path.endswith("CALACADEMY_SITE_2026_11_07B.3dm"):
        log("WRONG DOC, stopping")
        raise SystemExit
    if doc.Modified:
        log("note: doc has unsaved changes; continuing (SaveAs anyway)")
    log("model units: " + str(doc.ModelUnitSystem))

    before = set(o.Id for o in doc.Objects)
    log("existing objects: %d" % len(before))

    # layers
    def mk(name, color, parent=None):
        full = (parent + "::" + name) if parent else name
        if not rs.IsLayer(full):
            rs.AddLayer(name, color, True, False, parent)
        return full
    mk(PARENT, (90, 60, 160))
    L_B = mk("building", (90, 60, 160), PARENT)
    L_S = mk("site context", (90, 60, 160), PARENT)
    log("layers ok")

    res = rs.Command('-_Import "' + SKP + '" _Enter', False)
    log("import command result: " + str(res))
    new_ids = [o.Id for o in doc.Objects if o.Id not in before]
    log("new objects after import: %d" % len(new_ids))
    if not new_ids:
        log("NOTHING IMPORTED, stopping")
        raise SystemExit
    types = {}
    for i in new_ids:
        t = str(doc.Objects.FindId(i).ObjectType)
        types[t] = types.get(t, 0) + 1
    log("types: " + str(types))

    # explode block instances (recursive) so that geometry is real
    for _ in range(6):
        inst = [i for i in new_ids if doc.Objects.FindId(i) is not None and
                doc.Objects.FindId(i).ObjectType == Rhino.DocObjects.ObjectType.InstanceReference]
        if not inst: break
        rs.ExplodeBlockInstances(inst, True, False)
        new_ids = [o.Id for o in doc.Objects if o.Id not in before]
        log("exploded %d instances -> %d objects" % (len(inst), len(new_ids)))
    # drop any leftover non-geometry (none expected)
    bb = bbox_of(new_ids)
    log("import bbox: " + fmt_bb(bb))
    ext = max(bb.Max.X-bb.Min.X, bb.Max.Y-bb.Min.Y)
    if ext > 10000:
        s = 0.0254
        xf = Rhino.Geometry.Transform.Scale(Rhino.Geometry.Point3d.Origin, s)
        transform_ids(new_ids, xf)
        log("scaled by 0.0254 (inches came in as metres)")
        bb = bbox_of(new_ids)
        log("bbox after scale: " + fmt_bb(bb))
    else:
        log("units already metres-scale (extent %.1f), no scale" % ext)

    # registration by dome crowns
    verts = collect_vertices(new_ids)
    log("vertex count: %d" % len(verts))
    cen = Rhino.Geometry.Point3d(0, 0, 0)
    for v in verts:
        cen += Rhino.Geometry.Vector3d(v)
    cen = Rhino.Geometry.Point3d(cen.X/len(verts), cen.Y/len(verts), cen.Z/len(verts))
    log("centroid: %.2f %.2f %.2f" % (cen.X, cen.Y, cen.Z))
    near = [v for v in verts if math.hypot(v.X-cen.X, v.Y-cen.Y) <= 150.0]
    allztop = max(v.Z for v in verts)
    neartop = max(v.Z for v in near)
    log("overall top z %.2f ; top within 150 m of centroid %.2f" % (allztop, neartop))
    region = near if allztop > neartop + 0.5 else verts
    if region is near:
        log("terrain/context higher than central region; restricted to 150 m")
    top = max(v.Z for v in region)
    crowns = None
    for tol in (1.5, 4.0, 8.0):
        sel = [v for v in region if v.Z >= top - tol]
        cl = cluster(sel, 20.0)
        log("tol %.1f: %d verts, clusters (n, x, y, z): %s" % (tol, len(sel),
            [(c[3], round(c[0]/c[3],2), round(c[1]/c[3],2), round(c[2]/c[3],2)) for c in cl[:5]]))
        if len(cl) >= 2:
            crowns = cl[:2]
            break
    if crowns is None:
        log("fewer than two crowns found; no rotation; centring building bbox on origin")
        bbi = bbox_of(new_ids)
        c = bbi.Center
        xf = Rhino.Geometry.Transform.Translation(-c.X, -c.Y, 0)
        transform_ids(new_ids, xf)
    else:
        P = [Rhino.Geometry.Point3d(c[0]/c[3], c[1]/c[3], c[2]/c[3]) for c in crowns]
        log("crowns: " + str([(round(p.X,2), round(p.Y,2), round(p.Z,2)) for p in P]))
        vx, vy = P[1].X-P[0].X, P[1].Y-P[0].Y
        dist = math.hypot(vx, vy)
        a0 = -math.atan2(vy, vx)
        cands = []
        for a in (a0, a0 + math.pi):
            a = math.atan2(math.sin(a), math.cos(a))
            ca, sa = math.cos(a), math.sin(a)
            xs = [ca*v.X - sa*v.Y for v in near]
            ys = [sa*v.X + ca*v.Y for v in near]
            cands.append((a, max(xs)-min(xs), max(ys)-min(ys)))
        log("rotation candidates (deg, xext, yext): " + str([(round(math.degrees(c[0]),2), round(c[1],1), round(c[2],1)) for c in cands]))
        c1, c2 = cands
        if abs(c1[1]-c2[1]) / max(c1[1], c2[1]) > 0.03:
            best = c1 if c1[1] > c2[1] else c2
        else:
            best = c1 if abs(c1[0]) <= abs(c2[0]) else c2
            log("extent tie, picked smaller rotation")
        ang = best[0]
        ca, sa = math.cos(ang), math.sin(ang)
        mx, my = (P[0].X+P[1].X)/2, (P[0].Y+P[1].Y)/2
        rmx, rmy = ca*mx - sa*my, sa*mx + ca*my
        tx, ty = 0 - rmx, -4.0 - rmy
        zc = (P[0].Z + P[1].Z)/2
        tz = 19.3 - zc
        xf = Rhino.Geometry.Transform.Rotation(ang, Rhino.Geometry.Vector3d.ZAxis, Rhino.Geometry.Point3d.Origin)
        xf = Rhino.Geometry.Transform.Translation(tx, ty, tz) * xf
        transform_ids(new_ids, xf)
        log("rotation %.3f deg ; translation (%.3f, %.3f, %.3f)" % (math.degrees(ang), tx, ty, tz))
        newP = []
        for p in P:
            q = Rhino.Geometry.Point3d(p); q.Transform(xf); newP.append(q)
        log("crowns after: " + str([(round(q.X,3), round(q.Y,3), round(q.Z,3)) for q in newP]))
        tg = [Rhino.Geometry.Point3d(29, -4, 19.3), Rhino.Geometry.Point3d(-29, -4, 19.3)]
        d_a = newP[0].DistanceTo(tg[0]) + newP[1].DistanceTo(tg[1])
        d_b = newP[0].DistanceTo(tg[1]) + newP[1].DistanceTo(tg[0])
        pairs = [(0,0),(1,1)] if d_a <= d_b else [(0,1),(1,0)]
        for i, j in pairs:
            log("crown %d residual from (%.0f,-4,19.3): %.3f m" % (i, tg[j].X, newP[i].DistanceTo(tg[j])))
        log("crown-to-crown distance %.3f m (target 58)" % dist)

    # sort onto sublayers
    nb = ns = 0
    env_x, env_y = 84.5 + 10.0, 55.0 + 10.0
    for i in new_ids:
        o = doc.Objects.FindId(i)
        if o is None: continue
        b = o.Geometry.GetBoundingBox(True)
        inside = (b.Min.X >= -env_x and b.Max.X <= env_x and b.Min.Y >= -env_y and b.Max.Y <= env_y)
        lay = L_B if inside else L_S
        li = rs.LayerId(lay)
        idx = doc.Layers.FindByFullPath(lay, -1)
        a = o.Attributes.Duplicate()
        a.LayerIndex = idx
        doc.Objects.ModifyAttributes(i, a, True)
        if inside: nb += 1
        else: ns += 1
    log("sublayer counts: building=%d site context=%d" % (nb, ns))
    bb = bbox_of(new_ids)
    log("final bbox: " + fmt_bb(bb))

    # dot on FRAME
    frame = None
    for l in doc.Layers:
        if not l.IsDeleted and (l.Name.upper() == "FRAME" or l.FullPath.upper().endswith("FRAME")):
            frame = l.FullPath; break
    log("FRAME layer: " + str(frame))
    dot = Rhino.Geometry.TextDot("3D Warehouse 2014 SketchUp massing, id 1a4c209a43561ba445f5590ac69325a5, registered by the dome crowns; licence: use in own work, no redistribution", Rhino.Geometry.Point3d(0, 0, 25))
    at = Rhino.DocObjects.ObjectAttributes()
    if frame:
        at.LayerIndex = doc.Layers.FindByFullPath(frame, -1)
    doc.Objects.AddTextDot(dot, at)
    doc.Views.Redraw()

    # leftover empty import layers
    log("layers present: " + str([l.FullPath for l in doc.Layers if not l.IsDeleted]))

    r = rs.Command('-_SaveAs "' + OUT + '" _Enter', False)
    log("SaveAs result: " + str(r))
    log("active doc after: " + str(sc.doc.Path))
    if os.path.exists(OUT):
        log("C size bytes: %d" % os.path.getsize(OUT))
    else:
        log("C FILE NOT FOUND")
    log("DONE")
except SystemExit:
    log("stopped")
except Exception:
    log("ERROR: " + traceback.format_exc())
