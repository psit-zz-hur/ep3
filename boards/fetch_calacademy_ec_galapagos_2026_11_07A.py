"""Ecuador split into Galapagos / mainland for the CAS publisher, per decade of collecting year: counts only.
python -I -B fetch_calacademy_ec_galapagos_2026_11_07A.py -> CALACADEMY_GBIF_EC_PROVINCES_2026_11_07A.json (beside this file)
GBIF's country EC holds the Galapagos; stateProvince (free text) names them ('Galapagos Islands', 'Galapagos Prov.', ...)."""
import json, os, time, urllib.request, urllib.parse
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'CALACADEMY_GBIF_EC_PROVINCES_2026_11_07A.json')
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
    return 'https://api.gbif.org/v1/occurrence/search?' + urllib.parse.urlencode(kw, safe=',')


doc = dict(queried=time.strftime('%Y-%m-%dT%H:%M'), source='GBIF occurrence search API, publishingOrg = California Academy of Sciences, '
           'country = EC, facet = stateProvince by decade of collecting year', decades={})
for name, y0, y1 in BINS:
    url = q(publishingOrg=ORG, country='EC', limit=0, facet='stateProvince', facetLimit=1000, year=f'{y0},{y1}')
    r = get(url)
    cs = {c['name']: c['count'] for c in r['facets'][0]['counts']} if r.get('facets') else {}
    doc['decades'][name] = dict(query=url, total=r['count'], states=cs)
    print(name, r['count'], len(cs), flush=True)
json.dump(doc, open(OUT, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
print('wrote', OUT)
