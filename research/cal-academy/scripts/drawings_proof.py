import json, collections
import rhino3dm as r3
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle
D = r"C:\Users\bryan\Documents\Claude\ep3\data\cal-academy\drawings"
F = r"C:\Users\bryan\Documents\Claude\ep3\rhino\CALACADEMY_SITE_2026_11_07D.3dm"
m = r3.File3dm.Read(F)
lay = {l.Index: l.Name for l in m.Layers}
cnt = collections.Counter()
for o in m.Objects: cnt[lay[o.Attributes.LayerIndex]] += 1
print("LAYERS", len(lay))
for k in sorted(cnt): print(f"  {k}: {cnt[k]}")
def v(sid): return json.load(open(f"{D}\\vec\\{sid}_m3d.json"))["polylines3d"]
fig, ax = plt.subplots(1, 2, figsize=(18, 7.5), gridspec_kw=dict(width_ratios=[1.0, 1.35]))
a = ax[0]
for sid, c in (("drawing-352", "#222"),):
    for p in v(sid): a.plot([q[0] for q in p], [q[1] for q in p], c=c, lw=0.4)
a.add_patch(Rectangle((-84.5, -54.5), 169, 110, fill=False, ec="#2c92ff", lw=1.5))
for x in (29, -29): a.add_patch(Circle((x, -4), 13.7, fill=False, ec="#ff4400", lw=1.5))
a.add_patch(Rectangle((-10, -16.7), 20, 27.4, fill=False, ec="#ff4400", lw=1, ls="--"))
a.set_aspect("equal"); a.set_title("Overall Roof Plan A2.0.006 (traced, registered) over the massing: envelope 169 x 110, domes d 27.4 at x = +/-29\n(no main-floor plan sheet exists in the public RPBW set; roof plan shown)", fontsize=9); a.set_xlabel("x (m, +x = west)"); a.set_ylabel("y (m, +y = north)")
a.invert_xaxis()
b = ax[1]
for sid in ("drawing-328",):
    for p in v(sid): b.plot([q[0] for q in p], [q[2] for q in p], c="#222", lw=0.5)
for n, z in dict(aquarium=-7.6, main=0, mezz=4.6, roofSlab=9.6, deck=11.45, crown=19.3).items():
    b.axhline(z, c="#2c92ff", lw=0.7); b.text(-88, z + 0.3, f"{n} {z:+.2f}", fontsize=7, color="#2c92ff")
for x in (29, -29): b.add_patch(Circle((x, 5.6), 13.7, fill=False, ec="#ff4400", lw=1.5))
b.add_patch(Rectangle((-84.5, 9.6), 169, 0.3, fc="#555"))
b.set_aspect("equal"); b.invert_xaxis(); b.set_ylim(-14, 24); b.set_title("East-West building section SFR_DW_178 (traced) at y = -4, over the levels and dome spheres", fontsize=9); b.set_xlabel("x (m)"); b.set_ylabel("z (m)")
fig.tight_layout(); fig.savefig(r"C:\Users\bryan\Documents\Claude\ep3\boards\img\22_rpbw_drawings_registered.png", dpi=110)
