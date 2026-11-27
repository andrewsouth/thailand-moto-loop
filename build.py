"""Build the website: src/*.html -> index.html, plan.html, links.html (in the repo root).

GitHub Pages serves the repo root, so the built pages sit next to images/ and map/.
Run from this folder after any edit to src/:   python3 build.py
(If the route or map labels change, first run:  cd map && python3 build_map.py)

Placeholders in src/ pages:
  {{nav}}          the shared top bar
  {{photo:name}}   images/name.jpg
  {{map}}          the relief map (map/map.svg, with map/basemap.jpg behind it)
  {{credits}}      the photo credits line (from images/credits.json)
"""
import html
import json
import pathlib
import re

here = pathlib.Path(__file__).parent
SITE = "https://andrewsouth.github.io/thailand-moto-loop/"
DESC = "An 8-day adventure motorcycle tour of the Mae Hong Son Loop from Chiang Mai, Northern Thailand."

# Pages in nav order: (source file, nav label). Add a page here to put it in the top bar.
PAGES = [("index.html", "Tour"), ("plan.html", "Plan and budget"), ("links.html", "Maps and links")]

NAV_CSS = """
.sitenav{background:#18263a;color:#f2f1ec;font-family:Arial,Helvetica,sans-serif;font-size:.86rem;position:sticky;top:0;z-index:10}
.sitenav .in{max-width:820px;margin:0 auto;display:flex;align-items:center;gap:4px 18px;flex-wrap:wrap;padding:9px max(16px,env(safe-area-inset-right,0px)) 9px max(16px,env(safe-area-inset-left,0px))}
.sitenav .brand{font-family:Georgia,"Times New Roman",serif;font-size:1rem;color:#f2f1ec;text-decoration:none;margin-right:auto}
.sitenav a.pg{color:#b9c0c8;text-decoration:none;padding:3px 0;border-bottom:2px solid transparent}
.sitenav a.pg:hover{color:#f2f1ec}
.sitenav a.pg[aria-current]{color:#f2f1ec;border-bottom-color:#d6b06a}
body{margin:0}
@media print{.sitenav{display:none}}
"""

LABEL = {"cover1": "Doi Mae U-Kho (cover)", "cover2": "Pang Ung (banner)", "chiangmai": "Wat Chedi Luang",
         "doisuthep": "Doi Suthep", "huainamdang": "Huai Nam Dang", "pai": "Pai Canyon", "thamlod": "Tham Lod",
         "banrakthai": "Ban Rak Thai", "maehongson": "Wat Jong Kham", "khunyuam": "Doi Mae U-Kho",
         "obluang": "Ob Luang", "terraces": "Mae Klang Luang", "inthanon": "Doi Inthanon"}
credits = {c["name"]: c for c in json.loads((here / "images" / "credits.json").read_text())}
svg = (here / "map" / "map.svg").read_text().replace("{{basemap}}", "map/basemap.jpg")


def nav(current):
    links = "".join(
        f'<a class="pg" href="{f}"{" aria-current=page" if f == current else ""}>{label}</a>' for f, label in PAGES)
    return f'<nav class="sitenav" aria-label="Site"><div class="in"><a class="brand" href="index.html">Ride Northern Thailand</a>{links}</div></nav>'


for name, _ in PAGES:
    src = (here / "src" / name).read_text()
    used = []

    def photo(m):
        used.append(m.group(1))
        assert (here / "images" / f"{m.group(1)}.jpg").exists(), m.group(1)
        return f"images/{m.group(1)}.jpg"

    src = re.sub(r"\{\{photo:(\w+)\}\}", photo, src)
    src = src.replace("{{map}}", svg).replace("{{nav}}", nav(name))
    if "{{credits}}" in src:
        parts = [f'{LABEL.get(n, n)}: <a href="{html.escape(credits[n]["page"])}">{html.escape(credits[n]["artist"])}</a>, '
                 f'{html.escape(credits[n]["license"])}' for n in dict.fromkeys(used)]
        src = src.replace("{{credits}}", "Photos from Wikimedia Commons. " + "; ".join(parts) +
                          ". Map: relief by Esri and USGS; roads and border © OpenStreetMap contributors.")
    left = re.findall(r"\{\{[^}]*\}\}", src)
    assert not left, f"{name}: unfilled {left}"

    # split the source into head (charset, title, style) and body, then wrap as a full page
    cut = src.index("</style>") + len("</style>")
    head, body = src[:cut], src[cut:]
    head = head.replace('<meta charset="utf-8">', "").replace("</style>", NAV_CSS + "</style>")
    title = re.search(r"<title>(.*?)</title>", head).group(1)
    url = SITE + ("" if name == "index.html" else name)
    page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="description" content="{DESC}">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{DESC}">
<meta property="og:image" content="{SITE}images/cover1.jpg">
<meta property="og:url" content="{url}">
<meta property="og:type" content="website">
<meta name="twitter:card" content="summary_large_image">
{head.strip()}
</head>
<body>
{body.strip()}
</body>
</html>
"""
    (here / name).write_text(page)
    print(f"{name}: {len(page) // 1024} KB, photos: {len(set(used))}")
