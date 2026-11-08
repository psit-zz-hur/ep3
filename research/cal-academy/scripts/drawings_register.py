#!/usr/bin/env python3
"""RPBW drawings -> registered, traced, DXF. Sections first (Bryan 11/07), then elevations, plans, details.

All Fondazione sheets are RASTER ONLY (PDF = web JPG ~550-900 px + TCPDF frame), so every vector here is TRACED.
Frame: metres, Z up, origin = building centre at the main floor; x long axis (planetarium +x = west, rainforest -x = east),
y towards the north/concourse side.

Outputs (data/cal-academy/drawings): vec/<sheet>.json, vec/<sheet>.dxf, raster/place/<sheet>_place.png,
DRAWINGS_REGISTRATION_2026_11_07A.json
"""
import json, math, os, sys
import numpy as np, cv2
from PIL import Image
from skimage.morphology import skeletonize
import ezdxf

D = r"C:\Users\bryan\Documents\Claude\ep3\data\cal-academy\drawings"
RA = D + r"\raster"; VEC = D + r"\vec"; PL = RA + r"\place"
os.makedirs(VEC, exist_ok=True); os.makedirs(PL, exist_ok=True)
Z = (0, 0, 1)

# ---- sheet table -----------------------------------------------------------------------------------------------------
# kind 'v' vertical plane: px0 <-> coordinate 0 along U, py0 <-> z0, s px per metre (sh horizontal, sv vertical)
# kind 'p' plan: circles (planetarium px, rainforest px) -> scale, rotation, translation
S = []
def add(**k): S.append(k)

# 3/32" family scale 3.15 px/m (dome spacing 58 m / 183.5 px on the 1/16" roof plan = 3.13; 3/32" images measured 3.0-3.2)
FAM = 3.15
add(id="drawing-328", cls="section", order=1, title="East-West building section (SFR_DW_178), looking south, planetarium (+x) on the left",
    png="drawing-328_native.png", crop=(20, 150, 810, 380), trace="color", mode=("v", dict(px0=404.5, py0=302.0, sh=FAM, sv=FAM, z0=0.0, U=(-1, 0, 0), O=(0, -4.0, 0))),
    conf="medium", method="dome sphere centres px 312/497 -> x=+29/-29; floor line py 302 = z 0; crown px 242 -> z 19.05",
    checks=dict(dome_spacing_m=(497 - 312) / FAM, crown_z=(302 - 242) / FAM, outline_len_m=(678 - 178) / FAM), expect=dict(dome_spacing_m=58.0, crown_z=19.3, outline_len_m=169.0),
    plane="y = -4.0 (cut through the domes), faces +y")
add(id="drawing-336", cls="section", order=2, title="North-South building section (SFR_DW_179), cut x = 0 through the piazza, looking -x (east), north on the right",
    png="drawing-336_native.png", crop=(250, 150, 650, 390), trace="color", mode=("v", dict(px0=412.0, py0=312.0, sh=FAM, sv=FAM, z0=0.0, U=(0, 1, 0), O=(0, -3.0, 0))),
    conf="medium", method="blue piazza glazing centre px 412 -> y=-3; floor line py 312 = z 0; crown px 252 -> z 19.05; direction from the north portico (right)",
    checks=dict(crown_z=(312 - 252) / FAM, outline_len_m=(576 - 288) / FAM), expect=dict(crown_z=19.3, outline_len_m=110.0),
    plane="x = 0.0 (piazza), faces +x")
add(id="drawing-275", cls="section", order=3, title="North-South building section, coloured (SFR_DW_001); same linework as 336, placed on the same cut",
    png="drawing-275_native.png", crop=(250, 150, 650, 390), trace=None, mode=("v", dict(px0=412.0, py0=312.0, sh=FAM, sv=FAM, z0=0.0, U=(0, 1, 0), O=(0.5, -3.0, 0))),
    conf="medium", method="same registration as drawing-336, offset +0.5 m in x so the two rasters do not z-fight; raster only (vectors = drawing-336)",
    checks={}, expect={}, plane="x = +0.5")
