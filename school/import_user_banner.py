#!/usr/bin/env python3
"""One-shot import of an owner-supplied Canva-hosted banner into this repository.
The signed asset URL is deliberately temporary; the image is saved permanently to GitHub.
"""
from PIL import Image
from io import BytesIO
import os,urllib.request,urllib.error,re,pathlib
url=os.environ["CANVA_THUMB"]
variants=[
    url.replace("/height:76/","/height:774/").replace("/width:200?","/width:2033?"),
    url.replace("/height:76/","/height:774/").replace("/width:200?","/width:2033?").split("?")[0],
    url,
]
for i,candidate in enumerate(variants):
    try:
        request=urllib.request.Request(candidate,headers={"User-Agent":"Mozilla/5.0"})
        with urllib.request.urlopen(request,timeout=20) as response:
            data=response.read()
        im=Image.open(BytesIO(data))
        print("Candidate",i,"dimensions",im.size,"bytes",len(data))
        if im.width<200:continue
        path=pathlib.Path("assets/user-supplied-banner.webp")
        path.parent.mkdir(parents=True,exist_ok=True)
        from PIL import ImageFilter
        if im.width<1200:
            im=im.resize((1200,round(im.height*1200/im.width)),Image.Resampling.LANCZOS)
            im=im.filter(ImageFilter.UnsharpMask(radius=1.5,percent=85,threshold=2))
        im.convert("RGB").save(path,"WEBP",quality=84,method=6)
        print("Imported exact user banner:",path,path.stat().st_size)
        break
    except (urllib.error.HTTPError,urllib.error.URLError,ValueError) as exc:
        print("Candidate",i,"failed",type(exc).__name__)
else:
    raise SystemExit("Banner image preview was not available from Canva image CDN")
