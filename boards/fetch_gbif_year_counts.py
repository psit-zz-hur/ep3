"""Records per collecting year for the Academy's 12 GBIF datasets, the building slice and the Galapagos 1905-06 slice.
GBIF occurrence search, facet=year, limit=0 (counts only, no records), no key. Writes CALACADEMY_GBIF_YEAR_COUNTS_2026_11_07A.json beside this script.
python -I -B fetch_gbif_year_counts.py"""
import json, os, datetime, urllib.request as u, urllib.parse as p

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'CALACADEMY_GBIF_YEAR_COUNTS_2026_11_07A.json')
API = 'https://api.gbif.org/v1/occurrence/search?'
ORG = '66522820-055c-11d8-b84e-b8a03c50a862'
DATASETS = {   # 15b D1-D12
    'BOT': 'f934f8e2-32ca-46a7-b2f8-b032a4740454', 'ANTWEB': '13b70480-bd69-11dd-b15f-b8a03c50a862',
    'ENT': '14f3151a-e95d-493c-a40d-d9938ef62954', 'HERP': 'cece4fc2-1fec-4bb5-a335-7252548e3f0b',
    'IZ': '44bcde48-ac71-46f2-bf73-24fc3c008b6c', 'ICH': '5d6c10bd-ea31-4363-8b79-58c96d859f5b',
    'ORN': '4f29b6ab-20c0-4479-8795-4915bedcebd1', 'MAM': '6ce7290f-47f6-4046-8356-371f5b6749df',
    'TYPE': '6ec3c7f5-6233-48f6-b36a-06b867edbadd', 'GEO': '5e848873-567f-42dd-8a29-88056b9b33a4',
    'EGG': 'd3bc4c7d-325c-49ea-aa71-d915b2ee3204', 'MICRO': '3807f67c-a065-43eb-bc1b-e2176c09c03f',
}
BUILDING = 'POLYGON((-122.4678 37.7684,-122.4644 37.7684,-122.4644 37.7709,-122.4678 37.7709,-122.4678 37.7684))'


def q(params):
    params = dict(params, limit=0, facet='year', facetLimit=1000)
    url = API + p.urlencode(params)
    req = u.Request(url, headers={'User-Agent': 'calacademy-diagram-mockup/1.0'})
    d = json.load(u.urlopen(req, timeout=60))
    years = {int(c['name']): c['count'] for c in d['facets'][0]['counts']} if d.get('facets') else {}
    return {'query': url, 'total': d['count'], 'with_year': sum(years.values()), 'years': dict(sorted(years.items()))}


out = {'queried': datetime.datetime.now().isoformat(timespec='minutes'), 'source': 'GBIF occurrence search API, facet=year', 'datasets': {}}
for k, key in DATASETS.items():
    out['datasets'][k] = dict(q({'datasetKey': key}), datasetKey=key)
    r = out['datasets'][k]
    print(k, r['total'], r['with_year'], min(r['years'] or [0]), max(r['years'] or [0]))
out['building'] = q({'publishingOrg': ORG, 'geometry': BUILDING})
out['building_birds'] = q({'publishingOrg': ORG, 'geometry': BUILDING, 'datasetKey': DATASETS['ORN']})
out['galapagos_1905_06'] = q({'publishingOrg': ORG, 'country': 'EC', 'eventDate': '1905-01-01,1906-12-31'})
for k in ('building', 'building_birds', 'galapagos_1905_06'):
    print(k, out[k]['total'], out[k]['years'] if len(out[k]['years']) < 30 else '...')
json.dump(out, open(OUT, 'w', encoding='utf-8'), indent=1)
print(OUT)