# interior sections: Hough circle fit (sphere), r px -> 13.7 m
add(id="drawing-279", cls="section-interior", order=4, title="Interior Section Rain Forest (A5.2.001, 1/4in=1ft), sphere through the Osher Rainforest dome",
    png="drawing-279_native.png", crop=(15, 15, 605, 520), trace="cad", mode=("v", dict(px0=343.5, py0=280.5, sh=175.3 / 13.7, sv=175.3 / 13.7, z0=5.6, U=(-1, 0, 0), O=(-29.0, -3.5, 0))),
    conf="medium-high scale / low direction", method="Hough circle (343.5, 280.5, r 175.3 px) = 27.4 m sphere; centre at z = 5.6 above main floor, x = -29; sheet formula 48in x 1:48 / 738 px = 12.6 px/m agrees",
    checks=dict(sheet_formula_px_per_m=1.2192 * 1 / 738 * 0 + 738 / (1.2192 * 48)), expect=dict(sheet_formula_px_per_m=175.3 / 13.7), plane="y = -3.5 (cut through the dome, assumed E-W, faces +y)")
add(id="drawing-285", cls="section-interior", order=5, title="Interior Section Planetarium (A5.3.001, 1/4in=1ft), sphere through the Morrison Planetarium dome",
    png="drawing-285_native.png", crop=(15, 15, 605, 520), trace="cad", mode=("v", dict(px0=318.9, py0=288.9, sh=173.4 / 13.7, sv=173.4 / 13.7, z0=5.6, U=(-1, 0, 0), O=(29.0, -3.5, 0))),
    conf="medium-high scale / low direction", method="Hough circle (318.9, 288.9, r 173.4 px) = 27.4 m sphere; centre z 5.6, x = +29",
    checks=dict(sheet_formula_px_per_m=737 / (1.2192 * 48)), expect=dict(sheet_formula_px_per_m=173.4 / 13.7), plane="y = -3.5 (assumed E-W cut, faces +y)")
# booklet sections (earlier design stage composites)
add(id="booklet-section-A", cls="section", order=6, title="RPBW booklet p.4 long section A (coloured model section), looking north, rainforest (-x) left",
    png="booklet_section_A_looking_north.png", crop=(0, 0, 3316, 734), trace="booklet", mode=("v", dict(px0=1621.0, py0=498.0, sh=12.64, sv=12.64, z0=0.0, U=(1, 0, 0), O=(0, -5.0, 0))),
    conf="low", method="crown 244 px = 19.3 m -> 12.64 px/m; midpoint of the two hill crests (1042, 2200) -> x=0. Hill spacing is 91.6 m in this drawing vs 58 m built: earlier design / composite",
    checks=dict(dome_spacing_m=(2200 - 1042) / 12.64), expect=dict(dome_spacing_m=58.0), plane="y = -5.0, faces -y (viewer south)")
add(id="booklet-section-B", cls="section", order=7, title="RPBW booklet p.4 long section B (coloured model section), looking south, planetarium (+x) left",
    png="booklet_section_B_looking_south.png", crop=(0, 0, 3316, 727), trace="booklet", mode=("v", dict(px0=1610.0, py0=510.0, sh=14.2, sv=14.2, z0=0.0, U=(-1, 0, 0), O=(0, -3.0, 0))),
    conf="low", method="crown 275 px = 19.3 m -> 14.2 px/m; midpoint of hill crests (1040, 2180) -> x=0. Hill spacing 80 m vs 58 m built",
    checks=dict(dome_spacing_m=(2180 - 1040) / 14.2), expect=dict(dome_spacing_m=58.0), plane="y = -3.0, faces +y (viewer north)")
add(id="rpbw-long-section", cls="section", order=8, title="RPBW.com long section JPG 1400x343 (placed only if registered by Bryan)", png=None, crop=None, trace=None, mode=("x", {}),
    conf="none", method="not placed: same drawing family as booklet; kept as raster in raster/", checks={}, expect={}, plane="unplaced")
