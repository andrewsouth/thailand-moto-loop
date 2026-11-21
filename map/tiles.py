import math, subprocess, os
Z=11; W,E,S,N=97.60,99.12,18.03,19.72
def tx(lon): return (lon+180)/360*2**Z
def ty(lat): r=math.radians(lat); return (1-math.log(math.tan(r)+1/math.cos(r))/math.pi)/2*2**Z
x0,x1=int(tx(W)),int(tx(E)); y0,y1=int(ty(N)),int(ty(S))
os.makedirs('tiles',exist_ok=True); n=0
for x in range(x0,x1+1):
  for y in range(y0,y1+1):
    f=f'tiles/{Z}_{x}_{y}.jpg'
    if not os.path.exists(f):
      subprocess.run(['curl','-s','-f','-A','trip-map-builder/1.0','-o',f,f'https://server.arcgisonline.com/ArcGIS/rest/services/World_Shaded_Relief/MapServer/tile/{Z}/{y}/{x}'],check=True); n+=1
print('tiles x',x0,x1,'y',y0,y1,'downloaded',n)
