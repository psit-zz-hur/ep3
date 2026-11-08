import json, numpy as np
from PIL import Image
from scipy import ndimage as ndi
A = r"C:\Users\bryan\Documents\Claude\ep3\game\assets"
meta = json.load(open(A + r"\site_meta.json"))
dsm = np.asarray(Image.open(A + r"\site_dsm_rg.png").convert("RGB")).astype(float)
h = (dsm[..., 0] * 256 + dsm[..., 1]) * meta["z_scale"] + meta["z_base_m"] - meta["ground_m"]
res = meta["res_m"]; H, W = h.shape
X = -meta["width_m"] / 2 + np.arange(W) * res; Y = -(-meta["height_m"] / 2 + np.arange(H) * res)  # rhino y = -Z
# rhino coords: x = X, y = -Z
mask = np.zeros_like(h, bool)
jj, ii = np.mgrid[0:H, 0:W]
xx = X[ii]; yy = Y[jj]
box = (abs(xx) < 90) & (abs(yy) < 65)
hh = np.where(box, h, -99)
mx = ndi.maximum_filter(hh, size=int(10 / res))
pk = (hh == mx) & (hh > 12)
lab, n = ndi.label(pk)
cs = ndi.center_of_mass(pk, lab, range(1, n + 1))
out = sorted([(float(hh[int(c[0]), int(c[1])]), float(xx[int(c[0]), int(c[1])]), float(yy[int(c[0]), int(c[1])])) for c in cs], reverse=True)[:8]
for o in out: print("peak z=%.1f x=%.1f y=%.1f" % o)
# extent of the >=9 m roof (building mask)
bld = np.asarray(Image.open(A + r"\site_bldg_mask.png").convert("L")) > 127
sel = bld & box
print("bldg mask x %.1f..%.1f  y %.1f..%.1f" % (xx[sel].min(), xx[sel].max(), yy[sel].min(), yy[sel].max()))
