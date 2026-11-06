import json, urllib.request, urllib.parse, sys
sys.stdout.reconfigure(encoding='utf-8')
H={"User-Agent":"FinalPresentation/1.0 (educational; contact local)"}
def api(**p):
    p.update(format="json"); 
    u="https://commons.wikimedia.org/w/api.php?"+urllib.parse.urlencode(p)
    return json.load(urllib.request.urlopen(urllib.request.Request(u,headers=H)))
qs=sys.argv[1:]
for q in qs:
    r=api(action="query",generator="search",gsrsearch=q,gsrnamespace=6,gsrlimit=8,prop="imageinfo",iiprop="url|size|extmetadata",iiurlwidth=1600)
    print("##",q)
    for pg in (r.get("query",{}).get("pages",{}) or {}).values():
        ii=pg["imageinfo"][0];m=ii["extmetadata"]
        print(pg["title"],ii["width"],"x",ii["height"],"|",m.get("LicenseShortName",{}).get("value"),"|",m.get("Artist",{}).get("value","")[:40].replace("\n"," "))
