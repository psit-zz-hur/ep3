"""CALACADEMY_DIAGRAM_MOCKUP_2026_11_07A: a static picture of THE DIAGRAM viewer with the California Academy of Sciences as the institution.
MOCKUP, placeholder data. Nothing functional. Drawn by THE DIAGRAM [1] (Claude) for Bryan, 2026-11-07, from ep3/research/cal-academy files 16 and 17 (and the counts in 15b).

python -I -B build_calacademy_diagram_mockup.py  ->  CALACADEMY_DIAGRAM_MOCKUP_2026_11_07A.html beside this script
open it with #A (the full disc and paper) or #B (the two zeros); the PNGs are screenshots of those two."""
import json, math, os

HERE = os.path.dirname(os.path.abspath(__file__))
NE = os.path.normpath(os.path.join(HERE, '..', '..', 'disciplinary-evolution', 'fuller_chart', 'data_ne'))
OUT = os.path.join(HERE, 'CALACADEMY_DIAGRAM_MOCKUP_2026_11_07A.html')

BLACK, RED, BLUE, CANARY = '#000000', '#ff4400', '#2c92ff', '#ffd500'
LAT0, LON0 = 37.76986, -122.46609          # the Academy, Golden Gate Park (file 17)
EARTH = 6371.0088

# ---------- the disc: azimuthal equidistant on the Academy, great-circle radius (the viewer's "gc") ----------
CX, CY, RMAP = 425, 540, 292


def geo(lat, lon):
    p0, p, dl = math.radians(LAT0), math.radians(lat), math.radians(lon - LON0)
    c = math.acos(max(-1, min(1, math.sin(p0) * math.sin(p) + math.cos(p0) * math.cos(p) * math.cos(dl))))
    az = math.atan2(math.sin(dl) * math.cos(p), math.cos(p0) * math.sin(p) - math.sin(p0) * math.cos(p) * math.cos(dl))
    return c, az


def km(lat, lon):
    return geo(lat, lon)[0] * EARTH


def proj(lat, lon):
    c, az = geo(lat, lon)
    r = RMAP * c / math.pi
    return CX + r * math.sin(az), CY - r * math.cos(az)


def dens(ring):
    out = []
    for (a, b), (c, d) in zip(ring, ring[1:] + ring[:1]):
        n = max(1, int(max(abs(c - a), abs(d - b)) / 1.0))
        out += [(a + (c - a) * i / n, b + (d - b) * i / n) for i in range(n)]
    return out


def rings(fn, closed=True):
    g = json.load(open(os.path.join(NE, fn), encoding='utf-8'))
    out = []
    for f in g['features']:
        t, cs = f['geometry']['type'], f['geometry']['coordinates']
        polys = [cs] if t in ('Polygon', 'MultiLineString') else cs if t == 'MultiPolygon' else [[cs]]
        if t == 'MultiLineString': polys = [cs]
        for poly in polys:
            for ring in poly:
                pts = dens([(p[0], p[1]) for p in ring]) if closed else ring
                out.append(pts)
    return out


def path(rs, close=True):
    s = []
    for r in rs:
        xy = [proj(lat, lon) for lon, lat in r]
        s.append('M' + 'L'.join('%.1f,%.1f' % p for p in xy) + ('Z' if close else ''))
    return ''.join(s)


LAND = path(rings('ne_110m_land.geojson'))
LAKES = path(rings('ne_110m_lakes.geojson'))
BORD = path(rings('ne_110m_admin_0_boundary_lines_land.geojson', closed=False), close=False)

