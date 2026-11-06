import json, urllib.request, urllib.parse, time, re, os, sys
sys.stdout.reconfigure(encoding='utf-8')
H={"User-Agent":"FinalPresentation/1.0 (educational use)"}
T={
 "sunset":"File:Sunset at Ternate and Tidore Islands, Maluku.jpg",
 "tidore":"File:Tidore Island Indonesia Daytime.jpg",
 "halmahera":"File:Halmahera Island.jpg",
 "weda":"File:Weda Bay Nickel site.jpg",
 "rempah":"File:Spices, Pulau Tidore (Tidore Island), The Moluccas (15013115810).jpg",
 "obi":"File:Bakau di Pulau Obi Mayor.jpg",
 "morotai":"File:A beach on dodola island.jpg",
 "kapal":"File:KM Sinabung Pelni Ferry Bitung Sulawesi Utara.jpg",
 "cengkih":"File:Drying cengkih.jpg",
 "sanana":"File:Sanana - panoramio.jpg",
 "ternate":"File:Ternate, Maluku Islands, Indonesia 2.jpg",
}
def get(u,tries=5):
    for i in range(tries):
        try: return urllib.request.urlopen(urllib.request.Request(u,headers=H),timeout=60).read()
        except Exception as e:
            print("retry",e); time.sleep(5*(i+1))
    return None
titles="|".join(T.values())
u="https://commons.wikimedia.org/w/api.php?"+urllib.parse.urlencode(dict(action="query",format="json",titles=titles,prop="imageinfo",iiprop="url|extmetadata",iiurlwidth=1600))
r=json.loads(get(u))
os.makedirs("assets/photos",exist_ok=True)
credits={}
by={p["title"]:p for p in r["query"]["pages"].values()}
for k,t in T.items():
    p=by.get(t) or by.get(t.replace("_"," "))
    if not p or "imageinfo" not in p: print("missing",k); continue
    ii=p["imageinfo"][0];m=ii["extmetadata"]
    src=ii.get("thumburl") or ii["url"]
    time.sleep(3)
    b=get(src)
    if not b: print("fail",k); continue
    open(f"assets/photos/{k}.jpg","wb").write(b)
    art=re.sub("<[^>]+>","",m.get("Artist",{}).get("value","")).strip()
    credits[k]={"title":t[5:],"author":art[:80],"license":m.get("LicenseShortName",{}).get("value"),"page":ii["descriptionurl"]}
    print("ok",k,len(b),credits[k]["license"],art[:40])
json.dump(credits,open("assets/photos/credits.json","w",encoding="utf-8"),ensure_ascii=False,indent=1)
