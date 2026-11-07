import json,glob,numpy as np,laspy,sys
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.colors import LightSource
X0,X1,Y0,Y1=-13633150,-13632550,4546750,4547200
xs=[];ys=[];zs=[];cs=[];rs=[]
for fn in glob.glob('data/*.laz'):
    try: f=laspy.read(fn)
    except Exception as e: print('bad',fn,e); continue
    x=f.x; y=f.y; z=f.z; c=f.classification; r=f.return_number
    m=(x>=X0)&(x<=X1)&(y>=Y0)&(y<=Y1)&(c!=7)&(c!=18)
    xs.append(x[m]);ys.append(y[m]);zs.append(z[m]);cs.append(c[m]);rs.append(r[m])
x=np.concatenate(xs);y=np.concatenate(ys);z=np.concatenate(zs);c=np.concatenate(cs);r=np.concatenate(rs)
print('points',len(x), 'z range',z.min(),z.max())
# web mercator scale factor at lat 37.77 -> metres: cos(lat)
k=np.cos(np.radians(37.7699))
np.savez_compressed('cas_pts.npz',x=x,y=y,z=z,c=c,r=r)
res=0.5/k  # 0.5 m ground in mercator units
nx=int((X1-X0)/res)+1; ny=int((Y1-Y0)/res)+1
ix=((x-X0)/res).astype(int); iy=((Y1-y)/res).astype(int)
dsm=np.full((ny,nx),np.nan)
np.maximum.at(dsm, (iy,ix), z) if False else None
flat=iy*nx+ix
order=np.argsort(z)
dsm_flat=np.full(ny*nx,np.nan); dsm_flat[flat[order]]=z[order]  # last write = max z
dsm=dsm_flat.reshape(ny,nx)
# fill small holes
from scipy import ndimage
mask=np.isnan(dsm)
if mask.any():
    idx=ndimage.distance_transform_edt(mask,return_distances=False,return_indices=True)
    dsm=dsm[tuple(idx)]
np.save('dsm.npy',dsm)
ls=LightSource(azdeg=315,altdeg=45)
fig=plt.figure(figsize=(12,9),dpi=160); ax=fig.add_axes([0,0,1,1]); ax.axis('off')
rgb=ls.shade(dsm,cmap=plt.cm.terrain,blend_mode='soft',vert_exag=1.5,dx=0.5,dy=0.5,vmin=np.nanpercentile(dsm,1),vmax=np.nanpercentile(dsm,99.5))
ax.imshow(rgb)
fig.savefig('cas_lidar_dsm_hillshade.png'); plt.close()
# pure hillshade grayscale
fig=plt.figure(figsize=(12,9),dpi=160); ax=fig.add_axes([0,0,1,1]); ax.axis('off')
ax.imshow(ls.hillshade(dsm,vert_exag=2,dx=0.5,dy=0.5),cmap='gray')
fig.savefig('cas_lidar_hillshade_gray.png'); plt.close()
print('ok',dsm.shape)
