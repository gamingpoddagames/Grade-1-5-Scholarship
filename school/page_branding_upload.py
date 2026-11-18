#!/usr/bin/env python3
"""Apply approved brand images to a managed Facebook Page.
Uses Graph API Page photos, picture and cover; never logs tokens.
"""
import argparse
import json
import os
import urllib.parse
import urllib.request
import urllib.error
import uuid
from pathlib import Path

def multipart(url, fields, image=None):
    boundary="Branding"+uuid.uuid4().hex
    payload=bytearray()
    for name,value in fields.items():
        payload.extend(f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"\r\n\r\n{value}\r\n'.encode())
    if image is not None:
        file=Path(image)
        mime="image/jpeg" if file.suffix.lower() in (".jpg",".jpeg") else "image/png"
        payload.extend(f'--{boundary}\r\nContent-Disposition: form-data; name="source"; filename="{file.name}"\r\nContent-Type: {mime}\r\n\r\n'.encode())
        payload.extend(file.read_bytes())
        payload.extend(b'\r\n')
    payload.extend(f'--{boundary}--\r\n'.encode())
    req=urllib.request.Request(url,data=bytes(payload),headers={"Content-Type":f"multipart/form-data; boundary={boundary}"},method="POST")
    try:
        with urllib.request.urlopen(req,timeout=120) as response:
            return json.load(response)
    except urllib.error.HTTPError as exc:
        # Do not reveal response body (potentially sensitive).
        raise RuntimeError(f"Facebook Graph API request failed with HTTP {exc.code}") from None

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--logo",required=True)
    parser.add_argument("--cover",required=True)
    args=parser.parse_args()
    page=os.getenv("FB_PAGE_ID")
    token=os.getenv("FB_PAGE_ACCESS_TOKEN")
    version=os.getenv("FB_GRAPH_VERSION","v27.0")
    if not page or not token:
        raise SystemExit("Facebook Page access secrets unavailable; branding not applied")
    base=f"https://graph.facebook.com/{version}/{page}"
    # Save photos as unpublished assets so the Page feed is not flooded.
    picture=multipart(base+"/photos",{"access_token":token,"published":"false","message":"පුංචි නැණ මඟ - නිල Logo"},args.logo)
    if not picture.get("id"):
        raise RuntimeError("Page logo photo creation did not return an ID")
    print("Page logo photo uploaded:",picture["id"])
    cover=multipart(base+"/photos",{"access_token":token,"published":"false","message":"පුංචි නැණ මඟ - නිල Cover"},args.cover)
    if not cover.get("id"):
        raise RuntimeError("Page cover photo creation did not return an ID")
    print("Page cover photo uploaded:",cover["id"])
    # Meta permissions may allow asset creation but reject Page appearance mutation.
    try:
        profile=multipart(base+"/picture",{"access_token":token,"photo":picture["id"]})
        print("Page profile picture API response:", "success" if profile.get("success") else "review response")
    except RuntimeError as exc:
        print("Page profile picture update unavailable:",exc)
    try:
        result=multipart(base,{"access_token":token,"cover":cover["id"],"no_feed_story":"true"})
        print("Page cover update API response:", "success" if result.get("success") else "review response")
    except RuntimeError as exc:
        print("Page cover update unavailable:",exc)
    print("Branding API operations finished. Confirm actual Page appearance manually.")

if __name__=="__main__":
    main()
