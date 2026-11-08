"""California by county (GADM level 2) for the CAS publisher, per decade of collecting year: counts only.
python -I -B fetch_calacademy_ca_counties_2026_11_07A.py -> CALACADEMY_GBIF_CA_COUNTIES_2026_11_07A.json (beside this file)
GBIF occurrence search, no key; GADM covers only georeferenced records (the rest is California, county not given)."""
import json, os, time, urllib.request, urllib.parse
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'CALACADEMY_GBIF_CA_COUNTIES_2026_11_07A.json')
ORG = '66522820-055c-11d8-b84e-b8a03c50a862'
UA = {'User-Agent': 'calacademy-diagram/1.0'}
BINS = [('before 1850', 1500, 1849)] + [(str(d), d, d + 9) for d in range(1850, 2030, 10)]


def get(url):
    for i in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
                return json.loads(r.read().decode('utf-8'))
        except Exception as e:
            last = e; time.sleep(2 + 3 * i)
    raise last


def q(**kw):
    base = 'https://api.gbif.org/v1/occurrence/search?'
    return base + urllib.parse.urlencode(kw, safe=',')


doc = dict(queried=time.strftime('%Y-%m-%dT%H:%M'), source='GBIF occurrence search API, publishingOrg = California Academy of Sciences, '
           'gadmGid = USA.5_1 (California), facet = gadmLevel2Gid (county) by decade of collecting year; GADM = georeferenced records only',
           decades={}, names={})
allq = q(publishingOrg=ORG, gadmGid='USA.5_1', limit=0, facet='gadmLevel2Gid', facetLimit=100)
a = get(allq)
doc['all_years'] = dict(query=allq, total=a['count'], counties={c['name']: c['count'] for c in a['facets'][0]['counts']} if a.get('facets') else {})
for name, y0, y1 in BINS:
    url = q(publishingOrg=ORG, gadmGid='USA.5_1', limit=0, facet='gadmLevel2Gid', facetLimit=100, year=f'{y0},{y1}')
    r = get(url)
    cs = {c['name']: c['count'] for c in r['facets'][0]['counts']} if r.get('facets') else {}
    doc['decades'][name] = dict(query=url, total=r['count'], counties=cs)
    print(name, r['count'], len(cs), flush=True)
gids = sorted({g for d in doc['decades'].values() for g in d['counties']} | set(doc['all_years']['counties']))
for g in gids:
    try:
        r = get('https://api.gbif.org/v1/geocode/gadm/' + urllib.parse.quote(g))
        doc['names'][g] = r.get('name') or r.get('englishType') or g
    except Exception as e:
        doc['names'][g] = None
print(len(gids), 'counties named')
json.dump(doc, open(OUT, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
print('wrote', OUT)