# ---------- placeholder data (MOCKUP) ----------
# the 12 GBIF datasets (15b D1-D12): label, records (15b, live-tested), first / last collecting year (PLACEHOLDER), running
DATASETS = [
    ('BOTANY (BOT)', 1909776, 1850, 2029, True),
    ('ANTWEB', 917346, 1950, 2029, True),
    ('ENTOMOLOGY (ENT)', 352537, 1878, 2029, True),
    ('HERPETOLOGY (HERP)', 320148, 1886, 2029, True),
    ('INVERTEBRATE ZOOLOGY (IZ)', 285564, 1899, 2029, True),
    ('ICHTHYOLOGY (ICH)', 220947, 1890, 2029, True),
    ('ORNITHOLOGY (ORN)', 102794, 1868, 2029, True),
    ('MAMMALOGY (MAM)', 40006, 1892, 2029, True),
    ('GEOLOGY (GEO)', 23880, 1906, 2029, True),
    ('ENTOMOLOGY TYPE (TYPE)', 17942, 1880, 2021, False),
    ('ORNITHOLOGY EGG AND NEST (EGG)', 11190, 1871, 1992, False),
    ('GEOLOGY MICROFOSSIL', 241, 1951, 1988, False),
]
SERIES = [('PROCEEDINGS OF THE CALIFORNIA ACADEMY OF SCIENCES', 1854, 2029, True)]
COLLECTIONS = [  # OAC finding-aid ranges, PLACEHOLDER
    ('ALICE EASTWOOD PAPERS', 1879, 1953, False),
    ('ROLLO H. BECK PAPERS', 1897, 1949, False),
    ('GALAPAGOS EXPEDITION RECORDS', 1905, 1907, False),
    ('SAN FRANCISCO EARTHQUAKE OF 1906 COLLECTION', 1906, 1912, False),
]
BUILDINGS = [  # file 16, [verify] years kept as PLACEHOLDER
    ('MARKET STREET', 1891, 1906, False),
    ('GOLDEN GATE PARK HALLS', 1916, 2004, False),
    ('STEINHART AQUARIUM', 1923, 2004, False),
    ('MORRISON PLANETARIUM', 1952, 2004, False),
    ('HOWARD STREET (TEMPORARY)', 2004, 2008, False),
    ('PIANO BUILDING', 2008, 2029, True),
]
PEOPLE = [  # careers as spans, PLACEHOLDER
    ('ALICE EASTWOOD · BOTANY', 1892, 1949, False),
    ('JOHN VAN DENBURGH · HERPETOLOGY', 1894, 1924, False),
    ('JOSEPH R. SLEVIN · HERPETOLOGY', 1905, 1957, False),
    ('BARTON W. EVERMANN · DIRECTOR', 1914, 1932, False),
]
# collecting localities: name, lat, lon, [(from, to, specimens)]   PLACEHOLDER counts
PLACES = [
    ('SAN FRANCISCO BAY', 37.85, -122.25, [(1907, 2026, 96000)]),
    ('SIERRA NEVADA', 37.6, -119.2, [(1910, 2026, 58000)]),
    ('BAJA CALIFORNIA', 28.0, -113.0, [(1921, 2026, 31000)]),
    ('GALAPAGOS ISLANDS', -0.6, -90.4, [(1905, 1906, 4568)]),
    ('COSTA RICA', 10.0, -84.0, [(1960, 2026, 14000)]),
    ('OAXACA', 17.0, -96.7, [(1935, 2010, 9000)]),
    ('HAWAII', 20.0, -156.5, [(1920, 2020, 7000)]),
    ('ALASKA', 61.2, -149.9, [(1925, 2000, 3800)]),
    ('PERU', -12.0, -76.9, [(1950, 2020, 4200)]),
    ('PHILIPPINES', 13.6, 121.0, [(1950, 2015, 77824)]),
    ('YUNNAN', 25.0, 100.0, [(1980, 2026, 16000)]),
    ('PAPUA NEW GUINEA', -6.0, 145.0, [(1960, 2020, 8500)]),
    ('JAPAN', 35.0, 138.5, [(1930, 2010, 3000)]),
    ('AUSTRALIA', -25.0, 134.0, [(1960, 2020, 5200)]),
    ('MADAGASCAR', -19.0, 47.0, [(1990, 2026, 30000)]),
    ('GULF OF GUINEA', 1.5, 7.5, [(2001, 2026, 9000)]),
    ('SOUTH AFRICA', -33.9, 18.6, [(1975, 2026, 6000)]),
]
BUILDING_BIRDS = {2008: 88, 2009: 74, 2010: 31, 2011: 22, 2012: 25, 2013: 30, 2014: 41, 2015: 38, 2016: 33, 2017: 29, 2018: 52, 2019: 121, 2020: 18, 2021: 34, 2022: 56}   # sums to 692
BUILDING_OTHER = {2019: 150, 2022: 140, 2010: 30, 2014: 25, 2016: 34}   # insects and the rest, 379 -> 1,071 with the birds
GAL_KM = km(-0.6, -90.4)
LOMA_KM = km(37.04, -121.88)