# elevations
add(id="drawing-337", cls="elevation", order=10, title="North elevation, Music Concourse (SFR_DW_181), looking south, east (-x) on the right",
    png="drawing-337_native.png", crop=(20, 150, 810, 345), trace="color", mode=("v", dict(px0=421.0, py0=313.0, sh=FAM, sv=FAM, z0=0.0, U=(-1, 0, 0), O=(0, 65.0, 0))),
    conf="medium", method="canopy outline px 148..695 centred on x=0; floor py 313 = z 0; deck line py 274 -> 12.4 m, crown py 250 -> 20.0 m",
    checks=dict(canopy_len_m=(695 - 148) / FAM, crown_z=(313 - 250) / FAM), expect=dict(canopy_len_m=185.0, crown_z=19.3), plane="y = +65")
add(id="drawing-240", cls="elevation", order=11, title="South elevation, Middle Drive (SFR_DW_002), looking north, west (+x) on the right",
    png="drawing-240_native.png", crop=(20, 150, 810, 345), trace="color", mode=("v", dict(px0=390.0, py0=330.0, sh=FAM, sv=FAM, z0=0.0, U=(1, 0, 0), O=(0, -65.0, 0))),
    conf="low-medium", method="mid-point of the three hills (295, 485) -> x=0; ground py set so the dome top (py 271) = 19.3 m",
    checks=dict(hill_spacing_m=(485 - 295) / FAM), expect=dict(hill_spacing_m=58.0), plane="y = -65")
add(id="drawing-243", cls="elevation", order=12, title="West elevation, Shakespeare Garden (SFR_DW_003), looking east, north on the right",
    png="drawing-243_native.png", crop=(20, 150, 810, 345), trace="color", mode=("v", dict(px0=417.0, py0=318.0, sh=FAM, sv=FAM, z0=0.0, U=(0, 1, 0), O=(95.0, 0, 0))),
    conf="low-medium", method="building body px 270..565 centred y=0; ground py set so the middle hill top (py 257.5) = 19.3 m",
    checks=dict(body_len_m=(565 - 270) / FAM), expect=dict(body_len_m=110.0), plane="x = +95")
add(id="drawing-613-north", cls="elevation", order=13, title="Overall Building Elevations A3.0.001 (1/16in=1ft): 01 North building elevation",
    png="drawing-613_native.png", crop=(90, 15, 650, 225), trace="cad", mode=("v", dict(px0=359.8, py0=131.0, sh=3.10, sv=3.10, z0=0.0, U=(-1, 0, 0), O=(0, 75.0, 0))),
    conf="medium", method="column bubbles 22 x 24 ft bays (px 120..599.5) centred x=0; sheet formula 192/(1.2192 m) = 3.2 px/m; floor py 131",
    checks=dict(grid_len_m=(599.5 - 120) / 3.10, crown_z=(131 - 68) / 3.10), expect=dict(grid_len_m=21 * 7.3152, crown_z=19.3), plane="y = +75 (10 m behind 337 so they do not overlap)")
add(id="drawing-613-east", cls="elevation", order=14, title="Overall Building Elevations A3.0.001: 02 East building elevation, looking +x from the east, south on the right",
    png="drawing-613_native.png", crop=(90, 265, 650, 475), trace="cad", mode=("v", dict(px0=349.0, py0=385.0, sh=3.10, sv=3.10, z0=0.0, U=(0, -1, 0), O=(-95.0, 0, 0))),
    conf="low-medium", method="bubbles px 200..497.5 centred y=0; floor py 385", checks={}, expect={}, plane="x = -95")
