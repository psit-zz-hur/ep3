import numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.colors import LightSource
from scipy import ndimage
dsm=np.load('dsm.npy'); k=np.cos(np.radians(37.7699)); res=0.5
# building: large flat-ish elevated region. Use slope: roof deck has low slope; trees high slope. Height band 90-120, low local std.
sm=ndimage.gaussian_filter(dsm,1.5)
gy,gx=np.gradient(sm,res); slope=np.hypot(gx,gy)
cand=(sm>88)&(slope<1.2)
cand=ndimage.binary_opening(cand,iterations=3)
lab,n=ndimage.label(cand); sizes=ndimage.sum(cand,lab,range(1,n+1)); big=lab==(np.argmax(sizes)+1)
big=ndimage.binary_closing(ndimage.binary_dilation(big,iterations=12),iterations=12)
big=ndimage.binary_fill_holes(big)
ys,xs=np.where(big); cy,cx=ys.mean(),xs.mean()
# principal axis angle
cov=np.cov(np.vstack([xs-cx,ys-cy])); w,v=np.linalg.eigh(cov); ang=np.degrees(np.arctan2(v[1,1],v[0,1]))
print('centre',cx,cy,'angle',ang,'area m2',big.sum()*res*res)
half=150  # px = 75 m
pad=int(half*1.6)
y0,y1,x0,x1=int(cy-pad),int(cy+pad),int(cx-pad),int(cx+pad)
crop=dsm[max(y0,0):y1,max(x0,0):x1]
rot=ndimage.rotate(crop,ang,reshape=False,order=1,mode='nearest')
c=np.array(rot.shape)//2
roof=rot[c[0]-170:c[0]+170,c[1]-170:c[1]+170]
np.save('roof_rot.npy',roof)
ls=LightSource(azdeg=315,altdeg=45)
fig=plt.figure(figsize=(12,12),dpi=150); ax=fig.add_axes([0,0,1,1]); ax.axis('off')
rgb=ls.shade(roof,cmap=plt.cm.cividis,blend_mode='soft',vert_exag=2,dx=0.5,dy=0.5,vmin=np.nanpercentile(roof,2),vmax=np.nanpercentile(roof,99.5))
ax.imshow(rgb); fig.savefig('cas_roof_closeup.png'); plt.close()
# contour map of roof heights
fig=plt.figure(figsize=(12,12),dpi=150); ax=fig.add_axes([0,0,1,1]); ax.axis('off')
ax.imshow(ls.hillshade(roof,vert_exag=2,dx=0.5,dy=0.5),cmap='gray')
cs=ax.contour(roof,levels=np.arange(80,125,1),colors='#ff6a00',linewidths=0.4)
ax.contour(roof,levels=np.arange(80,125,5),colors='#ffffff',linewidths=0.9)
fig.savefig('cas_roof_contours_1m.png'); plt.close()
# profile along rotated x axis through dome peaks
smr=ndimage.gaussian_filter(np.nan_to_num(roof,nan=0),2)
pk=(smr==ndimage.maximum_filter(smr,size=80))&(smr>100)
py,px=np.where(pk); o=np.argsort(-smr[py,px]); py,px=py[o][:3],px[o][:3]
print('peaks',list(zip(px,py,smr[py,px])))
fig,axs=plt.subplots(2,1,figsize=(16,8),dpi=150)
for ax,row in zip(axs,py[:2]):
    prof=roof[row,:]; xs_=np.arange(len(prof))*res
    ax.fill_between(xs_,np.nanmin(roof)-1,prof,color='#1f1f1f'); ax.plot(xs_,prof,color='#ff7f0e',lw=1)
    ax.set_aspect('equal'); ax.set_ylabel('m NAVD88')
axs[1].set_xlabel('m along building long axis')
fig.tight_layout(); fig.savefig('cas_dome_profile.png'); plt.close()
print('roof z',np.nanmin(roof),np.nanmax(roof))
