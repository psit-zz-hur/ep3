"""Download all EPT nodes (all depths) intersecting the park bbox. Skips cached. 10 threads."""
import sys, json, time, pathlib, concurrent.futures as cf
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import territory_rasters as T
h = json.load(open(T.D / 'lidar2023' / 'park_hier.json'))
keys = [k for k in h if not ((T.N / f'{k}.laz').exists() and (T.N / f'{k}.laz').stat().st_size > 0)]
print('to download', len(keys), flush=True); t0 = time.time(); done = 0; bad = []
def dl(k):
    for i in range(5):
        try:
            r = T._get(f'{T.BASE}/ept-data/{k}.laz', 300)
            if r.status_code == 200:
                tmp = T.N / f'{k}.part'; tmp.write_bytes(r.content); tmp.replace(T.N / f'{k}.laz'); return k, len(r.content)
            return k, r.status_code
        except Exception as e: time.sleep(3)
    return k, 'fail'
with cf.ThreadPoolExecutor(10) as ex:
    for k, r in ex.map(dl, keys):
        done += 1
        if not isinstance(r, int) or r < 100: bad.append((k, r))
        if done % 500 == 0: print(done, len(keys), round(time.time() - t0), 's', flush=True)
print('DONE', done, 'bad', bad, round(time.time() - t0), 's', flush=True)