def counts_per_year(y):
    """placeholder records per year (the GBIF census shape: next to nothing before 1906, the 1905-06 jump, the climb)."""
    if y < 1905: v = 300 + 40 * (y - 1850)
    elif y <= 1906: v = 9000
    elif y < 1940: v = 1500 + 260 * (y - 1907)
    elif y < 1946: v = 5200
    else: v = 9000 + 520 * (y - 1946)
    if 2020 <= y <= 2021: v *= 0.7
    if y > 2024: v *= 0.6
    return v


def shape(y, s, e):
    """placeholder records-per-year shape: next to nothing before 1905, the 1905-06 Galapagos jump, the climb to today."""
    if y < s or y > e: return 0.0
    if y < 1905: return 0.12
    if y <= 1906: return 0.7
    if y < 1946: return 0.3
    return 0.35 + 0.65 * min(1, (y - 1946) / 70) ** 1.6


_SHAPE = {}


def rate(y, total, s, e):
    """placeholder records per year for a dataset: its live total (15b) spread over the shape above."""
    key = (total, s, e)
    if key not in _SHAPE: _SHAPE[key] = sum(shape(v, s, min(e, 2026)) for v in range(s, min(e, 2026) + 1))
    return total * shape(y, s, min(e, 2026)) / _SHAPE[key]


def thick(y, total, s, e):
    if y < s or y > e: return 0
    b = 0.25 if y < 1905 else (0.75 if y <= 1906 else 0.38 if y < 1946 else 0.55 + 0.45 * min(1, (y - 1946) / 70))
    return b * (1.2 + 7.0 * math.log10(total) / math.log10(1909776))


SHORT = {'BOTANY (BOT)': 'BOTANY', 'ANTWEB': 'ANTWEB', 'ENTOMOLOGY (ENT)': 'ENTOMOLOGY', 'HERPETOLOGY (HERP)': 'HERPETOLOGY',
         'INVERTEBRATE ZOOLOGY (IZ)': 'INVERTEBRATE ZOOLOGY', 'ICHTHYOLOGY (ICH)': 'ICHTHYOLOGY', 'ORNITHOLOGY (ORN)': 'ORNITHOLOGY',
         'MAMMALOGY (MAM)': 'MAMMALOGY', 'GEOLOGY (GEO)': 'GEOLOGY', 'ENTOMOLOGY TYPE (TYPE)': 'ENTOMOLOGY TYPE',
         'ORNITHOLOGY EGG AND NEST (EGG)': 'EGG AND NEST', 'GEOLOGY MICROFOSSIL': 'MICROFOSSIL'}


GBIF = json.load(open(os.path.join(HERE, 'CALACADEMY_GBIF_YEAR_COUNTS_2026_11_07A.json'), encoding='utf-8'))
YR = lambda d: {int(k): v for k, v in d['years'].items()}
CODE = {'BOTANY (BOT)': 'BOT', 'ANTWEB': 'ANTWEB', 'ENTOMOLOGY (ENT)': 'ENT', 'HERPETOLOGY (HERP)': 'HERP', 'INVERTEBRATE ZOOLOGY (IZ)': 'IZ',
        'ICHTHYOLOGY (ICH)': 'ICH', 'ORNITHOLOGY (ORN)': 'ORN', 'MAMMALOGY (MAM)': 'MAM', 'GEOLOGY (GEO)': 'GEO',
        'ENTOMOLOGY TYPE (TYPE)': 'TYPE', 'ORNITHOLOGY EGG AND NEST (EGG)': 'EGG', 'GEOLOGY MICROFOSSIL': 'MICRO'}


def sk_flows(B):
    """the flows: GBIF records per collecting year (queried 2026-11-07), real counts."""
    if B:
        g, b = GBIF['galapagos_1905_06'], GBIF['building_birds']
        return [dict(label='GALAPAGOS 1905–06 · ECUADOR', years=YR(g), undated=g['total'] - g['with_year']),
                dict(label='THE BUILDING · BIRDS (ORN)', years=YR(b), undated=b['total'] - b['with_year'])]
    out = []
    for lab, n, s_, e, run in DATASETS:
        d = GBIF['datasets'][CODE[lab]]
        out.append(dict(label=SHORT[lab], years=YR(d), undated=d['total'] - d['with_year']))
    return out


def sk_so_far(B):
    """specimens so far under the hand: every dated record with a collecting year up to 2026."""
    return sum(c for f in sk_flows(B) for yv, c in f['years'].items() if yv <= 2026)