# plans
add(id="drawing-352", cls="plan", order=20, title="Overall Roof Plan A2.0.006 (1/16in=1ft), north up",
    png="drawing-352_native.png", crop=(30, 60, 600, 525), trace="cad", mode=("p", dict(pl=(247.6, 356.0), rf=(431.1, 356.2), r=(42.8, 43.0), z=11.45)),
    conf="high", method="Hough circles (247.6,356.0 r42.8) and (431.1,356.2 r43.0) = 27.4 m domes; scale 3.13 px/m = sheet formula 1/16in; roof plan placed at the deck level 11.45 m",
    checks=dict(dome_spacing_m=(431.1 - 247.6) / (2 * 42.9 / 27.4), outer_band_w_m=(587 - 94) / (2 * 42.9 / 27.4), outer_band_h_m=(500 - 187) / (2 * 42.9 / 27.4)),
    expect=dict(dome_spacing_m=58.0, outer_band_w_m=169.0, outer_band_h_m=110.0), plane="z = 11.45")
add(id="drawing-235", cls="plan", order=21, title="Site plan (SFR_DW_006), coloured, north up, ground floor within",
    png="drawing-235_native.png", crop=(0, 0, 908, 550), trace="site", mode=("p", dict(pl=(371.4, 323.0), rf=(537.4, 325.0), r=(38.6, 35.6), z=0.0)),
    conf="medium", method="Hough circles (371.4,323 r38.6) and (537.4,325 r35.6); mean d 74.2 px = 27.4 m -> 2.71 px/m; sheet is NTS",
    checks=dict(dome_spacing_m=(537.4 - 371.4) / (74.2 / 27.4)), expect=dict(dome_spacing_m=58.0), plane="z = 0")
# details: scale from the sheet formula (48 in wide CD sheet): m/px = 1.2192 * den / native width
def det(i, sid, title, den, native_w, guess):
    add(id=sid, cls="detail", order=i, title=title, png=f"{sid}_native.png", crop=None, trace="cad",
        mode=("d", dict(mpp=1.2192 * den / native_w, slot=i - 30)),
        conf="scale low-medium, position NONE", method=f"UNPLACED, parked on the y=+130 row. Scale = 48in sheet x 1:{den} / {native_w} px = {1.2192 * den / native_w:.4f} m/px" + (" (scale 'as indicated' on the sheet: GUESS)" if guess else ""),
        checks={}, expect={}, plane="parked y=+130, needs Bryan for position (and scale if guessed)")
det(30, "drawing-311", "Roof details skylights (A8.4.040, 1in=1ft)", 12, 741, False)
det(31, "drawing-354", "Section of glass canopy with PV cells (1/4in=1ft)", 48, 702, False)
det(32, "drawing-355", "Canopy details typical (A8.4.001, as indicated)", 12, 737, True)
det(33, "drawing-303", "Piazza skylight details (A8.4.010, as indicated)", 12, 737, True)
det(34, "drawing-304", "Enlarged N/S lobby facade window-wall details (W2-04, 1.5in=1ft)", 8, 730, False)
det(35, "drawing-289", "3D Geometry Roof (A3.1.001, NTS axon)", 192, 736, True)


# ---- tracing ---------------------------------------------------------------------------------------------------------
def walk_skeleton(sk):
    """skeleton bool array -> list of (n,2) float arrays (x,y) pixel coords."""
    H, W = sk.shape
    ys, xs = np.nonzero(sk)
    pts = set(zip(xs.tolist(), ys.tolist()))
    nb = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def neigh(p): return [(p[0] + a, p[1] + b) for a, b in nb if (p[0] + a, p[1] + b) in pts]
    deg = {p: len(neigh(p)) for p in pts}
    seen_edges = set(); visited = set(); out = []
    def walk(start, nxt):
        path = [start, nxt]; prev, cur = start, nxt
        seen_edges.add((start, nxt)); seen_edges.add((nxt, start))
        while deg[cur] == 2:
            n = [q for q in neigh(cur) if q != prev]
            # prefer 4-neighbour to avoid stair-step shortcuts both ways
            nn = None
            for q in n:
                if (cur, q) not in seen_edges: nn = q; break
            if nn is None: break
            seen_edges.add((cur, nn)); seen_edges.add((nn, cur)); path.append(nn); prev, cur = cur, nn
            if cur == start: break
        return path
    nodes = [p for p in pts if deg[p] != 2]
    for p in nodes:
        for q in neigh(p):
            if (p, q) not in seen_edges: out.append(walk(p, q))
    for p in pts:  # closed loops
        if deg[p] == 2 and not any((p, q) in seen_edges for q in neigh(p)):
            q = neigh(p)[0]; out.append(walk(p, q))
    return [np.array(o, float) for o in out]


