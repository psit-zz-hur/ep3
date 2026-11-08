#! python 3
import math, os, traceback
import rhinoscriptsyntax as rs
import Rhino
import scriptcontext as sc

LOG = r"C:\Users\bryan\Documents\Claude\ep3\rhino\skp_register_log.txt"
OUT = r"C:\Users\bryan\Documents\Claude\ep3\rhino\CALACADEMY_SITE_2026_11_07C.3dm"
PARENT = "3D WAREHOUSE (2014 SketchUp massing)"
IMPORT_LAYERS = ("Layer0", "Meshes", "Layer 01")

def log(s):
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(str(s) + "\n")

def verts_of(g):
    if isinstance(g, Rhino.Geometry.Mesh):
        return [Rhino.Geometry.Point3d(v) for v in g.Vertices]
    if isinstance(g, Rhino.Geometry.Brep):
        return [v.Location for v in g.Vertices]
    if isinstance(g, Rhino.Geometry.Extrusion):
        b = g.ToBrep()
        return [v.Location for v in b.Vertices] if b else []
    return []

def bbox_of(ids):
    bb = Rhino.Geometry.BoundingBox.Empty
    for i in ids:
        o = sc.doc.Objects.FindId(i)
        if o is not None:
            bb.Union(o.Geometry.GetBoundingBox(True))
    return bb

def fmt_bb(bb):
    return "min(%.2f,%.2f,%.2f) max(%.2f,%.2f,%.2f) size(%.2f,%.2f,%.2f)" % (
        bb.Min.X, bb.Min.Y, bb.Min.Z, bb.Max.X, bb.Max.Y, bb.Max.Z,
        bb.Max.X-bb.Min.X, bb.Max.Y-bb.Min.Y, bb.Max.Z-bb.Min.Z)

def xform(ids, xf):
    for i in ids:
        sc.doc.Objects.Transform(i, xf, True)

def cluster(pts, radius):
    cl = []
    for p in sorted(pts, key=lambda q: -q.Z):
        for c in cl:
            if math.hypot(p.X-c[0]/c[3], p.Y-c[1]/c[3]) <= radius:
                c[0]+=p.X; c[1]+=p.Y; c[2]+=p.Z; c[3]+=1
                break
        else:
            cl.append([p.X, p.Y, p.Z, 1])
    cl.sort(key=lambda c: -c[3])
    return cl

def is_import_obj(o):
    li = o.Attributes.LayerIndex
    full = sc.doc.Layers[li].FullPath
    return any(part in IMPORT_LAYERS for part in full.split("::"))