def build(frame):
    B = frame == 'B'
    YEAR = 2026
    PK = 0.17 if B else 0.075   # the PING dial
    o = []
    A = o.append

    # ---------------- the disc ----------------
    ang = lambda y: (y - 1850) / 200 * 2 * math.pi
    pol = lambda r, a: (CX + r * math.sin(a), CY - r * math.cos(a))
    A('<g id="disc">')
    for d in range(1000, 20001, 1000):           # distance rings under the land
        r = RMAP * d / (math.pi * EARTH)
        A('<circle cx="%d" cy="%d" r="%.1f" fill="none" stroke="#000" stroke-width="%s"/>' % (CX, CY, r, '0.7' if d % 5000 == 0 else '0.3'))
    A('<circle cx="%d" cy="%d" r="%d" fill="none" stroke="#000" stroke-width="1"/>' % (CX, CY, RMAP))
    for k in range(0, 360, 30):                  # bearings
        a = math.radians(k); x, y = pol(RMAP, a)
        A('<line x1="%d" y1="%d" x2="%.1f" y2="%.1f" stroke="#000" stroke-width="0.3"/>' % (CX, CY, x, y))
    A('<path d="%s" fill="#000" fill-rule="nonzero"/>' % LAND)
    A('<path d="%s" fill="#fff"/>' % LAKES)
    A('<path d="%s" fill="none" stroke="#fff" stroke-width="0.45"/>' % BORD)
    for d, t in ((5000, '5,000 KM'), (10000, '10,000 KM'), (15000, '15,000 KM')):
        r = RMAP * d / (math.pi * EARTH)
        A('<text class="dk" x="%d" y="%.1f">%s</text>' % (CX + 3, CY - r - 2, t))
    A('<text class="dk" x="%d" y="%.1f">ANTIPODE · 20,015 KM</text>' % (CX + 3, CY - RMAP - 3))

    # pings: RDS red discs, the land inside them in FO blue (the tool's GOHARD ping look), sized by sqrt(specimens so far)
    pings = []
    for name, lat, lon, spans in PLACES:
        if B and name != 'GALAPAGOS ISLANDS': continue
        n = sum(c for s, e, c in spans if s <= YEAR)
        x, y = proj(lat, lon)
        pings.append((name, x, y, max(4.5, PK * math.sqrt(n)), n))
    nb = sum(BUILDING_BIRDS.values()) if B else sum(BUILDING_BIRDS.values()) + sum(BUILDING_OTHER.values())
    A('<clipPath id="pc%s">' % frame + ''.join('<circle cx="%.1f" cy="%.1f" r="%.1f"/>' % (x, y, r) for _, x, y, r, _ in pings) + '</clipPath>')
    for _, x, y, r, _ in pings: A('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s"/>' % (x, y, r, RED))
    A('<g clip-path="url(#pc%s)"><path d="%s" fill="%s"/></g>' % (frame, LAND, BLUE))
    for name, x, y, r, n in pings:
        if B or (n > 20000 and km(*[p for p in PLACES if p[0] == name][0][1:3]) > 3000) or name == 'GALAPAGOS ISLANDS':
            lab = name + (' · 1905–06 · %s SPECIMENS · %s KM' % (format(n, ','), format(int(round(GAL_KM, -2)), ',')) if B else '')
            A('<text class="pl" x="%.1f" y="%.1f">%s</text>' % (x + r + 3, y + 2.5, lab))
    # the centre: the building's own specimens at 0 km
    rb = max(4.5, PK * math.sqrt(nb))
    A('<circle cx="%d" cy="%d" r="%.1f" fill="%s"/>' % (CX, CY, rb, RED))
    A('<path d="M%d,%dh18M%d,%dv18" stroke="#000" stroke-width="2.4"/>' % (CX - 9, CY, CX, CY - 9))
    lab = 'THE BUILDING · %s WINDOW-STRIKE BIRDS · 0 KM' % format(nb, ',') if B else 'CAS · 0 KM · %s SPECIMENS AT THE BUILDING' % format(nb, ',')
    A('<text class="pl" x="%d" y="%d" style="text-anchor:end">%s</text>' % (CX - 12, CY + 22, lab))

    # the ring: the 12 datasets as arcs (12 o'clock = 1850, one turn = 200 years)
    R0 = RMAP + 14
    if not B:
        for i, (lab, n, s, e, run) in enumerate(DATASETS):
            yrs = [v for v in YR(GBIF['datasets'][CODE[lab]]) if v <= 2026]
            if not yrs: continue
            s, e = max(1850, min(yrs)), max(yrs)
            r = R0 + i * 6.2
            a0, a1 = ang(s), ang(min(e, 2029))
            x0, y0 = pol(r, a0); x1, y1 = pol(r, a1)
            w = 1.0 + 3.4 * math.log10(max(n, 10)) / math.log10(1909776)
            A('<path d="M%.1f,%.1fA%.1f,%.1f 0 %d 1 %.1f,%.1f" fill="none" stroke="#000" stroke-width="%.2f"/>' % (x0, y0, r, r, 1 if a1 - a0 > math.pi else 0, x1, y1, w))
    RY = R0 + 12 * 6.2 + 14                     # the year dial
    A('<circle cx="%d" cy="%d" r="%.1f" fill="none" stroke="#000" stroke-width="0.8"/>' % (CX, CY, RY))
    for y in range(1850, 2050):
        a = ang(y); big = y % 10 == 0
        x0, y0 = pol(RY, a); x1, y1 = pol(RY + (7 if big else 3), a)
        A('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#000" stroke-width="%s"/>' % (x0, y0, x1, y1, '0.9' if big else '0.4'))
        if big:
            A('<text class="dec" transform="rotate(%.2f %d %d)" x="%d" y="%.1f">%ds</text>' % (math.degrees(a) + 9, CX, CY, CX, CY - RY - 12, y))
    # the 1906 rule, radial, RDS red
    a = ang(1906); x0, y0 = pol(RMAP, a); x1, y1 = pol(RY + 9, a)
    A('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1.6"/>' % (x0, y0, x1, y1, RED))
    A('<text class="rl" transform="rotate(%.2f %.1f %.1f)" x="%.1f" y="%.1f">1906</text>' % (math.degrees(a) - 90, x1, y1, x1 + 4, y1 + 3))
    # the events on the dial: red ticks, Galapagos as a red arc (Bryan 11/07: the red events live on the disc and in the lanes)
    if not B:
        for yv, t in ((1853.3, '1853'), (1989.8, '1989'), (2008.8, '2008')):
            a = ang(yv); x0, y0 = pol(RY - 6, a); x1, y1 = pol(RY + 9, a)
            A('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1.6"/>' % (x0, y0, x1, y1, RED))
    a0, a1 = ang(1905.45), ang(1906.9); rr = RY - 4
    x0, y0 = pol(rr, a0); x1, y1 = pol(rr, a1)
    A('<path d="M%.1f,%.1fA%.1f,%.1f 0 0 1 %.1f,%.1f" fill="none" stroke="%s" stroke-width="5"/>' % (x0, y0, rr, rr, x1, y1, RED))
    # the hand
    a = ang(YEAR); x0, y0 = pol(RMAP - 40, a); x1, y1 = pol(RY + 30, a)
    A('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1.3"/>' % (x0, y0, x1, y1, RED))
    x2, y2 = pol(RY + 44, a)
    A('<text class="hand" x="%.1f" y="%.1f">%d</text>' % (x2 - 16, y2 + 5, YEAR))
    A('</g>')

    # ---------------- the chart: lanes and the records strip (the paper cut by Bryan, 11/07 21:19) ----------------
    X0, X1 = 1110, 1700
    X = lambda y: X0 + (y - 1850) * (X1 - X0) / 180
    A('<g id="chart">')
    # numerals (the chart's own, part of the drawing)
    so_far = sk_so_far(B)
    A('<text class="nl" x="%d" y="96">YEAR</text><text class="nb" x="%d" y="146">%d</text>' % (X0, X0, YEAR))
    A('<text class="nl" x="%d" y="96">SPECIMENS SO FAR</text><text class="nb" x="%d" y="146">%s</text>' % (X0 + 170, X0 + 170, format(so_far, ',')))
    A('<text class="nl r" x="%d" y="96">CALIFORNIA ACADEMY OF SCIENCES</text><text class="ns" x="%d" y="114">GOLDEN GATE PARK · 37.76986 N 122.46609 W · 0 KM</text>' % (X1, X1))
    # header: decades and years (Fuller's paper)
    HT = 168
    A('<rect x="%d" y="%d" width="%d" height="30" fill="none" stroke="#000" stroke-width="0.8"/>' % (X0, HT, X1 - X0))
    for y in range(1850, 2031):
        x = X(y)
        if y % 10 == 0:
            A('<line x1="%.1f" y1="%d" x2="%.1f" y2="%d" stroke="#000" stroke-width="0.8"/>' % (x, HT, x, HT + 30))
            if y < 2030: A('<text class="hd" x="%.1f" y="%d">%ds</text>' % (x + (X(y + 10) - x) / 2, HT + 16, y))
        A('<line x1="%.1f" y1="%d" x2="%.1f" y2="%d" stroke="#000" stroke-width="0.3"/>' % (x, HT + 21, x, HT + 30))
    A('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="#000" stroke-width="0.4"/>' % (X0, HT + 21, X1, HT + 21))

    # Bryan 11/07: the paper is gone (21:19); the lanes fill the height (21:20); the datasets are Sankey flows (21:3x):
    # width = specimens so far by collecting year (GBIF, cumulative, linear); "keep the representation accurate";
    # "Growth downwards on bottom edge, align to top": each band's top edge is flat, its bottom edge grows down
    EVENTS = [('1853 · FOUNDED · DOWNTOWN SAN FRANCISCO', 1853.3, None), ('GALAPAGOS · JUN 1905 – NOV 1906 · %s KM' % format(int(round(GAL_KM, -2)), ','), 1905.45, 1906.9),
              ('1906 · EARTHQUAKE AND FIRE · THE COLLECTION LOST', 1906.3, None), ('1989 · LOMA PRIETA · %d KM' % round(LOMA_KM), 1989.8, None), ('2008 · THE PIANO BUILDING OPENS', 2008.8, None)]
    TOP, FOOT, HDR, GAP, RO = HT + 46, 980, 22, 6, 12.5
    flows = sk_flows(B)
    if B:
        groups = [("EVENTS · THE ACADEMY'S OWN RECORD", 'ev', [EVENTS[1]]), ('THE TWO ZEROS · SPECIMENS SO FAR, BY COLLECTING YEAR', 'sk', flows)]
    else:
        groups = [("EVENTS · THE ACADEMY'S OWN RECORD", 'ev', EVENTS), ('DATASETS · GBIF · SPECIMENS SO FAR, BY COLLECTING YEAR', 'sk', flows), ('SERIES', 'bar', SERIES),
                  ('COLLECTIONS · OAC FINDING AIDS', 'bar', COLLECTIONS), ('BUILDINGS', 'bar', BUILDINGS), ('PEOPLE', 'bar', PEOPLE)]
    rest = FOOT - TOP - (HDR + GAP) * len(groups) - RO * sum(len(g[2]) for g in groups if g[1] != 'sk')
    y0 = TOP
    for title, kind, rows in groups:
        A('<text class="ln" x="%d" y="%.1f">%s</text>' % (X0 - 6, y0 + 8, title))
        y0 += HDR
        if kind == 'sk':
            MINR, G2 = 11.0, 2.0
            finals = [sum(c for yv, c in f['years'].items() if yv <= YEAR) for f in rows]
            S = rest / sum(fn + G2 for fn in finals)
            for _ in range(60): S *= rest / sum(max(S * fn, MINR) + G2 for fn in finals)
            xe = X(YEAR + 0.5)
            for f, fn in zip(rows, finals):
                h = max(S * fn, MINR)
                top = y0                                     # the flat top edge
                if fn > 0:
                    pts, run = [], sum(c for yv, c in f['years'].items() if yv < 1850)
                    for t in range(1850, YEAR + 1):
                        run += f['years'].get(t, 0)
                        pts.append((X(t + 0.5), top + S * run))
                    pts = [(X(1850), pts[0][1])] + pts
                    A('<path d="M%.1f,%.1fL%sL%.1f,%.1fZ" fill="#000"/>' % (X(1850), top, 'L'.join('%.1f,%.1f' % q for q in pts), xe, top))
                lab = '%s · <tspan class="tot">%s</tspan>' % (f['label'], format(fn, ','))
                if f.get('undated'): lab += ' · %s UNDATED' % format(f['undated'], ',')
                if fn == 0: lab = '%s · <tspan class="tot">%s</tspan> · NO COLLECTING YEAR IN GBIF' % (f['label'], format(f['undated'], ','))
                A('<text class="bl" x="%.1f" y="%.1f" style="text-anchor:start">%s</text>' % (xe + 8, top + min(h, 40) / 2 + 3 if fn else top + 7, lab))
                y0 += h + G2
            y0 += GAP
            continue
        for row in rows:
            h = RO; cy = y0 + h / 2
            if kind == 'ev':
                lab, s, e = row
                if e is None:
                    A('<circle cx="%.1f" cy="%.1f" r="3.4" fill="%s"/>' % (X(s), cy, RED))
                    lx, anc = (X(s) + 7, 'start') if s < 1980 else (X(s) - 7, 'end')
                else:
                    A('<rect x="%.1f" y="%.1f" width="%.1f" height="6.4" fill="%s"/>' % (X(s), cy - 3.2, X(e) - X(s), RED)); lx, anc = X(e) + 6, 'start'
                A('<text class="ev big" x="%.1f" y="%.1f" style="text-anchor:%s">%s</text>' % (lx, cy + 3, anc, lab))
            else:
                lab, s, e, run = row
                A('<rect x="%.1f" y="%.1f" width="%.1f" height="5.6" fill="#000"/>' % (X(s), cy - 2.8, X(min(e, 2029) + 1) - X(s)))
                if run:
                    xe2 = X(2029) + 3
                    A('<path d="M%.1f,%.1fL%.1f,%.1fL%.1f,%.1fZ" fill="#000"/>' % (xe2, cy - 2.8, xe2 + 26, cy, xe2, cy + 2.8))
                A('<text class="bl" x="%.1f" y="%.1f">%s</text>' % (X(s) - 5, cy + 3, lab))
            y0 += h
        y0 += GAP
    FOOT = y0
    A('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="#000" stroke-width="0.8"/>' % (X0, FOOT, X1, FOOT))
    for yv in range(1850, 2031, 10):
        A('<line x1="%.1f" y1="%d" x2="%.1f" y2="%d" stroke="#000" stroke-width="0.8"/>' % (X(yv), FOOT, X(yv), FOOT + 5))
    # the 1906 rule, red, through the lanes
    A('<line x1="%.1f" y1="%d" x2="%.1f" y2="%d" stroke="%s" stroke-width="1.6"/>' % (X(1906.3), HT, X(1906.3), FOOT, RED))
    PB = FOOT
    # the playhead
    A('<line x1="%.1f" y1="%d" x2="%.1f" y2="%d" stroke="%s" stroke-width="1"/>' % (X(YEAR + 0.5), HT - 10, X(YEAR + 0.5), PB, RED))
    A('<text class="ph" x="%.1f" y="%d">%d</text>' % (X(YEAR + 0.5) + 3, HT - 3, YEAR))
    A('</g>')
    return '\n'.join(o)