def trace_img(arr_rgb, mode, scale=2):
    g = cv2.cvtColor(arr_rgb, cv2.COLOR_RGB2GRAY)
    up = cv2.resize(g, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
    if mode == "cad":
        m = cv2.adaptiveThreshold(cv2.GaussianBlur(up, (3, 3), 0), 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 31, 14) > 0
        minlen = 7
    elif mode == "site":
        m = up < 85; minlen = 8
    elif mode == "booklet":
        up = cv2.resize(g, None, fx=1, fy=1); scale = 1
        m = up < 75; minlen = 25
    else:
        m = up < 185; minlen = 9
    m = m.astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(m, connectivity=8)
    keep = np.zeros(n, bool); keep[1:] = st[1:, cv2.CC_STAT_AREA] >= ((14 if mode in ("color", "site") else 6) * scale)
    m = keep[lab]
    sk = skeletonize(m)
    paths = walk_skeleton(sk)
    res = []
    for p in paths:
        if len(p) < 3: continue
        a = cv2.approxPolyDP(p.astype(np.float32).reshape(-1, 1, 2), 1.0 * (1 if scale == 1 else scale / 2), False).reshape(-1, 2) / scale
        L = np.sum(np.hypot(*np.diff(a, axis=0).T)) if len(a) > 1 else 0
        if L >= minlen: res.append(a)
    return res


# ---- mapping ---------------------------------------------------------------------------------------------------------
def make_map(sh):
    kind, p = sh["mode"]
    if kind == "v":
        U = np.array(p["U"], float)
        def f(px, py):
            u = (np.asarray(px, float) - p["px0"]) / p["sh"]; v = (p["py0"] - np.asarray(py, float)) / p["sv"] + p["z0"]
            O = np.array(p["O"], float)
            return np.stack([O[0] + u * U[0], O[1] + u * U[1], O[2] + v], -1), np.stack([u, v], -1)
        info = dict(scale_m_per_px=[1 / p["sh"], 1 / p["sv"]], rotation_deg=0.0, translation=list(p["O"]), plane=sh["plane"])
        return f, info
    if kind == "p":
        (lx, ly), (rx, ry) = p["pl"], p["rf"]; d = np.mean(p["r"]) * 2; s = d / 27.4
        # rhino metric before rotation: x = -(px - mx)/s, y = -(py - my)/s - 4
        mx, my = (lx + rx) / 2, (ly + ry) / 2
        vx, vy = -(rx - lx) / s, -(ry - ly) / s      # planetarium -> rainforest vector in metres; should be (-58, 0)
        ang = math.atan2(vy, vx) - math.pi         # rotate this vector onto -x
        ca, sa = math.cos(-ang), math.sin(-ang)
        def f(px, py):
            x = -(np.asarray(px, float) - mx) / s; y = -(np.asarray(py, float) - my) / s
            X = ca * x - sa * y; Y = sa * x + ca * y - 4.0
            return np.stack([X, Y, np.full_like(X, p["z"])], -1), np.stack([X, Y], -1)
        info = dict(scale_m_per_px=1 / s, rotation_deg=math.degrees(-ang), translation=[0, -4.0, p["z"]], plane=sh["plane"], px_per_m=s)
        return f, info
    if kind == "d":
        mpp = p["mpp"]; slot = p["slot"]
        ox = -90 + slot * 40.0
        def f(px, py):
            u = np.asarray(px, float) * mpp; v = -np.asarray(py, float) * mpp
            return np.stack([ox + u, np.full_like(u, 130.0), v + 30.0], -1), np.stack([ox + u, v + 30.0], -1)
        return f, dict(scale_m_per_px=mpp, rotation_deg=0.0, translation=[ox, 130.0, 30.0], plane=sh["plane"])
    return None, dict(plane="unplaced")


def main():
    reg = []
    for sh in sorted(S, key=lambda s: s["order"]):
        sid = sh["id"]
        entry = dict(sheet=sid, **{k: sh[k] for k in ("cls", "title", "conf", "method", "plane")})
        if sh["png"] is None:
            entry.update(placed=False); reg.append(entry); continue
        src = RA + "\\" + sh["png"]
        im = Image.open(src).convert("RGB")
        crop = sh["crop"] or (0, 0, im.width, im.height)
        x0, y0, x1, y1 = crop
        cim = im.crop(crop); place = PL + f"\\{sid}_place.png"; cim.save(place)
        f, info = make_map(sh)
        # corners of the crop (px in source frame) -> 3D
        cx = np.array([x0, x1, x1, x0], float); cy = np.array([y1, y1, y0, y0], float)  # bl, br, tr, tl
        c3, _ = f(cx, cy)
        residual = {}
        for k, v in sh["checks"].items():
            e = sh["expect"].get(k); residual[k] = dict(measured=round(float(v), 2), expected=None if e is None else round(float(e), 2), diff=None if e is None else round(float(v - e), 2))
        entry.update(placed=True, raster_png=place, source_png=src, crop_px=list(crop), corners_bl_br_tr_tl=c3.round(3).tolist(), residual=residual, **info)
        entry["mode"] = sh["mode"][0]; entry["params"] = {k: (list(v) if isinstance(v, tuple) else v) for k, v in sh["mode"][1].items()}
        # trace
        if sh["trace"]:
            arr = np.asarray(cim)
            paths = trace_img(arr, sh["trace"])
            # back to source px frame
            polys = [(p + np.array([x0, y0])).round(2).tolist() for p in paths]
            m3 = []; loc = []
            for p in paths:
                q = p + np.array([x0, y0]); P3, uv = f(q[:, 0], q[:, 1]); m3.append(P3.round(3).tolist()); loc.append(uv.round(3))
            vecq = "traced from raster (skeleton + Douglas-Peucker); " + {"cad": "adaptive threshold, line drawing", "color": "dark-ink threshold <150 (people, section cut, ground line; tree stipple partly)", "site": "dark-ink <85", "booklet": "dark-ink <75 on watercolour, rough"}[sh["trace"]]
            json.dump(dict(sheet=sid, units="source pixels (y down) of " + sh["png"], traced=True, quality=vecq, polylines=polys, registration=entry), open(VEC + f"\\{sid}.json", "w"))
            json.dump(dict(sheet=sid, units="metres", polylines3d=m3), open(VEC + f"\\{sid}_m3d.json", "w"))
            doc = ezdxf.new("R2010"); doc.units = 6  # metres
            doc.layers.add(f"{sid}_traced", color=8); msp = doc.modelspace()
            for uv in loc:
                if len(uv) >= 2: msp.add_lwpolyline([tuple(t) for t in uv.tolist()], dxfattribs={"layer": f"{sid}_traced"})
            msp.add_text(f"{sid} TRACED {sh['plane']} local (u,v) metres", dxfattribs={"height": 1.0, "layer": f"{sid}_traced"}).set_placement((0, -2))
            doc.saveas(VEC + f"\\{sid}.dxf")
            entry.update(vector="traced", n_polylines=len(paths), vector_json=VEC + f"\\{sid}_m3d.json", dxf=VEC + f"\\{sid}.dxf", vector_quality=vecq)
            print(sid, "traced", len(paths), "polylines")
        else:
            entry.update(vector="none (raster only)", n_polylines=0)
        reg.append(entry)
    json.dump(dict(frame="metres, Z up, origin = building centre at main floor (77.05 m NAVD88); x long axis, planetarium +x (west), north +y; made 2026-11-07 by drawings_register.py", sheets=reg),
              open(D + r"\DRAWINGS_REGISTRATION_2026_11_07A.json", "w"), indent=1)
    for e in reg:
        print(e["sheet"], e.get("placed"), e.get("conf"), json.dumps(e.get("residual", {}))[:160])

if __name__ == "__main__":
    main()
