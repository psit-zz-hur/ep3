"""Where the Academy's specimens came from: GBIF record counts per country, per decade of collecting year (publisher = the Academy).
GBIF occurrence search, facet=country, limit=0 (counts only), no key. Writes CALACADEMY_GBIF_COUNTRY_DECADES_2026_11_07A.json beside this script.
python -I -B fetch_gbif_country_decades.py"""
import json, os, datetime, urllib.request as u, urllib.parse as p

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'CALACADEMY_GBIF_COUNTRY_DECADES_2026_11_07A.json')
ORG = '66522820-055c-11d8-b84e-b8a03c50a862'


def q(params):
    params = dict(params, publishingOrg=ORG, limit=0, facet='country', facetLimit=400)
    url = 'https://api.gbif.org/v1/occurrence/search?' + p.urlencode(params)
    d = json.load(u.urlopen(u.Request(url, headers={'User-Agent': 'calacademy-diagram/1.0'}), timeout=90))
    return {'query': url, 'total': d['count'], 'countries': {c['name']: c['count'] for c in d['facets'][0]['counts']} if d.get('facets') else {}}


bins = [('before 1850', '1500,1849')] + [(str(d), '%d,%d' % (d, d + 9)) for d in range(1850, 2030, 10)]
out = {'queried': datetime.datetime.now().isoformat(timespec='minutes'), 'source': 'GBIF occurrence search API, publishingOrg = California Academy of Sciences, facet=country by decade of collecting year', 'decades': {}}
for name, yr in bins:
    out['decades'][name] = q({'year': yr})
    print(name, out['decades'][name]['total'], len(out['decades'][name]['countries']))
out['all_years'] = q({})
print('all', out['all_years']['total'], len(out['all_years']['countries']))
json.dump(out, open(OUT, 'w', encoding='utf-8'), indent=1)
print(OUT)