CSS = """
:root { color-scheme: light; }
html, body { margin: 0; background: #fff; }
body { width: 1920px; height: 1080px; overflow: hidden; font-family: 'Barlow', Arial, sans-serif; color: #000; position: relative; }
svg { position: absolute; left: 0; top: 0; }
text { font-family: 'Barlow Condensed', 'Arial Narrow', Arial, sans-serif; fill: #000; }
.dk, .pl { paint-order: stroke; stroke: #fff; stroke-width: 2.6px; stroke-linejoin: round; }
.dk { font-size: 6.5px; font-weight: 600; letter-spacing: .12em; }
.pl { font-size: 7.6px; font-weight: 600; letter-spacing: .12em; }
.dec { font-size: 9.5px; font-weight: 600; letter-spacing: .06em; text-anchor: middle; }
.ev.big { font-size: 8.4px; }
.rl, .ev { font-size: 7.2px; font-weight: 700; letter-spacing: .12em; fill: #ff4400; }
.hand { font-size: 15px; font-weight: 600; fill: #ff4400; }
.ph { font-size: 9px; font-weight: 600; fill: #ff4400; }
.nl { font-size: 9px; font-weight: 700; letter-spacing: .16em; }
.nb { font-size: 46px; font-weight: 500; letter-spacing: .01em; }
.ns { font-size: 7.5px; font-weight: 600; letter-spacing: .14em; text-anchor: end; }
.nl.r { text-anchor: end; }
.hd { font-size: 11px; font-weight: 700; letter-spacing: .04em; text-anchor: middle; }
.ln { font-size: 8px; font-weight: 700; letter-spacing: .16em; text-anchor: end; fill: #ff4400; }
.tot { font-size: 9px; font-weight: 700; letter-spacing: .06em; }
.bl { font-size: 7.6px; font-weight: 600; letter-spacing: .16em; text-anchor: end; }
.ak { font-size: 6.5px; font-weight: 600; letter-spacing: .1em; text-anchor: end; }
.gl { font-size: 6.6px; font-weight: 700; letter-spacing: .14em; text-anchor: end; }
#trow { position: absolute; left: 22px; bottom: 18px; display: flex; align-items: center; gap: 12px; font: 600 12px/1 'Barlow', Arial, sans-serif; letter-spacing: .06em; }
#trow .b { width: 26px; height: 26px; border: 1px solid #000; display: grid; place-items: center; font-size: 13px; box-sizing: border-box; }
#trow .b.on { background: #000; color: #fff; }
#trow .dash { width: 14px; text-align: center; font-size: 16px; }
#trow .k { margin-left: 18px; }
#trow .sl { width: 92px; height: 4px; background: #000; position: relative; border-radius: 2px; }
#trow .sl i { position: absolute; top: -5px; width: 14px; height: 14px; border-radius: 50%; background: #fff; border: 1.5px solid #000; box-sizing: border-box; }
#trow .v { min-width: 34px; font-weight: 500; }
#trow .pn { margin-left: 26px; border: 1px solid #000; padding: 6px 9px; text-transform: uppercase; }
#foot { position: absolute; right: 26px; bottom: 22px; text-align: right; font: 700 10px/1.5 'Barlow Condensed', Arial, sans-serif; letter-spacing: .2em; }
#foot .m { color: #ff4400; font-size: 12px; }
"""


