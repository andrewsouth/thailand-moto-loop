"""Stitch the relief tiles into basemap.jpg and write map.svg (route, labels, border mask).

Run from this folder after route.py and tiles.py:  python3 build_map.py
"""
import json, math, glob
from PIL import Image, ImageEnhance

Z = 11
W, E, S, N = 97.60, 99.12, 18.03, 19.72
OUT_W = 1400


def tx(lon): return (lon + 180) / 360 * 2 ** Z * 256
def ty(lat):
    r = math.radians(lat)
    return (1 - math.log(math.tan(r) + 1 / math.cos(r)) / math.pi) / 2 * 2 ** Z * 256


X0, Y0 = tx(W), ty(N)
CW, CH = tx(E) - X0, ty(S) - Y0
K = OUT_W / CW
OUT_H = round(CH * K)


def P(lat, lon): return ((tx(lon) - X0) * K, (ty(lat) - Y0) * K)


# ---- basemap
tiles = glob.glob('tiles/*.jpg')
xs = sorted({int(t.split('_')[1]) for t in tiles}); ys = sorted({int(t.split('_')[2].split('.')[0]) for t in tiles})
big = Image.new('RGB', ((xs[-1] - xs[0] + 1) * 256, (ys[-1] - ys[0] + 1) * 256))
for t in tiles:
    _, x, y = t[:-4].split('_')
    big.paste(Image.open(t), ((int(x.split('/')[-1]) - xs[0]) * 256, (int(y) - ys[0]) * 256))
ox, oy = X0 - xs[0] * 256, Y0 - ys[0] * 256
im = big.crop((round(ox), round(oy), round(ox + CW), round(oy + CH))).resize((OUT_W, OUT_H), Image.LANCZOS)
im = ImageEnhance.Color(im).enhance(0.55)
im = ImageEnhance.Brightness(im).enhance(1.04)
im.save('basemap.jpg', quality=74, optimize=True, progressive=True)


# ---- helpers
def rdp(pts, eps):
    if len(pts) < 3: return pts
    keep = [False] * len(pts); keep[0] = keep[-1] = True; stack = [(0, len(pts) - 1)]
    while stack:
        a, b = stack.pop(); (x1, y1), (x2, y2) = pts[a], pts[b]; dx, dy = x2 - x1, y2 - y1; L = math.hypot(dx, dy)
        best, bi = 0, -1
        for i in range(a + 1, b):
            d = (abs(dy * (pts[i][0] - x1) - dx * (pts[i][1] - y1)) / L) if L > 1e-6 else math.hypot(pts[i][0] - x1, pts[i][1] - y1)
            if d > best: best, bi = d, i
        if best > eps: keep[bi] = True; stack += [(a, bi), (bi, b)]
    return [p for p, k in zip(pts, keep) if k]


def path(coords, eps=0.7):
    pts = rdp([P(lat, lon) for lon, lat in coords], eps)
    return 'M' + ' L'.join(f'{x:.1f},{y:.1f}' for x, y in pts)


def hav(a, b):
    (lo1, la1), (lo2, la2) = a, b
    p = math.pi / 180
    h = math.sin((la2 - la1) * p / 2) ** 2 + math.cos(la1 * p) * math.cos(la2 * p) * math.sin((lo2 - lo1) * p / 2) ** 2
    return 12742 * math.asin(math.sqrt(h))


R = json.load(open('route.json'))
pts = R['points']; routes = R['routes']
main = routes['main']['coords']

# Ob Luang gorge: about 17 km west of Hot along Route 108
hot = pts['hot']; hi = min(range(len(main)), key=lambda i: hav(main[i], (hot[1], hot[0])))
acc, i = 0, hi
while i > 0 and acc < 17: acc += hav(main[i], main[i - 1]); i -= 1
obluang = (main[i][1], main[i][0])


def arrow(frac):
    # chevron pointing along the main route at a fraction of its length
    n = len(main); j = int(n * frac)
    (x1, y1), (x2, y2) = P(main[j][1], main[j][0]), P(main[j + 25][1], main[j + 25][0])
    ang = math.degrees(math.atan2(y2 - y1, x2 - x1))
    return f'<path d="M-7,-6 L3,0 L-7,6" transform="translate({x1:.1f} {y1:.1f}) rotate({ang:.0f})" fill="none" stroke="#fff" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/>' \
           f'<path d="M-7,-6 L3,0 L-7,6" transform="translate({x1:.1f} {y1:.1f}) rotate({ang:.0f})" fill="none" stroke="#8e2f22" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>'