try:
    open(LOG, "w").close()
    log("start")
    doc = sc.doc
    log("active doc: %s modified=%s units=%s" % (doc.Path, doc.Modified, doc.ModelUnitSystem))
    if not (doc.Path or "").endswith("CALACADEMY_SITE_2026_11_07B.3dm"):
        log("WRONG DOC, stopping")
        raise SystemExit

    # explode block instances on import layers
    for _ in range(6):
        inst = [o.Id for o in doc.Objects if is_import_obj(o) and
                o.ObjectType == Rhino.DocObjects.ObjectType.InstanceReference]
        if not inst: break
        before = set(o.Id for o in doc.Objects)
        rs.ExplodeBlockInstances(inst, True, False)
        log("exploded %d block instances" % len(inst))
    ids = [o.Id for o in doc.Objects if is_import_obj(o)]
    log("import objects: %d" % len(ids))
    if not ids:
        log("NO IMPORT OBJECTS FOUND, stopping")
        raise SystemExit
    types = {}
    for i in ids:
        t = str(doc.Objects.FindId(i).ObjectType)
        types[t] = types.get(t, 0) + 1
    log("types: " + str(types))
    bb = bbox_of(ids)
    log("bbox: " + fmt_bb(bb))
    ext = max(bb.Max.X-bb.Min.X, bb.Max.Y-bb.Min.Y)
    if ext > 10000:
        xform(ids, Rhino.Geometry.Transform.Scale(Rhino.Geometry.Point3d.Origin, 0.0254))
        log("scaled by 0.0254 (inches as metres)")
        bb = bbox_of(ids)
        log("bbox after scale: " + fmt_bb(bb))
    else:
        log("extent %.1f m, no scale" % ext)

    verts = []
    for i in ids:
        verts.extend(verts_of(doc.Objects.FindId(i).Geometry))
    log("vertices: %d" % len(verts))
    sx = sum(v.X for v in verts)/len(verts); sy = sum(v.Y for v in verts)/len(verts)
    log("centroid xy: %.2f %.2f" % (sx, sy))
    near = [v for v in verts if math.hypot(v.X-sx, v.Y-sy) <= 150.0]
    allztop = max(v.Z for v in verts); neartop = max(v.Z for v in near)
    log("top z overall %.2f, within 150 m %.2f" % (allztop, neartop))
    region = near if allztop > neartop + 0.5 else verts
    top = max(v.Z for v in region)
    crowns = None
    for tol in (1.5, 4.0, 8.0):
        sel = [v for v in region if v.Z >= top - tol]
        cl = cluster(sel, 20.0)
        log("tol %.1f: %d verts, clusters (n,x,y,z): %s" % (tol, len(sel),
            [(c[3], round(c[0]/c[3],2), round(c[1]/c[3],2), round(c[2]/c[3],2)) for c in cl[:5]]))
        if len(cl) >= 2:
            crowns = cl[:2]; break
    if crowns is None:
        log("fewer than two crowns; no rotation; centring bbox on origin")
        c = bbox_of(ids).Center
        xform(ids, Rhino.Geometry.Transform.Translation(-c.X, -c.Y, 0))
    else:
        P = [Rhino.Geometry.Point3d(c[0]/c[3], c[1]/c[3], c[2]/c[3]) for c in crowns]
        log("crowns: " + str([(round(p.X,2), round(p.Y,2), round(p.Z,2)) for p in P]))
        vx, vy = P[1].X-P[0].X, P[1].Y-P[0].Y
        a0 = -math.atan2(vy, vx)
        cands = []
        for a in (a0, a0 + math.pi):
            a = math.atan2(math.sin(a), math.cos(a))
            ca, sa = math.cos(a), math.sin(a)
            xs = [ca*v.X - sa*v.Y for v in near]
            ys = [sa*v.X + ca*v.Y for v in near]
            cands.append((a, max(xs)-min(xs), max(ys)-min(ys)))
        log("candidates (deg, xext, yext): " + str([(round(math.degrees(c[0]),2), round(c[1],1), round(c[2],1)) for c in cands]))
        c1, c2 = cands
        if abs(c1[1]-c2[1]) / max(c1[1], c2[1]) > 0.03:
            best = c1 if c1[1] > c2[1] else c2
        else:
            best = c1 if abs(c1[0]) <= abs(c2[0]) else c2
            log("extent tie, smaller rotation picked")
        ang = best[0]
        ca, sa = math.cos(ang), math.sin(ang)
        mx, my = (P[0].X+P[1].X)/2, (P[0].Y+P[1].Y)/2
        tx = -(ca*mx - sa*my); ty = -4.0 - (sa*mx + ca*my)
        tz = 19.3 - (P[0].Z+P[1].Z)/2
        xf = Rhino.Geometry.Transform.Translation(tx, ty, tz) * Rhino.Geometry.Transform.Rotation(ang, Rhino.Geometry.Vector3d.ZAxis, Rhino.Geometry.Point3d.Origin)
        xform(ids, xf)
        log("rotation %.3f deg; translation (%.3f, %.3f, %.3f)" % (math.degrees(ang), tx, ty, tz))
        newP = []
        for p in P:
            q = Rhino.Geometry.Point3d(p); q.Transform(xf); newP.append(q)
        log("crowns after: " + str([(round(q.X,3), round(q.Y,3), round(q.Z,3)) for q in newP]))
        tg = [Rhino.Geometry.Point3d(29, -4, 19.3), Rhino.Geometry.Point3d(-29, -4, 19.3)]
        da = newP[0].DistanceTo(tg[0]) + newP[1].DistanceTo(tg[1])
        db = newP[0].DistanceTo(tg[1]) + newP[1].DistanceTo(tg[0])
        pairs = [(0,0),(1,1)] if da <= db else [(0,1),(1,0)]
        for i, j in pairs:
            log("crown %d residual from (%.0f,-4,19.3): %.3f m" % (i, tg[j].X, newP[i].DistanceTo(tg[j])))
        log("crown-to-crown distance %.3f m (target 58)" % math.hypot(vx, vy))

    # layers
    def mk(name, parent=None):
        full = (parent + "::" + name) if parent else name
        if not rs.IsLayer(full):
            rs.AddLayer(name, (90, 60, 160), True, False, parent)
        return full
    mk(PARENT)
    L_B = mk("building", PARENT); L_S = mk("site context", PARENT)
    iB = doc.Layers.FindByFullPath(L_B, -1); iS = doc.Layers.FindByFullPath(L_S, -1)
    nb = ns = 0
    ex, ey = 94.5, 65.0
    for i in ids:
        o = doc.Objects.FindId(i)
        b = o.Geometry.GetBoundingBox(True)
        inside = b.Min.X >= -ex and b.Max.X <= ex and b.Min.Y >= -ey and b.Max.Y <= ey
        a = o.Attributes.Duplicate()
        a.LayerIndex = iB if inside else iS
        doc.Objects.ModifyAttributes(i, a, True)
        if inside: nb += 1
        else: ns += 1
    log("sublayer counts: building=%d site context=%d" % (nb, ns))
    log("final bbox: " + fmt_bb(bbox_of(ids)))

    # delete empty import layers
    for name in IMPORT_LAYERS:
        if rs.IsLayer(name):
            try:
                if not rs.LayerChildCount(name) and rs.IsLayerEmpty(name):
                    rs.DeleteLayer(name); log("deleted empty layer " + name)
                else:
                    log("kept layer %s (children or objects)" % name)
            except Exception as e:
                log("layer %s delete failed: %s" % (name, e))

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

    r = rs.Command('-_SaveAs "' + OUT + '" _Enter', False)
    log("SaveAs result: " + str(r))
    log("active doc after: " + str(sc.doc.Path))
    log("C size bytes: %d" % os.path.getsize(OUT) if os.path.exists(OUT) else "C FILE NOT FOUND")
    log("DONE")
except SystemExit:
    log("stopped")
except Exception:
    log("ERROR: " + traceback.format_exc())
