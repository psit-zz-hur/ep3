import fitz, glob, os, json
D = r"C:\Users\bryan\Documents\Claude\ep3\data\cal-academy\drawings"
out = {}
for f in sorted(glob.glob(D + r"\drawing-*.pdf")):
    d = fitz.open(f); pg = d[0]
    dr = pg.get_drawings()
    imgs = pg.get_images(full=True)
    txt = pg.get_text().replace("\n", " | ")
    out[os.path.basename(f)] = dict(pages=len(d), w=pg.rect.width, h=pg.rect.height, paths=len(dr), images=len(imgs),
                                    imgsizes=[(i[2], i[3]) for i in imgs], text=txt[:400])
    print(os.path.basename(f), len(d), round(pg.rect.width), round(pg.rect.height), "paths", len(dr), "imgs", [(i[2], i[3]) for i in imgs], "|", txt[:300])
for f in ("fondazione_catalogue.pdf", "fondazione_booklet.pdf"):
    p = os.path.join(D, f)
    if os.path.exists(p):
        d = fitz.open(p); print(f, len(d), [(round(x.rect.width), round(x.rect.height)) for x in list(d)[:3]])
        if "booklet" in f:
            for i, x in enumerate(d): print(" p", i + 1, round(x.rect.width), round(x.rect.height), "paths", len(x.get_drawings()), "imgs", len(x.get_images()), x.get_text()[:100].replace("\n", " "))
json.dump(out, open(D + r"\census_raw.json", "w"), indent=1)