# Thailand mask (lighten the Myanmar side)
th = json.load(open('thailand.json'))[0]['geojson']['coordinates'][0]
clip = [(lon, lat) for lon, lat in th if W - 1 < lon < E + 1 and S - 1 < lat < N + 1]
mask = f'M0,0 H{OUT_W} V{OUT_H} H0 Z ' + path(th, 0.5) + ' Z'

# labels: (name, lat, lon, dx, dy, anchor, kind, day)
L = [
    ('Chiang Mai', *pts['cm'], -34, 62, 'end', 'city', 'Days 1–2, 7'),
    ('Pai', *pts['pai'], 12, 5, 'start', 'town', 'Day 3'),
    ('Soppong', *pts['soppong'], 12, 16, 'start', 'town', None),
    ('Mae Hong Son', *pts['mhs'], 14, 5, 'start', 'town', 'Day 4'),
    ('Khun Yuam', *pts['khunyuam'], 14, 5, 'start', 'town', 'Day 5'),
    ('Mae Sariang', *pts['sariang'], 16, -38, 'start', 'town', None),
    ('Mae Klang Luang', *pts['klangluang'], 14, 18, 'start', 'town', 'Day 6'),
    ('Tham Lod Cave', *pts['thamlod'], 10, -6, 'start', 'poi', None),
    ('Ban Rak Thai', *pts['rakthai'], 10, -8, 'start', 'poi', None),
    ('Pang Ung', *pts['pangung'], 10, 4, 'start', 'poi', None),
    ('Doi Mae U-Kho', *pts['maeukho'], 10, 4, 'start', 'poi', None),
    ('Ob Luang Gorge', *obluang, 0, 50, 'middle', 'poi', None),
    ('Doi Inthanon', *pts['summit'], -10, -6, 'end', 'poi', '2,565 m'),
    ('Huai Nam Dang', 19.3083, 98.6008, 10, 4, 'start', 'poi', None),
    ('Doi Suthep', *pts['suthep'], -10, -6, 'end', 'poi', None),
    ('Samoeng', *pts['samoeng'], -10, 4, 'end', 'poi', None),
    ('Mae Malai', *pts['maemalai'], 10, 4, 'start', 'minor', None),
    ('Chom Thong', *pts['chomthong'], 10, 4, 'start', 'minor', None),
    ('Hot', *pts['hot'], 10, 4, 'start', 'minor', None),
]

o = [f'<svg viewBox="0 0 {OUT_W} {OUT_H}" xmlns="http://www.w3.org/2000/svg" font-family="Arial,Helvetica,sans-serif">',
     f'<image href="{{{{basemap}}}}" x="0" y="0" width="{OUT_W}" height="{OUT_H}"/>',
     f'<path d="{mask}" fill="#f4f3ef" fill-opacity=".62" fill-rule="evenodd"/>',
     f'<path d="{path(th, 0.5)}" fill="none" stroke="#7a7368" stroke-width="3" stroke-dasharray="12 8" stroke-linecap="round"/>',
     '<text x="58" y="1180" font-size="26" letter-spacing="14" fill="#6d6a63" transform="rotate(-90 58 1180)">MYANMAR</text>',
     '<text x="1130" y="1600" font-size="26" letter-spacing="14" fill="#6d6a63" opacity=".8">THAILAND</text>']
# side trips
for k in ('samoeng', 'suthep', 'thamlod', 'maeukho', 'summit'):
    d = path(routes[k]['coords'])
    o.append(f'<path d="{d}" fill="none" stroke="#fff" stroke-width="7" stroke-linecap="round" stroke-linejoin="round" opacity=".8"/>')
    o.append(f'<path d="{d}" fill="none" stroke="#a5803c" stroke-width="3.4" stroke-dasharray="7 6" stroke-linecap="round" stroke-linejoin="round"/>')
d = path(main)
o.append(f'<path d="{d}" fill="none" stroke="#fff" stroke-width="10" stroke-linecap="round" stroke-linejoin="round" opacity=".85"/>')
o.append(f'<path d="{d}" fill="none" stroke="#9b3b2e" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>')
o += [arrow(f) for f in (0.08, 0.27, 0.47, 0.66)]
# markers and labels
NUM = {'Chiang Mai': 1, 'Doi Suthep': 2, 'Huai Nam Dang': 3, 'Pai': 4, 'Tham Lod Cave': 5, 'Ban Rak Thai': 6, 'Mae Hong Son': 7,
       'Doi Mae U-Kho': 8, 'Ob Luang Gorge': 9, 'Mae Klang Luang': 10, 'Doi Inthanon': 11}