def page():
    a, b = build('A'), build('B')
    trow = lambda v, slider_year: ('<div id="trow"><span class="dash">–</span><span class="b%s">1</span><span class="b%s">2</span><span class="b">3</span>'
                                   '<span class="b">&#9654;</span><span class="k">YEAR</span><span class="sl"><i style="left:%dpx"></i></span><span class="v">2026</span>'
                                   '<span class="k">SPEED</span><span class="sl"><i style="left:22px"></i></span><span class="v">6 yr/s</span>'
                                   '<span class="k">PING</span><span class="sl"><i style="left:%dpx"></i></span><span class="v">%s</span>'
                                   '<span class="pn">Panels</span></div>') % (' on' if v == 'A' else '', ' on' if v == 'B' else '', slider_year, 40 if v == 'A' else 80, '92 u' if v == 'A' else '210 u')
    foot = lambda v: ('<div id="foot"><div class="m">MOCKUP · DATASET BANDS: GBIF, REAL COUNTS (QUERIED 2026-11-07) · DISC PINGS, LANES AND EVENTS: PLACEHOLDER</div>'
                      '<div>THE COLLECTING DISC · CALIFORNIA ACADEMY OF SCIENCES · %s</div>'
                      '<div>DATASETS: GBIF (CAS, 12 DATASETS) · ARCHIVES: OAC FINDING AIDS · MAP: NATURAL EARTH 1:110M</div></div>') % (
                          'VIEW 1 · ALL LAYERS' if v == 'A' else 'VIEW 2 · THE TWO ZEROS: GALAPAGOS 1905–06 AND THE BUILDING\'S WINDOW-STRIKE BIRDS')
    return ('<!doctype html>\n<html lang="en"><head><meta charset="utf-8">\n<title>Cal Academy diagram mockup</title>\n'
            '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
            '<link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@400;500;600;700&family=Barlow:wght@400;500;600&display=swap" rel="stylesheet">\n'
            '<style>' + CSS + '</style></head><body>\n'
            '<!-- MOCKUP, placeholder data. THE DIAGRAM [1] for Bryan, 2026-11-07. #A full disc and paper, #B the two zeros. -->\n'
            '<section id="A"><svg width="1920" height="1080" viewBox="0 0 1920 1080">' + a + '</svg>' + trow('A', 86) + foot('A') + '</section>\n'
            '<section id="B"><svg width="1920" height="1080" viewBox="0 0 1920 1080">' + b + '</svg>' + trow('B', 86) + foot('B') + '</section>\n'
            '<style>section { position: absolute; inset: 0; } #B { display: none; } body.b #A { display: none; } body.b #B { display: block; }</style>\n'
            '<script>function f() { document.body.className = location.hash === "#B" ? "b" : ""; } addEventListener("hashchange", f); f();</script>\n'
            '</body></html>\n')


open(OUT, 'w', encoding='utf-8').write(page())
print(OUT, os.path.getsize(OUT), 'bytes · Galapagos %.0f km · Loma Prieta %.0f km' % (GAL_KM, LOMA_KM))
