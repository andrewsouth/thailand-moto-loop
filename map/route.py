import json, subprocess, time
UA={'User-Agent':'trip-map-builder/1.0'}
P={'cm':(18.7883,98.9853),'maemalai':(19.0958,98.9361),'pai':(19.3581,98.4406),'soppong':(19.5160,98.2537),
 'thamlod':(19.5652,98.2790),'rakthai':(19.5861,97.9458),'pangung':(19.5116,97.9202),'mhs':(19.3015,97.9685),
 'khunyuam':(18.8285,97.9370),'maeukho':(18.8984,98.0894),'sariang':(18.1596,97.9301),'hot':(18.1935,98.6117),
 'chomthong':(18.4221,98.6773),'klangluang':(18.5374,98.5460),'summit':(18.5886,98.4870),
 'suthep':(18.8048,98.9216),'maerim':(18.9150,98.9440),'samoeng':(18.8478,98.7320),'hangdong':(18.6870,98.9190)}
SEG={'main':['cm','maemalai','pai','soppong','rakthai','pangung','mhs','khunyuam','sariang','hot','chomthong','klangluang','chomthong','cm'],
 'thamlod':['soppong','thamlod'],'maeukho':['khunyuam','maeukho'],'summit':['klangluang','summit'],
 'samoeng':['cm','maerim','samoeng','hangdong','cm'],'suthep':['cm','suthep']}
out={}
for k,seq in SEG.items():
    co=';'.join(f'{P[s][1]},{P[s][0]}' for s in seq)
    u=f'https://router.project-osrm.org/route/v1/driving/{co}?overview=full&geometries=geojson'
    d=json.loads(subprocess.run(['curl','-s','-A',UA['User-Agent'],u],capture_output=True,text=True,timeout=90).stdout)
    r=d['routes'][0]; out[k]={'coords':r['geometry']['coordinates'],'km':r['distance']/1000,
      'legs':[round(l['distance']/1000) for l in r['legs']]}
    print(k, round(r['distance']/1000), 'km', out[k]['legs'], len(r['geometry']['coordinates']),'pts'); time.sleep(1.2)
json.dump({'points':P,'routes':out},open('route.json','w'))