badges = []
for name, lat, lon, dx, dy, anc, kind, day in L:
    x, y = P(lat, lon)
    if kind == 'city':
        o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="13" fill="#18263a" stroke="#fff" stroke-width="3"/><circle cx="{x:.1f}" cy="{y:.1f}" r="5" fill="#fff"/>')
    elif kind == 'town':
        o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="9" fill="#fff" stroke="#18263a" stroke-width="3.5"/>')
    elif kind == 'poi':
        o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="6" fill="#a5803c" stroke="#fff" stroke-width="2.2"/>')
    else:
        o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="#59606a" stroke="#fff" stroke-width="1.6"/>')
    size = {'city': 38, 'town': 31, 'poi': 23, 'minor': 20}[kind]
    font = 'Georgia,serif' if kind in ('city', 'town') else 'Arial,Helvetica,sans-serif'
    fill = {'city': '#18263a', 'town': '#18263a', 'poi': '#2b2f35', 'minor': '#4a4f57'}[kind]
    if name in NUM:
        r = 24 if kind == 'city' else 19
        badges.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="#18263a" stroke="#fff" stroke-width="3.5"/>'
                      f'<text x="{x:.1f}" y="{y + 8:.1f}" text-anchor="middle" font-family="Georgia,serif" font-size="{24 if r < 24 else 26}" fill="#fff">{NUM[name]}</text>')
        if kind != 'city':
            if dx > 0: dx += 12
            elif dx < 0: dx -= 12
    tx_, ty_ = x + dx, y + dy
    halo = 'paint-order="stroke" stroke="#f7f6f2" stroke-width="7" stroke-linejoin="round"'
    o.append(f'<text x="{tx_:.1f}" y="{ty_:.1f}" text-anchor="{anc}" font-family="{font}" font-size="{size}" fill="{fill}" {halo}>{name}</text>')
    if day:
        o.append(f'<text x="{tx_:.1f}" y="{ty_ + size * 0.95:.1f}" text-anchor="{anc}" font-family="Georgia,serif" font-style="italic" font-size="{round(size * 0.72)}" fill="#8a6a2e" {halo}>{day}</text>')
o += badges
# compass, scale, credit
km50 = P(18.1, 98.6)[0] - P(18.1, 98.6 + 50 / (111.32 * math.cos(math.radians(18.1))))[0]
km50 = abs(km50)
sx, sy = OUT_W - 60 - km50, OUT_H - 70
o.append(f'<g transform="translate({OUT_W - 70} 90)" fill="#18263a"><path d="M0,-34 L13,12 L0,3 L-13,12 Z"/><text y="44" text-anchor="middle" font-size="24" font-family="Georgia,serif">N</text></g>')
o.append(f'<g font-size="20" fill="#2b2f35"><rect x="{sx - 16:.0f}" y="{sy - 44}" width="{km50 + 32:.0f}" height="66" rx="6" fill="#f7f6f2" fill-opacity=".85"/>'
         f'<line x1="{sx:.1f}" y1="{sy}" x2="{sx + km50:.1f}" y2="{sy}" stroke="#2b2f35" stroke-width="3"/>'
         f'<line x1="{sx:.1f}" y1="{sy - 8}" x2="{sx:.1f}" y2="{sy + 8}" stroke="#2b2f35" stroke-width="3"/><line x1="{sx + km50 / 2:.1f}" y1="{sy - 6}" x2="{sx + km50 / 2:.1f}" y2="{sy + 6}" stroke="#2b2f35" stroke-width="2"/><line x1="{sx + km50:.1f}" y1="{sy - 8}" x2="{sx + km50:.1f}" y2="{sy + 8}" stroke="#2b2f35" stroke-width="3"/>'
         f'<text x="{sx:.1f}" y="{sy - 16}">0</text><text x="{sx + km50 / 2:.1f}" y="{sy - 16}" text-anchor="middle">25</text><text x="{sx + km50:.1f}" y="{sy - 16}" text-anchor="end">50 km</text></g>')
o.append(f'<text x="14" y="{OUT_H - 14}" font-size="15" fill="#4a4f57" {halo if False else ""}>Relief: Esri, USGS · Roads and border: © OpenStreetMap contributors</text>')
o.append('</svg>')
open('map.svg', 'w').write('\n'.join(o))
print('basemap', OUT_W, OUT_H, 'map.svg', len('\n'.join(o)) // 1024, 'KB', 'obluang', obluang)
