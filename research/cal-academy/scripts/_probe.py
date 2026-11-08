import sys,collections,pathlib
sys.path.insert(0,'research/cal-academy/scripts')
import territory_rasters as T
from pyproj import Transformer
import json
tr=Transformer.from_crs('EPSG:4326','EPSG:3857',always_xy=True)
x0,y0=tr.transform(-122.5120,37.7635);x1,y1=tr.transform(-122.4520,37.7750)
h=T.ept_nodes(x0-20,x1+20,y0-20,y1+20)
json.dump(h,open('data/cal-academy/lidar2023/park_hier.json','w'))
c=collections.Counter();p=collections.Counter()
for k,v in h.items():
    d=int(k.split('-')[0]);c[d]+=1;p[d]+=v
cached={f.stem for f in T.N.glob('*.laz') if f.stat().st_size>0}
print(sorted(c.items()));print(sorted(p.items()),sum(p.values()))
print('cached in park',sum(1 for k in h if k in cached),'of',len(h))
print('bytes cached',sum((T.N/f'{k}.laz').stat().st_size for k in h if k in cached)/1e6)
