import json,os,sys,subprocess,concurrent.futures as cf
base='https://s3-us-west-2.amazonaws.com/usgs-lidar-public/CA_SanFrancisco_1_B23'
ept=json.load(open('ept.json')); b=ept['bounds']; size=b[3]-b[0]
# target bbox (EPSG:3857): Academy + concourse edge
X0,X1,Y0,Y1=-13633150,-13632550,4546750,4547200
def node_bounds(key):
    d,x,y,z=map(int,key.split('-')); s=size/2**d
    return (b[0]+x*s,b[0]+(x+1)*s,b[1]+y*s,b[1]+(y+1)*s)
def inter(key):
    x0,x1,y0,y1=node_bounds(key); return not (x1<X0 or x0>X1 or y1<Y0 or y0>Y1)
hier={}
def load_h(key):
    fn=f'h_{key}.json'
    if not os.path.exists(fn):
        subprocess.run(['curl','-sS','--max-time','60','-o',fn,f'{base}/ept-hierarchy/{key}.json'],check=True)
    return json.load(open(fn))
def walk(hkey):
    h=load_h(hkey)
    for k,v in h.items():
        if not inter(k): continue
        if v==-1: walk(k)
        elif v>0: hier[k]=v
walk('0-0-0-0')
print('nodes',len(hier),'pts',sum(hier.values()))
json.dump(hier,open('nodes.json','w'))
os.makedirs('data',exist_ok=True)
def dl(k):
    fn=f'data/{k}.laz'
    if os.path.exists(fn) and os.path.getsize(fn)>0: return k,'cached'
    r=subprocess.run(['curl','-sS','--max-time','300','-o',fn,f'{base}/ept-data/{k}.laz'])
    return k,r.returncode
with cf.ThreadPoolExecutor(12) as ex:
    res=list(ex.map(dl,hier.keys()))
bad=[k for k,r in res if r not in ('cached',0)]
print('downloaded',len(res)-len(bad),'failed',len(bad))
