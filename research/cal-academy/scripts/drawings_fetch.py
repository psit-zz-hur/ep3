"""Fetch RPBW / Fondazione drawing sheets (reference use only, (c) RPBW). Sequential, 2 s apart."""
import os, time, requests, re
D = r"C:\Users\bryan\Documents\Claude\ep3\data\cal-academy\drawings"
os.makedirs(D, exist_ok=True)
os.makedirs(os.path.join(D, "archdaily"), exist_ok=True)
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
H = {"User-Agent": UA}
items = []
base = "https://www.fondazionerenzopiano.org/en/project/california-academy-of-sciences/"
for n in "235 352 289 613 337 243 240 336 275 328 279 285 311 354 355 303 304".split():
    items.append((f"{base}drawing-{n}.pdf", f"drawing-{n}.pdf"))
items.append(("https://www.fondazionerenzopiano.org/en/project/california-academy-of-sciences.pdf", "fondazione_catalogue.pdf"))
items.append(("https://www.fondazionerenzopiano.org/en/page/california-california-academy-of-sciences/download-book", "fondazione_booklet.pdf"))
items.append(("https://cdn.sanity.io/images/zi3g9jaq/production/9037e5ae3a056f89e4e311055a5b8f15e203f05c-1400x343.jpg", "rpbw_long_section.jpg"))
items.append(("https://cdn.sanity.io/images/zi3g9jaq/production/4c998f3c54927ae6e708e8583119c19361fd92db-1320x1023.jpg", "rpbw_roof_section_detail.jpg"))

def get(u, name):
    p = os.path.join(D, name)
    if os.path.exists(p) and os.path.getsize(p) > 10000:
        print("skip", name); return
    try:
        r = requests.get(u, headers=H, timeout=120)
        if r.status_code == 200 and len(r.content) > 1000:
            open(p, "wb").write(r.content); print("ok  ", name, len(r.content))
        else:
            print("FAIL", name, r.status_code, len(r.content))
    except Exception as e:
        print("ERR ", name, e)
    time.sleep(2)

for u, n in items:
    get(u, n)
# ArchDaily
try:
    r = requests.get("https://www.archdaily.com/6810/california-academy-of-sciences-renzo-piano", headers=H, timeout=60)
    urls = sorted(set(re.findall(r'https://images\.adsttc\.com/media/images/[^"\' ?]+/medium_jpg/stringio\.jpg', r.text)))
    print("archdaily urls", len(urls), r.status_code)
    for u in urls:
        u2 = u.replace("medium_jpg", "large_jpg")
        n = "archdaily/ad_" + "_".join(u2.split("/")[6:8]) + ".jpg"
        get(u2, n)
except Exception as e:
    print("archdaily ERR", e)
