import json, math, os, shutil, zipfile

topo = json.load(open("geo_indonesia.json", encoding="utf-8"))
sx, sy = topo["transform"]["scale"]
tx, ty = topo["transform"]["translate"]

arcs = []
for a in topo["arcs"]:
    x = y = 0
    pts = []
    for dx, dy in a:
        x += dx; y += dy
        pts.append((x * sx + tx, y * sy + ty))
    arcs.append(pts)

def arc_pts(i):
    return arcs[i] if i >= 0 else arcs[~i][::-1]

def ring(idx):
    out = []
    for i in idx:
        p = arc_pts(i)
        out.extend(p if not out else p[1:])
    return out

feats = []
for g in topo["objects"]["kab"]["geometries"]:
    pr = g["properties"]
    if pr["p"] != "8200":
        continue
    polys = g["arcs"] if g["type"] == "MultiPolygon" else [g["arcs"]]
    rings = [[ring(r) for r in poly] for poly in polys]
    feats.append((pr["k"], pr["name"].title().replace("Kota ", "Kota "), rings))

lon0 = min(p[0] for f in feats for poly in f[2] for r in poly for p in r)
lon1 = max(p[0] for f in feats for poly in f[2] for r in poly for p in r)
lat0 = min(p[1] for f in feats for poly in f[2] for r in poly for p in r)
lat1 = max(p[1] for f in feats for poly in f[2] for r in poly for p in r)
latc = (lat0 + lat1) / 2
K = 100.0
def proj(lon, lat):
    return ((lon - lon0) * math.cos(math.radians(latc)) * K, (lat1 - lat) * K)

def simplify(pts, tol=0.0025):
    out = [pts[0]]
    for p in pts[1:]:
        if abs(p[0] - out[-1][0]) + abs(p[1] - out[-1][1]) >= tol:
            out.append(p)
    return out

res = {}
for k, name, rings in feats:
    d = ""
    for poly in rings:
        for r in poly:
            r = simplify(r)
            if len(r) < 4:
                continue
            q = [proj(*p) for p in r]
            d += "M" + "L".join(f"{a:.1f},{b:.1f}" for a, b in q) + "Z"
    res[k] = {"name": name, "d": d}

w, h = proj(lon1, lat0)
data = {
    "w": round(w, 1), "h": round(h, 1), "regions": res,
    "pts": {
        "weda": proj(127.97, 0.33),
        "obi": proj(127.65, -1.55),
        "ternate": proj(127.37, 0.79),
        "tobelo": proj(127.99, 1.73),
        "sanana": proj(125.97, -2.06),
        "labuha": proj(127.50, -0.63),
    },
}
os.makedirs("assets", exist_ok=True)
with open("assets/malut-map.js", "w", encoding="utf-8") as f:
    f.write("window.MALUT_MAP=" + json.dumps(data) + ";")
print(len(feats), "regions", data["w"], data["h"], os.path.getsize("assets/malut-map.js"), "bytes")

with zipfile.ZipFile("Kel 4 (1).pptx") as z:
    for src, dst in [("image2", "bappenas"), ("image5", "cover"), ("image4", "emas2045"), ("image3", "berakhlak")]:
        open(f"assets/{dst}.png", "wb").write(z.read(f"ppt/media/{src}.png"))
