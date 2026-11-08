#! python 3
# Adds every placed RPBW drawing sheet as a Rhino Picture object (shows in every display mode except wireframe).
import json, os, traceback
import rhinoscriptsyntax as rs
import Rhino
import scriptcontext as sc

LOG = r"C:\Users\bryan\Documents\Claude\ep3\rhino\drawings_pictures_log.txt"
REG = r"C:\Users\bryan\Documents\Claude\ep3\data\cal-academy\drawings\DRAWINGS_REGISTRATION_2026_11_07A.json"
PARENT = "DRAWINGS PICTURES"

def log(s):
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(str(s) + "\n")

def ensure_layer(name):
    if not rs.IsLayer(name):
        rs.AddLayer(name)
    return name

def main():
    open(LOG, "w", encoding="utf-8").close()
    reg = json.load(open(REG, encoding="utf-8"))
    ensure_layer(PARENT)
    n = 0
    for e in reg["sheets"]:
        if not e.get("placed"):
            continue
        sid = e["sheet"]
        try:
            png = e["raster_png"]
            if not os.path.exists(png):
                log("MISSING PNG %s %s" % (sid, png)); continue
            bl, br, tr, tl = [Rhino.Geometry.Point3d(*c) for c in e["corners_bl_br_tr_tl"]]
            xv = br - bl; yv = tl - bl
            w = xv.Length; h = yv.Length
            xv.Unitize(); yv.Unitize()
            plane = rs.PlaneFromFrame(bl, xv, yv)
            layer = "%s::%s %s" % (PARENT, e["cls"], sid)
            ensure_layer(layer)
            oid = rs.AddPictureFrame(plane, png, w, h, True, False, False, False)
            if not oid:
                log("FAILED %s" % sid); continue
            rs.ObjectLayer(oid, layer)
            rs.ObjectName(oid, "%s | %s | %s | conf %s | %s" % (sid, e["cls"], e["plane"], e["conf"], e["method"]))
            log("OK %s  %.2f x %.2f m  plane %s  layer %s" % (sid, w, h, e["plane"], layer))
            n += 1
        except Exception:
            log("ERR %s\n%s" % (sid, traceback.format_exc()))
    rs.Redraw()
    log("pictures: %d" % n)
    log("DONE")

main()
