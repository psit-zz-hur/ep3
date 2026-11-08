"""Raster pass: per Fondazione sheet PDF -> native embedded drawing PNG (the real pixels), 300 dpi full page, cropped drawing."""
import fitz, glob, os, io, shutil
from PIL import Image
D = r"C:\Users\bryan\Documents\Claude\ep3\data\cal-academy\drawings"
R = D + r"\raster"; os.makedirs(R, exist_ok=True)
for f in sorted(glob.glob(D + r"\drawing-*.pdf")):
    n = os.path.basename(f)[8:11]
    d = fitz.open(f); pg = d[0]
    best = None
    for x in pg.get_images(full=True):
        if best is None or x[2] * x[3] > best[2] * best[3]: best = x
    e = d.extract_image(best[0])
    im = Image.open(io.BytesIO(e["image"])).convert("RGB")
    im.save(f"{R}\\drawing-{n}_native.png")
    bb = pg.get_image_bbox(best)
    pix = pg.get_pixmap(dpi=300); pix.save(f"{R}\\drawing-{n}_page300.png")
    k = 300 / 72
    crop = Image.open(f"{R}\\drawing-{n}_page300.png").crop((int(bb.x0 * k), int(bb.y0 * k), int(bb.x1 * k), int(bb.y1 * k)))
    crop.save(f"{R}\\drawing-{n}_crop300.png")
    print(n, im.size, [round(v) for v in bb], crop.size)
# booklet long sections: stitch the two halves
B = D + r"\booklet_img"
for name, a, b in (("booklet_section_A_looking_north", 79, 83), ("booklet_section_B_looking_south", 77, 81)):
    A_ = Image.open(f"{B}\\bk_{a}.jpeg").convert("RGB"); B_ = Image.open(f"{B}\\bk_{b}.jpeg").convert("RGB")
    h = max(A_.height, B_.height)
    im = Image.new("RGB", (A_.width + B_.width, h), "white"); im.paste(A_, (0, 0)); im.paste(B_, (A_.width, 0))
    im.save(f"{R}\\{name}.png"); print(name, im.size)
for f in ("rpbw_long_section.jpg", "rpbw_roof_section_detail.jpg"):
    shutil.copy(D + "\\" + f, R + "\\" + f)
